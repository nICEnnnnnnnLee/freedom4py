#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""

from util import sni_helper
from config import config
import asyncio
import re
import socket
import struct


UNKNOWN_TYPE = config.UNKNOWN_TYPE
PLAIN = config.PLAIN
HTTP_PROXY = config.HTTP_PROXY
HTTPS_PROXY = config.HTTPS_PROXY
SNI_PROXY = config.SNI_PROXY
SOCKS5_PROXY = config.SOCKS5_PROXY


def getHost(sni):
    host = hosts.get(sni, sni)
    return host


hosts = config.hosts
# (proxy_type, server_reader, server_writer, host, port)


async def socks5_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    if not data:
        data = await client_reader.readexactly(3)
        if data != b'\x05\x01\x00':
            return SOCKS5_PROXY, None, None, None, None
    # 1. no auth https://tools.ietf.org/html/rfc1928#page-3
    client_writer.write(b"\x05\x00")
    await client_writer.drain()
    # 2. https://tools.ietf.org/html/rfc1928#page-4
    data = await client_reader.readexactly(4)
    mode = data[1]
    addrtype = data[3]
    # 3. reply https://tools.ietf.org/html/rfc1928#page-5
    # Command not support          b"\x05\x07\x00\x01"
    # Address type not supported   b"\x05\x08\x00\x01"
    # Connection refused           b"\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00"
    if mode == 1:  # 1. Tcp connect
        # print('addrtype', addrtype)
        if addrtype == 1:       # IPv4
            _host = socket.inet_ntoa(await client_reader.readexactly(4))
        elif addrtype == 3:     # Domain name
            addr_len = await client_reader.readexactly(1)[0]
            _host = await client_reader.readexactly(addr_len)
        _port = struct.unpack('>H', await client_reader.readexactly(2))[0]
        if not (host and port):
            host = _host
            port = _port
        # print('getHost(host), port', getHost(host), port)
        server_reader, server_writer = await open(
            getHost(host), port, **args)

        # 构建回复
        reply = b"\x05\x00\x00\x01"
        local_host, local_port = server_writer.get_extra_info('sockname')
        reply += socket.inet_aton(local_host) + struct.pack(">H", local_port)
        client_writer.write(reply)
        return SOCKS5_PROXY, server_reader, server_writer, host, port
    else:
        client_writer.write(b"\x05\x07\x00\x01")  # Command not supported
        await client_writer.drain()
        return SOCKS5_PROXY, None, None, None, None


async def https_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    # print('https_handler data:', data)
    if not data:
        data = await client_reader.readuntil(b'\r\n\r\n')
    if not (host and port):
        head = data.decode('latin1')
        search = re.search(
            r'^CONNECT ([^:]+)(?::([0-9]+))? HTTP[0-9/\.]+\r\n', head)
        if search:
            host = search.group(1)
            port = int(search.group(2)) if search.group(2) else 443
        else:
            return await http_handler(client_reader, client_writer, data=data)
    if (host and port):
        server_reader, server_writer = await open(
            getHost(host), port, **args)
        client_writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
        return HTTPS_PROXY, server_reader, server_writer, host, port
    else:
        return HTTPS_PROXY, None, None, None, None


async def http_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    if data is None:
        data = await client_reader.readuntil(b'\r\n\r\n')
    if not (host and port):
        head = data.decode('latin1')
        search = re.search(r'\r\nHost: ([^:]+)(?::([0-9]+))?\r\n', head)
        if search:
            host = search.group(1)
            port = int(search.group(2)) if search.group(2) else 80
    if (host and port):
        server_reader, server_writer = await open(
            getHost(host), port, **args)
        server_writer.write(data)
        return HTTP_PROXY, server_reader, server_writer, host, port
    return HTTP_PROXY, None, None, None, None


async def sni_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    if data is None:
        data = await client_reader.read(1024)
    if not host:
        host = sni_helper.GetSniFromSslPlainText(data)
    if not port:
        port = 443
    if host is not None:
        server_reader, server_writer = await open(
            getHost(host), port, **args)
        server_writer.write(data)
        return SNI_PROXY, server_reader, server_writer, host, port
    return UNKNOWN_TYPE, None, None, None, None


_alphas = b'NUIEDLGORPSTCAnuiedlgorpstca'


async def unkown_type_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    # data = await client_reader.read(1024)
    try:
        # print('unkown_type_handler is running')
        data = await client_reader.readexactly(3)
        if data == b'\x05\x01\x00':  # socks5 no auth
            # print('unkown_type_handler: socks5')
            return await socks5_handler(client_reader, client_writer, host=None, port=None, data=data, open=open, **args)
        elif data[0] in _alphas and data[1] in _alphas and data[2] in _alphas:
            tail = await client_reader.readuntil(b'\r\n\r\n')
            data += tail
            if data.startswith(b'CONNECT'):
                # print('unkown_type_handler: https')
                return await https_handler(client_reader, client_writer, host=None, port=None, data=data, open=open, **args)
            elif data.startswith(b"GET ") or data.startswith(b"POST ") or data.startswith(b"PUT ")\
                    or data.startswith(b"DELETE ") or data.startswith(b"OPTIONS ") or data.startswith(b"TRACE "):
                # print('unkown_type_handler: http')
                return await http_handler(client_reader, client_writer, host=None, port=None, data=data, open=open, **args)
        else:
            # print('unkown_type_handler: sni')
            return await sni_handler(client_reader, client_writer, host=None, port=None, data=data, open=open, **args)
    except Exception as e:
        return UNKNOWN_TYPE, None, None, None, None


async def plain_handler(client_reader, client_writer, host=None, port=None, data=None, open=None, **args):
    # print('plain_handler connect to (host, port) -  data', host, port, data)
    server_reader, server_writer = \
        await open(
            getHost(host), port, **args)
    return PLAIN, server_reader, server_writer, host, port

_handlers = {
    str(UNKNOWN_TYPE): unkown_type_handler,
    str(PLAIN): plain_handler,
    str(HTTP_PROXY): http_handler,
    str(HTTPS_PROXY): https_handler,
    str(SNI_PROXY): sni_handler,
    str(SOCKS5_PROXY): socks5_handler,
}


async def doSomethingBeforePip(client_reader, client_writer, proxy_type=None, host=None, port=None, data=None, open=None,**kwargs):
    # proxy_type, host, port
    if proxy_type is not None:
        co = _handlers.get(proxy_type, unkown_type_handler)
        return await co(client_reader, client_writer, host=host, port=port, data=data, open=open,**kwargs)
    else:
        return await unkown_type_handler(client_reader, client_writer,
                                         host=host, port=port, data=data, open=open,**kwargs)


async def closeQuietly(writer):
    try:
        if writer:
            writer.close()
            await writer.wait_closed()
    except:
        pass


async def pip(from_reader, to_writer, *kargs):
    try:
        await to_writer.drain()
        data = await from_reader.read(1024)
        while data:
            to_writer.write(data)
            await to_writer.drain()
            data = await from_reader.read(1024)
    except Exception as e:
        pass
    finally:
        await closeQuietly(to_writer)
