from shutil import copyfile
from os.path import join, dirname
import os
import docx
from lib.downloaders import TextDownloader


class Chap:
    def __init__(self, name, downloader_cls):
        self.name = name
        self.downloader_cls = downloader_cls

    def requirements(self, id_dict):
        return [(self.downloader_cls, [id_dict[self.name]])]

    def get_dst(self, directory):
        return join(directory, self.name + self.downloader_cls.file_ext)

    def pack(self, directory, id_dict):
        src = join('dist', 'cache', self.downloader_cls.dir_name,
                   id_dict[self.name] + self.downloader_cls.file_ext)
        dst = self.get_dst(directory)
        copyfile(src, dst)


class DocxMerge:
    def __init__(self, name, names, downloader_cls):
        if downloader_cls.file_ext != '.docx':
            raise ValueError("Downloader must be of type docx")
        self.name = name
        self.names = names
        self.downloader_cls = downloader_cls

    def requirements(self, id_dict):
        return [(self.downloader_cls, [id_dict[name] for name in self.names])]

    def get_dst(self, directory):
        return join(directory, self.name + '.docx')

    def pack(self, directory, id_dict):
        doc_list = [join('dist', 'cache', self.downloader_cls.dir_name,
                    id_dict[name] + '.docx') for name in self.names]

        # the first chapter is the one all others
        # are added to in the following loop
        first_doc = docx.Document(doc_list[0])
        # Appending a page break in the end
        first_doc.add_page_break()

        for index, other in enumerate(doc_list[1:]):

            # Opening the other chapter
            other_doc = docx.Document(other)
            if index < len(doc_list) - 1:
                # Appending a page break in the end
                other_doc.add_page_break()

            # adding the contents of the other chapter to the first
            for element in other_doc.element.body:
                first_doc.element.body.append(element)

        # saving the newly created merged document
        first_doc.save(self.get_dst(directory))


class TextMerge:
    def __init__(self, name, names):
        self.name = name
        self.names = names
        self.downloader_cls = TextDownloader

    def requirements(self, id_dict):
        return [(self.downloader_cls, [id_dict[name] for name in self.names])]

    def get_dst(self, directory):
        return join(directory, self.name + '.txt')

    def pack(self, directory, id_dict):
        file_list = [join('dist', 'cache', self.downloader_cls.dir_name,
                     id_dict[name] + '.txt') for name in self.names]

        page_break = """

###############################################################

""".encode('utf-8-sig')

        with open(self.get_dst(directory), 'wb') as outfile:
            for index, path in enumerate(file_list):
                with open(path, 'rb') as fin:
                    if index != 0:
                        outfile.write(page_break)
                    outfile.write(fin.read())
