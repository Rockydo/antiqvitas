#!/usr/bin/env python3
"""Autonomous EU5 launcher, console hand, screenshot recorder, and process guard."""

from __future__ import annotations

import argparse
import atexit
import csv
import ctypes
import json
import os
import re
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
OBSERVER_MONITOR_LOCK = runtime_state_directory(ROOT) / "gamedriver_observer.lock"
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


def release_observer_monitor_lock(pid: int) -> None:
    """Release only the monitor lease created by this exact process."""
    try:
        payload = json.loads(OBSERVER_MONITOR_LOCK.read_text(encoding="utf-8"))
        if int(payload.get("pid", -1)) == pid:
            OBSERVER_MONITOR_LOCK.unlink(missing_ok=True)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        pass


def acquire_observer_monitor_lock() -> None:
    """Permit one keyboard-driving observer monitor at a time.

    A cancelled orchestration shell can leave its child Python process alive on
    Windows.  Without this lease, two monitors alternate Space and invalidate a
    supposedly continuous campaign.  Stale PID files are recovered atomically.
    """
    OBSERVER_MONITOR_LOCK.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"pid": os.getpid(), "started_at": now()}) + "\n"
    for _ in range(3):
        try:
            descriptor = os.open(
                OBSERVER_MONITOR_LOCK,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
            )
        except FileExistsError:
            try:
                owner = json.loads(
                    OBSERVER_MONITOR_LOCK.read_text(encoding="utf-8")
                )
                owner_pid = int(owner.get("pid", -1))
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                owner_pid = -1
            if owner_pid == os.getpid():
                return
            if owner_pid > 0 and psutil.pid_exists(owner_pid):
                try:
                    command = " ".join(psutil.Process(owner_pid).cmdline()).lower()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    command = ""
                if "gamedriver.py" in command and (
                    " observer " in f" {command} "
                    or " observer-recover " in f" {command} "
                ):
                    raise RuntimeError(
                        f"observer monitor already active in PID {owner_pid}"
                    )
            try:
                OBSERVER_MONITOR_LOCK.unlink()
            except FileNotFoundError:
                pass
            continue
        else:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(payload)
            atexit.register(release_observer_monitor_lock, os.getpid())
            return
    raise RuntimeError("could not acquire the observer monitor lease")


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


def select_playset(mode: str) -> None:
    """Make the requested launch mode real before starting EU5.

    The game executable reads the persisted launcher playset; a launch flag does
    not choose between vanilla and ANTIQVITAS.  Keep this in the driver so every
    standalone control run has the mode it reports in its session state.
    """
    argument = "--enable" if mode == "mod" else "--vanilla"
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools/enable_mod.py"), argument],
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


def set_fixed_settings(user_dir: Path, resolution: str | None = None) -> None:
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
            "display_mode": "windowed",
            "resolution": resolution or f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}",
            # These are the installed JSON keys (not the display labels).  A
            # missing key lets the renderer choose an FSR2 path; that path has
            # repeatedly crashed this host inside ffxFsr2ResourceIsNull.
            "upscale": "DISABLED",
            "upscale_quality": "off",
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
    # Keep automated UI coordinates in the same 1:1 space as the fixed
    # window.  A persisted 110% UI scale makes Clausewitz draw controls below
    # their input hitboxes on this host, so menu actions can target the wrong
    # row even though the screenshot looks correct.
    value.setdefault("GUI", {}).update({"scale": "1.0"})
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
        select_playset(args.mode)
        cfg = config()
        user_dir = Path(str(cfg["user_dir"]))
        game_exe = Path(str(cfg["game_exe"]))
        close_game_crash_reporters(game_exe)
        set_fixed_settings(user_dir, args.resolution)
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
    time.sleep(0.18)
    pyautogui.mouseDown(button=button)
    time.sleep(0.08)
    pyautogui.mouseUp(button=button)
    return x, y


def save_window_capture(target: Path) -> object:
    """Capture the foreground EU5 window, never the surrounding desktop."""
    image = capture_window_image()
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    print(target)
    return image


def capture_window_image() -> object:
    """Return a current physical-pixel capture of the foreground EU5 window."""
    import pyautogui

    window = activate_window()
    return pyautogui.screenshot(
        region=(window.left, window.top, window.width, window.height)
    )


