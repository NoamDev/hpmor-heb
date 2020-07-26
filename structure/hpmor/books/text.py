from lib.packers import TextMerge
pack = [
    TextMerge("1", ["{:03d}".format(n) for n in range(1, 22)]),
    TextMerge("2", ["{:03d}".format(n) for n in range(22, 38)]),
    TextMerge("3", ["{:03d}".format(n) for n in range(38, 65)]),
    TextMerge("4", ["{:03d}".format(n) for n in range(65, 86)]),
    TextMerge("5", ["{:03d}".format(n) for n in range(86, 100)]),
    TextMerge("6", ["{:03d}".format(n) for n in range(100, 122)]),
]
