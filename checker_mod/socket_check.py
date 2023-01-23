import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

from colorama import Fore
from colorama import init

init()


class SockCheck:
    def __init__(self, exts, urls):
        self.exts = exts
        self.urls = urls
        self.good_sock = []
        self.bad_sock = []

    @staticmethod
    def get_port(url):
        try:
            if ":" in urlparse(url).netloc:
                return int(urlparse(url).netloc.split(":")[-1])
            else:
                return 80 if urlparse(url).scheme == "http" else 443
        except ValueError:
            return 80 if urlparse(url).scheme == "http" else 443

    def print_status(self):
        print("\r\033[K", end="")
        print(f"\r{Fore.YELLOW}Sock Check: {Fore.RESET}"
              f"{len(self.good_sock) + len(self.bad_sock)}/"
              f"{len(self.exts)} | {Fore.YELLOW}Good Sock: {Fore.RESET}{len(self.good_sock)} | "
              f"{Fore.YELLOW}Bad Sock: {Fore.RESET}{len(self.bad_sock)}", end="")

    def sock_connect(self, port, ext, url):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(7)
        try:
            s.connect((urlparse(url).hostname, port))
            s.send(f'GET / HTTP/1.1\r\nHost:{urlparse(url).hostname}\r\n\r\n'.encode())
            rec = s.recv(32)
            if rec:
                self.good_sock.append(f'{ext}\n{url}\n')
                self.print_status()
                s.close()
                return
            self.bad_sock.append(f'{ext}\n{url}\n')
            self.print_status()
            return
        except Exception:
            s.close()
            self.bad_sock.append(f'{ext}\n{url}\n')
            self.print_status()
            return

    def sock_scan(self):
        with ThreadPoolExecutor() as executor:
            for num, url in enumerate(self.urls):
                executor.submit(self.sock_connect, port=self.get_port(url), ext=self.exts[num], url=url)
        self.print_status()
        print(f"\n{Fore.CYAN}Sock Online: {Fore.RESET}{len(self.good_sock)} | {Fore.CYAN}Sock Offline: "
              f"{Fore.RESET}{len(self.bad_sock)}")
        print(Fore.GREEN + "-" * 60 + "\n")
        return self.good_sock, self.bad_sock
