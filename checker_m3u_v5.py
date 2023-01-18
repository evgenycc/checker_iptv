# pip install colorama requests bs4 lxml

import copy
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from os import system
from pathlib import Path
from re import findall
from urllib.parse import urljoin

import cv2
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from colorama import init
from pytube import YouTube, exceptions

requests.packages.urllib3.disable_warnings()

init()

text_plain = {"23 45 58 54", "5B 70 6C 61 79 6C 69 73", "74 65 78 74 2F 70 6C 61 69 6E", "EF BB BF 00", "FF FE 00 00",
              "74 65 78 74 2F 70 6C 61 69 6E", "3B 20 63 68 61 72 73 65 74 3D", "49 53 4F 2D 38 38 35 39 2D 31",
              "69 73 6F 2D 38 38 35 39 2D 31", "55 54 46 2D 38", "FE FF 00 00"}

html = {"7B 22", "3C 21 44 4F 43 54 59 50 45 20", "48 54 4D 4C TT", "3C 48 54 4D 4C TT", "3C 48 45 41 44 TT",
        "3C 53 43 52 49 50 54 TT", "3C 49 46 52 41 4D 45 TT", "3C 48 31 TT", "3C 44 49 56 TT", "3C 46 4F 4E 54 TT",
        "3C 54 41 42 4C 45 TT", "3C 41 TT", "3C 53 54 59 4C 45 TT", "3C 54 49 54 4C 45 TT", "3C 42 TT", "3C 42 52 TT",
        "3C 42 4F 44 59 TT", "3C 50 TT", "3C 21 2D 2D TT", "3C 3F 78 6D 6C", "25 50 44 46 2D", "4E 6F", "3C 41", "3C",
        "45 52"}

stop_list = ["/errors/", "test_end.ts", "buy.ts", "money.ts", "buy_packet.ts", "empty.ts", "key.ts", "/error/",
             "/NOT_CLIENT/", "http://logo.apk-red.com/tv/hata.jpg", "http://v.viplime.fun/video/user.ts", "/forbidden/",
             "zabava-block-htvod.cdn.ngenix.net", "err-ru.sulfat.li", "/000/", "BanT0ken", "/activate/", "/404/",
             "/405/", "www.cloudflare-terms-of-service-abuse.com", "http://cdn01.lifeyosso.fun:8080/connect/mono.m3u8",
             "http://nl4.iptv.monster/9999/video.m3u8", "http://v.viplime.fun/video/block.ts", "auth.m3u8", "/block/",
             "auth", "logout", "VDO-X-404", "offline", "logout.mp4", "error.tv4.live", "block-ip-video.ts", "/420/",
             "delete.ts", "http://langamepp.com/user.mp4", "http://m.megafonpro.ru/http_errors?error=404"]

headers = {
    "User-Agent": "libmpv",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Icy-MetaData": "1"
}

status = []
error = []
cnt = 0


