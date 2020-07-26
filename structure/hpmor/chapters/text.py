from lib.packers import Chap
from lib.downloaders import TextDownloader
pack = [
    Chap("{:03d}".format(n), TextDownloader)
    for n in range(1, 122+1)
]
