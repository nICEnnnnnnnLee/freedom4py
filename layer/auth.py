#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import base64
import random
import hashlib
import time
import re
from asyncio.streams import StreamWriter, StreamReader
from config import config


def get_md5(content):
    md5 = hashlib.md5()
    md5.update(content.encode('utf-8'))
    return md5.hexdigest()


def genCookieStr(cookies):
    cookieList = [f'{key}={value}' for (key, value) in cookies.items()]
    return '; '.join(cookieList)


def gen_new_Cookie(host, port, proxy_type):
    if proxy_type is None:
        pass


async def send_auth(reader, writer, host=None, port=None, proxy_type=None):
    # print('send_auth host, port, proxy_type:', proxy_type, host, port)
    new_cookie = raw_cookies.copy()
    _time = int(time.time()*1000)
    _token = get_md5(pwd + salt + str(_time))
    new_cookie.update({
        'my_time': _time,
        'my_token': _token,
    })
    if (proxy_type is not None) and host and port:
        new_cookie.update({
            'my_type': proxy_type,
            'my_domain': host,
            'my_port': port,
        })
        # print('gen new cookie')
    else:
        # print('use raw cookie')
        pass

    bytes_header = _send_auth(new_cookie)
    writer.write(bytes_header)

    await writer.drain()
    # 检查头部返回结果 结果中必须含有 auth: ok 字段
    data = await reader.readuntil(b'\r\n\r\n')
    # print('data auth reply', data)
    if b'auth: ok\r\n' not in data:
        # if b'HTTP/1.1 101 Switching Protocols\r\n' not in data:
        return None
    # 更新cookie
    data_str = data.decode('utf-8')
    re_iter = re.finditer(
        'Set-Cookie: ([^=]+)=([^:]+);', data_str, flags=re.IGNORECASE)
    for match in re_iter:
        raw_cookies[match.group(1)] = match.group(2)
    return data


async def reply_auth(reader, writer):
    try:
        # print('auth.reply_auth')
        data = await asyncio.wait_for(reader.readuntil(b'\r\n\r\n'), 60.0)
        data = data.decode('utf-8')
        # print('data', data)
        search = re.search(r'\r\nCookie:(.*?)\r\n', data, flags=re.IGNORECASE)
        if search:
            cookie_str = search.group(1)
            # print('cookie_str', cookie_str)
            # print('users', users)
            _username = get(cookie_str, 'my_username')
            _token = get(cookie_str, 'my_token')
            _time = get(cookie_str, 'my_time')
            _pwd = users.get(_username)
            _time_delta = time.time() - int(_time)/1000
            # print('_time_delta', _time_delta)
            if _time and (_time_delta < 3600) and _pwd:
                _valid_token = get_md5(_pwd + salt + _time)
                if _token == _valid_token:
                    _type = get(cookie_str, 'my_type')
                    _domain = get(cookie_str, 'my_domain')
                    _port = get(cookie_str, 'my_port')
                    writer.write(bytes_reply_auth_ok)
                    await writer.drain()
                    return _type, _domain, _port
            print(' not a valid user')
    except Exception as e:
        print(e)
        #raise e
        pass
    writer.write(bytes_reply_403)
    await writer.drain()
    # return None, None, None


def get(cookie_str, key):
    search = re.search(f'{key} *=([^;]*)', cookie_str)
    if search:
        return search.group(1).strip()


def _reply_403():
    headers = [
        r'HTTP/1.1 403 Forbidden',
        r'Content-Length: 0',
        r'Connection: closed',
        r'Server: newbee/1.2.2',
        '\r\n',
    ]
    head = '\r\n'.join(headers)
    return head.encode('utf-8')


def _reply_auth_ok():
    headers = [
        r'HTTP/1.1 101 Switching Protocols',
        r'Upgrade: websocket',
        r'auth: ok',
        f'Sec-WebSocket-Accept: {server_websocket_key}',
        '\r\n',
    ]
    head = '\r\n'.join(headers)
    return head.encode('utf-8')


def _send_auth(cookies):
    headers = [
        f'GET {path} HTTP/{http_version}',
        f'Host: {domain}:{port}',
        f'User-Agent: {user_agent}',
        r'Accept: */*',
        r'Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        r'Accept-Encoding: gzip',
        r'Sec-WebSocket-Version: 13',
        f'Origin: https://{domain}',
        r'Sec-WebSocket-Extensions: permessage-deflate',
        f'Sec-WebSocket-Key: {local_websocket_key}',
        r'Connection: keep-alive, Upgrade',
        r'Pragma: no-cache',
        r'Cache-Control: no-cache',
        r'Upgrade: websocket',
        f'Cookie: {genCookieStr(cookies)}',
        '\r\n',
    ]
    head = '\r\n'.join(headers)
    return head.encode('utf-8')


if config.run == config.LOCAL:
    path = config.path
    http_version = config.http_version
    domain = config.domain
    port = config.port
    user_agent = config.user_agent
    username = config.username
    pwd = config.pwd
    salt = config.salt
    # __current_time = int(time.time()*1000)
    # token = get_md5(pwd + salt + str(__current_time))
    raw_cookies = config.cookies
    random_bytes = bytes([random.randint(0, 255) for i in range(16)])
    local_websocket_key = str(
        base64.encodebytes(random_bytes), 'utf-8').strip()
    raw_cookies.update({
        # "my_token":  token,
        "my_username":  username,
    })
    bytes_send_auth = _send_auth(raw_cookies)
elif config.run == 'remote':
    random_bytes = bytes([random.randint(0, 255) for i in range(16)])
    server_websocket_key = str(
        base64.encodebytes(random_bytes), 'utf-8').strip()
    users = config.users
    salt = config.salt
    bytes_reply_403 = _reply_403()
    bytes_reply_auth_ok = _reply_auth_ok()
