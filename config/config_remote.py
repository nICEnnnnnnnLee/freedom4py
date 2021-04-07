

hosts = {                                   # 自定义域名ip映射, 可以为{}
    "www.baidu.com": "14.215.177.38",
}

server_remote = {
    "addr": '0.0.0.0',                    # 监听ip 127.0.0.1 仅监听本地; 0.0.0.0表示监听来自网络的ip
    "port": 2377,                           # 监听端口
    "ssl": True,                            # 代理服务器是否开启ssl(套了nginx后建议关闭)
    "sslConfig": {                          # ssl 为true时生效, 本地server的证书
        'certfile': r'./cert/youdomain.pem',
        'keyfile': r'./cert/youdomain.key',
    },
}

users = {                                   # 有效的用户组
    'username': 'pwd',
    'admin': 'admin',
}
salt = '4567'                               # 用户名密码校验的盐值, 需要与客户端一致