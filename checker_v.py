import shutil
import sys
import time
from os import system
from pathlib import Path
from platform import system as sys_pl

from colorama import Fore
from colorama import init

from checker_mod.check_content import ContentCheck
from checker_mod.rtmp_check import rtmp_run
from checker_mod.save_result import save_status_error
from checker_mod.socket_check import SockCheck
from checker_mod.check_bad_sock import CheckBadSock

init()

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}


def main():
    path = input("\nВведите путь к директории: ")
    if not Path(path).exists() or not Path(path).is_dir() or not path:
        print("Директория не существует")
        sys.exit(0)

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
            print(f'\n\n\n{Fore.YELLOW}Checked file: {Fore.RESET}{Path(file).name} | {Fore.YELLOW}Count: {Fore.RESET}{n} | '
                  f'{Fore.YELLOW}File: {Fore.RESET}{nm + 1}/{len(files)}')
            print(Fore.GREEN + "=" * 59 + "\n")

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
            scheck = SockCheck(exts, urls)
            good_sock, bad_sock = scheck.sock_scan()

            if bad_sock:
                ch_bs = CheckBadSock(bad_sock)
                good_url, bad_url = ch_bs.check_sock_run()
                if bad_url:
                    offline_all.extend(bad_url)
                if good_url:
                    good_sock.extend(good_url)

            if good_sock:
                chcontent = ContentCheck(good_sock)
                online_ch, offline_ch = chcontent.check_run()
                if offline_ch:
                    offline_all.extend(offline_ch)
                if online_ch:
                    online_all.extend(online_ch)

            if rtmp:
                good_rtmp, bad_rtmp = rtmp_run(rtmp)
                if good_rtmp:
                    online_all.extend(good_rtmp)
                if bad_rtmp:
                    offline_all.extend(bad_rtmp)

            save_status_error(file, online_all, offline_all)

            print(f"\n{Fore.GREEN}{'All'.ljust(8)}{Fore.RESET}|{str(int((len(online_all)) + (len(offline_all)))).center(6)}| "
                  f"{Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Online'.ljust(8)}{Fore.RESET}|{str(int(len(online_all))).center(6)}| "
                  f"{Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Offline'.ljust(8)}{Fore.RESET}|{str(int(len(offline_all))).center(6)}| "
                  f"{Fore.GREEN}channels\n")

            print(Fore.GREEN + "-" * 60 + "\n")
            if len(files) > 1:
                print(f'{Fore.GREEN}Scan "{Path(file).name}" time {Fore.RESET}| '
                      f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
                      f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
                      f'{int(time.monotonic() - time_start) % 60:02d} с.\n')
                print(Fore.GREEN + "-" * 60)
            exts.clear()
            urls.clear()
            online_all.clear()
            offline_all.clear()
            rtmp.clear()

            Path(file).unlink()
        print(f'{Fore.CYAN}\nAll Scan time {Fore.RESET}| '
              f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
              f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
              f'{int(time.monotonic() - time_start) % 60:02d} с.\n')

        print(Fore.GREEN + "-" * 60 + "")
        if sys_pl() == "Linux":
            system(f'''notify-send "All operation complete"''')
        print(Fore.YELLOW + "[!] All operation complete")
        print(Fore.GREEN + "-" * 60 + "\n")
    except UnicodeDecodeError:
        print(f"\nНе могу декодировать данные: {Path(file).name}\n")
        if sys_pl() == "Linux":
            system(f'''notify-send "Не могу декодировать данные: {Path(file).name}"''')
        sys.exit(0)


if __name__ == "__main__":
    main()
