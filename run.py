import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run_bot():
    cmd = [sys.executable, str(ROOT / "src" / "bot" / "main.py")]
    print(f"Arrancando bot con: {' '.join(cmd)}")
    subprocess.call(cmd, cwd=str(ROOT))


def run_web(port: int = 8000):
    cmd = [sys.executable, "-m", "http.server", str(port)]
    print(f"Sirviendo web en http://127.0.0.1:{port}")
    subprocess.call(cmd, cwd=str(ROOT / "web"))


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
        run_web(args.port)
        run_bot()


if __name__ == "__main__":
    main()
