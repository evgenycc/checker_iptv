from concurrent.futures import ThreadPoolExecutor

import cv2
from colorama import Fore
from colorama import init

init()

good_rtmp, bad_rtmp = [], []


def check_rtmp(url, ext, rtmp):
    video = cv2.VideoCapture(url)
    while True:
        grabbed, frame = video.read()
        if grabbed:
            video.release()
            good_rtmp.append(f'{ext}\n{url}\n')
            print_status(rtmp)
            return
        bad_rtmp.append(f'{ext}\n{url}\n')
        print_status(rtmp)
        return


def print_status(rtmp):
    print("\r\033[K", end="")
    print(f"\r{Fore.YELLOW}Check: {Fore.RESET}{len(good_rtmp) + len(bad_rtmp)}/{rtmp} | "
          f"{Fore.YELLOW}Online: {Fore.RESET}{len(good_rtmp)} | {Fore.YELLOW}Offline: "
          f"{Fore.RESET}{len(bad_rtmp)}", end="")


def rtmp_run(rtmp):
    if rtmp:
        print("\r\033[K", end="")
        with ThreadPoolExecutor(max_workers=5) as executor:
            for i in rtmp:
                ext = i.split("\n")[0].strip()
                url = i.split("\n")[1].strip()
                executor.submit(check_rtmp, url=url, ext=ext, rtmp=len(rtmp))

    print_status(len(rtmp))
    return good_rtmp, bad_rtmp
