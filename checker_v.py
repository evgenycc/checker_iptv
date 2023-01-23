import sys
import time
from os import system
from pathlib import Path

from colorama import Fore
from colorama import init

from checker_mod.check_content import ContentCheck
from checker_mod.rtmp_check import rtmp_run
from checker_mod.save_result import save_status_error
from checker_mod.socket_check import SockCheck

init()

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}


def main():
    path = '/home/vev/py_proj/tv_checker/for_check'

    time_start = time.monotonic()
    exts, urls, online_all, offline_all, rtmp = [], [], [], [], []

    files = [fil for fil in Path(path).iterdir() if Path(fil).suffix == ".m3u"]

    file = ""
    try:
        for nm, file in enumerate(sorted(files)):
            n = 0
            with open(file, 'r', encoding='utf-8') as f:
                for nn in f.readlines():
                    if nn.startswith("http"):
                        n += 1
            print(f'\n{Fore.YELLOW}Checked file: {Fore.RESET}{Path(file).name} | {Fore.YELLOW}Count: {Fore.RESET}{n} | '
                  f'{Fore.YELLOW}File: {Fore.RESET}{nm + 1}/{len(files)}\n')
            print(Fore.GREEN + "-" * 60 + "\n")

            ext = ""
            with open(file, 'r', encoding='utf-8') as fl:
                for ln in fl.readlines():
                    if ln.startswith('#EXTINF'):
                        ext = ln.strip()
                        continue
                    elif ln.startswith("rtmp"):
                        if ext == "":
                            ext = "#EXTINF:-1, No title"
                        rtmp.append(f"{ext}\n{ln.strip()}\n")
                        continue
                    elif ln.startswith("http"):
                        if ext == "":
                            ext = "#EXTINF:-1, No title"
                        if len(ln.strip().split()) > 1:
                            ln = ln.strip().replace(" ", "")
                        exts.append(ext)
                        urls.append(ln.strip())
            sock_time = time.monotonic()
            scheck = SockCheck(exts, urls)
            good_sock, bad_sock = scheck.sock_scan()
            if bad_sock:
                for bs in bad_sock:
                    offline_all.append(bs)

            print(f'{Fore.GREEN}Scan time Sock {Fore.RESET}| '
                  f'{(int(time.monotonic() - sock_time) // 3600) % 24:d} ч. '
                  f'{(int(time.monotonic() - sock_time) // 60) % 60:02d} м. '
                  f'{int(time.monotonic() - sock_time) % 60:02d} с.\n')
            print(Fore.GREEN + "-" * 60 + "\n")

            if good_sock:
                chcontent = ContentCheck(good_sock)
                online_ch, offline_ch = chcontent.check_run()
                if offline_ch:
                    for off in offline_ch:
                        offline_all.append(off)
                if online_ch:
                    for och in online_ch:
                        online_all.append(och)

            if rtmp:
                good_rtmp, bad_rtmp = rtmp_run(rtmp)
                if good_rtmp:
                    for rt in good_rtmp:
                        online_all.append(rt)
                if bad_rtmp:
                    for bt in bad_rtmp:
                        offline_all.append(bt)

            save_status_error(file, online_all, offline_all)
            # if path_err := save_status_error(file, online_all, offline_all):
            #     rech_run(path_err)

            # print(Fore.YELLOW + "ОБЩИЙ РЕЗУЛЬТАТ")
            # print(Fore.GREEN + "\n" + "-" * 60 + "\n")
            print(f"\n{Fore.GREEN}{'All'.ljust(8)}{Fore.RESET}|{str(int((len(online_all)) + (len(offline_all)))).center(6)}| "
                  f"{Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Online'.ljust(8)}{Fore.RESET}|{str(int(len(online_all))).center(6)}| "
                  f"{Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Offline'.ljust(8)}{Fore.RESET}|{str(int(len(offline_all))).center(6)}| "
                  f"{Fore.GREEN}channels\n")

            print(f'{Fore.GREEN}Scan time {Fore.RESET}| '
                  f'{(int(time.monotonic() - sock_time) // 3600) % 24:d} ч. '
                  f'{(int(time.monotonic() - sock_time) // 60) % 60:02d} м. '
                  f'{int(time.monotonic() - sock_time) % 60:02d} с.\n')

            print(Fore.GREEN + "-" * 60 + "\n")

            exts.clear()
            urls.clear()
            online_all.clear()
            offline_all.clear()
            rtmp.clear()

            Path(file).unlink()
        print(f'{Fore.GREEN}All Scan time {Fore.RESET}| '
              f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
              f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
              f'{int(time.monotonic() - time_start) % 60:02d} с.\n')

        print(Fore.GREEN + "-" * 60 + "\n")
        system(f'''notify-send "All operation complete"''')
    except UnicodeDecodeError:
        print(f"\nНе могу декодировать данные: {Path(file).name}\n")
        system(f'''notify-send "Не могу декодировать данные: {Path(file).name}"''')
        sys.exit(0)


if __name__ == "__main__":
    main()
