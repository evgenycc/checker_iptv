import socket
import ssl
from urllib.parse import urlparse


def port_get(url: str) -> int:
    if ":" in urlparse(url).netloc:
        return int(str(urlparse(url).netloc).split(":")[-1])
    else:
        return 80 if urlparse(url).scheme == "http" else 443


def chunk_url(url: str) -> tuple:
    key = f'?{url.split("/")[-1].split("?")[-1]}' if "?" in url else ""
    host = urlparse(url).hostname
    path = f'{urlparse(url).path}{key}'
    return host, path


def sock_ch(url: str) -> bool:
    port = port_get(url)
    host, path = chunk_url(url)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))

        if port == 443:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock, server_hostname=host)

        sock.sendall(f"GET {path} HTTP/1.1\r\nHost:{host}\r\n\r\n".encode())

        data = sock.recv(1024)
        sock.close()

        if data:
            return True
        return False
    except Exception:
        sock.close()
        return False
