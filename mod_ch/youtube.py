from pytube import YouTube, exceptions


def check_youtube(url: str) -> bool:
    try:
        yt = YouTube(url)
        if yt.video_id:
            return True
    except exceptions.RegexMatchError:
        return False
