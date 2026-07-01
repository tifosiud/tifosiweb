import argparse
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def check_port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def run_bot_process():
    cmd = [sys.executable, str(ROOT / "src" / "bot" / "main.py")]
    print(f"Arrancando bot con: {' '.join(cmd)}")
    return subprocess.Popen(cmd, cwd=str(ROOT))


def run_web_process(port: int = 8000):
    if not check_port_available(port):
        raise RuntimeError(f"El puerto {port} ya está en uso")

    cmd = [sys.executable, str(ROOT / "web_server.py"), "--port", str(port)]
    print(f"Sirviendo web en http://127.0.0.1:{port}")
    return subprocess.Popen(cmd, cwd=str(ROOT))


def monitor_processes(processes: dict[str, subprocess.Popen]):
    try:
        while True:
            for name, proc in processes.items():
                exit_code = proc.poll()
                if exit_code is not None:
                    print(f"Proceso '{name}' terminó con código {exit_code}")
                    for stop_name, stop_proc in processes.items():
                        if stop_name != name and stop_proc.poll() is None:
                            print(f"Deteniendo proceso restante: {stop_name}")
                            stop_proc.terminate()
                    return exit_code
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Interrupción recibida. Deteniendo procesos...")
        for name, proc in processes.items():
            if proc.poll() is None:
                print(f"Terminando {name}")
                proc.terminate()
        raise


def main():
    parser = argparse.ArgumentParser(description="Launcher del proyecto Tifosi")
    parser.add_argument("mode", choices=["bot", "web", "both"], default="both")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if args.mode == "bot":
        process = run_bot_process()
        process.wait()
    elif args.mode == "web":
        process = run_web_process(args.port)
        process.wait()
    else:
        web_proc = run_web_process(args.port)
        bot_proc = run_bot_process()
        monitor_processes({"web": web_proc, "bot": bot_proc})


if __name__ == "__main__":
    main()
