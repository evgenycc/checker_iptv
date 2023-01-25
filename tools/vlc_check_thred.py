# pip install python-vlc

import concurrent.futures
import subprocess
import sys
import time
from pathlib import Path

import vlc
from colorama import Fore
from colorama import init

init()

status = []
error = []
st_count, err_count, all_ch = 0, 0, 0


def save_status_error(path):
    (Path(path).parent / 'checked_vlc').mkdir(exist_ok=True)
    if len(status) > 0:
        name = Path(path).parent / 'checked_vlc' / f'good_vlc.m3u'
        with open(name, "a", encoding='utf-8') as f:
            for item in status:
                if "tricolor" in item:
                    continue
                f.write(f"{item}")
    if len(error) > 0:
        name = Path(path).parent / 'checked_vlc' / f'error_vlc.m3u'
        with open(name, "a", encoding='utf-8') as f:
            for item in error:
                f.write(f"{item}")


def vlc_player(url, ext, nm):
    player, state = "", ""
    try:
        instance = vlc.Instance('--input-repeat=-1', '--no-fullscreen')
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        player.play()
        time.sleep(0.5)
        state = str(player.get_state())

        if state in ["vlc.State.Error", "State.Error", "State.Ended", "State.Opening"]:
            player.stop()
            error.append(f'{ext}\n{url}\n')
            print(f'\n{nm} | Stream is working. Current state = {state.upper()}\n')
            return
        else:
            print(f'\n{nm} | Stream is working. Current state = {state.upper()}\n')
            player.stop()
            status.append(f'{ext}\n{url}\n')
            return
    except Exception:
        print(f'\nStream is dead. Current state = {state}\n')
        player.stop()
        error.append(f'{ext}\n{url}\n')
        return


def main():
    global status, error, st_count, err_count, all_ch
    path = input("Введите путь к директории: ")
    if not Path(path).exists() or not Path(path).is_dir():
        print("Директории не существует или введенный путь не ведет к директории")
        sys.exit(0)

    time_start = time.monotonic()
    for num, path in enumerate(Path(path).iterdir()):
        if Path(path).suffix == ".m3u":
            nm = 0
            print(f"Проверка файла: {num + 1} | {path}\n")
            if not Path(path).exists():
                sys.exit(0)
            ext = ""
            with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
                with open(path, 'r', encoding='utf-8') as file:
                    for line in file.readlines():
                        if line.startswith("#EXTINF"):
                            ext = line.strip()
                            continue
                        if line.startswith("http"):
                            nm += 1
                            all_ch += 1
                            executor.submit(vlc_player, url=line.strip(), ext=ext, nm=nm)
                            time.sleep(0.3)

            save_status_error(path)
            subprocess.Popen("clear", shell=True)
            time.sleep(0.3)
            print(f"\nGood: {len(status)}")
            print(f"Error: {len(error)}\n")
            st_count = st_count + len(status)
            err_count = err_count + len(error)
            status.clear()
            error.clear()
            Path(path).unlink()

    print(f"\nAll Channel: {all_ch}")
    print(f"\nAll Good: {st_count}")
    print(f"All Error: {err_count}\n")
    print(f'{Fore.LIGHTGREEN_EX}All Scan time | {Fore.RESET}'
          f'{(int(time.monotonic() - time_start) // 3600) % 24:d} ч. '
          f'{(int(time.monotonic() - time_start) // 60) % 60:02d} м. '
          f'{int(time.monotonic() - time_start) % 60:02d} с.\n')


if __name__ == "__main__":
    main()
