#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from asyncio.streams import StreamWriter, StreamReader

class ChunkedWriter:

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
        content = ('%x\r\n' % (len(data))).encode('utf-8')
        self._writer.write(content)
        self._writer.write(data)
        self._writer.write(b'\r\n')
        # print('写入chunked数据', data, content)

    def writelines(self, data):
        raise Exception('Not implemented!')

    def write_eof(self):
        return self._writer.write_eof()

    def can_write_eof(self):
        return self._writer.can_write_eof()

    def close(self):
        self._writer.write(b'0\r\n\r\n')
        if self.can_write_eof():
            self.write_eof()
        return self._writer.close()

    def is_closing(self):
        return self._writer.is_closing()

    async def wait_closed(self):
        await self._writer.wait_closed()

    def get_extra_info(self, name, default=None):
        return self._writer.get_extra_info(name, default)

    async def drain(self):
        await self._writer.drain()


async def unchunkReader(reader, unchunkedReader):
    try:
        while not reader.at_eof():
            # print('unchunkReader read size')
            data = await reader.readline()
            if len(data) == 0:
                continue
            size = int(data[:-2], 16)
            if size == 0:
                # print('unchunkReader size == 0')
                data = await reader.read(2)
                unchunkedReader.feed_eof()
                break
            # print('unchunkReader read data')
            data = await reader.readexactly(size)
            # print('unchunkReader read data \r\n')
            _end = await reader.readexactly(2)
            if _end == b'\r\n':
                unchunkedReader.feed_data(data)
                continue
            raise Exception(
                f'chunked data: {len(data)} not equals {size + 2}')
    except Exception as e:
        print('------------', e)
        unchunkedReader.feed_eof()
        unchunkedReader.set_exception(e)
        raise e
    # print('unchunkedReader end')
    # print(f'unchunkedReader.at_eof() {unchunkedReader.at_eof()}')
    # print(f'reader.at_eof() {reader.at_eof()}')

def chunk(reader, writer):
    return reader, ChunkedWriter(writer)


def unchunk(reader, writer):
    new_reader = StreamReader(limit=reader._limit, loop=reader._loop)
    task = asyncio.create_task(unchunkReader(reader, new_reader))
    # asyncio.gather([task])
    _feed_eof = new_reader.feed_eof

    def new_feed_eof():
        if not task.done():
            task.cancel()
        _feed_eof()
    new_reader.feed_eof = new_feed_eof
    return new_reader, writer


def exception_handler(loop, context):
    # print(loop)
    # print(context)
    # print(type(loop))
    # print(type(context))
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')

loop = asyncio.get_event_loop()
loop.set_exception_handler(exception_handler)