def agenda_overlay_visible(image: object) -> bool:
    """Recognize the large brown startup Agenda, not merely the pause banner."""
    if country_selector_visible(image):
        # The country-selection map's unexplored brown sea otherwise matches
        # the Agenda panel heuristic and would click Close on the lobby.
        return False
    width, height = image.size
    panel = image.convert("RGB").crop(
        (round(width * 0.30), round(height * 0.08),
         round(width * 0.70), round(height * 0.93))
    )
    pixels = tuple(panel.get_flattened_data())
    brown = sum(
        red > green * 1.15 and red > blue * 1.15 and red > 35
        for red, green, blue in pixels
    )
    return brown / max(1, len(pixels)) >= 0.35


def country_selector_visible(image: object) -> bool:
    """True while Random Country / Observe still occupy the lobby top bar."""
    width, height = image.size
    # Skip the Windows title bar (~0.03 of this 1920x1080 windowed frame).
    region = image.convert("RGB").crop(
        (round(width * 0.175), round(height * 0.032),
         round(width * 0.300), round(height * 0.062))
    )
    pixels = tuple(region.get_flattened_data())
    navy = sum(
        red < 60 and blue > 50 and blue > red + 20
        for red, green, blue in pixels
    )
    return navy / max(1, len(pixels)) >= 0.20


def find_play_button(image: object) -> tuple[float, float] | None:
    """Locate the dark-bronze Play-as-country control on the country-selection map."""
    width, height = image.size
    rgb = image.convert("RGB")
    x0, x1 = round(width * 0.40), round(width * 0.60)
    y0, y1 = round(height * 0.835), round(height * 0.885)
    xs: list[int] = []
    ys: list[int] = []
    for y in range(y0, y1, 2):
        for x in range(x0, x1, 2):
            red, green, blue = rgb.getpixel((x, y))
            if (
                40 < red < 150
                and 20 < green < 100
                and blue < 55
                and red > green > blue
                and red - blue > 20
            ):
                xs.append(x)
                ys.append(y)
    if len(xs) < 40:
        return None
    return (sum(xs) / len(xs) / width, sum(ys) / len(ys) / height)


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
    """Wait for a fully rendered Continue-to-game transition.

    A loaded save can display an almost-full loading bar for several minutes;
    a fixed sleep is unsafe.  The installed build writes state 4 and a cached-
    data completion marker *before* the final visible loading frame disappears,
    so neither log marker alone authorizes selector input.  Require both the
    local transition records and five stable rendered frames without the
    verified loading bar before clicking an Observer control.
    """
    debug = user_dir / "logs" / "debug.log"
    deadline = time.monotonic() + timeout
    scan_offset = start_offset
    saw_state_four = False
    saw_cache_finish = False
    last_change = time.monotonic()
    last_size = start_offset
    non_loading_since: float | None = None
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
        logs_ready = (
            saw_state_four
            and saw_cache_finish
            and time.monotonic() - last_change >= cache_settle
        )
        if logs_ready:
            try:
                import pyautogui

                window = activate_window()
                image = pyautogui.screenshot(
                    region=(window.left, window.top, window.width, window.height)
                )
                visible_loading = loading_progress(image) is not None
            except RuntimeError:
                visible_loading = True
            if visible_loading:
                non_loading_since = None
            elif non_loading_since is None:
                non_loading_since = time.monotonic()
            elif time.monotonic() - non_loading_since >= 5:
                print(
                    "gamedriver: MainMenu->Game, cached-data, and visible "
                    "loading completion detected"
                )
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
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    target_dir.mkdir(parents=True, exist_ok=True)
    # A responsive branded window can appear while its first resource cache is
    # still consuming input.  Clicking New Game in that interval is ignored,
    # while the loading-bar pixel heuristic can mistake main-menu ornament for
    # a low percentage and later report a false selector.  Require a rendered,
    # log-quiet menu before establishing the transition-log offset or clicking.
    ready = wait_ready(argparse.Namespace(
        timeout=min(args.timeout, 480),
        minimum=args.menu_minimum,
        quiet_seconds=args.menu_quiet_seconds,
        max_cpu=1000,
        capture=None,
        session=session,
    ))
    if ready:
        print("gamedriver: main menu did not become input-ready", file=sys.stderr)
        return ready
    debug_offset = debug.stat().st_size if debug.exists() else 0
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
    observer_image = save_window_capture(
        target_dir / f"{prefix}_observer_enabled.png"
    )
    # Stock 1.3.11 can require a one-time confirmation when the active game
    # rule forbids changing countries after entering Observer.  The conversion
    # overrides that rule for its autonomous test surface, so this modal was
    # previously visible only in paired vanilla controls.  If left open, both
    # subsequent Start clicks land harmlessly behind it and the driver reports
    # a misleading live-game failure.  Recognize the dialog's two equal action
    # buttons and choose its explicit right-hand confirmation; do not apply the
    # relaxed pair rule to normal in-game event handling.
    confirmation, reason, candidate_count = observer_modal_action(
        observer_image, accept_confirmation_pair=True
    )
    if confirmation is not None and reason == "confirmation_rightmost":
        click_normalized(
            confirmation[0] / observer_image.width,
            confirmation[1] / observer_image.height,
        )
        time.sleep(args.ui_settle)
        save_window_capture(target_dir / f"{prefix}_observer_confirmed.png")
        print(
            "gamedriver: accepted Observer game-rule confirmation "
            f"({candidate_count} action candidates)"
        )
    # The enabled-Observer dropdown does not cover the start button. Starting
    # directly with the dropdown open is deterministic.  The former two-Escape
    # workaround became unsafe in 1.3.11: depending on frame timing it could
    # accept the selector's go-back action and silently return to the main menu.
    # The map is visible as soon as cached data finishes, but the start button
    # is not reliably interactive until its following UI frame.
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
                resolution="1920x1080",
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
        # The branded 1920x1080 menu puts Continue at y=0.327.  The former
        # 0.360 coordinate landed on New Game and silently reset an AD 7
        # recovery attempt to 1.1.1.
        click_normalized(0.14, 0.327)
        time.sleep(args.ui_settle)
        save_window_capture(target_dir / f"{prefix}_continue_attempt{ui_attempt}.png")
        # The 1.3.11 Continue confirmation is visually styled like an ordinary
        # question dialog, but its only action is the gold ``Continue`` row at
        # the lower left.  Neither the physical Enter scan code nor VK_RETURN
        # activates it on the current build.  Click the explicit action after
        # a complete settle frame; this also prevents a silent timeout followed
        # by selector clicks against the still-open main-menu dialog.
        time.sleep(args.confirm_settle)
        click_normalized(0.210, 0.526)
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


