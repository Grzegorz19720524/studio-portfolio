import socket
import ssl
import hashlib
import base64
import struct
import os
import threading
import time
import urllib.parse
from typing import Callable


# WebSocket opcodes
OP_CONTINUATION = 0x0
OP_TEXT = 0x1
OP_BINARY = 0x2
OP_CLOSE = 0x8
OP_PING = 0x9
OP_PONG = 0xA

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WebSocketError(Exception):
    pass


class WebSocketClosed(WebSocketError):
    def __init__(self, code: int = 1000, reason: str = "") -> None:
        self.code = code
        self.reason = reason
        super().__init__(f"WebSocket closed: {code} {reason}")


class Frame:
    def __init__(self, opcode: int, payload: bytes, fin: bool = True) -> None:
        self.opcode = opcode
        self.payload = payload
        self.fin = fin

    @property
    def is_text(self) -> bool:
        return self.opcode == OP_TEXT

    @property
    def is_binary(self) -> bool:
        return self.opcode == OP_BINARY

    @property
    def is_close(self) -> bool:
        return self.opcode == OP_CLOSE

    @property
    def is_ping(self) -> bool:
        return self.opcode == OP_PING

    @property
    def is_pong(self) -> bool:
        return self.opcode == OP_PONG

    def __repr__(self) -> str:
        return f"Frame(opcode={self.opcode:#x}, len={len(self.payload)}, fin={self.fin})"


def _encode_frame(opcode: int, payload: bytes, mask: bool = True) -> bytes:
    fin_op = 0x80 | opcode
    length = len(payload)
    mask_bit = 0x80 if mask else 0x00

    if length < 126:
        header = struct.pack("BB", fin_op, mask_bit | length)
    elif length < 65536:
        header = struct.pack("!BBH", fin_op, mask_bit | 126, length)
    else:
        header = struct.pack("!BBQ", fin_op, mask_bit | 127, length)

    if mask:
        masking_key = os.urandom(4)
        masked = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))
        return header + masking_key + masked
    return header + payload


