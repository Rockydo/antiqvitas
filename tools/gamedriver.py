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

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "baselines/runtime/gamedriver_session.json"


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
            "display_mode": "windowed",
            "resolution": "1280x720",
            "vsync": False,
            "setting_framerate_cap": 30,
            "quality": "low",
            "mapobject_quality": "low",
            "anti_aliasing": "disabled",
            "animated_portraits": False,
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


def process_from_state() -> psutil.Process:
    value = state()
    process = psutil.Process(int(value["pid"]))
    if process.create_time() != value["process_create_time"]:
        raise RuntimeError("PID was reused; refusing to control an unrelated process")
    return process


def launch(args: argparse.Namespace) -> int:
    ensure_steam()
    cfg = config()
    user_dir = Path(str(cfg["user_dir"]))
    set_fixed_settings(user_dir)
    logs = user_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    command = [
        str(cfg["game_exe"]),
        f"--user_dir={user_dir}",
        "-debug_mode",
        "--ignore-disable-mods-on-crash",
    ]
    if args.leavepops:
        command.append("-leavepops")
    command.extend(args.extra)
    flags = subprocess.CREATE_NEW_PROCESS_GROUP
    if args.hidden:
        flags |= subprocess.CREATE_NO_WINDOW
    popen = subprocess.Popen(
        command,
        cwd=Path(str(cfg["game_exe"])).parent,
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
    }
    save_state(value)
    print(json.dumps(value, indent=2))
    return 0


def find_window():
    import pygetwindow

    candidates = [
        window
        for window in pygetwindow.getAllWindows()
        if "Europa Universalis V" in window.title and window.width > 300
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
    process.cpu_percent()
    while time.monotonic() < deadline:
        if not process.is_running() or process.status() == psutil.STATUS_ZOMBIE:
            print(f"gamedriver: process exited with {process.wait(timeout=1)}", file=sys.stderr)
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
        cpu = process.cpu_percent(interval=1)
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
        1280,
        720,
        swp_showwindow | swp_noownerzorder,
    )
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

    window = activate_window()
    if not (0 <= args.x <= 1 and 0 <= args.y <= 1):
        raise ValueError("click coordinates must be normalized fractions from 0 through 1")
    x = window.left + round(window.width * args.x)
    y = window.top + round(window.height * args.y)
    pyautogui.click(x, y)
    time.sleep(args.settle)
    print(f"clicked normalized ({args.x:.3f}, {args.y:.3f}) at ({x}, {y})")
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


def press_console_key(vk: int) -> None:
    key_up = 0x0002
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk, 0, key_up, 0)


def press_scan_code(scan_code: int) -> None:
    key_up = 0x0002
    scan_flag = 0x0008
    ctypes.windll.user32.keybd_event(0, scan_code, scan_flag, 0)
    ctypes.windll.user32.keybd_event(0, scan_code, scan_flag | key_up, 0)


def console(args: argparse.Namespace) -> int:
    import pyautogui

    window = focus_game()
    # Physical key directly below Escape (scan code 0x29) works across QWERTY
    # and AZERTY layouts; virtual-key fallbacks cover OEM mappings.
    if args.already_open:
        pyautogui.click(
            window.left + int(window.width * 0.14),
            window.top + int(window.height * 0.74),
        )
        time.sleep(0.4)
    else:
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
        press_scan_code(0x29)
        time.sleep(0.5)
    print(f"console command sent: {args.command}")
    return 0


def key(args: argparse.Namespace) -> int:
    import pyautogui

    focus_game()
    if args.char:
        pyautogui.press(args.code)
    elif args.scan:
        press_scan_code(int(args.code, 0))
    else:
        press_console_key(int(args.code, 0))
    time.sleep(args.settle)
    print(f"key sent: {'scan' if args.scan else 'vk'} {args.code}")
    return 0


def stop(args: argparse.Namespace) -> int:
    try:
        process = process_from_state()
    except (FileNotFoundError, psutil.NoSuchProcess):
        print("gamedriver: already stopped")
        return 0
    if process.is_running():
        process.terminate()
        try:
            process.wait(timeout=args.timeout)
        except psutil.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    print("gamedriver: stopped")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="subcommand", required=True)
    launch_parser = sub.add_parser("launch")
    launch_parser.add_argument("--mode", choices=("vanilla", "mod"), default="mod")
    launch_parser.add_argument("--leavepops", action="store_true")
    launch_parser.add_argument("--hidden", action="store_true")
    launch_parser.add_argument("extra", nargs="*")
    launch_parser.set_defaults(func=launch)
    wait_parser = sub.add_parser("wait")
    wait_parser.add_argument("--timeout", type=int, default=480)
    wait_parser.add_argument("--minimum", type=int, default=45)
    wait_parser.add_argument("--quiet-seconds", type=int, default=15)
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
    click_parser = sub.add_parser("click")
    click_parser.add_argument("x", type=float, help="horizontal normalized position")
    click_parser.add_argument("y", type=float, help="vertical normalized position")
    click_parser.add_argument("--settle", type=float, default=2)
    click_parser.add_argument("--capture", help="capture this name after the click")
    click_parser.add_argument("--session")
    click_parser.set_defaults(func=click)
    hotkey_parser = sub.add_parser("hotkey")
    hotkey_parser.add_argument("keys", help="keys separated by '+', e.g. ctrl+s")
    hotkey_parser.add_argument("--settle", type=float, default=2)
    hotkey_parser.add_argument("--capture", help="capture this name after the hotkey")
    hotkey_parser.add_argument("--session")
    hotkey_parser.set_defaults(func=hotkey)
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
    stop_parser = sub.add_parser("stop")
    stop_parser.add_argument("--timeout", type=int, default=10)
    stop_parser.set_defaults(func=stop)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
