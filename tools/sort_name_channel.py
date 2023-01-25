import json
import sys
from pathlib import Path

sort_ch = dict()


def save_dict(name: str):
    """
    Сохранение результатов в файлы.

    :param name: Путь к файлу для сохранения json.
    """
    with open(name, 'w', encoding='utf-8') as f:
        json.dump(sort_ch, f, indent=4, ensure_ascii=False)
    m3u_name = Path(name).parent / f'{Path(name).name.replace(Path(name).suffix, "")}_sort.m3u'
    with open(m3u_name, 'w', encoding='utf-8') as file:
        file.write("#EXTM3U\n")
        for key in sort_ch:
            for item in sort_ch.get(key):
                file.write(f'{sort_ch.get(key).get(item)}\n{item}\n')
                print("\r\033[K", end="")
                print(f"\rСохранение: {sort_ch.get(key).get(item).split(',')[-1].replace('#EXTGRP:', '').strip()} | {item}", end="")
    print("")


def sort_channel(ext: str, name: str, url: str):
    """
    Сортировка каналов по наименованиям в словаре.

    :param ext: Описание канала.
    :param name: Имя канала.
    :param url: Ссылка на канал.
    """
    if name not in sort_ch:
        sort_ch[name] = dict()
    sort_ch[name].update({url: ext})


def main():
    """
    Открытие файла. Перебор ссылок и описаний. Передача в функцию
    для добавления в словарь.
    """
    print("\nСортировка каналов по имени".upper())
    print("")
    path = input("Введите путь к файлу m3u >>> ")

    if not Path(path).exists() or not Path(path).is_file():
        print("Пути не существует")
        sys.exit(0)

    ext, name = "", ""
    with open(path, 'r', encoding='utf-8') as f:
        for ln in f.readlines():
            if ln.startswith("#EXTINF"):
                ext = ln.strip()
                name = "No name" if ext.split(',')[-1].replace('#EXTGRP:', '').strip() is None \
                    else ext.split(',')[-1].replace('#EXTGRP:', '').strip()
                continue
            elif ln.startswith("http"):
                sort_channel(ext, name, ln.strip())
                pass
    s_name = Path(path).parent / f'{Path(path).name.replace(Path(path).suffix, "")}_sort.json'
    save_dict(str(s_name))


if __name__ == "__main__":
    main()
