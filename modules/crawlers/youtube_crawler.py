import yt_dlp

def download_subtitles(url):

    ydl_opts = {
        'writesubtitles': True,
        'skip_download': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