def save_status_error(path: str):
    """
    Сохранение содержимого списков status и error с рабочими и нерабочими ссылками.

    :param path: Путь к открытому для проверки файлу.
    """
    global status, error
    print("\n\n" + "-" * 60)
    print(f"\n{Fore.CYAN}SAVE DATA IN FILE\n{'-'*17}\n")
    (Path.cwd() / "checked").mkdir(exist_ok=True)

    if len(status) > 0:
        (Path.cwd() / "checked" / "good").mkdir(exist_ok=True)
        try:
            name = Path.cwd() / "checked" / "good" / f'{Path(path).name.split(Path(path).suffix)[0]}_good_' \
                                                     f'{int(len(status))}.m3u'
        except ValueError:
            name = Path.cwd() / "checked" / "good" / f'{Path(path).name}_good_{int(len(status))}.m3u'
        with open(name, "a", encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for item in sorted(status):
                f.write(f"{item}")
        print(f'{Fore.GREEN}GOOD SAVED: {Fore.YELLOW}"checked / good" -> "{name.name}"')

    if len(error) > 0:
        (Path.cwd() / "checked" / "error").mkdir(exist_ok=True)
        try:
            name = Path.cwd() / "checked" / "error" / f'{Path(path).name.split(Path(path).suffix)[0]}_error_' \
                                                      f'{int(len(error))}.m3u'
        except ValueError:
            name = Path.cwd() / "checked" / "error" / f'{Path(path).name}_error_{int(len(error))}.m3u'
        with open(name, "a", encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for item in sorted(error):
                f.write(f"{item}")
        print(f'{Fore.GREEN}ERROR SAVED: {Fore.YELLOW}"checked / error" -> "{name.name}"')

    print(Fore.GREEN + "\n" + "-" * 60)


def find_mpd(txt: str, url: str) -> bool:
    """
    Парсинг плейлиста в формате xml с расширением ".mpd".

    :param txt: Текст запроса.
    :param url: Стартовый url для формирования ссылки на сегмент потока.
    :return: True или False, в зависимости от полученных результатов.
    """
    soup = BeautifulSoup(txt, 'xml')
    seg = soup.find_all('SegmentTemplate')
    seg_list = []
    for i in seg:
        if i.get('initialization') is not None:
            seg_list.append(urljoin(url, i.get('initialization')))
    if seg_list:
        return True if load_txt(seg_list[0]) else False


def find_stop(url: str) -> bool:
    """
    Поиск паттернов с помощью которых можно отсеять некоторые
    каналы с заблокированным содержимым.

    :param url: Ссылка для поиска паттерна.
    :return: True или False в зависимости от результата.
    """
    for st in stop_list:
        if findall(f"{st}", url):
            return True
    return False


def find_link(url: str, text: str) -> (list, bool):
    """
    Поиск ссылок на сегменты потока в полученном тексте запроса.

    :param url: Ссылка на поток, для формирования ссылки на сегмент.
    :param text: Текст запроса для поиска ссылок на сегменты или сегментов.
    :return: Список со ссылками или False.
    """
    lnk = []
    for i in text.splitlines():
        if i.startswith("#"):
            continue
        elif not i.strip():
            continue
        lnk.append(i.strip()) if i.startswith("http") else lnk.append(urljoin(url, i.strip()))
    return lnk if lnk else False


def load_txt(ses, url: str) -> bool:
    """
    Получение данных по ссылке на поток.

    :param ses: Сессия.
    :param url: Ссылка на поток.
    :return: True или False в зависимости от полученного результата.
    """
    # Проверка наличия ссылки на YouTube и запуск
    # проверки наличия идентификатора видео.
    # Если идентификатор есть, ссылка рабочая.
    if url.startswith("https://www.youtube.com") \
            or url.startswith("https://youtube.com") \
            or url.startswith("http://www.youtube.com") \
            or url.startswith("http://youtube.com"):
        try:
            yt = YouTube("http://www.youtube.com/watch?v=6UFOJjDqL_g")
            if yt.video_id:
                return True
        except exceptions.RegexMatchError:
            return False
    try:
        # Запрос данных по ссылке на поток с включенной функцией получения данных в потоке. Если статус-код 200,
        # выполняем последующие проверки. Первая - наличие в ссылке расширения с файлом xml, в котором
        # парсятся ссылки на сегменты видео.
        res = ses.get(url, headers=headers, timeout=10, stream=True, allow_redirects=True, verify=False)
        if res.status_code == 200:
            if find_stop(res.url):
                return False

            if ".mpd" in res.url:
                if find_mpd(res.text, res.url):
                    return True
                return False

            # Итерация по поученному контенту и проверка первых 64 байт на наличие
            # в получаемом потоке определенного типа данных по их сигнатуре.
            # Переводим байты в hex, проверяем: 1. Наличие ссылки (сигнатура: 68 74...);
            # 2. Проверка наличия в полученных данных html. Если есть, возвращаем False;
            # 3. Проверка наличия в полученных данных текста. Если находим, передаем в
            # функцию для обработки.
            # Если поток получен, но в нем не найдена ни одна сигнатура, будем считать,
            # что в данном потоке передаются медиа-данные, а значит возвращаем True.
            for chunk in res.iter_content(64):
                hex_bytes = " ".join(['{:02X}'.format(byte) for byte in chunk])
                if hex_bytes[0:11] == "68 74 74 70":
                    if load_txt(ses, chunk.decode().strip()):
                        return True
                for it in html:
                    if hex_bytes[0:len(it)].upper() == it:
                        return False
                for tx_pl in text_plain:
                    if hex_bytes[0:len(tx_pl)].upper() == tx_pl:
                        for item in res.iter_content(1024):
                            chunk = chunk + item
                        if lnk := find_link(res.url, chunk.decode()):
                            if len(lnk) > 10:
                                lnk = lnk[-10:]
                            for ln in lnk:
                                if find_stop(ln):
                                    return False
                                if load_txt(ses, ln):
                                    return True
                                continue
                        elif not lnk:
                            return False
                    continue
                return True
            return False
        return False
    except Exception as ex:
        return True if "ICY 200 OK" in str(ex) else False


def check_rtmp(url: str) -> bool:
    """
    Проверка медиа-потока по протоколу передачи данных rtmp.
    Для проверки используется OpenCV.

    :param url: Ссылка на поток для проверки.
    :return: True или False в зависимости от результата.
    """
    video = cv2.VideoCapture(url)
    while True:
        grabbed, frame = video.read()
        if grabbed:
            video.release()
            return True
        return False


def verification(url: str, ext: str, count: int, re_ch=False):
    """
    Запуск проверки ссылок на поток и обработка результатов
    возвращенных из функции проверки.

    :param url: Ссылка на поток.
    :param ext: Описание потока.
    :param count: Количество ссылок для перепроверки.
    :param re_ch: Статус перепроверки.
    """
    global status, error, cnt

    if re_ch == "rtmp":
        if check_rtmp(url):
            status.append(f'{ext}\n{url}\n')
            cnt += 1
            print(f"\r{Fore.YELLOW}Check rtmp: {Fore.RESET}{cnt}/{count} | {Fore.YELLOW}Online: {Fore.RESET}"
                  f"{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
            return
        else:
            error.append(f'{ext}\n{url}\n')
            cnt += 1
            print(f"\r{Fore.YELLOW}Check rtmp: {Fore.RESET}{cnt}/{count} | {Fore.YELLOW}Online: {Fore.RESET}"
                  f"{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
            return

    ses = requests.Session()

    if load_txt(ses, url):
        status.append(f'{ext}\n{url}\n')
        if re_ch:
            cnt += 1
            print(f"\r{Fore.YELLOW}Re-Check: {Fore.RESET}{cnt}/{count} | {Fore.YELLOW}Online: {Fore.RESET}"
                  f"{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
        else:
            print(f"\r{Fore.YELLOW}Check: {Fore.RESET}{len(status) + len(error)}/{count} | {Fore.YELLOW}Online: "
                  f"{Fore.RESET}{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
    else:
        error.append(f'{ext}\n{url}\n')
        if re_ch:
            cnt += 1
            print(f"\r{Fore.YELLOW}Re-Check: {Fore.RESET}{cnt}/{count} | {Fore.YELLOW}Online: {Fore.RESET}"
                  f"{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
        else:
            print(f"\r{Fore.YELLOW}Check: {Fore.RESET}{len(status) + len(error)}/{count} | {Fore.YELLOW}Online: "
                  f"{Fore.RESET}{len(status)} | {Fore.YELLOW}Offline: {Fore.RESET}{len(error)}",
                  end="")
    ses.close()


def main():
    """
    Получение данных от пользователя о сканируемой директории.
    Формирование списка файлов в директории.
    Подсчет количества ссылок на потоки и вывод в терминал.
    Запуск потоков для проверки наличия медиа-контента.
    Запуск перепроверки нерабочих потоков.
    Вывод данных о результатах проверки в терминал.
    """
    global status, error, cnt
    # path = input("\nВведите путь к директории с m3u: ")
    # if not Path(path).exists() or not Path(path).is_dir():
    #     print("Нет такой директории или указанный путь не является директорией")
    #     sys.exit(0)
    path = "/home/vev/py_proj/checker_v4/000"

    time_start = time.monotonic()

    files = [fil for fil in Path(path).iterdir() if Path(fil).suffix == ".m3u"]
    rtmp = []

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

            num = 0
            ext = ""
            with ThreadPoolExecutor(max_workers=5) as executor:
                with open(file, 'r', encoding='utf-8') as fl:
                    for line in fl.readlines():
                        if line.startswith("#EXTINF"):
                            ext = line.strip()
                            continue
                        elif line.startswith("rtmp"):
                            rtmp.append(f"{ext}\n{line.strip()}")
                        elif line.startswith("http"):
                            num += 1
                            if len(line.strip().split()) > 1:
                                line = line.strip().replace(" ", "")
                            executor.submit(verification, url=line.strip(), ext=ext, count=n)

            if error:
                re_check = copy.deepcopy(error)
                error.clear()
                print("\r\033[K", end="")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for i in re_check:
                        ext = i.split("\n")[0].strip()
                        url = i.split("\n")[1].strip()
                        executor.submit(verification, url=url, ext=ext, count=len(re_check), re_ch=True)
                re_check.clear()
                cnt = 0

            if rtmp:
                print("\r\033[K", end="")
                with ThreadPoolExecutor(max_workers=5) as executor:
                    for i in rtmp:
                        ext = i.split("\n")[0].strip()
                        url = i.split("\n")[1].strip()
                        executor.submit(verification, url=url, ext=ext, count=len(rtmp), re_ch="rtmp")
                rtmp.clear()
                cnt = 0

            save_status_error(str(file))
            print(f"\n{Fore.GREEN}{'All'.ljust(8)}{Fore.RESET}|{str(int((len(status)) + (len(error)))).center(6)}| {Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Online'.ljust(8)}{Fore.RESET}|{str(int(len(status))).center(6)}| {Fore.GREEN}channels")
            print(f"{Fore.GREEN}{'Offline'.ljust(8)}{Fore.RESET}|{str(int(len(error))).center(6)}| {Fore.GREEN}channels\n")

            print(f'{Fore.GREEN}Scan time {Fore.RESET}| '
                  f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
                  f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
                  f'{int(time.monotonic() - time_start) % 60:02d} с.\n')
            print(Fore.GREEN + "-" * 60 + "\n")

            status.clear()
            error.clear()

            Path(file).unlink()
        system(f'''notify-send "All operation complete"''')
    except UnicodeDecodeError:
        print(f"\nНе могу декодировать данные: {Path(file).name}\n")
        system(f'''notify-send "Не могу декодировать данные: {Path(file).name}"''')
        sys.exit(0)


if __name__ == "__main__":
    main()
