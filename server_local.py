#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import asyncio
import ssl
import sys
import re
from layer import _chunked, _gzip, auth, handler
from config import config



async def socket_handler(client_reader, client_writer):
    # print('a request is post')
    try:
        server_reader, server_writer = (None, None)
        if config.is_parsed_remote:
            # server_reader, server_writer = await justOpenConnectionToServer()
            server_reader, server_writer = await establishPureConnection(host=None, port=None)
        else:
            proxy_type, server_reader, server_writer, *_ = \
                await handler.doSomethingBeforePip(
                    client_reader, client_writer,
                    proxy_type=config.UNKNOWN_TYPE,
                    host=config.server_local['remote'],
                    port=int(config.server_local['port']),
                    open=establishPureConnection,
                    # server_reader=server_reader,
                    # server_writer=server_writer,
                )
        # 直接架设管道
        asyncio.create_task(handler.pip(client_reader, server_writer))
        asyncio.create_task(handler.pip(server_reader, client_writer))
    except Exception as e:
        await handler.closeQuietly(client_writer)
        await handler.closeQuietly(server_writer)

async def justOpenConnectionToServer():
    if config.server_local["remote"]["ssl"]:
        ssl_context = True if config.server_local["remote"]["verify"] else ssl._create_unverified_context()
        server_reader, server_writer = await asyncio.open_connection(
            config.server_local["remote"]["addr"],
            config.server_local["remote"]["port"],
            server_hostname=config.server_local["remote"]["server_hostname"],
            ssl=ssl_context)
    else:
        server_reader, server_writer = await asyncio.open_connection(
            config.server_local["remote"]["addr"],
            config.server_local["remote"]["port"])
    return server_reader, server_writer

async def establishPureConnection(host, port, **kwargs):
    # print('local establishPureConnection is running..')
    if host and port and pac is not None:
        proxy_str = pac.find_proxy_for_url('/', host)
        if proxy_str.startswith('DIRECT'):
            print(f'proxy directly  to ==> {host}:{port} ')
            return await asyncio.open_connection(host, port)
        print(f'proxy by server to ==> {host}:{port} ')
    
    server_reader, server_writer = await justOpenConnectionToServer()
    data = await auth.send_auth(server_reader, server_writer, host=host, port=port, proxy_type=config.PLAIN)
    if data is None:
        print('Cannot estabish connection to server')
        raise Exception('tried to connect to server: auth failed')
    # print('auth header:', data)
    # 根据需要架设管道解析数据
    #print('header is back\r\n', data.decode())
    if b'Transfer-Encoding: chunked' in data:
        server_reader, server_writer = _chunked.unchunk(
            server_reader, server_writer)
    if b'Content-Encoding: gzip' in data:
        server_reader, server_writer = _gzip.gzip_decompress(
            server_reader, server_writer)
    return server_reader, server_writer

async def try_load_pac():
    if config.usePac:
        global pac
        try:
            if isinstance(config.pacAddr,dict):
                from util import http
                res = await http.get(**config.pacAddr)
                if res.statusCode == 200:
                    pac_js = res.data.decode('utf-8')
            elif isinstance(config.pacAddr, str):
                with open(config.pacAddr, 'r') as f:
                    pac_js = f.read()
            from pac.pac import PACFile
            pac = PACFile(pac_js)
        except Exception as e:
            print(e)
            import warnings
            warnings.warn('PAC module load failed')
            pac = None
async def main():
    await try_load_pac();
    if config.server_local['ssl']:
        ssl_context = None
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(**conf)
        server = await asyncio.start_server(
            socket_handler, config.server_local['addr'], config.server_local['port'], ssl=ssl_context)
    else:
        server = await asyncio.start_server(
            socket_handler, config.server_local['addr'], config.server_local['port'])
    async with server:
        await server.serve_forever()

conf = config.server_local['sslConfig']
pac = None
if __name__ == '__main__':
    import logging
    logging.getLogger('asyncio').setLevel(logging.DEBUG)
    asyncio.run(main())

    '''
    for task in asyncio.Task.all_tasks():
        task.cancel()
    '''