def start_country(args: argparse.Namespace) -> int:
    """Start the country already selected by the new-game map.

    ``capture-new-game-loading`` enters through the requested map coordinate,
    which leaves that country selected in the lobby.  Starting it directly is
    essential for player-country runtime gates: toggling Observer first lets
    January on-start effects execute before a later console tag takeover.
    """
    session = args.session or datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = ROOT / "docs/screens" / session
    time.sleep(args.country_selection_settle)
    click_normalized(args.country_x, args.country_y)
    time.sleep(args.ui_settle)
    save_window_capture(target_dir / "manual_country_selected.png")
    # Country-map tooltips cover Play. Park inside the left country panel so
    # the map does not edge-scroll (the title bar previously panned to the
    # Arctic and made the Agenda heuristic fire on brown ocean).
    import pyautogui

    window = activate_window()
    pyautogui.moveTo(
        window.left + round(window.width * 0.14),
        window.top + round(window.height * 0.42),
        duration=0.15,
    )
    time.sleep(max(1.0, args.ui_settle))
    dismissed = save_window_capture(target_dir / "manual_country_tooltip_dismissed.png")
    located = find_play_button(dismissed)
    if located is not None:
        print(f"gamedriver: Play button at ({located[0]:.3f}, {located[1]:.3f})")
    start_x = located[0] if located is not None else args.start_x
    start_y = located[1] if located is not None else args.start_y
    for attempt in range(1, 3):
        time.sleep(args.start_enable_settle if attempt == 1 else args.ui_settle)
        click_normalized(start_x, start_y)
        time.sleep(args.ui_settle)
        attempt_image = save_window_capture(
            target_dir / f"manual_country_start_attempt{attempt}.png"
        )
        if country_selector_visible(attempt_image):
            relocated = find_play_button(attempt_image)
            if relocated is not None:
                start_x, start_y = relocated
                print(
                    f"gamedriver: lobby still visible; Play retry at "
                    f"({start_x:.3f}, {start_y:.3f})"
                )
            print("gamedriver: Play click did not leave country selection")
            continue
        if attempt == 1:
            # A direct player start opens the Agenda overlay before the normal
            # paused HUD. Its Close button is stable at this native layout. If
            # the user has disabled the Agenda, this lands harmlessly on the
            # map while the game is still paused.
            # The overlay can render before its input context is ready. Wait
            # until it is visibly present, then allow a complete settle frame;
            # if the user's preference already suppresses it, do not click the
            # underlying map at the old fixed coordinate.
            agenda_image = attempt_image
            agenda_deadline = time.monotonic() + 8
            while (
                not agenda_overlay_visible(agenda_image)
                and time.monotonic() < agenda_deadline
            ):
                time.sleep(0.25)
                agenda_image = capture_window_image()
            if agenda_overlay_visible(agenda_image):
                time.sleep(2)
                if args.disable_startup_agenda:
                    click_normalized(0.322, 0.902)
                    time.sleep(args.ui_settle)
                for close_attempt in range(1, 3):
                    click_normalized(0.665, 0.902)
                    time.sleep(args.ui_settle)
                    closed_image = save_window_capture(
                        target_dir
                        / f"manual_country_agenda_close_attempt{close_attempt}.png"
                    )
                    if not agenda_overlay_visible(closed_image):
                        break
                    time.sleep(2)
            save_window_capture(target_dir / "manual_country_agenda_dismissed.png")
        if wait_for_observer_pause(max(45, args.live_timeout)):
            save_window_capture(target_dir / "manual_country_live.png")
            print("gamedriver: selected country entered live game")
            return 0
        print(
            f"gamedriver: country start attempt {attempt} did not show the "
            "pause banner; retrying"
        )
    print("gamedriver: could not start selected country", file=sys.stderr)
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


