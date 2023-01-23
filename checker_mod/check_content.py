from concurrent.futures import ThreadPoolExecutor
from re import findall
from urllib.parse import urlparse, urljoin

import httpx
from bs4 import BeautifulSoup
from colorama import Fore
from colorama import init
from pytube import YouTube, exceptions

init()

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}

text_plain = ["23 45 58 54", "5B 70 6C 61 79 6C 69 73", "74 65 78 74 2F 70 6C 61 69 6E", "EF BB BF 00", "FF FE 00 00",
              "74 65 78 74 2F 70 6C 61 69 6E", "3B 20 63 68 61 72 73 65 74 3D", "49 53 4F 2D 38 38 35 39 2D 31",
              "69 73 6F 2D 38 38 35 39 2D 31", "55 54 46 2D 38", "FE FF 00 00"]

html = ["7B 22", "3C 21 44 4F 43 54 59 50 45 20", "48 54 4D 4C TT", "3C 48 54 4D 4C TT", "3C 48 45 41 44 TT",
        "3C 53 43 52 49 50 54 TT", "3C 49 46 52 41 4D 45 TT", "3C 48 31 TT", "3C 44 49 56 TT", "3C 46 4F 4E 54 TT",
        "3C 54 41 42 4C 45 TT", "3C 41 TT", "3C 53 54 59 4C 45 TT", "3C 54 49 54 4C 45 TT", "3C 42 TT", "3C 42 52 TT",
        "3C 42 4F 44 59 TT", "3C 50 TT", "3C 21 2D 2D TT", "3C 3F 78 6D 6C", "25 50 44 46 2D", "4E 6F", "3C 41", "3C",
        "45 52"]

stop_list = ["/errors/", "test_end.ts", "buy.ts", "money.ts", "buy_packet.ts", "empty.ts", "key.ts", "/error/",
             "/NOT_CLIENT/", "http://logo.apk-red.com/tv/hata.jpg", "http://v.viplime.fun/video/user.ts", "/forbidden/",
             "zabava-block-htvod.cdn.ngenix.net", "err-ru.sulfat.li", "/000/", "BanT0ken", "/activate/", "/404/",
             "/405/", "www.cloudflare-terms-of-service-abuse.com", "http://cdn01.lifeyosso.fun:8080/connect/mono.m3u8",
             "http://nl4.iptv.monster/9999/video.m3u8", "http://v.viplime.fun/video/block.ts", "auth.m3u8", "/block/",
             "auth", "logout", "VDO-X-404", "offline", "logout.mp4", "error.tv4.live", "block-ip-video.ts",
             "delete.ts", "http://langamepp.com/user.mp4", "http://m.megafonpro.ru/http_errors?error=404"]


class ContentCheck:
    def __init__(self, good_status, re_ch=False):
        self.good_status = good_status
        self.re_ch = re_ch
        self.online = []
        self.offline = []

    @staticmethod
    def find_stop(url):
        if "route441cz" in str(urlparse(url).hostname):
            return False
        for st in stop_list:
            if findall(f"{st}", url):
                return True
        return False

    @staticmethod
    def find_link(text, url):
        lnk = []
        for i in text.splitlines():
            if i.startswith("#"):
                continue
            elif not i.strip():
                continue
            lnk.append(i.strip()) if i.startswith("http") else lnk.append(urljoin(url, i.strip()))
        return lnk

    def find_mpd(self, txt, url, ext):
        soup = BeautifulSoup(txt, 'xml')
        seg = soup.find_all("Representation")
        seg_list = []
        for i in seg:
            try:
                initial = i.find('SegmentTemplate').get('initialization')
                seg_list.append(urljoin(url, initial))
            except AttributeError:
                continue
        if seg_list:
            return True if self.check_content(seg_list[-1], ext) else False

    @staticmethod
    def check_youtube(url):
        try:
            yt = YouTube(url)
            if yt.video_id:
                return True
        except exceptions.RegexMatchError:
            return False

    def print_status(self):
        ch = 'Re-Check' if self.re_ch else 'Check Content'

        print("\r\033[K", end="")
        print(f"\r{Fore.YELLOW}{ch}: {Fore.RESET}{len(self.online) + len(self.offline)}/{len(self.good_status)} | "
              f"{Fore.YELLOW}Online: {Fore.RESET}{len(self.online)} | {Fore.YELLOW}Offline: "
              f"{Fore.RESET}{len(self.offline)}", end="")

    def check_link(self, lnk, ext):
        for ln in lnk:
            if self.find_stop(ln):
                return False
            if self.check_content(ln, ext):
                return True
        return False

    def check_content(self, url, ext):
        timeout = 20 if self.re_ch else 35
        if self.find_stop(url):
            return False

        if url.startswith("https://www.youtube.com") \
                or url.startswith("https://youtube.com") \
                or url.startswith("http://www.youtube.com") \
                or url.startswith("http://youtube.com"):
            if self.check_youtube(url):
                return True
            else:
                return False

        try:
            with httpx.stream("GET", url=url, headers=headers, timeout=timeout, follow_redirects=True, verify=False) as res:
                if 200 <= res.status_code <= 299:
                    if ".mpd" in str(res.url):
                        text = res.read()
                        if self.find_mpd(text, str(res.url), ext):
                            return True
                        else:
                            return False

                    if self.find_stop(str(res.url)):
                        return False

                    for chunk in res.iter_bytes():
                        hex_bytes = " ".join(['{:02X}'.format(byte) for byte in chunk])
                        if hex_bytes[0:11] == "68 74 74 70":
                            if self.check_content(chunk.decode().strip(), ext):
                                return True
                        for it in html:
                            if hex_bytes[0:len(it)].upper() == it:
                                raise Exception
                        for tx_pl in text_plain:
                            if hex_bytes[0:len(tx_pl)].upper() == tx_pl:
                                if lnk := self.find_link(chunk.decode(), str(res.url)):
                                    if len(lnk) > 10:
                                        lnk = lnk[-10:]
                                    if self.check_link(lnk, ext):
                                        return True
                                    return False
                                else:
                                    return False
                            continue
                        return True
                    return False
                return False
        except Exception as ex:
            if ex is None:
                print(f'\n{ex}\n')
            self.print_status()
            return True if "ICY 200 OK" in str(ex) else False

    def verify(self, url, ext):
        if self.check_content(url, ext):
            self.online.append(f'{ext}\n{url}\n')
            self.print_status()
        else:
            self.offline.append(f'{ext}\n{url}\n')
            self.print_status()

    def check_run(self):
        with ThreadPoolExecutor(max_workers=5) as executor:
            for item in self.good_status:
                executor.submit(self.verify, url=item.split("\n")[1].strip(), ext=item.split("\n")[0].strip())
        self.print_status()
        print(Fore.GREEN + "\n" + "-" * 60 + "\n")
        return self.online, self.offline


