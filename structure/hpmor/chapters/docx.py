from lib.packers import Chap
from lib.downloaders import DocxDownloader
pack = [
    Chap("{:03d}".format(n), DocxDownloader)
    for n in range(1, 122+1)
]
