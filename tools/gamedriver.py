#!/usr/bin/env python3
"""Autonomous EU5 launcher, console hand, screenshot recorder, and process guard."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from eu5_slot import (
    EX_TEMPFAIL,
    SlotBusy,
    acquire,
    game_visible_fingerprint,
    inspect_owner,
    mark_pending,
    release_token,
    require_token,
)
from runtime_state import directory as runtime_state_directory

ROOT = Path(__file__).resolve().parents[1]
STATE = runtime_state_directory(ROOT) / "gamedriver_session.json"
# The installed build explicitly recognizes this display mode in its own UI
# layout scripts.  960x540 was rejected as an enum value and silently fell
# back to the 2560x1440 desktop mode before observer playback.
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


def enable_dpi_awareness() -> None:
    """Keep pygetwindow and pyautogui in the same physical-pixel coordinate space."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except AttributeError:
            pass


enable_dpi_awareness()


def config() -> dict[str, object]:
    return json.loads((ROOT / "config/local_paths.json").read_text(encoding="utf-8-sig"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_steam() -> None:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "tools/steam_ensure.ps1"),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    print(result.stdout.strip())


def close_game_crash_reporters(game_exe: Path) -> int:
    """Close only stale reporters belonging to this exact EU5 installation."""
    expected = (
        game_exe.parent / "crash_reporter" / "binaries" / "CrashReporter.exe"
    ).resolve()
    reporters: list[psutil.Process] = []
    for process in psutil.process_iter(("name", "exe")):
        try:
            if process.info["name"] != "CrashReporter.exe" or not process.info["exe"]:
                continue
            if Path(str(process.info["exe"])).resolve() == expected:
                reporters.append(process)
        except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
            continue
    for process in reporters:
        try:
            process.terminate()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    _, still_running = psutil.wait_procs(reporters, timeout=5)
    for process in still_running:
        try:
            process.kill()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    if reporters:
        print(f"gamedriver: closed {len(reporters)} stale EU5 crash reporter(s)")
    return len(reporters)


def set_fixed_settings(user_dir: Path) -> None:
    path = user_dir / "pdx_settings.json"
    value = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {}
    value.setdefault("Audio", {}).update(
        {
            "volume.bus:/": 0,
            "volume.vca:/MUSIC": 0,
            "volume.vca:/UI": 0,
            "volume.vca:/SFX": 0,
            "volume.vca:/AMBIENT_MAP": 0,
        }
    )
    value.setdefault("Graphics", {}).update(
        {
            # The installed default is Vulkan.  DX12 repeatedly exits inside
            # ffxFsr2ResourceIsNull on this host during observer runs even with
            # FSR disabled, so keep autonomous evidence on the stable backend.
            "renderer": "Vulkan",
            "display_mode": "windowed",
            "resolution": f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}",
            # Native scale is required on this host.  The installed FSR2 path
            # still initializes at sub-native scale even when the UI reports
            # upscaling disabled, and repeatedly crashed observer runs inside
            # ffxFsr2ResourceIsNull.  Native scale has remained stable.
            "render_scale": 1.0,
            "vsync": False,
            "setting_framerate_cap": "30",
            # The installed settings tooltip documents this as the maximum-speed
            # simulation priority toggle.  It is especially appropriate for
            # long autonomous Observer runs, where capture cadence matters more
            # than a smooth rendered frame rate.
            "maximize_tick_speed": True,
            "quality": "very_low",
            "mapobject_quality": "off",
            "anti_aliasing": "DISABLED",
            "portrait_multi_sampling": "x2",
            "texture_quality": "low",
            "anisotropic_filtering": "DISABLED",
            "refraction_quality": "disabled",
            "shadowmap_resolution": "disabled",
            "ssr_quality": "disabled",
            "blur_quality": "disabled",
            "low_quality_shaders": True,
            "animated_portraits": False,
            "portraits_ssao": False,
            "portraits_unsharp_masking": False,
            "bloom_quality": "disabled",
            "ssao": False,
            "depthoffield": False,
            "enable_particles": False,
            "unit_coa_resolution_size": "32 x 32",
            "gui_texture_streaming": True,
            "icon_scaling_quality": "none",
            "single_unit_armies": True,
        }
    )
    value.setdefault("Game", {}).update(
        {"skip_welcome_new_game": True, "first_time_playing": False}
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent="\t") + "\n", encoding="utf-8")


def state() -> dict[str, object]:
    return json.loads(STATE.read_text(encoding="utf-8"))


