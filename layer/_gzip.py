#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import gzip
from asyncio.streams import StreamWriter, StreamReader

class GzipWriter:

    def __init__(self, writer):
        self._writer = writer
        self._transport = writer._transport
        
    def __repr__(self):
        info = [self.__class__.__name__,
                f'transport={self._writer._transport!r}']
        if self._writer._reader is not None:
            info.append(f'reader={self._writer._reader!r}')
        return '<{}>'.format(' '.join(info))

    @property
    def transport(self):
        return self._writer.transport()

    def write(self, data):
        content = gzip.compress(data)
        self._writer.write(content)
        # print('写入gzip数据', data, content)

    def writelines(self, data):
        raise Exception('Not implemented!')

    def write_eof(self):
        return self._writer.write_eof()

    def can_write_eof(self):
        return self._writer.can_write_eof()

    def close(self):
        if self.can_write_eof():
            self.write_eof()
        return self._writer.close()

    def is_closing(self):
        return self._writer.is_closing()

    async def wait_closed(self):
        if self.can_write_eof():
            self.write_eof()
        await self._writer.wait_closed()

    def get_extra_info(self, name, default=None):
        return self._writer.get_extra_info(name, default)

    async def drain(self):
        await self._writer.drain()

count = 0
async def decompressReader(reader, decompressReader):
    try:
        _buffer = None
        while not reader.at_eof():
            # print('decompressReader reader.readline()')
            data = await reader.readline()
            if len(data) == 0:
                # print('decompressReader len(data)')
                continue
            if _buffer:
                data = _buffer + data
            try:
                decompressReader.feed_data(gzip.decompress(data))
                _buffer = None
            except:
                global count
                count += 1
                _buffer = data
            continue
    except Exception as e:
        print('------------', e)
        #decompressReader.set_exception(e)
    decompressReader.feed_eof()
    # print('decompressReader end')
    # print(f'decompressReader.at_eof() {decompressReader.at_eof()}')
    # print(f'reader.at_eof() {reader.at_eof()}')

def gzip_compress(reader, writer):
    return reader, GzipWriter(writer)


def gzip_decompress(reader, writer):
    new_reader = StreamReader(limit=reader._limit, loop=reader._loop)
    task = asyncio.create_task(decompressReader(reader, new_reader))
    _feed_eof = new_reader.feed_eof
    def new_feed_eof():
        if not task.done():
            task.cancel()
        _feed_eof()
    new_reader.feed_eof = new_feed_eof
    return new_reader, writer


# def exception_handler(loop, context):
#     print(loop)
#     print(context)
#     print(type(loop))
#     print(type(context))


# loop = asyncio.get_event_loop()
# loop.set_exception_handler(exception_handler)
