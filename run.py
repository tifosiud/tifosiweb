import argparse
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PID_FILE = ROOT / "tmp" / "bot.pid"


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def is_process_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def bot_is_running() -> bool:
    if not PID_FILE.exists():
        return False

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        return is_process_running(pid)
    except (ValueError, OSError):
        return False


def start_process(command, cwd, name):
    print(f"Arrancando {name} con: {' '.join(map(str, command))}")
    return subprocess.Popen(command, cwd=str(cwd), stdout=sys.stdout, stderr=sys.stderr, stdin=subprocess.DEVNULL)


def run_bot():
    if bot_is_running():
        print("Ya hay una instancia del bot en ejecución; se omite el arranque.")
        return None

    try:
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            if pid > 0:
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)
    except (ValueError, OSError, ProcessLookupError):
        pass

    return start_process([sys.executable, str(ROOT / "src" / "bot" / "main.py")], ROOT, "bot")


def run_web(port: int = 8000):
    if is_port_in_use(port):
        print(f"El puerto {port} ya está en uso; se omite el servidor web.")
        return None

    return start_process([sys.executable, "-m", "http.server", str(port)], ROOT / "web", "web")


def run_both(port: int):
    web_process = run_web(port)
    bot_process = run_bot()

    if web_process is None and bot_process is None:
        return

    try:
        while True:
            if web_process is not None and web_process.poll() is not None:
                break
            if bot_process is not None and bot_process.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Deteniendo procesos...")
    finally:
        for process in [web_process, bot_process]:
            if process is not None and process.poll() is None:
                process.terminate()


def main():
    parser = argparse.ArgumentParser(description="Launcher del proyecto Tifosi")
    parser.add_argument("mode", choices=["bot", "web", "both"], default="both")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode == "bot":
        run_bot()
    elif args.mode == "web":
        run_web(args.port)
    else:
        run_both(args.port)


if __name__ == "__main__":
    main()
