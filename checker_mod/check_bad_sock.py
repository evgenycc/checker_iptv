from concurrent.futures import ThreadPoolExecutor

import requests
from colorama import Fore
from colorama import init

init()

requests.packages.urllib3.disable_warnings()

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}


class CheckBadSock:
    def __init__(self, bad_sock):
        self.bad_sock = bad_sock
        self.good_url = []
        self.bad_url = []

    @staticmethod
    def check_sock(url):
        try:
            rs = requests.get(url=url, headers=headers, timeout=7, stream=True, allow_redirects=True, verify=False)
            if 200 <= rs.status_code <= 299:
                return True
            return False
        except Exception:
            return False

    def print_status(self):
        print("\r\033[K", end="")
        print(f"\r{Fore.YELLOW}Check BadSock: {Fore.RESET}{len(self.good_url) + len(self.bad_url)}/"
              f"{len(self.bad_sock)} | {Fore.YELLOW}Online Sock: {Fore.RESET}{len(self.good_url)} | "
              f"{Fore.YELLOW}Offline Sock: {Fore.RESET}{len(self.bad_url)}", end="")

    def verify_sock(self, url, ext):
        if self.check_sock(url):
            self.good_url.append(f'{ext}\n{url}\n')
            self.print_status()
        else:
            self.bad_url.append(f'{ext}\n{url}\n')
            self.print_status()

    def check_sock_run(self):
        temp = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for item in self.bad_sock:
                temp.append(item)

                if len(item) >= 5:
                    for tmp in temp:
                        ext = tmp.split("\n")[0].strip()
                        url = tmp.split("\n")[1].strip()
                        executor.submit(self.verify_sock, url=url, ext=ext)
                    temp.clear()
            if len(item) < 5:
                for tmp in temp:
                    ext = tmp.split("\n")[0].strip()
                    url = tmp.split("\n")[1].strip()
                    executor.submit(self.verify_sock, url=url, ext=ext)
                temp.clear()
        print(Fore.GREEN + "\n" + "-" * 60 + "\n")
        return self.good_url, self.bad_url