def wait_loading_complete(args: argparse.Namespace) -> int:
    """Wait for a currently active save-load plate to disappear visibly.

    Console ``load`` does not emit the menu transition markers used by
    ``resume-observer``.  Visual completion is the only safe common contract:
    never issue a follow-up console command while the percentage plate remains.
    """
    import pyautogui

    deadline = time.monotonic() + args.timeout
    stable = 0
    saw_loading = False
    while time.monotonic() < deadline:
        window = activate_window()
        image = pyautogui.screenshot(
            region=(window.left, window.top, window.width, window.height)
        )
        progress = loading_progress(image)
        if progress is None:
            stable += 1
            if stable >= args.stable_frames:
                if args.require_loading_plate and not saw_loading:
                    stable = 0
                    time.sleep(args.interval)
                    continue
                if args.session:
                    capture = ROOT / "docs/screens" / args.session / "load_complete.png"
                    capture.parent.mkdir(parents=True, exist_ok=True)
                    image.save(capture)
                    print(capture)
                print(
                    "gamedriver: visible load complete"
                    + (" after loading plate" if saw_loading else " (no loading plate seen)")
                )
                return 0
        else:
            saw_loading = True
            stable = 0
        time.sleep(args.interval)
    raise RuntimeError("timed out waiting for visible load completion")


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
    left = int(width * 0.44)
    top = int(height * 0.18)
    right = int(width * 0.56)
    bottom = int(height * 0.22)
    region = image.crop((left, top, right, bottom)).convert("RGB").resize((80, 40))
    pixels = list(
        region.get_flattened_data()
        if hasattr(region, "get_flattened_data")
        else region.getdata()
    )
    strict_red = sum(
        1
        for value_r, value_g, value_b in pixels
        if value_r >= 80 and value_r >= value_g * 1.45 and value_r >= value_b * 1.65
    )
    muted_red = sum(
        1
        for value_r, value_g, value_b in pixels
        # The open notification drawer is a uniform dark brown (roughly
        # 43/32/25 on the native capture) in this same screen band.  Requiring
        # actual red luminance keeps its hue from impersonating the muted
        # diagonally-striped pause plaque.
        if value_r >= 60 and value_r >= value_g * 1.25 and value_r >= value_b * 1.35
    )
    strict_ratio = strict_red / len(pixels)
    muted_ratio = muted_red / len(pixels)
    # Event-triggered pauses use the diagonally striped muted banner, whereas a
    # manual pause uses the solid red variant.  Both occupy this exact narrow
    # normalized band.
    # Native authored events render the striped plaque substantially darker
    # than manual pauses on this production path (the Immensum Bellum window
    # measures about 0.24).  The notification drawer cannot satisfy this lower
    # bound because its red channel remains below the >=60 luminance guard.
    return strict_ratio >= 0.18 or muted_ratio >= 0.20, max(
        strict_ratio, muted_ratio
    )


