import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

from colorama import Fore
from colorama import init

from mod_ch.sock_check import sock_ch
from mod_ch.recheck_sock import recheck
from mod_ch.stream_chex import stream
from mod_ch.save_result import save_status_error

init()

online = []
offline = []


def print_status(count):
    global online, offline
    print("\r\033[K", end="")
    print(f"\r{Fore.YELLOW}[~] Check Stream: {Fore.RESET}{len(online) + len(offline)}/{count} | {Fore.YELLOW}Online: "
          f"{Fore.RESET}{len(online)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(offline)}", end="")


def verify(ext, url, count):
    global online, offline
    if "udp" in urlparse(url).path or urlparse(url).scheme == "rtmp":
        if sock_ch(url):
            online.append(f'{ext}\n{url}\n')
            print_status(count)
        else:
            offline.append(f'{ext}\n{url}\n')
            print_status(count)
    elif sock_ch(url):
        if stream(url):
            online.append(f'{ext}\n{url}\n')
            print_status(count)
        else:
            offline.append(f'{ext}\n{url}\n')
            print_status(count)
    else:
        if recheck(url):
            if stream(url):
                online.append(f'{ext}\n{url}\n')
                print_status(count)
            else:
                offline.append(f'{ext}\n{url}\n')
                print_status(count)
        else:
            offline.append(f'{ext}\n{url}\n')
            print_status(count)


def check(links):
    with ThreadPoolExecutor(max_workers=5) as executor:
        temp = []
        for i in links:
            temp.append(i)
            if len(temp) >= 5:
                for link in temp:
                    ext = link.split("\n")[0].strip()
                    url = link.split("\n")[1].strip()
                    executor.submit(verify, ext=ext, url=url, count=len(links))
                    time.sleep(random.uniform(0.1, 0.9))
                temp.clear()
        if len(temp) < 5:
            for link in temp:
                ext = link.split("\n")[0].strip()
                url = link.split("\n")[1].strip()
                executor.submit(verify, ext=ext, url=url, count=len(links))
                time.sleep(random.uniform(0.1, 0.9))
            temp.clear()
    executor.shutdown()
    print_status(len(links))
    print(Fore.GREEN + "\n\n" + "-" * 60 + "\n")


def main():
    global online, offline

    path = input("\nВведите путь к директории: ")
    if not Path(path).exists() or not Path(path).is_dir() or not path:
        print("Директория не существует")
        sys.exit(0)

    time_start = time.monotonic()

    links = []
    files = [fil for fil in Path(path).iterdir() if Path(fil).suffix == ".m3u"]
    for nm, file in enumerate(sorted(files)):
        n = 0
        try:
            ext = ""
            with open(file, 'r', encoding='utf-8') as f:
                for nn in f.readlines():
                    if nn.startswith('#EXTINF'):
                        ext = nn.strip()
                        continue
                    elif nn.startswith("http"):
                        n += 1
                        if ext == "":
                            ext = "#EXTINF:-1, No title"
                        links.append(f'{ext}\n{nn.strip()}\n')
        except UnicodeDecodeError:
            print(f"\n[!!!] Не могу декодировать данные: {Path(file).name}\n")
            sys.exit(0)

        print(f'\n\n\n{Fore.YELLOW}[!] Checked file: {Fore.RESET}{Path(file).name} | {Fore.YELLOW}Count: '
              f'{Fore.RESET}{n} | {Fore.YELLOW}File: {Fore.RESET}{nm + 1}/{len(files)}')
        dl = len(f'[!] Checked file: {Path(file).name} | Count:{n} | File: {nm + 1}/{len(files)}') + 3
        print(Fore.GREEN + "=" * dl + "\n")

        check(links)

        save_status_error(str(file), online, offline)

        print(f"\n{Fore.GREEN}{'[*] All'.ljust(12)}{Fore.RESET}|{str(int((len(online)) + (len(offline)))).center(6)}| "
              f"{Fore.GREEN}channels")
        print(f"{Fore.GREEN}{'[*] Online'.ljust(12)}{Fore.RESET}|{str(int(len(online))).center(6)}| "
              f"{Fore.GREEN}channels")
        print(f"{Fore.GREEN}{'[*] Offline'.ljust(12)}{Fore.RESET}|{str(int(len(offline))).center(6)}| "
              f"{Fore.GREEN}channels\n")

        print(Fore.GREEN + "-" * 60 + "\n")

        if len(files) > 1:
            print(f'{Fore.GREEN}[@] Scan "{Path(file).name}" time {Fore.RESET}| '
                  f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
                  f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
                  f'{int(time.monotonic() - time_start) % 60:02d} с.\n')
            print(Fore.GREEN + "-" * 60)

        Path(file).unlink()

        online.clear()
        offline.clear()
        links.clear()

    print(f'{Fore.CYAN}\n[@] All Scan time {Fore.RESET}| '
          f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
          f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
          f'{int(time.monotonic() - time_start) % 60:02d} с.\n')


if __name__ == "__main__":
    main()
