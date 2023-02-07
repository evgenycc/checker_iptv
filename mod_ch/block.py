from re import findall
from urllib.parse import urlparse

stop_list = {"err-ru.sulfat.li", "www.cloudflare-terms-of-service-abuse.com", "http://logo.apk-red.com/tv/hata.jpg",
             "http://v.viplime.fun/video/user.ts", "http://cdn01.lifeyosso.fun:8080/connect/mono.m3u8",
             "test_end.ts", "http://nl4.iptv.monster/9999/video.m3u8", "http://v.viplime.fun/video/block.ts",
             "buy.ts", "delete.ts", "http://langamepp.com/user.mp4", "http://m.megafonpro.ru/http_errors?error=404",
             "money.ts", "empty.ts", "https://zabava-block-htvod.cdn.ngenix.net/", "buy_packet.ts", "auth.m3u8",
             "logout.mp4", "BanT0ken", "auth", "logout", "VDO-X-404", "offline", "error.tv4.live",
             "block-ip-video.ts", "key.ts", "http://z1.cloudys.club/video/user.ts",
             "http://m.megafonpro.ru/rkn?channel=2m"}

# "tricolor.tv"

stop_middle = {"/errors/", "/error/", "/NOT_CLIENT/", "/forbidden/", "/000/", "/activate/", "/404/", "/405/",
               "/block/", "/407/", "/420/", "/Nothings-Is-Free-lol/"}


def block_check(url: str) -> bool:
    for st in stop_list:
        if findall(f"{st}", url):
            return True
    for st in stop_middle:
        if findall(f"{st}", url):
            if "route441cz" in str(urlparse(url).hostname):
                return False
            return True
    return False
