#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import asyncio
import sys
import os
import re
import ssl
currentDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(currentDir)
sys.path.append(parentDir)
from layer import _gzip
from layer import _chunked
ssl._create_default_https_context = ssl._create_unverified_context

defaultHeaders = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Accept": "*/*",
}

class Response:
    def __init__(self, data, headers, statusCode, statusBrief):
        self.data = data
        self.headers = headers
        self.statusCode = statusCode
        self.statusBrief = statusBrief

async def get(host, *kargs, **kwargs):
    return await request(host, *kargs, method='GET', **kwargs)

async def request(host: str, path: str = '/', port: int = None, \
    scheme: str = 'HTTPS', server_hostname: str = None, verify:bool = True,\
    method: str = 'GET', data:bytes = None, timeout = 20.0, headers: dict = None):
    # set default settings
    if scheme == 'HTTPS':
        port = 443 if port is None else port
        server_hostname = host if server_hostname is None else server_hostname
        _ssl = True if verify else ssl._create_unverified_context()
    else:
        port = 80 if port is None else port
        server_hostname = None
        _ssl = None
    # establish connection
    reader, writer = \
        await asyncio.open_connection(host, port,
                                      server_hostname=server_hostname,
                                      ssl=_ssl)
    # send HTTP head
    new_header = defaultHeaders.copy()
    new_header['Host'] = f'{host}:{port}'
    if data:
        new_header['Content-length'] = len(data)
    if isinstance(headers, dict):
        new_header.update(headers)
    head = [f'{method} {path} HTTP/1.1']
    for key, value in new_header.items():
        head.append(f'{key}: {value}')
    head.append('\r\n')
    content = '\r\n'.join(head)
    writer.write(content.encode('latin1'))
    await writer.drain()
    if data:
        writer.write(data)
        await writer.drain()
    # parse HTTP head response
    response_data = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), timeout=timeout)
    lines = response_data.decode('utf-8').splitlines()
    search = re.search(r'HTTP/1\.1 ([0-9]+) (.*)' ,lines[0])
    statusCode, statusBrief = int(search.group(1)), search.group(2)
    headers = {}
    for index in range(1, len(lines) -1):
        line = lines[index]
        search = re.search(r'([^:]+) *: *(.*)' ,line)
        if search:
            headers[search.group(1).lower()] = search.group(2).strip()
    # decompress or un-trucate the data
    if b'Transfer-Encoding: chunked' in response_data:
        reader, writer = _chunked.unchunk(reader, writer)
    if b'Content-Encoding: gzip' in response_data:
        reader, writer = _gzip.gzip_decompress(reader, writer)
    # 
    content = b''
    try:
        if 'content-length' in headers:
            length = int(headers['content-length'])
            content = await asyncio.wait_for(reader.readexactly(length), timeout=timeout)
        else:
            temp_data = await asyncio.wait_for(reader.read(1024), timeout=timeout)
            while temp_data:
                content += temp_data
                temp_data = await asyncio.wait_for(reader.read(1024), timeout=timeout)
    except Exception as e:
        raise e
        pass
    writer.close()
    response = Response(content, headers, statusCode, statusBrief)
    return response


async def a_test():
    import base64
    import dns_helper
    domain = 'www.baidu.com'
    a_query = dns_helper.gen_A_query(domain, id = 1)
    domain_base64 = base64.encodebytes(a_query).decode().strip('\r\n=')
    print(domain_base64)
    # headers = {
    #     'accept': 'application/dns-message'
    # }
    res = await get('dns.alidns.com', path = '/dns-query?dns=' + domain_base64)
    # res = await get('doh.pub', path = '/dns-query?dns=' + domain_base64)
    # res = await get('cloudflare-dns.com', path = '/dns-query?dns=' + domain_base64)
    if res.statusCode == 200:
        dns = dns_helper.parse(res.data)
        if dns is None:
            print('dns is None')
        else:
            print(dns.id)
            if len(dns.answer) > 0:
                for answer in dns.answer:
                    print(answer._name, answer._rData)
    else:
        print(res.statusCode, res.statusBrief)
    pass
if __name__ == '__main__':

    asyncio.run(a_test())
