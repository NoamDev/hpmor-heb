from lib.packers import DocxMerge
from lib.downloaders import DocxDownloader
pack = [
    DocxMerge("1", ["{:03d}".format(n) for n in range(1, 22)],
              DocxDownloader),
    DocxMerge("2", ["{:03d}".format(n) for n in range(22, 38)],
              DocxDownloader),
    DocxMerge("3", ["{:03d}".format(n) for n in range(38, 65)],
              DocxDownloader),
    DocxMerge("4", ["{:03d}".format(n) for n in range(65, 86)],
              DocxDownloader),
    DocxMerge("5", ["{:03d}".format(n) for n in range(86, 100)],
              DocxDownloader),
    DocxMerge("6", ["{:03d}".format(n) for n in range(100, 122)],
              DocxDownloader),
]
