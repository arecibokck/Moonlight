from pytube import YouTube
import sys

def yt_download(url, n):

    yt = YouTube(url)

    yt.set_filename(str(n))

    video = yt.get('mp4', '720p')

    video.download(<path>)

if __name__=="__main__":

  yt_download(sys.argv[1], sys.argv[2])
