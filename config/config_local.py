from .config_basic import *

hosts = {                                   # 域名ip映射，本地解析时会用到
    "www.baidu.com": "14.215.177.38",
}
usePac = True
# pacAddr 可以是dict形式的网址，也可以是本地文件
# 'https://raw.githubusercontent.com/zhiyi7/gfw-pac/master/gfw.pac'
# pacAddr = {
#     'host': 'raw.githubusercontent.com',
#     'path': '/zhiyi7/gfw-pac/master/gfw.pac',
#     'scheme': 'HTTPS',
#     'verify': True
# }
pacAddr = './gfw_pac'


server_local = {
    "addr": '0.0.0.0',                      # 本地监听ip
    "port": 2376,                           # 本地监听端口
    "ssl": False,                           # 本地代理服务器开启ssl
    "sslConfig": {                          # ssl 为true时生效, 本地server的证书
        'certfile': r'./cert/youdomain.pem',
        'keyfile': r'./cert/youdomain.key',
    },
    "remote": {
        "addr": 'youdomain',                # 远程ip/domain
        "port": 443,                       # 远程端口
        # "addr": '127.0.0.1',                # 远程ip/domain
        # "port": 2377,                       # 远程端口
        "ssl": True,                        # 与remote建立的连接是否套上ssl
        "verify": False,
        "server_hostname": 'youdomain',   # remote.ssl 为true时生效，发送的sni名称
    },
}

##### 用于伪装的HTTP的头部, 域名/端口设置不正确可能无法建立连接  #####
path = '/path'
http_version = '1.1'
domain = 'youdomain'  # 自定义，或者server_local['remote']['server_hostname']
port = '443'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

##### 用于鉴权 #####
username = 'username'                   # 用户名
pwd = 'pwd'                             # 密码
salt = '4567'                           # 盐值,用于加密密码
cookies = {                             # 初始cookies, 将会加入 伪装的HTTP的头部
    "my_type":  UNKNOWN_TYPE,           # 该参数将指示服务器如何处理数据流, 不知道的话直接UNKNOWN_TYPE
    "my_domain":  '',                   # 配合 my_type 使用, 域名、端口有效时，服务器将直接以此来建立连接
    "my_port":  '0',                    # 配合 my_type 使用, 域名、端口有效时，服务器将直接以此来建立连接
}

# 是否在远程解析
is_parsed_remote = False
