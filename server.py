"""Calculadora local: sirve la interfaz y evalúa expresiones de forma segura."""

from __future__ import annotations

import json
import webbrowser
from decimal import Decimal, DivisionByZero, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HOST = "127.0.0.1"
PORT = 8765
STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_EXPRESSION_LENGTH = 200

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
}


class CalculatorError(Exception):
    """Expresión que no se puede calcular."""


class Parser:
    """Analizador de expresiones con + - * / y unario +/-. No usa eval."""

    def __init__(self, source: str) -> None:
        self.source = (
            source.replace(" ", "")
            .replace("×", "*")
            .replace("÷", "/")
            .replace("−", "-")
        )
        self.index = 0

    def parse(self) -> Decimal:
        if not self.source:
            raise CalculatorError("vacía")
        value = self._expression()
        if self.index != len(self.source):
            raise CalculatorError("incompleta")
        return value

    def _peek(self) -> str:
        if self.index >= len(self.source):
            return ""
        return self.source[self.index]

    def _consume(self) -> str:
        char = self._peek()
        self.index += 1
        return char

    def _expression(self) -> Decimal:
        value = self._term()
        while self._peek() in {"+", "-"}:
            operator = self._consume()
            right = self._term()
            value = value + right if operator == "+" else value - right
        return value

    def _term(self) -> Decimal:
        value = self._unary()
        while self._peek() in {"*", "/"}:
            operator = self._consume()
            right = self._unary()
            if operator == "*":
                value *= right
            else:
                if right == 0:
                    raise CalculatorError("división por cero")
                value /= right
        return value

    def _unary(self) -> Decimal:
        peeked = self._peek()
        if peeked in {"+", "-"}:
            operator = self._consume()
            value = self._unary()
            return value if operator == "+" else -value
        return self._number()

    def _number(self) -> Decimal:
        start = self.index
        saw_digit = False
        saw_dot = False
        while True:
            char = self._peek()
            if char.isdigit():
                saw_digit = True
                self._consume()
            elif char == "." and not saw_dot:
                saw_dot = True
                self._consume()
            else:
                break
        if not saw_digit or start == self.index:
            raise CalculatorError("número inválido")
        token = self.source[start:self.index]
        if token in {".", "+", "-"}:
            raise CalculatorError("número inválido")
        try:
            return Decimal(token)
        except InvalidOperation as exc:
            raise CalculatorError("número inválido") from exc


def format_number(value: Decimal) -> str:
    try:
        value = value.quantize(Decimal("0.0000000001"))
        text = format(value, "f")
    except (InvalidOperation, DivisionByZero) as exc:
        raise CalculatorError("resultado inválido") from exc
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def evaluate(expression: str) -> str:
    if not isinstance(expression, str):
        raise CalculatorError("expresión inválida")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise CalculatorError("expresión demasiado larga")
    try:
        return format_number(Parser(expression).parse())
    except DivisionByZero as exc:
        raise CalculatorError("división por cero") from exc


class CalculatorHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        if path in ("", "/"):
            path = "/index.html"
        file_path = (STATIC_DIR / path.lstrip("/")).resolve()
        if not _is_inside(file_path, STATIC_DIR) or not file_path.is_file():
            self._send_json(404, {"error": "No encontrado"})
            return
        content_type = CONTENT_TYPES.get(file_path.suffix, "application/octet-stream")
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/calculate":
            self._send_json(404, {"error": "No encontrado"})
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 4096:
            self._send_json(400, {"error": "Error"})
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            result = evaluate(payload.get("expression", ""))
        except (CalculatorError, json.JSONDecodeError, UnicodeDecodeError, ValueError):
            self._send_json(400, {"error": "Error"})
            return
        self._send_json(200, {"result": result})

    def log_message(self, format: str, *args) -> None:
        return

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return False
    return True


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), CalculatorHandler)
    url = f"http://{HOST}:{PORT}"
    print(f"Calculadora en {url}")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