def observer_modal_action(
    image, *, accept_confirmation_pair: bool = False
) -> tuple[tuple[int, int] | None, str, int]:
    """Return a safe action point for a blocking central EU5 dialog.

    Event choices and report dialogs use the installed interface's blue action
    button texture.  Detecting those connected components is substantially safer
    than clicking a fixed point whenever the pause banner is visible: a normal
    player pause has no such component, while option counts and report layouts
    vary.  The search is deliberately restricted to the lower half of the central
    dialog area so map water, side panels, and the bottom HUD cannot qualify.
    """
    try:
        import cv2
        import numpy
    except ImportError:
        return None, "opencv_unavailable", 0

    rgb = numpy.asarray(image.convert("RGB"))
    height, width = rgb.shape[:2]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    mask = cv2.inRange(hsv, (90, 60, 40), (125, 255, 255))
    mask[: int(height * 0.54), :] = 0
    # Peace-treaty and stacked victory acknowledgements place their Ok row
    # below the older 0.79 chancellor-report bound.  Keep the bottom HUD
    # (compass / outliner chrome near 0.95) out of the search.
    mask[int(height * 0.94) :, :] = 0
    mask[:, : int(width * 0.34)] = 0
    mask[:, int(width * 0.66) :] = 0
    _, _, stats, _ = cv2.connectedComponentsWithStats(mask)
    candidates: list[tuple[int, int, int, int, int]] = []
    for x, y, box_width, box_height, area in stats[1:]:
        if not (50 <= box_width <= int(width * 0.31)):
            continue
        if not (12 <= box_height <= 60 and area >= 800):
            continue
        if box_width / box_height < 2.2:
            continue
        candidates.append(
            (int(x), int(y), int(box_width), int(box_height), int(area))
        )
    candidates.sort(key=lambda box: (box[1], box[0]))
    if not candidates:
        return None, "none", 0

    # Chancellor/succession reports place a descriptive button and a compact OK
    # button on the same row.  Select that rightmost compact action.  Authored
    # event choices are vertically stacked, for which the first option is the
    # deterministic unattended-production choice.
    first_y = candidates[0][1]
    same_row = [box for box in candidates if abs(box[1] - first_y) <= 10]
    stacked_event_actions = [
        box for box in candidates
        if box[0] > width * 0.35
        and box[0] + box[2] < width * 0.65
        and box[2] > width * 0.20
    ]
    compact_report_actions = [
        box for box in candidates
        # Chancellor Ok sits near 0.53; peace-treaty Ok near 0.516; a lone
        # centred death/succession Ok sits near 0.482.  "Go to" remains left
        # of 0.45 on the measured layouts.
        if box[0] > width * 0.47
        and box[1] > height * 0.58
        and box[2] < width * 0.08
    ]
    compact_goto_ok_pairs = []
    if len(same_row) == 2:
        left_box, right_box = sorted(same_row, key=lambda box: box[0])
        compact_pair = (
            abs(left_box[2] - right_box[2]) <= width * 0.02
            and width * 0.028 <= left_box[2] <= width * 0.09
            and width * 0.40 <= left_box[0] <= width * 0.50
            and width * 0.48 <= right_box[0] <= width * 0.58
        )
        if compact_pair:
            compact_goto_ok_pairs.append(right_box)
    centered_overlay_acknowledgements = [
        box for box in candidates
        if width * 0.38 < box[0] < width * 0.48
        and height * 0.60 < box[1] < height * 0.68
        and width * 0.07 < box[2] < width * 0.14
        and any(
            other[1] > box[1] + box[3]
            and other[2] > width * 0.20
            for other in candidates
        )
    ]
    # A compact report is a foreground acknowledgement.  It must win over any
    # wide actions still visible in a window underneath it; otherwise a report
    # stacked over a situation panel can make the unattended driver click the
    # obscured panel and leave the map in that situation's visualization.
    # When both are present, the tiny right-side OK is the acknowledgement;
    # the wider centred row is "Show Character Information" and leaves the
    # report open.  Some report variants expose only that centred action, so it
    # remains the fallback ahead of any underlying situation choices.
    if compact_report_actions:
        selected = max(compact_report_actions, key=lambda box: box[0])
        reason = "report_ok_single"
    elif compact_goto_ok_pairs:
        selected = compact_goto_ok_pairs[0]
        reason = "report_ok_compact_pair"
    elif centered_overlay_acknowledgements:
        selected = min(
            centered_overlay_acknowledgements, key=lambda box: (box[1], box[0])
        )
        reason = "report_ok_overlay"
    elif len(stacked_event_actions) >= 2 and (
        max(box[1] for box in stacked_event_actions)
        - min(box[1] for box in stacked_event_actions)
    ) > 15:
        selected = min(stacked_event_actions, key=lambda box: (box[1], box[0]))
        reason = "event_first_option"
    elif len(same_row) >= 2 and min(box[2] for box in same_row) * 2 < max(
        box[2] for box in same_row
    ):
        selected = max(same_row, key=lambda box: box[0])
        reason = "report_ok"
    elif accept_confirmation_pair and len(same_row) == 2:
        left_box, right_box = sorted(same_row, key=lambda box: box[0])
        widths_match = abs(left_box[2] - right_box[2]) <= width * 0.015
        confirmation_geometry = (
            widths_match
            and height * 0.54 < left_box[1] < height * 0.66
            and width * 0.34 < left_box[0] < width * 0.46
            and width * 0.54 < right_box[0] < width * 0.66
            and width * 0.07 < left_box[2] < width * 0.13
            and width * 0.07 < right_box[2] < width * 0.13
        )
        if not confirmation_geometry:
            return None, "none", len(candidates)
        selected = right_box
        reason = "confirmation_rightmost"
    else:
        # A map tooltip can contain one blue debug row in the same broad
        # screen region as an event.  It is not actionable and, after an event
        # closes above the map, repeatedly clicking it can keep a manually
        # paused game stuck forever.  Accept a lone fallback only when it has
        # the wide, centred geometry of a genuine authored choice.
        central_wide = [
            box for box in candidates
            if box[0] > width * 0.35
            and box[0] + box[2] < width * 0.65
            and box[2] > width * 0.18
        ]
        if not central_wide:
            return None, "none", len(candidates)
        selected = min(central_wide, key=lambda box: (box[1], box[0]))
        reason = "event_first_option"
    x, y, box_width, box_height, _ = selected
    return (x + box_width // 2, y + box_height // 2), reason, len(candidates)


def gui_resource_counts(pid: int) -> tuple[int | None, int | None]:
    """Return process GDI and USER object counts on Windows."""
    handle = None
    try:
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return None, None
        gdi = int(ctypes.windll.user32.GetGuiResources(handle, 0))
        user = int(ctypes.windll.user32.GetGuiResources(handle, 1))
        return gdi, user
    except (AttributeError, OSError):
        return None, None
    finally:
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)


