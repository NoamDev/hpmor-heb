from lib.packers import Chap
from lib.downloaders import PdfDownloader
pack = [
    Chap("{:03d}".format(n), PdfDownloader)
    for n in range(1, 122+1)
]
