from re import findall
from urllib.parse import urljoin

from .block import block_check
from .stream_chex import stream


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
