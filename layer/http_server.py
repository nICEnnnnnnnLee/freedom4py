#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import asyncio
import ssl
import sys
import re
try:
    from . import config, _chunked, _gzip
except:
    import config, _chunked, _gzip

def genHeader():
    raw = '''
HTTP/1.1 200 OK
Cache-Control: max-age=0, must-revalidate
Content-Type: text/plain
Server: apache
Transfer-Encoding: chunked
Content-Encoding: gzip
    '''
    lines = raw.strip().splitlines()
    header = '\r\n'.join(lines)
    header += '\r\n\r\n'
    print(header)
    return header

async def socket_handler(client_reader, client_writer):

    data = await client_reader.read(1024)
    data = data.decode('utf-8')
    # TODO 合法性检查
    print(genHeader())
    client_writer.write(genHeader().encode('utf-8'))
    await client_writer.drain()

    client_reader, client_writer = _chunked.chunk(client_reader, client_writer)
    client_reader, client_writer = _gzip.gzip_compress(client_reader, client_writer)

    client_writer.write('{"key": "value"}\r\n'.encode('utf-8'))
    await client_writer.drain()
    client_writer.write('{"key1": "value1"}\r\n'.encode('utf-8'))
    await client_writer.drain()
    client_writer.write('{"key2": "value2"}\r\n'.encode('utf-8'))
    await client_writer.drain()
    client_writer.close()
    await asyncio.sleep(1)
    print('client_writer closed')

async def pip(from_reader, to_writer):
    try:
        await to_writer.drain()
        data = await from_reader.read(1024)
        while data:
            to_writer.write(data)
            await to_writer.drain()
            data = await from_reader.read(1024)
    except Exception as e:
        print(e, '\r\n-layer_server-\r\n')
        pass
    finally:
        if not to_writer.is_closing():
            to_writer.close()
            await to_writer.wait_closed()


async def main():
    if config.http_server['ssl']:
        ssl_context = None
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(**conf)
        server = await asyncio.start_server(
            socket_handler, config.http_server['addr'], config.http_server['port'], ssl=ssl_context)
    else:
        server = await asyncio.start_server(
            socket_handler, config.http_server['addr'], config.http_server['port'])
    async with server:
        await server.serve_forever()


def getHost(sni):
    host = hosts.get(sni, sni)
    return host


hosts = config.hosts
conf = config.http_server['sslConfig']
if __name__ == '__main__':
    asyncio.run(main())
    #asyncio.run(socket_handler('', ''))
