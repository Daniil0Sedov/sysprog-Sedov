import argparse
import json
from pathlib import Path
import socket
import struct


def main():
    parser = argparse.ArgumentParser(description="Отправка файла по TCP")
    parser.add_argument("file", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    try:
        with args.file.open("rb") as source, socket.create_connection((args.host, args.port), timeout=30) as conn:
            size = args.file.stat().st_size
            header = json.dumps({"name": args.file.name, "size": size}, ensure_ascii=False).encode("utf-8")
            conn.sendall(struct.pack("!I", len(header)) + header)
            remaining = size
            while remaining:
                chunk = source.read(min(64 * 1024, remaining))
                if not chunk:
                    raise OSError("Файл изменился во время чтения")
                conn.sendall(chunk)
                remaining -= len(chunk)
            reply = b""
            while not reply.endswith(b"\n") and len(reply) < 32:
                chunk = conn.recv(32 - len(reply))
                if not chunk:
                    break
                reply += chunk
            if reply != b"OK\n":
                raise ConnectionError("Сервер не подтвердил приём")
        print(f"Отправлен {args.file.name}: {size} байт")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Ошибка: {exc}\n")


if __name__ == "__main__":
    main()
