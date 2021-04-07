#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import asyncio
import ssl
import sys
import re
from layer import handler, _chunked, _gzip, auth
from config import config


async def socket_handler(client_reader, client_writer):
    try:
        local = client_writer.get_extra_info('sockname')
        # print('recv connection from ', local)
        server_reader, server_writer = (None, None)
        # 响应请求的鉴权
        #proxy_type, host, port = auth.reply_auth(client_reader, client_writer)
        result = await auth.reply_auth(client_reader, client_writer)
        if result is None:
            client_writer.close()
            return
        # print(result)
        # 根据数据流提取信息, 建立连接
        proxy_type, server_reader, server_writer, *_ = \
            await handler.doSomethingBeforePip(
                client_reader, client_writer,
                proxy_type=result[0], host=result[1], port=int(result[2]),
                open=establishPureConnection)
        if server_reader is None:
            print('proxy_type err:', proxy_type)
            client_writer.close()
            return
        local = server_writer.get_extra_info('sockname')
        remote = server_writer.get_extra_info('peername')
        print(f'{local} ==> {remote}, type : {proxy_type}')
        # 建立管道
        asyncio.create_task(handler.pip(client_reader, server_writer))
        asyncio.create_task(handler.pip(server_reader, client_writer))
    except Exception as e:
        await handler.closeQuietly(client_writer)
        await handler.closeQuietly(server_writer)
        # Exception.with_traceback(e)
        # raise e


async def establishPureConnection(host, port, *kargs, **kwargs):
    # print('host:', host, ',port:', port)
    return await asyncio.open_connection(host, port)


async def main():
    if config.server_remote['ssl']:
        ssl_context = None
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_context.load_cert_chain(**conf)
        server = await asyncio.start_server(
            socket_handler, config.server_remote['addr'], config.server_remote['port'], ssl=ssl_context)
    else:
        server = await asyncio.start_server(
            socket_handler, config.server_remote['addr'], config.server_remote['port'])
    print("listening on port: %s, use SSL: %s\n"%(config.server_remote['port'], config.server_remote['ssl']))
    async with server:
        await server.serve_forever()


conf = config.server_remote['sslConfig']
if __name__ == '__main__':
    asyncio.run(main())
    #asyncio.run(socket_handler('', ''))
