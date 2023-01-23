from pathlib import Path

from colorama import Fore
from colorama import init

init()


def save_status_error(path: str, status, error):
    print(f"{Fore.CYAN}SAVE DATA IN FILE\n{'-' * 17}\n")
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

    path_err = ""
    if len(error) > 0:
        (Path.cwd() / "checked" / "error").mkdir(exist_ok=True)
        try:
            name = Path.cwd() / "checked" / "error" / f'{Path(path).name.split(Path(path).suffix)[0]}_error_' \
                                                      f'{int(len(error))}.m3u'
            path_err = name
        except ValueError:
            name = Path.cwd() / "checked" / "error" / f'{Path(path).name}_error_{int(len(error))}.m3u'
            path_err = name
        with open(name, "a", encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            for item in sorted(error):
                f.write(f"{item}")
        print(f'{Fore.GREEN}ERROR SAVED: {Fore.YELLOW}"checked / error" -> "{name.name}"')

    print(Fore.GREEN + "\n" + "-" * 60)
    return path_err
