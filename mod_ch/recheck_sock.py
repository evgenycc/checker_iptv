import requests

from .block import block_check

requests.packages.urllib3.disable_warnings()

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}


def recheck(url):
    try:
        rs = requests.get(url=url, headers=headers, stream=True, timeout=7, allow_redirects=True, verify=False)
        if 200 <= rs.status_code <= 299:
            if block_check(rs.url):
                return False
            if loc := rs.headers.get("Location"):
                if block_check(loc):
                    return False
            return True
        return False
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return False
    except Exception as ex:
        return True if "ICY 200 OK" in str(ex) else False
