from concurrent.futures import ThreadPoolExecutor
from re import findall
from urllib.parse import urlparse, urljoin

import httpx
import requests
from colorama import Fore
from colorama import init

from .block import block_check
from .youtube import check_youtube

requests.packages.urllib3.disable_warnings()
init()

text_plain = ["23 45 58 54", "5B 70 6C 61 79 6C 69 73", "74 65 78 74 2F 70 6C 61 69 6E", "EF BB BF 00", "FF FE 00 00",
              "74 65 78 74 2F 70 6C 61 69 6E", "3B 20 63 68 61 72 73 65 74 3D", "49 53 4F 2D 38 38 35 39 2D 31",
              "69 73 6F 2D 38 38 35 39 2D 31", "55 54 46 2D 38", "FE FF 00 00"]

html = ["7B 22", "3C 21 44 4F 43 54 59 50 45 20", "48 54 4D 4C TT", "3C 48 54 4D 4C TT", "3C 48 45 41 44 TT",
        "3C 53 43 52 49 50 54 TT", "3C 49 46 52 41 4D 45 TT", "3C 48 31 TT", "3C 44 49 56 TT", "3C 46 4F 4E 54 TT",
        "3C 54 41 42 4C 45 TT", "3C 41 TT", "3C 53 54 59 4C 45 TT", "3C 54 49 54 4C 45 TT", "3C 42 TT", "3C 42 52 TT",
        "3C 42 4F 44 59 TT", "3C 50 TT", "3C 21 2D 2D TT", "3C 3F 78 6D 6C", "25 50 44 46 2D", "4E 6F", "3C 41", "3C",
        "45 52"]

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}

# headers = {
#     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0'
# }


def find_m3u8(txt: str, url: str) -> (str, bool):
    m3u8 = findall(r".*\.m3u8.*", txt)
    if m3u8:
        list_m3u8 = []
        for m in m3u8:
            if not m.startswith("#EXT"):
                list_m3u8.append(m)
        link_serv = list_m3u8[-1].strip() if list_m3u8[-1].startswith("http") else urljoin(url, list_m3u8[-1].strip())
        return link_serv
    return False


def find_link(text, url):
    if lin := find_m3u8(text, url):
        if stream(lin):
            return True
        return False
    else:
        lnk = []
        for i in text.splitlines():
            if i.startswith("#"):
                continue
            elif not i.strip():
                continue
            else:
                lnk.append(i.strip()) if i.startswith("http") else lnk.append(urljoin(url, i.strip()))
        if lnk:
            if block_check(lnk[-1]):
                return False
            return True
        return False


def hex_check(res):
    for chunk in res.iter_bytes():
        hex_bytes = " ".join(['{:02X}'.format(byte) for byte in chunk])
        if hex_bytes[0:11] == "68 74 74 70":
            if stream(chunk.decode().strip()):
                return True
        for it in html:
            if hex_bytes[0:len(it)].upper() == it:
                return False
        for tx_pl in text_plain:
            if hex_bytes[0:len(tx_pl)].upper() == tx_pl:
                if find_link(chunk.decode(), str(res.url)):
                    return True
                return False
        return True


def stream(url):
    if block_check(str(url)):
        return False
    if url.startswith("https://www.youtube.com") \
            or url.startswith("https://youtube.com") \
            or url.startswith("http://www.youtube.com") \
            or url.startswith("http://youtube.com"):
        if check_youtube(url):
            return True
        return False
    try:
        with httpx.stream("GET", url=url, headers=headers, timeout=25, follow_redirects=True, verify=False) as res:
            if 200 <= res.status_code <= 299:
                if block_check(str(res.url)):
                    return False
                if loc := res.headers.get("Location"):
                    if block_check(loc):
                        return False
                if ".mpd" in url:
                    for chunk in res.iter_bytes():
                        if chunk:
                            return True
                        return False
                if hex_check(res):
                    return True
                return False
            return False
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False
    except Exception as ex:
        return True if "ICY 200 OK" in str(ex) else False
