import subprocess
import sys
import time
from pathlib import Path

from colorama import Fore
from colorama import init
from simple_term_menu import TerminalMenu

init()

split_set = []
num = 0


def save_split(path: str, cnt: str):
    """
    Сохранение информации с указанным количеством элементов.

    :param cnt: Кол-во файлов для разбивки.
    :param path: Путь к исходному файлу.
    """
    global num
    dir_split = Path(path).parent / f"split_{cnt}_channel_{str(Path(path).name.split(Path(path).suffix)[0])}"
    s = f'0{str(num)}' if num < 10 else num
    dir_split.mkdir(exist_ok=True)
    with open(dir_split / f"{Path(path).name.split(Path(path).suffix)[0]}_{s}.m3u", "a",
              encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for sst in split_set:
            f.write(sst)


def split_list(path: str, chunk_count: int):
    """
    Разбивка общего количества каналов на указанное в переменной.
    Сохранение разбитых частей в файлы.

    :param path: Путь к папке с файлом.
    :param chunk_count: Количество каналов в файле после разбивки.
    """
    global num, split_set

    num_line = len(f"РАЗБИВАЮ ФАЙЛ НА ЧАСТИ ПО {chunk_count} ЭЛ.")
    print(Fore.YELLOW + f"\nРАЗБИВАЮ ФАЙЛ НА ЧАСТИ ПО {chunk_count} ЭЛ.\n{Fore.GREEN}{'-'*num_line}")
    ext_inf = '#EXTINF: -1, Null'
    try:
        with open(path, 'r', encoding='utf-8') as file:
            for line in file.readlines():
                if line.startswith("#EXTINF"):
                    ext_inf = line.strip()
                elif line.startswith("http"):
                    split_set.append(f"{ext_inf}\n{line.strip()}\n")
                if len(split_set) == chunk_count:
                    num += 1
                    print(Fore.YELLOW + f"\rЧасть {Fore.BLUE}{num+1} {Fore.YELLOW}обработана", end="")
                    save_split(path, str(chunk_count))
                    split_set.clear()
        if 0 < len(split_set) < chunk_count:
            num += 1
            print(Fore.YELLOW + f"\rЧасть {Fore.BLUE}{num} {Fore.YELLOW}обработана", end="")
            save_split(path, str(chunk_count))
        print(f"\r\b", end="")
        print(Fore.GREEN + f"Файл {Path(path).name} разбит. Количество частей: {Fore.BLUE}{num}")
    except UnicodeDecodeError:
        print(f"Не могу декодировать данные: {Path(path).name}")
        sys.exit(0)


def main():
    """
    Получение пользовательских данных. Запуск разбивки файла.
    """
    global split_set, num
    subprocess.call("clear", shell=True)
    try:
        print(f"{Fore.GREEN}{'-'*47}\n{Fore.YELLOW}РАЗБИВКА ФАЙЛА M3U НА БОЛЕЕ МЕЛКИЕ ЧАСТИ\n{Fore.GREEN}"
              f"{'-'*47}\n")
        opt = ["1.Обработка файла", "2.Обработка директории", "3.Выход"]
        ch = TerminalMenu(opt).show()
        if opt[ch] == "1.Обработка файла":
            path = input(Fore.RESET + "Введите путь к файлу: ")
            if not Path(path).exists() or path == "" or not Path(path).is_file():
                print(Fore.RED + "Введенного пути не существует")
                sys.exit(0)
            chunk_count = input("Введите количество каналов в файле: ")
            st = time.monotonic()
            split_list(path, int(chunk_count))
            print(f"{Fore.GREEN}Затраченное время: {Fore.BLUE}{time.monotonic() - st:.2f} c.")
        elif opt[ch] == "2.Обработка директории":
            path = input("Введите путь к директории: ")
            if not Path(path).exists() or path == "" or not Path(path).is_dir():
                print(Fore.RED + "Введенного пути не существует")
                sys.exit(0)
            chunk_count = input("Введите количество каналов в файле: ")
            st = time.monotonic()
            for file in Path(path).iterdir():
                if Path(file).suffix == ".m3u":
                    split_list(str(file), int(chunk_count))
                    split_set.clear()
                    num = 0
            print(f"{Fore.GREEN}Затраченное время: {Fore.BLUE}{time.monotonic() - st:.2f} c.")
        elif opt[ch] == "3.Выход":
            raise TypeError
    except (KeyboardInterrupt, TypeError):
        subprocess.call("clear", shell=True)
        print(Fore.YELLOW + "\n\nGood by, my friend! Good by!\n")


if __name__ == "__main__":
    main()
