import argparse
import http.server
import socketserver
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
WEB_ROOT = PROJECT_ROOT / "web"


class TifosiRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]

        if path in ("", "/"):
            return str(WEB_ROOT / "index.html")

        if path == "/index.html":
            return str(WEB_ROOT / "index.html")

        if path.startswith("/web/"):
            return str(WEB_ROOT / path[len("/web/"):].lstrip("/"))

        if path in ("/app.js", "/styles.css"):
            return str(WEB_ROOT / path.lstrip("/"))

        if path.startswith("/front/"):
            return str(WEB_ROOT / path.lstrip("/"))

        project_path = PROJECT_ROOT / path.lstrip("/")
        if project_path.exists():
            return str(project_path)

        web_path = WEB_ROOT / path.lstrip("/")
        return str(web_path)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description="Servidor web para Tifosi")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    with socketserver.TCPServer(("0.0.0.0", args.port), TifosiRequestHandler) as httpd:
        print(f"Sirviendo web en http://127.0.0.1:{args.port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Servidor detenido")


if __name__ == "__main__":
    main()
