#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys, os
import re
import ssl
currentDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(currentDir)
sys.path.append(parentDir)
from config import config
import _chunked
import _gzip

ssl._create_default_https_context = ssl._create_unverified_context
"""
将数据增加一层
"""

# https://www.pythonheidong.com/static/bootstrap/Bootstrap_files/bootstrap.min.css


def genHeader():
    raw = '''
GET / HTTP/1.1
Host: www.baidu.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip
Connection: keep-alive
Cookie: Hm_lvt_11f780e4e4ccd4e99b101eac776e93e4=1616133496,1616162064,1616208515,1616307187; __cfduid=d70c9e55b2aaa4a0514d566bbce3d82631615536919
Upgrade-Insecure-Requests: 1
Pragma: no-cache
Cache-Control: no-cache
    '''

#     raw = '''
# GET http://union.china.com.cn/zhuanti/43476.files/owl.carousel.css HTTP/1.1
# Host: union.china.com.cn
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0
# Accept: text/css,*/*;q=0.1
# Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
# Accept-Encoding: gzip
# Connection: keep-alive
# Referer: http://innovate.china.com.cn/node_1009951.html
# Cookie: wdcid=550becec7b95c6e4
#     '''
    lines = raw.strip().splitlines()
    header = '\r\n'.join(lines)
    header += '\r\n\r\n'
    print(header)
    return header
# 'Content-Length: 1024\r\n' + \


async def main():
    print('--main--')
    print(config.http_client)
    if config.http_client["ssl"]:
        reader, writer = \
            await asyncio.open_connection(config.http_client["addr"],
                                          config.http_client["port"],
                                          server_hostname=config.http_client["server_hostname"],
                                          ssl=ssl._create_unverified_context())
    else:
        reader, writer = \
            await asyncio.open_connection(config.http_client["addr"],
                                          config.http_client["port"])
    print('--main begin--')
    writer.write(genHeader().encode('latin1'))
    await writer.drain()
    print('header is sent')
    data = await reader.readuntil(b'\r\n\r\n')
    print('header is back\r\n', data.decode())
    if b'Transfer-Encoding: chunked' in data:
        reader, writer = _chunked.unchunk(reader, writer)
    if b'Content-Encoding: gzip' in data:
        reader, writer = _gzip.gzip_decompress(reader, writer)
    data = await reader.read(1024)
    while data:
        print(data)
        # print('\r\nxxxxxxxxxxxxxxx\r\n')
        # print(data[:5])
        data = asyncio.wait_for(reader.read(1024), timeout=120.0)
        #data = await reader.read(1024)
    # print('\rclient end\r\n')

async def a_test():
    pass
if __name__ == '__main__':
    
    #asyncio.run(main())
    
    # str = 'www.example.com'
    # bytes_data = str.encode('utf-8')
    # print(type(bytes_data))
    # hex_data = [ "%x"%x for x in bytes_data]
    # print(hex_data)
    # str = '2001:db8:abcd:12:1:2:3:4'
    # print(str.encode('utf-8'))
    response = '''
    00 00 81 80 00 01 00 01 00 00 00 00 03 77 77 77
    07 65 78 61 6d 70 6c 65 03 63 6f 6d 00 00 1c 00
    01 c0 0c 00 1c 00 01 00 00 0e 7d 00 10 20 01 0d
    b8 ab cd 00 12 00 01 00 02 00 03 00 04
    '''
    res_strs = response.strip().replace('  ', '').replace('\n', ' ').split(' ')
    res_bytes_list = [ int(str, base=16) for str in res_strs]
    res_bytes = bytes(res_bytes_list)
    print(res_bytes)
    res_str = res_bytes.decode('ascii')
    print(res_str)
