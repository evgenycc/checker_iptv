import shutil
import sys
import time
from pathlib import Path

from colorama import Fore
from colorama import init

init()

count = 0
links = set()
merge = []
error = []


def check_url_inline(url: str, ext_info: str):
    """
    Проверка дубликатов и добавление в основное множество.

    :param url: Ссылка для проверки.
    :param ext_info: Информация о канале.
    """
    global count, links, merge
    if url.strip() not in links:
        merge.append(f'{ext_info}\n{url.strip()}\n')
        count += 1
    links.add(url.strip())


def save_merge(name: str):
    """
    Сохранение проверенных данных без дубликатов.

    :param name: Имя для сохраняемого файла.
    """
    global count, merge
    with open(Path.cwd() / f"{name}.m3u", "w", encoding="utf-8") as ch:
        ch.write("#EXTM3U\n")
        for channel in merge:
            ch.write(channel)

    if error:
        for file in error:
            (Path(file).parent / 'unicode_error').mkdir(exist_ok=True)
            shutil.move(file, Path(file).parent / 'unicode_error' / Path(file).name)
        print("\nИмеются файлы требующие исправления кодировки.\nСмотрите файл: 'error.txt'\n")
        with open(Path.cwd() / "error.txt", "w", encoding="utf-8") as er:
            er.write("Файлы требующие исправления кодировки: \n\n")
            for err in error:
                er.write(f'{Path(err).name}\n')

    print(f"{Fore.GREEN}\nОригинальных ссылок: {Fore.BLUE}{count}")


def merged(path_dir, flag):
    """
    Выборка информации о файле и ссылок из плейлиста.

    :param path_dir: Ссылка на папку с файлами.
    :param flag: Флаг очистки информации. 0 - не очищает; 1 - очищает, оставляет только название канала.
    """
    count_file = 0
    print("")
    for nn, file in enumerate(Path(path_dir).iterdir()):
        count_file += 1
        print("\r\033[K", end="")
        print(f'\r{Fore.YELLOW}{count_file} | Обработка: {nn+1}', end="")
        if file.suffix == ".m3u":
            ext_info = ''
            try:
                with open(file, 'r', encoding="utf-8") as f:
                    for item in f.readlines():
                        if item.startswith("#EXTINF"):
                            ext_info = f"#EXTINF:-1 ,{item.split(',')[-1].replace('#EXTGRP:', '').strip()}" \
                                if flag == 1 else item.strip()
                        elif item.startswith("http"):
                            if item.strip().split("/")[-1].split(".")[-1] == "mpd" \
                                    or item.strip().split("/")[-1].split(".")[-1] == "flv":
                                continue
                            check_url_inline(item.strip(), ext_info)
            except UnicodeDecodeError:
                error.append(file)
                continue
    return count_file


def main():
    """
    Получение пользовательских данных. Запуск функций проверки
    на дубликаты и сохранения проверенного.

    """
    global merge, count
    print(f"{Fore.GREEN}{'-' * 43}\n{Fore.YELLOW}ПРОВЕРКА НА ДУБЛИКАТЫ И ОБЪЕДИНЕНИЕ КАНАЛОВ\n{Fore.GREEN}{'-' * 43}\n")
    path = input(Fore.RESET + "Введите путь к директории: ")
    name = input("Введите имя для объединенного файла: ")

    if not Path(path).exists() or not Path(path).is_dir():
        print(Fore.RED + "Директории не существует")
        sys.exit(0)
    st = time.monotonic()
    count_file = merged(path, 0)
    save_merge(name)
    print("\r\033[K", end="")
    print(f"\n{Fore.GREEN}Обработано файлов: {Fore.BLUE}{count_file}")
    print(f"{Fore.GREEN}Затраченное время: {Fore.BLUE}{time.monotonic() - st:.2f} c.")


if __name__ == "__main__":
    main()
