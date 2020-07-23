from lib.packers import Chap
from lib.downloaders import EpubDownloader
pack = [
    Chap("{:03d}".format(n), EpubDownloader)
    for n in range(1, 122+1)
]
