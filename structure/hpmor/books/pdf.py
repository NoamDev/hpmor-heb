from lib.packers import PdfMerge
pack = [
    PdfMerge("1", ["{:03d}".format(n) for n in range(1, 22)]),
    PdfMerge("2", ["{:03d}".format(n) for n in range(22, 38)]),
    PdfMerge("3", ["{:03d}".format(n) for n in range(38, 65)]),
    PdfMerge("4", ["{:03d}".format(n) for n in range(65, 86)]),
    PdfMerge("5", ["{:03d}".format(n) for n in range(86, 100)]),
    PdfMerge("6", ["{:03d}".format(n) for n in range(100, 122)]),
]