def _recv_exactly(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise WebSocketError("Connection closed unexpectedly")
        buf += chunk
    return buf


def _decode_frame(sock: socket.socket) -> Frame:
    header = _recv_exactly(sock, 2)
    byte0, byte1 = header[0], header[1]
    fin = bool(byte0 & 0x80)
    opcode = byte0 & 0x0F
    masked = bool(byte1 & 0x80)
    length = byte1 & 0x7F

    if length == 126:
        length = struct.unpack("!H", _recv_exactly(sock, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _recv_exactly(sock, 8))[0]

    masking_key = _recv_exactly(sock, 4) if masked else b""
    payload = _recv_exactly(sock, length)

    if masked:
        payload = bytes(b ^ masking_key[i % 4] for i, b in enumerate(payload))

    return Frame(opcode, payload, fin)


def _handshake(sock: socket.socket, host: str, port: int, path: str, extra_headers: dict) -> None:
    key = base64.b64encode(os.urandom(16)).decode()
    headers = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
    )
    for k, v in extra_headers.items():
        headers += f"{k}: {v}\r\n"
    headers += "\r\n"
    sock.sendall(headers.encode())

    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(4096)
        if not chunk:
            raise WebSocketError("Server closed connection during handshake")
        response += chunk

    lines = response.split(b"\r\n")
    status_line = lines[0].decode()
    if "101" not in status_line:
        raise WebSocketError(f"Handshake failed: {status_line}")

    resp_headers = {}
    for line in lines[1:]:
        if b": " in line:
            k, _, v = line.partition(b": ")
            resp_headers[k.lower().decode()] = v.decode()

    expected = base64.b64encode(
        hashlib.sha1((key + GUID).encode()).digest()
    ).decode()
    actual = resp_headers.get("sec-websocket-accept", "")
    if actual != expected:
        raise WebSocketError(f"Invalid Sec-WebSocket-Accept: {actual!r}")


class WebSocketClient:
    def __init__(
        self,
        url: str,
        *,
        timeout: float | None = 30.0,
        extra_headers: dict[str, str] | None = None,
        on_message: Callable[[str | bytes], None] | None = None,
        on_close: Callable[[int, str], None] | None = None,
        on_error: Callable[[Exception], None] | None = None,
        on_ping: Callable[[bytes], None] | None = None,
    ) -> None:
        self.url = url
        self.timeout = timeout
        self._extra_headers = extra_headers or {}
        self.on_message = on_message
        self.on_close = on_close
        self.on_error = on_error
        self.on_ping = on_ping
        self._sock: socket.socket | None = None
        self._closed = False
        self._lock = threading.Lock()
        self._listen_thread: threading.Thread | None = None

    def connect(self) -> "WebSocketClient":
        parsed = urllib.parse.urlparse(self.url)
        scheme = parsed.scheme
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if scheme == "wss" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        raw = socket.create_connection((host, port), timeout=self.timeout)
        if scheme == "wss":
            ctx = ssl.create_default_context()
            self._sock = ctx.wrap_socket(raw, server_hostname=host)
        else:
            self._sock = raw

        _handshake(self._sock, host, port, path, self._extra_headers)
        self._closed = False
        return self

    def __enter__(self) -> "WebSocketClient":
        return self.connect()

    def __exit__(self, *_) -> None:
        self.close()

    def send(self, message: str | bytes) -> None:
        if self._closed or self._sock is None:
            raise WebSocketClosed()
        if isinstance(message, str):
            payload = message.encode("utf-8")
            opcode = OP_TEXT
        else:
            payload = message
            opcode = OP_BINARY
        with self._lock:
            self._sock.sendall(_encode_frame(opcode, payload))

    def send_binary(self, data: bytes) -> None:
        self.send(data)

    def ping(self, data: bytes = b"") -> None:
        if self._closed or self._sock is None:
            raise WebSocketClosed()
        with self._lock:
            self._sock.sendall(_encode_frame(OP_PING, data))

    def pong(self, data: bytes = b"") -> None:
        if self._closed or self._sock is None:
            raise WebSocketClosed()
        with self._lock:
            self._sock.sendall(_encode_frame(OP_PONG, data))

    def recv(self) -> str | bytes:
        if self._sock is None:
            raise WebSocketClosed()
        fragments: list[bytes] = []
        first_opcode = OP_TEXT
        while True:
            frame = _decode_frame(self._sock)
            if frame.is_ping:
                self.pong(frame.payload)
                if self.on_ping:
                    self.on_ping(frame.payload)
                continue
            if frame.is_pong:
                continue
            if frame.is_close:
                code = 1000
                reason = ""
                if len(frame.payload) >= 2:
                    code = struct.unpack("!H", frame.payload[:2])[0]
                    reason = frame.payload[2:].decode("utf-8", errors="replace")
                self._send_close(code)
                self._closed = True
                raise WebSocketClosed(code, reason)
            if frame.opcode != OP_CONTINUATION:
                first_opcode = frame.opcode
            fragments.append(frame.payload)
            if frame.fin:
                break
        payload = b"".join(fragments)
        return payload.decode("utf-8") if first_opcode == OP_TEXT else payload

    def recv_text(self) -> str:
        msg = self.recv()
        return msg if isinstance(msg, str) else msg.decode("utf-8")

    def recv_bytes(self) -> bytes:
        msg = self.recv()
        return msg if isinstance(msg, bytes) else msg.encode("utf-8")

    def _send_close(self, code: int = 1000, reason: str = "") -> None:
        try:
            payload = struct.pack("!H", code) + reason.encode("utf-8")
            with self._lock:
                if self._sock:
                    self._sock.sendall(_encode_frame(OP_CLOSE, payload))
        except Exception:
            pass

    def close(self, code: int = 1000, reason: str = "") -> None:
        if self._closed:
            return
        self._closed = True
        self._send_close(code, reason)
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None
        if self.on_close:
            self.on_close(code, reason)

    def listen(self) -> None:
        """Block and dispatch messages to on_message callback until closed."""
        try:
            while not self._closed:
                try:
                    msg = self.recv()
                    if self.on_message:
                        self.on_message(msg)
                except WebSocketClosed as e:
                    if self.on_close:
                        self.on_close(e.code, e.reason)
                    break
                except Exception as e:
                    if self.on_error:
                        self.on_error(e)
                    break
        finally:
            self.close()

    def listen_in_background(self) -> threading.Thread:
        t = threading.Thread(target=self.listen, daemon=True)
        t.start()
        self._listen_thread = t
        return t

    @property
    def is_connected(self) -> bool:
        return not self._closed and self._sock is not None

    def __repr__(self) -> str:
        return f"WebSocketClient(url={self.url!r}, connected={self.is_connected})"


def connect(
    url: str,
    *,
    timeout: float = 30.0,
    extra_headers: dict[str, str] | None = None,
    on_message: Callable | None = None,
    on_close: Callable | None = None,
    on_error: Callable | None = None,
) -> WebSocketClient:
    return WebSocketClient(
        url,
        timeout=timeout,
        extra_headers=extra_headers,
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
    ).connect()


if __name__ == "__main__":
    print("--- WebSocket echo test (wss://echo.websocket.org) ---")

    messages_received = []
    closed_event = threading.Event()

    def on_msg(msg):
        messages_received.append(msg)
        print("received:", repr(msg))

    def on_cls(code, reason):
        print(f"closed: code={code} reason={repr(reason)}")
        closed_event.set()

    def on_err(exc):
        print(f"error: {exc}")
        closed_event.set()

    try:
        ws = WebSocketClient(
            "wss://echo.websocket.org",
            on_message=on_msg,
            on_close=on_cls,
            on_error=on_err,
            timeout=10.0,
        )
        ws.connect()
        print("connected:", ws)

        ws.listen_in_background()

        ws.send("hello, websocket!")
        time.sleep(0.3)
        ws.send("second message")
        time.sleep(0.3)
        ws.send_binary(b"\x01\x02\x03\x04")
        time.sleep(0.3)
        ws.ping(b"ping-data")
        time.sleep(0.3)

        ws.close()
        closed_event.wait(timeout=3.0)

        print("total messages received:", len(messages_received))

    except Exception as e:
        print(f"test skipped ({type(e).__name__}: {e})")

    print("\n--- Frame encoding ---")
    frame = _encode_frame(OP_TEXT, b"hello", mask=False)
    print("text frame (no mask):", frame.hex())

    frame_bin = _encode_frame(OP_BINARY, b"\x00\xFF", mask=False)
    print("binary frame (no mask):", frame_bin.hex())

    close_frame = _encode_frame(OP_CLOSE, struct.pack("!H", 1000) + b"done", mask=False)
    print("close frame (no mask):", close_frame.hex())

    print("\n--- WebSocketClient repr ---")
    dummy = WebSocketClient("wss://example.com/ws", timeout=5.0)
    print(dummy)

    print("\n--- WebSocketError hierarchy ---")
    try:
        raise WebSocketClosed(1001, "going away")
    except WebSocketError as e:
        print(f"caught WebSocketError: {e}")
