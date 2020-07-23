from lib.packers import Chap
from lib.downloaders import SuggestionsDocxDownloader
pack = [
    Chap("{:03d}".format(n), SuggestionsDocxDownloader)
    for n in range(1, 122+1)
]