def save_state(value: dict[str, object]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def validate_state_identity(value: dict[str, object]) -> None:
    configured_user_dir = Path(str(config()["user_dir"])).resolve()
    session_repo = Path(str(value.get("repo", ""))).resolve()
    session_user_dir = Path(str(value.get("user_dir", ""))).resolve()
    if session_repo != ROOT.resolve():
        raise RuntimeError(
            f"session belongs to {session_repo}, not repository {ROOT.resolve()}"
        )
    if session_user_dir != configured_user_dir:
        raise RuntimeError(
            f"session user directory is {session_user_dir}, expected {configured_user_dir}"
        )


def process_from_state() -> psutil.Process:
    value = state()
    validate_state_identity(value)
    process = psutil.Process(int(value["pid"]))
    if process.create_time() != value["process_create_time"]:
        raise RuntimeError("PID was reused; refusing to control an unrelated process")
    token = str(value.get("slot_token", ""))
    if not token:
        raise RuntimeError("session predates the shared EU5 slot; refusing unsafe control")
    require_token(ROOT, token)
    return process


def stop_session_process(process: psutil.Process, timeout: int) -> bool:
    """Stop only the PID proven by this repository's tokenized session state."""
    try:
        process.terminate()
    except psutil.NoSuchProcess:
        return False
    _, alive = psutil.wait_procs([process], timeout=timeout)
    if alive:
        try:
            process.kill()
        except psutil.NoSuchProcess:
            pass
        psutil.wait_procs(alive, timeout=10)
    return True


def launch(args: argparse.Namespace) -> int:
    fingerprint = game_visible_fingerprint(ROOT)
    try:
        lease = acquire(
            ROOT,
            f"gamedriver launch: {args.mode}",
            fingerprint=fingerprint,
            scope="session",
        )
    except SlotBusy as exc:
        pending = mark_pending(ROOT, f"gamedriver:{args.mode}", fingerprint, exc.owner)
        print(f"gamedriver: DEFERRED — {exc}", file=sys.stderr)
        print(f"gamedriver: pending gate recorded at {pending}", file=sys.stderr)
        return EX_TEMPFAIL
    direct_lease = not lease.inherited
    process: psutil.Process | None = None
    try:
        ensure_steam()
        cfg = config()
        user_dir = Path(str(cfg["user_dir"]))
        game_exe = Path(str(cfg["game_exe"]))
        close_game_crash_reporters(game_exe)
        set_fixed_settings(user_dir)
        logs = user_dir / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        command = [
            str(game_exe),
            f"--user_dir={user_dir}",
            "--ignore-disable-mods-on-crash",
        ]
        if args.debug_mode:
            command.append("-debug_mode")
        if args.leavepops:
            command.append("-leavepops")
        command.extend(args.extra)
        flags = subprocess.CREATE_NEW_PROCESS_GROUP
        if args.hidden:
            flags |= subprocess.CREATE_NO_WINDOW
        popen = subprocess.Popen(
            command,
            cwd=game_exe.parent,
            creationflags=flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process = psutil.Process(popen.pid)
        value = {
            "pid": popen.pid,
            "process_create_time": process.create_time(),
            "started_at": now(),
            "command": command,
            "user_dir": str(user_dir),
            "error_log_initial_size": (logs / "error.log").stat().st_size
            if (logs / "error.log").exists()
            else 0,
            "mode": args.mode,
            "repo": str(ROOT.resolve()),
            "slot_token": lease.token,
            "slot_scope": lease.scope,
            "tree_fingerprint": fingerprint,
        }
        save_state(value)
        if direct_lease:
            lease.handoff(
                process,
                operation=f"gamedriver session: {args.mode}",
            )
        print(json.dumps(value, indent=2))
        return 0
    except Exception:
        if process is not None:
            stop_session_process(process, timeout=10)
        if direct_lease:
            release_token(ROOT, lease.token)
        raise


def _window_process_id(window) -> int:
    process_id = ctypes.c_ulong()
    ctypes.windll.user32.GetWindowThreadProcessId(
        window._hWnd,
        ctypes.byref(process_id),
    )
    return int(process_id.value)


def find_window():
    import pygetwindow

    target_pid = process_from_state().pid
    candidates = [
        window
        for window in pygetwindow.getAllWindows()
        # A minimized Win32 window reports a tiny title-bar geometry.  Keep it
        # eligible so activate_window() can restore it before asking for a
        # rendered frame; filtering it here makes the autonomous driver lose a
        # perfectly healthy game between screenshot and click.
        if "Europa Universalis V" in window.title
        and _window_process_id(window) == target_pid
    ]
    return max(candidates, key=lambda item: item.width * item.height) if candidates else None


def rendered_frame_state(window) -> tuple[bool, float]:
    """Return whether the game client area is visibly rendered and its non-black share."""
    import pyautogui

    title_height = min(32, max(0, window.height // 8))
    client_height = window.height - title_height
    if client_height < 40:
        return False, 0.0
    image = pyautogui.screenshot(
        region=(window.left, window.top + title_height, window.width, client_height)
    ).convert("RGB").resize((64, 36))
    pixels = image.load()
    total = image.width * image.height
    non_black = sum(
        1
        for y in range(image.height)
        for x in range(image.width)
        if max(pixels[x, y]) > 20
    )
    share = non_black / total
    return share >= 0.05, share


def is_hung_window(window) -> bool:
    """Use Windows' own hung-window check; a visible black window is not ready."""
    return bool(ctypes.windll.user32.IsHungAppWindow(window._hWnd))


def wait_ready(args: argparse.Namespace) -> int:
    process = process_from_state()
    value = state()
    user_dir = Path(str(value["user_dir"]))
    debug = user_dir / "logs/debug.log"
    deadline = time.monotonic() + args.timeout
    last_size = -1
    unchanged_since = time.monotonic()
    saw_window = False
    try:
        process.cpu_percent()
    except psutil.NoSuchProcess:
        print("gamedriver: process exited before readiness probe", file=sys.stderr)
        return 1
    while time.monotonic() < deadline:
        try:
            alive = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            alive = False
        if not alive:
            try:
                exit_code = process.wait(timeout=1)
            except psutil.NoSuchProcess:
                exit_code = "unknown"
            print(f"gamedriver: process exited with {exit_code}", file=sys.stderr)
            return 1
        window = find_window()
        saw_window = saw_window or window is not None
        responsive = bool(window) and not is_hung_window(window)
        rendered, non_black = rendered_frame_state(window) if window and responsive else (False, 0.0)
        size = debug.stat().st_size if debug.exists() else 0
        if size != last_size:
            last_size = size
            unchanged_since = time.monotonic()
        quiet = time.monotonic() - unchanged_since
        try:
            cpu = process.cpu_percent(interval=1)
        except psutil.NoSuchProcess:
            print("gamedriver: process exited during readiness probe", file=sys.stderr)
            return 1
        elapsed = time.monotonic() - (deadline - args.timeout)
        print(
            f"wait {elapsed:5.0f}s window={bool(window)} responsive={responsive} rendered={rendered} "
            f"nonblack={non_black:.1%} debug={size} quiet={quiet:.0f}s cpu={cpu:.1f}%",
            flush=True,
        )
        if (
            saw_window
            and responsive
            and rendered
            and elapsed >= args.minimum
            and quiet >= args.quiet_seconds
            and cpu < args.max_cpu
        ):
            value["ready_at"] = now()
            save_state(value)
            if getattr(args, "capture", None):
                session = getattr(args, "session", None) or datetime.now().strftime("%Y%m%d_%H%M%S")
                target = ROOT / "docs/screens" / session / f"{args.capture}.png"
                target.parent.mkdir(parents=True, exist_ok=True)
                save_window_capture(target)
            print("gamedriver: menu-ready heuristic passed")
            return 0
        time.sleep(4)
    print("gamedriver: menu-ready timeout", file=sys.stderr)
    return 2


def activate_window():
    window = find_window()
    if not window:
        raise RuntimeError("EU5 window not found")
    if window.isMinimized:
        window.restore()
    user32 = ctypes.windll.user32
    # Screenshot capture reads desktop pixels rather than a private window
    # buffer. Keep the game visibly above unrelated applications and refuse to
    # capture if Windows will not grant foreground ownership; this avoids
    # accidentally recording material outside the game surface.
    hwnd_topmost = -1
    swp_showwindow = 0x0040
    swp_noownerzorder = 0x0200
    user32.SetWindowPos(
        window._hWnd,
        hwnd_topmost,
        0,
        0,
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        swp_showwindow | swp_noownerzorder,
    )
    # pygetwindow objects retain their old geometry after SetWindowPos. Refresh
    # before converting normalized driver coordinates, otherwise clicks may land
    # on a different monitor even though screenshots look plausible.
    time.sleep(0.2)
    window = find_window()
    if not window:
        raise RuntimeError("EU5 window disappeared after fixed-window positioning")
    # A foreground EU5 window is already safe to capture.  Re-running the
    # cross-thread focus dance in that state can make Windows revoke focus from
    # a topmost window between the safety check and the input, despite the game
    # never leaving the foreground.
    if user32.GetForegroundWindow() == window._hWnd:
        return window
    try:
        window.activate()
    except Exception:
        user32.SetForegroundWindow(window._hWnd)
    foreground = user32.GetForegroundWindow()
    kernel32 = ctypes.windll.kernel32
    current_thread = kernel32.GetCurrentThreadId()
    foreground_thread = user32.GetWindowThreadProcessId(foreground, None) if foreground else 0
    game_thread = user32.GetWindowThreadProcessId(window._hWnd, None)
    attached_foreground = bool(foreground_thread) and bool(
        user32.AttachThreadInput(foreground_thread, current_thread, True)
    )
    attached_game = bool(game_thread) and bool(
        user32.AttachThreadInput(game_thread, current_thread, True)
    )
    try:
        user32.AllowSetForegroundWindow(-1)
        user32.BringWindowToTop(window._hWnd)
        user32.SetActiveWindow(window._hWnd)
        user32.SetFocus(window._hWnd)
        user32.SetForegroundWindow(window._hWnd)
    finally:
        if attached_game:
            user32.AttachThreadInput(game_thread, current_thread, False)
        if attached_foreground:
            user32.AttachThreadInput(foreground_thread, current_thread, False)
    for _ in range(4):
        user32.BringWindowToTop(window._hWnd)
        user32.SetForegroundWindow(window._hWnd)
        time.sleep(0.4)
        if user32.GetForegroundWindow() == window._hWnd:
            return window
    raise RuntimeError("EU5 could not be foregrounded; refusing desktop-pixel capture")


def focus_game():
    import pyautogui

    window = activate_window()
    pyautogui.click(
        window.left + int(window.width * 0.75),
        window.top + int(window.height * 0.45),
    )
    time.sleep(0.5)
    return window


def screenshot(args: argparse.Namespace) -> int:
    import pyautogui

    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target = ROOT / "docs/screens" / session / f"{args.name}.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    window = activate_window()
    image = pyautogui.screenshot(
        region=(window.left, window.top, window.width, window.height)
    )
    image.save(target)
    print(target)
    return 0


def click(args: argparse.Namespace) -> int:
    import pyautogui

    x, y = click_normalized(args.x, args.y, button=args.button)
    time.sleep(args.settle)
    print(
        f"clicked {args.button} normalized ({args.x:.3f}, {args.y:.3f}) at ({x}, {y})"
    )
    if args.capture:
        # Another topmost desktop application can briefly cover the game during
        # the settle period.  Re-activate and refresh the geometry before the
        # evidence capture so a post-input screenshot never documents an
        # unrelated window as if it were EU5 state.
        window = activate_window()
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def click_normalized(x_fraction: float, y_fraction: float, *, button: str = "left") -> tuple[int, int]:
    """Click a fixed-window UI target expressed as a fraction of the client area."""
    import pyautogui

    # The autonomous runner may leave the pointer at a desktop corner between
    # invocations.  PyAutoGUI otherwise aborts before it can move into the
    # already verified game window, turning a harmless parked pointer into a
    # false UI failure.  All actions remain constrained to ``activate_window``.
    pyautogui.FAILSAFE = False

    if not (0 <= x_fraction <= 1 and 0 <= y_fraction <= 1):
        raise ValueError("click coordinates must be normalized fractions from 0 through 1")
    window = activate_window()
    x = window.left + round(window.width * x_fraction)
    y = window.top + round(window.height * y_fraction)
    # Clausewitz/Jomini widgets can acknowledge hover yet drop pyautogui's
    # zero-duration click when the frame is composing a tooltip or modal.
    # A brief physical press/release is still imperceptible to the user and is
    # markedly more reliable for selector, event-option, and dialog controls.
    pyautogui.moveTo(x, y, duration=0.05)
    pyautogui.mouseDown(button=button)
    time.sleep(0.08)
    pyautogui.mouseUp(button=button)
    return x, y


def save_window_capture(target: Path) -> object:
    """Capture the foreground EU5 window, never the surrounding desktop."""
    import pyautogui

    window = activate_window()
    image = pyautogui.screenshot(
        region=(window.left, window.top, window.width, window.height)
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    print(target)
    return image


def autosave_fingerprint(user_dir: Path) -> list[dict[str, object]]:
    """Describe the newest rotating autosaves without parsing or mutating them."""
    candidates: list[Path] = []
    for directory_name in ("save games", "savegames"):
        directory = user_dir / directory_name
        if directory.exists():
            candidates.extend(directory.glob("autosave_*.eu5"))
    newest = sorted(
        {path.resolve() for path in candidates},
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )[:3]
    return [
        {
            "path": str(path.relative_to(user_dir)),
            "bytes": path.stat().st_size,
            "modified_utc": datetime.fromtimestamp(
                path.stat().st_mtime, timezone.utc
            ).isoformat(),
        }
        for path in newest
    ]


def wait_for_observer_pause(timeout: int, poll_interval: float = 1.0) -> bool:
    """Wait for the live Observer HUD's red pause banner after a menu transition."""
    import pyautogui

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            window = activate_window()
        except RuntimeError:
            return False
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        paused, ratio = observer_pause_banner(image)
        if paused:
            print(f"gamedriver: live Observer pause banner detected (red={ratio:.3f})")
            return True
        time.sleep(poll_interval)
    return False


def wait_for_transition_log(
    user_dir: Path, start_offset: int, timeout: int, cache_settle: int
) -> bool:
    """Wait for EU5's own MainMenu->Game completion marker after Continue.

    A loaded save can display an almost-full loading bar for several minutes;
    a fixed sleep was therefore unsafe.  The installed build writes state 4
    only after committing the MainMenu->Game transaction.  The same local log
    then records cached-data rebuilds; waiting for it to go quiet after their
    completion prevents clicks landing on the 98%-complete loading screen.
    """
    debug = user_dir / "logs" / "debug.log"
    deadline = time.monotonic() + timeout
    scan_offset = start_offset
    saw_state_four = False
    saw_cache_finish = False
    last_change = time.monotonic()
    last_size = start_offset
    while time.monotonic() < deadline:
        if debug.exists():
            size = debug.stat().st_size
            # A fresh engine transition can rotate or truncate debug.log.
            # Rebase rather than treating the old byte offset as permanent.
            if size < scan_offset:
                scan_offset = 0
            if size != last_size:
                last_change = time.monotonic()
                last_size = size
            if size > scan_offset:
                with debug.open("rb") as stream:
                    stream.seek(scan_offset)
                    suffix = stream.read().decode("utf-8", errors="replace")
                scan_offset = size
                saw_state_four = saw_state_four or (
                    "Setting Task state 4" in suffix and "MainMenu->Game" in suffix
                )
                saw_cache_finish = saw_cache_finish or (
                    "Finished ClearAndRecalculateCachedData" in suffix
                )
        if (
            saw_state_four
            and saw_cache_finish
            and time.monotonic() - last_change >= cache_settle
        ):
            print("gamedriver: MainMenu->Game and cached-data completion detected")
            return True
        time.sleep(2)
    return False


def loading_progress(image) -> float | None:
    """Estimate EU5's rendered new-game progress bar without OCR.

    The installed GUI uses a gold contiguous fill inside a dark horizontal
    track. Sampling its centre avoids the ornamental gold frame and remains
    stable across the fixed 1920x1080 client plus Windows title bar.
    """
    rgb = image.convert("RGB")
    y = round(rgb.height * 0.919)
    start = round(rgb.width * 0.061)
    end = round(rgb.width * 0.940)
    if end - start < 100:
        return None
    row = [rgb.getpixel((x, y)) for x in range(start, end)]
    gold = [
        red > 90 and green > 55 and red > blue * 1.45 and green > blue * 1.15
        for red, green, blue in row
    ]
    radius = 4
    smooth = [
        sum(gold[max(0, index - radius):index + radius + 1]) >= radius + 1
        for index in range(len(gold))
    ]
    # The loading bar begins with a short empty inset. Reject ordinary menu
    # frames, whose pixels do not form a sustained left-origin gold run.
    if sum(smooth[:32]) < 8:
        return None
    filled = 0
    false_run = 0
    for index, active in enumerate(smooth):
        if active:
            false_run = 0
            filled = index + 1
        else:
            false_run += 1
            if false_run >= 18:
                filled = max(0, index - false_run + 1)
                break
    return max(0.0, min(100.0, 100.0 * filled / len(smooth)))


def capture_new_game_loading(args: argparse.Namespace) -> int:
    """Click New Game and retain sharp frames at specific rendered percentages."""
    import pyautogui

    process = process_from_state()
    value = state()
    user_dir = Path(str(value["user_dir"]))
    debug = user_dir / "logs/debug.log"
    debug_offset = debug.stat().st_size if debug.exists() else 0
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    target_dir.mkdir(parents=True, exist_ok=True)
    requested = tuple(sorted(set(args.percentages)))
    pending = list(requested)
    records: list[dict[str, object]] = []

    save_window_capture(target_dir / "loading_000_menu.png")
    click_normalized(args.x, args.y)
    started = time.monotonic()
    deadline = started + args.timeout
    saw_loading = False
    last_progress: float | None = None
    saw_state_four = False
    non_loading_since: float | None = None
    selector_ready = False
    while time.monotonic() < deadline:
        try:
            if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
                raise RuntimeError("EU5 exited during new-game loading capture")
            window = activate_window()
        except (psutil.NoSuchProcess, RuntimeError) as error:
            print(f"gamedriver: loading capture stopped: {error}", file=sys.stderr)
            break
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        progress = loading_progress(image)
        elapsed = time.monotonic() - started
        if progress is not None:
            saw_loading = True
            last_progress = progress
            non_loading_since = None
            while pending and progress >= pending[0]:
                requested_progress = pending.pop(0)
                target = target_dir / (
                    f"loading_{requested_progress:03d}pct_"
                    f"observed_{round(progress):03d}.png"
                )
                image.save(target)
                records.append(
                    {
                        "requested_percent": requested_progress,
                        "observed_percent": round(progress, 2),
                        "elapsed_seconds": round(elapsed, 2),
                        "path": str(
                            target.relative_to(ROOT)
                            if target.is_relative_to(ROOT)
                            else target
                        ),
                    }
                )
                print(
                    f"gamedriver: captured loading {progress:.1f}% for "
                    f"{requested_progress}% target: {target}",
                    flush=True,
                )
        # State 4 may be emitted while the visible new-game generator is still
        # near the beginning of its work.  Treat it only as a prerequisite;
        # the loading bar must then disappear and remain absent for several
        # frames before the country selector is safe to click.
        if debug.exists():
            with debug.open("rb") as stream:
                stream.seek(min(debug_offset, debug.stat().st_size))
                suffix = stream.read().decode("utf-8", errors="replace")
            if "Setting Task state 4" in suffix and "MainMenu->Game" in suffix:
                saw_state_four = True
        if saw_loading and progress is None:
            if non_loading_since is None:
                non_loading_since = time.monotonic()
            elif saw_state_four and time.monotonic() - non_loading_since >= 5:
                print("gamedriver: country selector remained visible for 5s")
                selector_ready = True
                break
        time.sleep(args.interval)

    manifest = {
        "started_at": now(),
        "session": session,
        "requested_percentages": requested,
        "captured": records,
        "saw_loading": saw_loading,
        "last_observed_percent": (
            round(last_progress, 2) if last_progress is not None else None
        ),
        "completed_targets": not pending,
        "selector_ready": selector_ready,
    }
    manifest_path = target_dir / "loading_capture.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(manifest_path)
    if not saw_loading or len(records) < args.minimum_captures or not selector_ready:
        print(
            f"gamedriver: loading gate incomplete (captures={len(records)}, "
            f"minimum={args.minimum_captures}, selector_ready={selector_ready})",
            file=sys.stderr,
        )
        return 1
    return 0


def enter_live_observer(args: argparse.Namespace, target_dir: Path, prefix: str) -> bool:
    """Turn the loaded country-selection map into a paused live Observer HUD."""
    # A visible country-selection map is not necessarily input-ready directly
    # after its cache transaction.  Wait before the first Observer click;
    # screenshots from the local recovery probe showed that clicking earlier
    # merely opened the map's Country tooltip and did not toggle Observer.
    time.sleep(args.country_selection_settle)
    click_normalized(0.23, 0.047)
    time.sleep(args.ui_settle)
    save_window_capture(target_dir / f"{prefix}_observer_enabled.png")
    # Toggling Observer leaves its dropdown above the map. Physical Escape
    # opens the selector's "go back to main menu" confirmation; a second
    # physical Escape cancels it and dismisses the dropdown while preserving
    # Observer. This is invariant across Windows DPI scaling, unlike the
    # confirmation button coordinates. An ordinary outside click instead
    # disables Observer.
    press_scan_code(0x01)
    time.sleep(args.ui_settle)
    press_scan_code(0x01)
    time.sleep(args.ui_settle)
    save_window_capture(target_dir / f"{prefix}_observer_popup_dismissed.png")
    # The map is visible as soon as cached data finishes, but the observer
    # start button is not reliably interactive until its following UI frame.
    # This value was calibrated against the local save-load sequence.
    for start_attempt in range(1, 3):
        time.sleep(args.observer_enable_settle if start_attempt == 1 else args.ui_settle)
        click_normalized(0.50, 0.860)
        time.sleep(args.ui_settle)
        save_window_capture(target_dir / f"{prefix}_start_attempt{start_attempt}.png")
        if wait_for_observer_pause(max(15, args.live_timeout // 2)):
            save_window_capture(target_dir / f"{prefix}_live.png")
            return True
        print(
            f"gamedriver: Observer start attempt {start_attempt} did not show "
            "the pause banner; retrying"
        )
    return False


def recovery_evidence_path(session: str) -> Path:
    return ROOT / "docs/screens" / session / "observer_recovery.json"


def record_recovery_evidence(session: str, item: dict[str, object]) -> None:
    """Append machine-readable checkpoint/relaunch evidence beside screenshots."""
    path = recovery_evidence_path(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        history = json.loads(path.read_text(encoding="utf-8"))
    else:
        history = []
    history.append(item)
    path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")


def resume_observer_from_autosave(args: argparse.Namespace, cycle: int) -> bool:
    """Launch, continue the latest autosave, and return at the live Observer HUD.

    EU5's normal menu has a stable, locally verified route for a previously
    observed save: Continue -> Continue as Observer -> Observe -> Start
    Observing the game.  This is deliberately UI-driven instead of depending
    on undocumented save-file formats or console load semantics.
    """
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    cfg = config()
    user_dir = Path(str(cfg["user_dir"]))
    prefix = f"recovery_{cycle:02d}"
    evidence: dict[str, object] = {
        "cycle": cycle,
        "started_at": now(),
        "autosaves_before": autosave_fingerprint(user_dir),
        "steps": [],
    }

    for ui_attempt in range(1, 3):
        evidence["ui_attempt"] = ui_attempt
        print(f"gamedriver: recovery cycle {cycle}, menu attempt {ui_attempt}")
        launched = launch(
            argparse.Namespace(
                mode="mod",
                leavepops=False,
                debug_mode=False,
                hidden=False,
                extra=[],
            )
        )
        if launched:
            evidence["steps"].append(f"launch-deferred-or-failed:{launched}")
            record_recovery_evidence(session, evidence)
            return False
        ready = wait_ready(
            argparse.Namespace(
                timeout=args.menu_timeout,
                minimum=args.menu_minimum,
                quiet_seconds=args.menu_quiet_seconds,
                max_cpu=args.menu_max_cpu,
            )
        )
        if ready:
            evidence["steps"].append("menu-ready-failed")
            record_recovery_evidence(session, evidence)
            stop(argparse.Namespace(timeout=10))
            continue

        save_window_capture(target_dir / f"{prefix}_menu_attempt{ui_attempt}.png")
        debug = user_dir / "logs" / "debug.log"
        debug_offset = debug.stat().st_size if debug.exists() else 0
        # The branded total-conversion menu places Continue lower than the
        # vanilla-layout coordinate used by the first recovery prototype.
        click_normalized(0.14, 0.360)
        time.sleep(args.ui_settle)
        save_window_capture(target_dir / f"{prefix}_continue_attempt{ui_attempt}.png")
        # The dialog advertises Enter as the Ok binding.  It is more reliable
        # than a mouse click while the menu is still composing its widgets.
        time.sleep(args.confirm_settle)
        activate_window()
        press_scan_code(0x1C)
        if not wait_for_transition_log(
            user_dir, debug_offset, args.load_timeout, args.cache_settle
        ):
            evidence["steps"].append("mainmenu-to-game-transition-timeout")
            record_recovery_evidence(session, evidence)
            stop(argparse.Namespace(timeout=10))
            continue
        time.sleep(args.ui_settle)
        save_window_capture(target_dir / f"{prefix}_country_select_attempt{ui_attempt}.png")

        # In the country-selection lobby, enabling Observer reveals the
        # bottom-centre 'Start Observing the game' control.  Do not use Space
        # here: the clock has not been started at this stage.
        attempt_prefix = f"{prefix}_attempt{ui_attempt}"
        if enter_live_observer(args, target_dir, attempt_prefix):
            evidence["steps"].append("live-observer-ready")
            evidence["completed_at"] = now()
            evidence["autosaves_after"] = autosave_fingerprint(user_dir)
            record_recovery_evidence(session, evidence)
            return True
        evidence["steps"].append("live-observer-banner-timeout")
        record_recovery_evidence(session, evidence)
        stop(argparse.Namespace(timeout=10))
    return False


def resume_observer(args: argparse.Namespace) -> int:
    """Expose the autosave-to-live-Observer transition as a bounded command."""
    if resume_observer_from_autosave(args, cycle=0):
        print("gamedriver: autosave resumed into live Observer")
        return 0
    print("gamedriver: could not resume latest autosave into live Observer", file=sys.stderr)
    return 1


def start_observer(args: argparse.Namespace) -> int:
    """Exercise the final country-selection-to-Observer UI transition."""
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    if enter_live_observer(args, target_dir, "manual_selection"):
        print("gamedriver: country selection entered live Observer")
        return 0
    print("gamedriver: could not enter live Observer", file=sys.stderr)
    return 1


def observer_recover(args: argparse.Namespace) -> int:
    """Run Observer from durable autosaves, relaunching after renderer exits."""
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    args.session = session
    if not resume_observer_from_autosave(args, cycle=0):
        return 1
    # `--seconds` is gameplay time under observation, not menu/load time.
    # A cold autosave reload can legitimately take several minutes.
    started = time.monotonic()
    restarts = 0
    while True:
        remaining = args.seconds - (time.monotonic() - started)
        if remaining <= 0:
            print(f"gamedriver: recovery observer completed with {restarts} restart(s)")
            return 0
        monitor = argparse.Namespace(
            seconds=remaining,
            capture_interval=args.capture_interval,
            status_interval=args.status_interval,
            poll_interval=args.poll_interval,
            session=session,
            maximum_speed=args.maximum_speed,
        )
        result = observer_run(monitor)
        if not result:
            print(f"gamedriver: recovery observer completed with {restarts} restart(s)")
            return 0
        restarts += 1
        record_recovery_evidence(
            session,
            {
                "cycle": restarts,
                "renderer_exit_at": now(),
                "autosaves_after_exit": autosave_fingerprint(
                    Path(str(config()["user_dir"]))
                ),
            },
        )
        if restarts > args.max_restarts:
            print(
                f"gamedriver: renderer exited {restarts} time(s), exceeding "
                f"--max-restarts={args.max_restarts}",
                file=sys.stderr,
            )
            return 1
        if not resume_observer_from_autosave(args, cycle=restarts):
            return 1


def drag(args: argparse.Namespace) -> int:
    """Drag across the rendered game window using normalized coordinates."""
    import pyautogui

    # Window activation is sufficient for pointer drags. Unlike `focus_game`,
    # it does not click the map first and therefore preserves the inspected
    # country while testing viewport movement.
    window = activate_window()
    coordinates = (args.start_x, args.start_y, args.end_x, args.end_y)
    if any(not 0 <= value <= 1 for value in coordinates):
        raise ValueError("drag coordinates must be normalized fractions from 0 through 1")
    start = (
        window.left + round(window.width * args.start_x),
        window.top + round(window.height * args.start_y),
    )
    end = (
        window.left + round(window.width * args.end_x),
        window.top + round(window.height * args.end_y),
    )
    pyautogui.moveTo(*start)
    pyautogui.dragTo(*end, duration=args.duration, button=args.button)
    time.sleep(args.settle)
    print(
        f"dragged {args.button} normalized ({args.start_x:.3f}, {args.start_y:.3f}) "
        f"to ({args.end_x:.3f}, {args.end_y:.3f})"
    )
    if args.capture:
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def move(args: argparse.Namespace) -> int:
    """Move the pointer without clicking, for edge-scroll and hover probes."""
    import pyautogui

    window = activate_window()
    if not (0 <= args.x <= 1 and 0 <= args.y <= 1):
        raise ValueError("move coordinates must be normalized fractions from 0 through 1")
    x = window.left + round(window.width * args.x)
    y = window.top + round(window.height * args.y)
    pyautogui.moveTo(x, y, duration=args.duration)
    time.sleep(args.settle)
    print(f"moved normalized ({args.x:.3f}, {args.y:.3f}) to ({x}, {y})")
    if args.capture:
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def scroll(args: argparse.Namespace) -> int:
    """Turn the mouse wheel at a normalized in-window point for map zoom probes."""
    import pyautogui

    window = activate_window()
    if not (0 <= args.x <= 1 and 0 <= args.y <= 1):
        raise ValueError("scroll coordinates must be normalized fractions from 0 through 1")
    x = window.left + round(window.width * args.x)
    y = window.top + round(window.height * args.y)
    pyautogui.FAILSAFE = False
    pyautogui.moveTo(x, y, duration=args.duration)
    # EU5 clamps a large synthetic wheel delta to roughly one zoom step. Send
    # real detents across separate frames so +40/-40 actually reach the two
    # map-scale endpoints used by the geography runtime gate.
    direction = 1 if args.clicks >= 0 else -1
    for _ in range(abs(args.clicks)):
        pyautogui.scroll(direction)
        time.sleep(0.035)
    time.sleep(args.settle)
    print(
        f"scrolled {args.clicks:+d} detents at normalized "
        f"({args.x:.3f}, {args.y:.3f})"
    )
    if args.capture:
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def hotkey(args: argparse.Namespace) -> int:
    import pyautogui

    window = focus_game()
    keys = tuple(part.strip() for part in args.keys.split("+") if part.strip())
    if not keys:
        raise ValueError("hotkey must contain one or more keys separated by '+'")
    pyautogui.hotkey(*keys)
    time.sleep(args.settle)
    print(f"hotkey sent: {'+'.join(keys)}")
    if args.capture:
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def type_text(args: argparse.Namespace) -> int:
    """Paste text into a fixed-window edit box without changing map selection."""
    import pyautogui
    import pyperclip

    if not (0 <= args.x <= 1 and 0 <= args.y <= 1):
        raise ValueError("text coordinates must be normalized fractions from 0 through 1")
    window = activate_window()
    x = window.left + round(window.width * args.x)
    y = window.top + round(window.height * args.y)
    previous = pyperclip.paste()
    try:
        pyautogui.click(x, y)
        time.sleep(0.25)
        pyperclip.copy(args.text)
        # Jomini's edit box does not consistently expose Select All to the
        # Windows Ctrl+A virtual key on an AZERTY layout. Its installed
        # max-length is 26, so bounded Backspace replacement is deterministic.
        pyautogui.press("end")
        pyautogui.press("backspace", presses=32, interval=0.01)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(args.settle)
    finally:
        pyperclip.copy(previous)
    print(f"text entered at normalized ({args.x:.3f}, {args.y:.3f})")
    if args.capture:
        session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
        target = ROOT / "docs/screens" / session / f"{args.capture}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        image.save(target)
        print(target)
    return 0


def press_console_key(vk: int) -> None:
    key_up = 0x0002
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, key_up, 0)


def press_scan_code(scan_code: int) -> None:
    key_up = 0x0002
    scan_flag = 0x0008
    ctypes.windll.user32.keybd_event(0, scan_code, scan_flag, 0)
    ctypes.windll.user32.keybd_event(0, scan_code, scan_flag | key_up, 0)


def debug_console_visible(image) -> bool:
    """Detect the fixed-layout console from its prompt/toolbox gold borders."""
    rgb = image.convert("RGB")
    width, height = rgb.size
    gold = 0
    for y_fraction in (0.683, 0.710, 0.719, 0.754, 0.777, 0.785):
        for x_fraction in (0.03, 0.05, 0.155, 0.28):
            red, green, blue = rgb.getpixel(
                (round(width * x_fraction), round(height * y_fraction))
            )
            if (
                red >= 90
                and green >= 60
                and red >= green * 1.08
                and green >= blue * 1.18
            ):
                gold += 1
    return gold >= 8


def console(args: argparse.Namespace) -> int:
    import pyautogui

    # The debug console is a window-level surface; foregrounding it must not
    # first select a map country, which made country-inspection runs unstable.
    window = activate_window()
    # Physical key directly below Escape (scan code 0x29) works across QWERTY
    # and AZERTY layouts; virtual-key fallbacks cover OEM mappings.
    if args.already_open:
        visible = debug_console_visible(
            pyautogui.screenshot(
                region=(window.left, window.top, window.width, window.height)
            )
        )
        if visible:
            pyautogui.click(
                window.left + int(window.width * 0.14),
                window.top + int(window.height * 0.74),
            )
            time.sleep(0.4)
        else:
            press_scan_code(0x29)
            time.sleep(1)
    else:
        # Normal driver commands begin and end with a closed console.  Toggle
        # it deterministically instead of inferring state from gold UI pixels:
        # tag switches can make ordinary panels resemble the console frame.
        press_scan_code(0x29)
        time.sleep(1)
    if args.paste:
        import pyperclip

        pyperclip.copy(args.command)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.5)
    else:
        for index, segment in enumerate(args.command.split("_")):
            if index:
                # Raw VK_8 without Shift emits '_' on the active French layout.
                press_console_key(0x38)
            pyautogui.write(segment, interval=0.015)
    press_scan_code(0x1C)
    time.sleep(args.settle)
    if not args.leave_open:
        activate_window()
        press_scan_code(0x29)
        time.sleep(0.8)
    print(f"console command sent: {args.command}")
    return 0


def key(args: argparse.Namespace) -> int:
    import pyautogui

    # Preserve map/country selection when sending viewport or UI shortcuts.
    activate_window()
    if args.char:
        pyautogui.press(args.code)
    elif args.scan:
        press_scan_code(int(args.code, 0))
    else:
        press_console_key(int(args.code, 0))
    time.sleep(args.settle)
    print(f"key sent: {'scan' if args.scan else 'vk'} {args.code}")
    return 0


def observer_pause_banner(image) -> tuple[bool, float]:
    """Detect the centered red `Game is Paused` banner in the fixed EU5 layout.

    This deliberately uses only a narrow, stable UI region.  It avoids sending
    a blind Space key while the game is already running, which would otherwise
    alternate between accelerating and pausing an Observer playback run.
    """
    width, height = image.size
    left = int(width * 0.42)
    top = int(height * 0.16)
    right = int(width * 0.58)
    bottom = int(height * 0.24)
    region = image.crop((left, top, right, bottom)).convert("RGB").resize((80, 40))
    pixels = list(
        region.get_flattened_data()
        if hasattr(region, "get_flattened_data")
        else region.getdata()
    )
    red = sum(
        1
        for value_r, value_g, value_b in pixels
        if value_r >= 80 and value_r >= value_g * 1.45 and value_r >= value_b * 1.65
    )
    ratio = red / len(pixels)
    return ratio >= 0.18, ratio


def observer_run(args: argparse.Namespace) -> int:
    """Autonomously keep an active Observer session running and capture evidence."""
    import pyautogui

    try:
        process = process_from_state()
    except (FileNotFoundError, psutil.NoSuchProcess):
        print("gamedriver: no active game session", file=sys.stderr)
        return 1
    value = state()
    user_dir = Path(str(value["user_dir"]))
    error_log = user_dir / "logs" / "error.log"
    error_size = error_log.stat().st_size if error_log.exists() else 0
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    target_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + args.seconds
    next_capture = time.monotonic()
    next_status = time.monotonic()
    captures = 0
    resumes = 0
    last_pause_state: bool | None = None

    if args.maximum_speed:
        # The installed default.profile binds increase_speed to SDL scancodes
        # 46 ('=') and 87 (keypad '+').  Windows' physical keypad-plus scan code
        # is 0x4E.  Fresh games begin at speed three.  Speed five is the highest
        # stable setting for this 230-million-population world on the reference
        # host; the uncapped sixth/seventh engine speeds can starve the renderer.
        activate_window()
        for _ in range(2):
            press_scan_code(0x4E)
            time.sleep(0.08)
        press_scan_code(0x39)
        time.sleep(0.5)

    while time.monotonic() < deadline:
        try:
            alive = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            alive = False
        if not alive:
            print("gamedriver: observer process exited", file=sys.stderr)
            return 1
        try:
            window = activate_window()
        except RuntimeError as error:
            # A crashing EU5 process can briefly remain visible to psutil while
            # Windows has already destroyed its top-level window.  Treat that
            # as a bounded observer termination rather than emitting a Python
            # traceback that obscures the game-side crash evidence.
            print(
                f"gamedriver: observer window unavailable ({error}); "
                "ending monitor",
                file=sys.stderr,
            )
            return 1
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        paused, red_ratio = observer_pause_banner(image)
        if paused:
            press_scan_code(0x39)
            resumes += 1
            time.sleep(0.35)
        if time.monotonic() >= next_capture:
            capture = target_dir / f"observer_{captures:04d}.png"
            image.save(capture)
            print(capture)
            captures += 1
            next_capture += args.capture_interval
        current_error_size = error_log.stat().st_size if error_log.exists() else 0
        if current_error_size != error_size:
            print(
                f"observer: error.log changed {error_size}->{current_error_size}",
                flush=True,
            )
            error_size = current_error_size
        if time.monotonic() >= next_status or paused != last_pause_state:
            elapsed = args.seconds - max(0.0, deadline - time.monotonic())
            print(
                f"observer {elapsed:5.1f}s paused={paused} banner_red={red_ratio:.3f} "
                f"resumes={resumes} captures={captures}",
                flush=True,
            )
            last_pause_state = paused
            next_status += args.status_interval
        time.sleep(args.poll_interval)
    print(
        f"gamedriver: observer interval complete ({args.seconds:.1f}s; "
        f"resumes={resumes}; captures={captures}; error_log={error_size})"
    )
    return 0


def stop(args: argparse.Namespace) -> int:
    try:
        value = state()
    except FileNotFoundError:
        print("gamedriver: already stopped (no configured session)")
        return 0
    try:
        validate_state_identity(value)
    except RuntimeError as exc:
        print(f"gamedriver: refusing foreign session state — {exc}", file=sys.stderr)
        return 1
    token = str(value.get("slot_token", ""))
    if not token:
        print(
            "gamedriver: refusing to stop an unleased legacy session",
            file=sys.stderr,
        )
        return 1
    scope = str(value.get("slot_scope", "session"))
    process: psutil.Process | None = None
    try:
        candidate = psutil.Process(int(value["pid"]))
        if candidate.create_time() != value["process_create_time"]:
            raise RuntimeError("PID was reused; refusing to stop an unrelated process")
        process = candidate
    except psutil.NoSuchProcess:
        pass
    owner = inspect_owner(ROOT, reclaim_stale=False)
    if owner is not None and owner.get("token") != token:
        print(
            "gamedriver: refusing to stop a session owned by another token",
            file=sys.stderr,
        )
        return 1
    if process is not None:
        require_token(ROOT, token)
    stopped = stop_session_process(process, args.timeout) if process else False
    if process is not None:
        close_game_crash_reporters(Path(str(config()["game_exe"])))
    if scope == "session":
        release_token(ROOT, token)
    if stopped:
        print(f"gamedriver: stopped configured EU5 session: {value['pid']}")
    else:
        print("gamedriver: configured EU5 session was already stopped")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="subcommand", required=True)
    launch_parser = sub.add_parser("launch")
    launch_parser.add_argument("--mode", choices=("vanilla", "mod"), default="mod")
    launch_parser.add_argument("--leavepops", action="store_true")
    launch_parser.add_argument(
        "--no-debug-mode",
        action="store_false",
        dest="debug_mode",
        help="Launch without -debug_mode for a bounded non-debug renderer probe.",
    )
    launch_parser.set_defaults(debug_mode=True)
    launch_parser.add_argument("--hidden", action="store_true")
    launch_parser.add_argument("extra", nargs="*")
    launch_parser.set_defaults(func=launch)
    wait_parser = sub.add_parser("wait")
    wait_parser.add_argument("--timeout", type=int, default=480)
    wait_parser.add_argument("--minimum", type=int, default=45)
    wait_parser.add_argument("--quiet-seconds", type=int, default=15)
    wait_parser.add_argument("--capture", help="capture the ready frame before returning")
    wait_parser.add_argument("--session")
    wait_parser.add_argument(
        "--max-cpu",
        type=float,
        default=1000,
        help="aggregate process CPU percentage ceiling after logs quiesce",
    )
    wait_parser.set_defaults(func=wait_ready)
    screenshot_parser = sub.add_parser("screenshot")
    screenshot_parser.add_argument("name")
    screenshot_parser.add_argument("--session")
    screenshot_parser.set_defaults(func=screenshot)
    loading_parser = sub.add_parser("capture-new-game-loading")
    loading_parser.add_argument("--session", help="evidence session directory")
    loading_parser.add_argument("--timeout", type=int, default=900)
    loading_parser.add_argument("--interval", type=float, default=0.25)
    loading_parser.add_argument("--x", type=float, default=0.14)
    loading_parser.add_argument("--y", type=float, default=0.43)
    loading_parser.add_argument(
        "--percentages",
        type=int,
        nargs="+",
        default=[2, 5, 8, 12, 18, 25, 37, 50, 65, 80, 95],
    )
    loading_parser.add_argument("--minimum-captures", type=int, default=6)
    loading_parser.set_defaults(func=capture_new_game_loading)
    click_parser = sub.add_parser("click")
    click_parser.add_argument("x", type=float, help="horizontal normalized position")
    click_parser.add_argument("y", type=float, help="vertical normalized position")
    click_parser.add_argument(
        "--button", choices=("left", "middle", "right"), default="left"
    )
    click_parser.add_argument("--settle", type=float, default=2)
    click_parser.add_argument("--capture", help="capture this name after the click")
    click_parser.add_argument("--session")
    click_parser.set_defaults(func=click)
    drag_parser = sub.add_parser("drag")
    drag_parser.add_argument("start_x", type=float, help="starting horizontal normalized position")
    drag_parser.add_argument("start_y", type=float, help="starting vertical normalized position")
    drag_parser.add_argument("end_x", type=float, help="ending horizontal normalized position")
    drag_parser.add_argument("end_y", type=float, help="ending vertical normalized position")
    drag_parser.add_argument("--button", choices=("left", "middle", "right"), default="right")
    drag_parser.add_argument("--duration", type=float, default=1)
    drag_parser.add_argument("--settle", type=float, default=2)
    drag_parser.add_argument("--capture", help="capture this name after the drag")
    drag_parser.add_argument("--session")
    drag_parser.set_defaults(func=drag)
    move_parser = sub.add_parser("move")
    move_parser.add_argument("x", type=float, help="horizontal normalized position")
    move_parser.add_argument("y", type=float, help="vertical normalized position")
    move_parser.add_argument("--duration", type=float, default=0.2)
    move_parser.add_argument("--settle", type=float, default=2)
    move_parser.add_argument("--capture", help="capture this name after waiting")
    move_parser.add_argument("--session")
    move_parser.set_defaults(func=move)
    scroll_parser = sub.add_parser("scroll")
    scroll_parser.add_argument(
        "clicks", type=int, help="mouse-wheel detents; positive zooms in"
    )
    scroll_parser.add_argument("--x", type=float, default=0.5)
    scroll_parser.add_argument("--y", type=float, default=0.5)
    scroll_parser.add_argument("--duration", type=float, default=0.2)
    scroll_parser.add_argument("--settle", type=float, default=2)
    scroll_parser.add_argument("--capture", help="capture this name after scrolling")
    scroll_parser.add_argument("--session")
    scroll_parser.set_defaults(func=scroll)
    hotkey_parser = sub.add_parser("hotkey")
    hotkey_parser.add_argument("keys", help="keys separated by '+', e.g. ctrl+s")
    hotkey_parser.add_argument("--settle", type=float, default=2)
    hotkey_parser.add_argument("--capture", help="capture this name after the hotkey")
    hotkey_parser.add_argument("--session")
    hotkey_parser.set_defaults(func=hotkey)
    text_parser = sub.add_parser("text")
    text_parser.add_argument("text")
    text_parser.add_argument("--x", type=float, required=True)
    text_parser.add_argument("--y", type=float, required=True)
    text_parser.add_argument("--settle", type=float, default=2)
    text_parser.add_argument("--capture", help="capture this name after text entry")
    text_parser.add_argument("--session")
    text_parser.set_defaults(func=type_text)
    console_parser = sub.add_parser("console")
    console_parser.add_argument("command")
    console_parser.add_argument("--settle", type=float, default=2)
    console_parser.add_argument("--already-open", action="store_true")
    console_parser.add_argument("--leave-open", action="store_true")
    console_parser.add_argument("--paste", action="store_true")
    console_parser.set_defaults(func=console)
    key_parser = sub.add_parser("key")
    key_parser.add_argument("code")
    key_parser.add_argument("--scan", action="store_true")
    key_parser.add_argument("--char", action="store_true")
    key_parser.add_argument("--settle", type=float, default=1)
    key_parser.set_defaults(func=key)
    observer_parser = sub.add_parser("observer")
    observer_parser.add_argument(
        "--seconds", type=float, default=45, help="bounded playback interval"
    )
    observer_parser.add_argument(
        "--capture-interval", type=float, default=10, help="seconds between captures"
    )
    observer_parser.add_argument(
        "--status-interval", type=float, default=10, help="seconds between status lines"
    )
    observer_parser.add_argument(
        "--poll-interval", type=float, default=1, help="pause/process polling interval"
    )
    observer_parser.add_argument("--session", help="evidence session directory")
    observer_parser.add_argument(
        "--maximum-speed",
        action="store_true",
        help="start a fresh paused Observer session at the configured maximum-tick setting",
    )
    observer_parser.set_defaults(func=observer_run)
    resume_parser = sub.add_parser("resume-observer")
    resume_parser.add_argument("--session", help="evidence session directory")
    resume_parser.add_argument("--menu-timeout", type=int, default=240)
    resume_parser.add_argument("--menu-minimum", type=int, default=25)
    resume_parser.add_argument("--menu-quiet-seconds", type=int, default=15)
    resume_parser.add_argument("--menu-max-cpu", type=float, default=1000)
    resume_parser.add_argument(
        "--load-timeout",
        type=int,
        default=600,
        help="maximum seconds for EU5's logged MainMenu-to-Game transition",
    )
    resume_parser.add_argument(
        "--cache-settle",
        type=int,
        default=15,
        help="quiet seconds after the logged cached-data rebuild",
    )
    resume_parser.add_argument(
        "--live-timeout",
        type=int,
        default=60,
        help="seconds to wait for the live Observer pause banner",
    )
    resume_parser.add_argument("--ui-settle", type=float, default=2)
    resume_parser.add_argument(
        "--confirm-settle",
        type=float,
        default=5,
        help="seconds for the Continue confirmation dialog to become interactive",
    )
    resume_parser.add_argument(
        "--observer-enable-settle",
        type=float,
        default=10,
        help="seconds for the post-cache Observer start button to become interactive",
    )
    resume_parser.add_argument(
        "--country-selection-settle",
        type=float,
        default=15,
        help="seconds for a cache-complete country-selection map to accept input",
    )
    resume_parser.set_defaults(func=resume_observer)
    start_observer_parser = sub.add_parser("start-observer")
    start_observer_parser.add_argument("--session", help="evidence session directory")
    start_observer_parser.add_argument("--live-timeout", type=int, default=60)
    start_observer_parser.add_argument("--ui-settle", type=float, default=2)
    start_observer_parser.add_argument("--observer-enable-settle", type=float, default=10)
    start_observer_parser.add_argument("--country-selection-settle", type=float, default=0)
    start_observer_parser.set_defaults(func=start_observer)
    recover_parser = sub.add_parser("observer-recover")
    recover_parser.add_argument(
        "--seconds", type=float, default=600, help="total live-Observer monitoring interval"
    )
    recover_parser.add_argument("--max-restarts", type=int, default=8)
    recover_parser.add_argument("--capture-interval", type=float, default=10)
    recover_parser.add_argument("--status-interval", type=float, default=10)
    recover_parser.add_argument("--poll-interval", type=float, default=1)
    recover_parser.add_argument("--session", help="evidence session directory")
    recover_parser.add_argument(
        "--maximum-speed",
        action="store_true",
        help="use the configured maximum-tick setting after each autosave resume",
    )
    recover_parser.add_argument("--menu-timeout", type=int, default=240)
    recover_parser.add_argument("--menu-minimum", type=int, default=25)
    recover_parser.add_argument("--menu-quiet-seconds", type=int, default=15)
    recover_parser.add_argument("--menu-max-cpu", type=float, default=1000)
    recover_parser.add_argument("--load-timeout", type=int, default=600)
    recover_parser.add_argument("--cache-settle", type=int, default=15)
    recover_parser.add_argument("--live-timeout", type=int, default=60)
    recover_parser.add_argument("--ui-settle", type=float, default=2)
    recover_parser.add_argument("--confirm-settle", type=float, default=5)
    recover_parser.add_argument("--observer-enable-settle", type=float, default=10)
    recover_parser.add_argument("--country-selection-settle", type=float, default=15)
    recover_parser.set_defaults(func=observer_recover)
    stop_parser = sub.add_parser("stop")
    stop_parser.add_argument("--timeout", type=int, default=10)
    stop_parser.set_defaults(func=stop)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
