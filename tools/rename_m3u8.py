from pathlib import Path

num = 0
print("\nПереименование файлов m3u8".upper())
print("")

for file in Path(input("Введите путь к директории для переименования>>> ")).iterdir():
    if Path(file).suffix == ".m3u8":
        if Path(file).exists():
            num += 1
            name = f'{Path(file).name.split(Path(file).suffix)[0]}_{num}_copy.m3u'
        else:
            name = f'{Path(file).name.split(Path(file).suffix)[0]}.m3u'
        print(name)
        Path(file).rename(f'{Path(file).parent / name}')