def gpu_memory_mib() -> tuple[int | None, int | None]:
    """Return total used/installed NVIDIA VRAM, if the host exposes it."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None, None
    if result.returncode:
        return None, None
    rows = []
    for line in result.stdout.splitlines():
        try:
            used, total = (int(value.strip()) for value in line.split(",", 1))
        except (TypeError, ValueError):
            continue
        rows.append((used, total))
    return (
        (sum(used for used, _ in rows), sum(total for _, total in rows))
        if rows else (None, None)
    )


def observer_telemetry(
    process: psutil.Process,
    *,
    elapsed: float,
    paused: bool,
    resumes: int,
    captures: int,
    error_size: int,
    crash_count: int,
) -> dict[str, object]:
    """Sample the resource surfaces required by the long-runtime gates."""
    memory = process.memory_info()._asdict()
    system_memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    gdi, user = gui_resource_counts(process.pid)
    gpu_used, gpu_total = gpu_memory_mib()
    try:
        handles = process.num_handles()
    except (AttributeError, psutil.AccessDenied, psutil.NoSuchProcess):
        handles = None
    try:
        threads = process.num_threads()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        threads = None
    return {
        "utc": now(),
        "elapsed_seconds": round(elapsed, 3),
        "pid": process.pid,
        "paused": int(paused),
        "resumes": resumes,
        "captures": captures,
        "rss_mib": round(memory.get("rss", 0) / 1048576, 3),
        "vms_mib": round(memory.get("vms", 0) / 1048576, 3),
        "private_mib": round(memory.get("private", 0) / 1048576, 3),
        "pagefile_mib": round(memory.get("pagefile", 0) / 1048576, 3),
        "system_used_mib": round(system_memory.used / 1048576, 3),
        "system_available_mib": round(system_memory.available / 1048576, 3),
        "swap_used_mib": round(swap.used / 1048576, 3),
        "gpu_used_mib": gpu_used,
        "gpu_total_mib": gpu_total,
        "gdi_objects": gdi,
        "user_objects": user,
        "handles": handles,
        "threads": threads,
        "error_log_bytes": error_size,
        "crash_directories": crash_count,
    }


def append_csv(path: Path, row: dict[str, object]) -> None:
    exists = path.is_file() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(row))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def append_driver_event(path: Path, kind: str, **payload: object) -> None:
    event = {"utc": now(), "kind": kind, **payload}
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def observer_run(args: argparse.Namespace) -> int:
    """Autonomously keep an active Observer session running and capture evidence."""
    import pyautogui

    try:
        acquire_observer_monitor_lock()
    except RuntimeError as exc:
        print(f"gamedriver: {exc}", file=sys.stderr)
        return 1
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
    telemetry_path = target_dir / "resource_telemetry.csv"
    event_path = target_dir / "driver_events.jsonl"
    crash_root = user_dir / "crashes"
    deadline = time.monotonic() + args.seconds
    next_capture = time.monotonic()
    next_status = time.monotonic()
    existing_captures = [
        int(match.group(1))
        for path in target_dir.glob("observer_*.png")
        if (match := re.fullmatch(r"observer_(\d+)\.png", path.name))
    ]
    existing_modals = [
        int(match.group(1))
        for path in target_dir.glob("modal_*_before.png")
        if (match := re.fullmatch(r"modal_(\d+)_before\.png", path.name))
    ]
    captures = max(existing_captures, default=-1) + 1
    resumes = max(existing_modals, default=-1) + 1
    last_pause_state: bool | None = None
    paused_without_action_since: float | None = None
    resume_sent_for_pause = False

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
        # Leave the actual unpause to the verified loop below.  Sending Space
        # here raced the first composed frame: the stale pause banner caused
        # the loop to send a second Space and silently pause the campaign
        # again after only a few days.
        time.sleep(0.5)

    # A direct country start can leave the pointer over the selected capital's
    # army or navy. Its large pinned hover card obscures central report/event
    # buttons, so park on the title bar before the first detector frame.
    initial_window = activate_window()
    pyautogui.moveTo(
        initial_window.left + initial_window.width // 2,
        initial_window.top + 8,
        duration=0.05,
    )
    time.sleep(0.25)

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
        action, action_reason, candidate_count = observer_modal_action(image)
        # Character-death and chancellor reports can be non-pausing overlays.
        # Their compact OK layout is safe to dismiss even while simulation runs;
        # wide authored choices still require a verified pause banner.
        may_act = paused or action_reason.startswith("report_ok")
        if may_act:
            if action is not None:
                paused_without_action_since = None
                resume_sent_for_pause = False
                modal_capture = target_dir / f"modal_{resumes:04d}_before.png"
                image.save(modal_capture)
                # PyGetWindow reports DPI-logical window coordinates on this
                # host while ImageGrab returns physical screenshot pixels.
                # Convert the detected image point back into the window's input
                # coordinate space before clicking it.
                input_x = int(round(action[0] * window.width / image.width))
                input_y = int(round(action[1] * window.height / image.height))
                target_x = window.left + input_x
                target_y = window.top + input_y
                # Event-option widgets do not always accept a synthetic click
                # in the same frame that first establishes their hover state.
                # Give Jomini one composed hover frame, then use an explicit
                # physical press/release.  This is particularly important when
                # a report was just dismissed from above an authored event.
                pyautogui.moveTo(target_x, target_y, duration=0.08)
                time.sleep(0.18)
                pyautogui.mouseDown(button="left")
                time.sleep(0.08)
                pyautogui.mouseUp(button="left")
                resumes += 1
                append_driver_event(
                    event_path,
                    "modal_action",
                    capture=modal_capture.name,
                    action_reason=action_reason,
                    candidate_count=candidate_count,
                    image_x=action[0],
                    image_y=action[1],
                    input_x=input_x,
                    input_y=input_y,
                    resumes=resumes,
                )
                time.sleep(0.7)
                # Park away from the revealed map so the next frame cannot
                # mistake a location tooltip for another event choice.
                pyautogui.moveTo(
                    window.left + window.width // 2,
                    window.top + 8,
                    duration=0.05,
                )
                time.sleep(0.12)
                after = pyautogui.screenshot(
                    region=(window.left, window.top, window.width, window.height)
                )
                after.save(target_dir / f"modal_{resumes - 1:04d}_after.png")
            elif paused:
                # The pause banner is composed one or more frames before some
                # authored event windows.  Do not toggle Space immediately:
                # allow the modal detector a full second to see the choice UI,
                # then resume only a genuinely bare pause.
                if paused_without_action_since is None:
                    paused_without_action_since = time.monotonic()
                elif (
                    (
                        not resume_sent_for_pause
                        and time.monotonic() - paused_without_action_since >= 1.0
                    )
                    or (
                        resume_sent_for_pause
                        and time.monotonic() - paused_without_action_since >= 4.0
                    )
                ):
                    press_scan_code(0x39)
                    resumes += 1
                    # Keep the timestamp so a still-visible pause banner is a
                    # failed attempt, not a terminal success.  Retry after a
                    # bounded four-second confirmation window until the next
                    # frame proves that time is actually running.
                    paused_without_action_since = time.monotonic()
                    resume_sent_for_pause = True
                    append_driver_event(
                        event_path, "pause_resumed", elapsed_seconds=round(
                            args.seconds - max(0.0, deadline - time.monotonic()), 3
                        ), resumes=resumes,
                    )
                    time.sleep(0.35)
        else:
            paused_without_action_since = None
            resume_sent_for_pause = False
        if time.monotonic() >= next_capture:
            capture = target_dir / f"observer_{captures:04d}.png"
            image.save(capture)
            print(capture)
            append_driver_event(
                event_path, "screenshot", capture=capture.name, captures=captures + 1
            )
            captures += 1
            next_capture += args.capture_interval
        current_error_size = error_log.stat().st_size if error_log.exists() else 0
        if current_error_size != error_size:
            print(
                f"observer: error.log changed {error_size}->{current_error_size}",
                flush=True,
            )
            append_driver_event(
                event_path, "error_log_changed", before=error_size,
                after=current_error_size,
            )
            error_size = current_error_size
        if time.monotonic() >= next_status or paused != last_pause_state:
            elapsed = args.seconds - max(0.0, deadline - time.monotonic())
            crash_count = sum(
                1 for path in crash_root.iterdir() if path.is_dir()
            ) if crash_root.is_dir() else 0
            telemetry = observer_telemetry(
                process,
                elapsed=elapsed,
                paused=paused,
                resumes=resumes,
                captures=captures,
                error_size=error_size,
                crash_count=crash_count,
            )
            append_csv(telemetry_path, telemetry)
            append_driver_event(event_path, "telemetry", **telemetry)
            print(
                f"observer {elapsed:5.1f}s paused={paused} banner_red={red_ratio:.3f} "
                f"resumes={resumes} captures={captures} "
                f"rss={telemetry['rss_mib']}MiB private={telemetry['private_mib']}MiB "
                f"vram={telemetry['gpu_used_mib']}MiB user={telemetry['user_objects']}",
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
    # A stopped PID is not a resumable driver session.  Keeping its state file
    # made the next UI command try to attach to a dead process instead of
    # reporting that a fresh launch was required.
    STATE.unlink(missing_ok=True)
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
    launch_parser.add_argument(
        "--resolution",
        choices=("1280x720", "1920x1080"),
        help="Use a supported native window resolution for a bounded renderer probe.",
    )
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
    # The branded ANTIQVITAS menu places New Game above Load Game.  Keep the
    # default on the verified centre of New Game at the fixed 1920x1080 layout;
    # 0.43 selects Load Game and leaves the loading gate waiting on a save list.
    loading_parser.add_argument("--y", type=float, default=0.383)
    loading_parser.add_argument(
        "--percentages",
        type=int,
        nargs="+",
        default=[2, 5, 8, 12, 18, 25, 37, 50, 65, 80, 95],
    )
    loading_parser.add_argument("--minimum-captures", type=int, default=6)
    loading_parser.add_argument(
        "--menu-minimum",
        type=int,
        default=15,
        help="minimum rendered-menu settle before clicking New Game",
    )
    loading_parser.add_argument(
        "--menu-quiet-seconds",
        type=int,
        default=10,
        help="required debug-log quiet period before clicking New Game",
    )
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
    load_wait_parser = sub.add_parser("wait-loading-complete")
    load_wait_parser.add_argument("--timeout", type=int, default=300)
    load_wait_parser.add_argument("--interval", type=float, default=1)
    load_wait_parser.add_argument("--stable-frames", type=int, default=5)
    load_wait_parser.add_argument("--require-loading-plate", action="store_true")
    load_wait_parser.add_argument("--session")
    load_wait_parser.set_defaults(func=wait_loading_complete)
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
    start_country_parser = sub.add_parser("start-country")
    start_country_parser.add_argument("--session", help="evidence session directory")
    start_country_parser.add_argument("--live-timeout", type=int, default=60)
    start_country_parser.add_argument("--ui-settle", type=float, default=2)
    start_country_parser.add_argument("--start-enable-settle", type=float, default=8)
    start_country_parser.add_argument("--country-selection-settle", type=float, default=0)
    start_country_parser.add_argument("--country-x", type=float, default=0.27)
    start_country_parser.add_argument("--country-y", type=float, default=0.62)
    start_country_parser.add_argument(
        "--start-x",
        type=float,
        default=0.50,
        help="Play-as-country button; used only if the bronze-button locator misses",
    )
    start_country_parser.add_argument("--start-y", type=float, default=0.868)
    start_country_parser.add_argument(
        "--disable-startup-agenda",
        action="store_true",
        help="persist the Agenda opt-out before closing it",
    )
    start_country_parser.set_defaults(func=start_country)
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
