import os
from os.path import join
from shutil import copyfile
import re
from abc import abstractmethod

from zipfile import ZipFile
import tempfile
import glob
from typing import List

import asyncio
import aiohttp

import docx

done = set()


class Downloader:
    def __init__(self, dist):
        self.folder = join(dist, 'cache', self.dir_name)
        os.makedirs(self.folder, exist_ok=True)

    def download(self, ids):
        print("Downloading {} files with {}".format(len(ids), str(type(self))))
        loop = asyncio.get_event_loop()
        self.s = aiohttp.ClientSession()

        remaining_ids = ids
        futures = [self.download_single(id) for id in remaining_ids]
        for i in range(5):
            gathered = asyncio.gather(*futures,  return_exceptions=True)
            results = loop.run_until_complete(gathered)
            errors = [x for x in results if isinstance(x, Exception)]
            non_client = [e for e in errors
                          if not isinstance(e, aiohttp.ClientError)]
            if non_client:
                raise Exception(repr(non_client))
            remaining_ids = [id for result, id in zip(results, remaining_ids)
                             if isinstance(result, Exception)]
            if remaining_ids:
                if i < 4:
                    print("Connection error. {} left. Retrying..."
                          .format(len(remaining_ids)))
                    futures = [self.download_single(id)
                               for id in remaining_ids]
                else:
                    raise Exception(repr(errors))
            else:
                break

        loop.run_until_complete(self.s.close())
        self.s = None

    async def download_mime(self, file, gid, file_type):
        url = 'https://docs.google.com/document/d/{id}/export?format={type}' \
                .format(id=gid, type=file_type)
        r = await self.s.get(url, raise_for_status=True)
        content = await r.read()
        open(file, 'wb').write(content)

    async def download_single(self, gid):
        """ A wrapper method for do_download
        to make sure a file do not get downloaded twice"""
        if (type(self), gid) in done:
            return
        await self.do_download(gid)
        done.add((type(self), gid))

    def set_modified(self, gid, rev_id):
        open(join(self.folder, gid), 'w').write(rev_id)

    def get_modified(self, gid):
        try:
            return open(join(self.folder, gid)).read()
        except FileNotFoundError:
            return None

    @classmethod
    def requires(cls):
        return []

    @property
    @abstractmethod
    def dir_name():
        pass

    @property
    @abstractmethod
    def file_ext():
        pass

    @abstractmethod
    def do_download(self, gid):
        pass


class SuggestionsDocxDownloader(Downloader):
    file_ext = '.docx'
    dir_name = 'suggestions_docx'

    async def do_download(self, gid):
        file = join(self.folder, gid + '.docx')
        file_type = 'docx'
        await self.download_mime(file, gid, file_type)
        # Word requires cs_italic and cs_bold for hebrew characters
        doc = docx.Document(file)
        for p in doc.paragraphs:
            for r in p.runs:
                if r.font.italic:
                    r.font.cs_italic = True
                if r.font.bold:
                    r.font.cs_bold = True
        doc.save(file)


class DocxDownloader(Downloader):
    file_ext = '.docx'
    dir_name = 'docx'

    @classmethod
    def requires(cls):
        return [SuggestionsDocxDownloader]

    async def do_download(self, gid):
        src = join('dist', 'cache', SuggestionsDocxDownloader.dir_name,
                   gid + '.docx')
        file = join(self.folder, gid + '.docx')
        copyfile(src, file)


class PdfDownloader(Downloader):
    file_ext = '.pdf'
    dir_name = 'pdf'

    async def do_download(self, gid):
        file = join(self.folder, gid + '.pdf')
        file_type = 'pdf'
        await self.download_mime(file, gid, file_type)


class TextDownloader(Downloader):
    file_ext = '.txt'
    dir_name = 'txt'

    async def do_download(self, gid):
        file = join(self.folder, gid + '.txt')
        file_type = 'txt'
        await self.download_mime(file, gid, file_type)


class EpubDownloader(Downloader):
    file_ext = '.epub'
    dir_name = 'epub'

    async def do_download(self, gid):
        file = join(self.folder, gid + '.epub')
        file_type = 'epub'
        await self.download_mime(file, gid, file_type)

        # Remove white characters between html tags
        with tempfile.TemporaryDirectory() as directory:
            with ZipFile(file, 'r') as zipfin:
                zipfin.extractall(path=directory)
            for html in glob.glob(join(directory, '**', '*.xhtml')):
                with open(html, 'rb') as fin:
                    content = fin.read().decode('utf-8')
                    replaced = re.sub(r'>\s*<', '><', content)
                    with open(html, 'wb') as fout:
                        fout.write(replaced.encode('utf-8'))
            with ZipFile(file, 'w') as zipfout:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        path = join(root, file)
                        relpath = os.path.relpath(path, directory)
                        zipfout.write(path, arcname=relpath)
