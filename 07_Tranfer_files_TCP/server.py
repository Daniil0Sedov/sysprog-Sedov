import argparse
import json
import os
from pathlib import Path
import socket
import struct
import tempfile

CHUNK = 64 * 1024
MAX_HEADER = 8192


def read_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        part = sock.recv(size - len(data))
        if not part:
            raise ConnectionError("Соединение прервано")
        data.extend(part)
    return bytes(data)


def receive_file(conn, directory):
    length = struct.unpack("!I", read_exact(conn, 4))[0]
    if not 0 < length <= MAX_HEADER:
        raise ValueError("Недопустимый заголовок")
    header = json.loads(read_exact(conn, length).decode("utf-8"))
    name, size = header["name"], header["size"]
    if not isinstance(name, str) or name in ("", ".", "..") or "/" in name or "\\" in name or ":" in name:
        raise ValueError("Недопустимое имя файла")
    if not isinstance(size, int) or isinstance(size, bool) or not 0 <= size <= 1024 * 1024 * 1024:
        raise ValueError("Недопустимый размер файла")
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(dir=directory, prefix=".upload-", delete=False) as output:
            temp_name = output.name
            remaining = size
            while remaining:
                chunk = conn.recv(min(CHUNK, remaining))
                if not chunk:
                    raise ConnectionError(f"Передача прервана, осталось {remaining} байт")
                output.write(chunk)
                remaining -= len(chunk)
        os.replace(temp_name, directory / name)
        temp_name = None
        conn.sendall(b"OK\n")
        print(f"Получен {name}: {size} байт", flush=True)
    finally:
        if temp_name is not None:
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser(description="Приём файлов по TCP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--dir", type=Path, default=Path("received"))
    args = parser.parse_args()
    args.dir.mkdir(parents=True, exist_ok=True)
    with socket.socket() as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen()
        print(f"Ожидание: {args.host}:{args.port}; папка {args.dir.resolve()}", flush=True)
        while True:
            conn, address = server.accept()
            with conn:
                conn.settimeout(30)
                try:
                    receive_file(conn, args.dir)
                except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
                    print(f"Ошибка от {address}: {exc}", flush=True)
                    try:
                        conn.sendall(b"ERROR\n")
                    except OSError:
                        pass


if __name__ == "__main__":
    main()
