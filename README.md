<h1 align="center">  
    <strong>
        Freedom
    </strong>
</h1>
<p align="center">
    端到端数据流量伪装加密研究
  <br/>
    <strong>仅供学习研究使用，请勿用于非法用途</strong>
</p>


## :star:相关Repo
| 项目名称  | 简介 | 
| ------------- | ------------- |   
| [freedom4py](https://github.com/nICEnnnnnnnLee/freedom4py)  |  python3实现，包含local端、remote端  | 
| [freedom4j](https://github.com/nICEnnnnnnnLee/freedom4j)  |  java实现，包含local端、remote端  | 
| [freedom4NG](https://github.com/nICEnnnnnnnLee/freedom4NG)  | Android java实现，仅包含local端；单独使用可作为DNS、Host修改器 | 
 



## :star:一句话说明  
将本地代理数据伪装成指向远程端的HTTP(S) WebSocket流量。

## :star:简介  
+ 在配置正确的情况下，python3、java、Android版本的local端和remote端可以配合使用。  
+ local端实现了HTTP(S)、SOCKS5、SNI的自动代理，仅需一个端口，即可自动识别各种代理类型。  
+ local端支持pac文件解析，可将流量分为直连和走remote端两种。  
+ local端到remote端可以套上一层HTTP(S)，表现行为与Websocket无异，经测试**可过CDN与Nginx**。  
+ local端到remote端支持简单的用户名密码验证。  
+ 支持一种特殊模式，该模式下将数据原封不动加密转发，remote端解密后识别特征再进行HTTP(S)、SOCKS5、SNI的自动代理。  
+ 包含了一个不成熟的DNS服务器实现，可以通过DNS over HTTPS查询结果，再以UDP报文的方式返回结果。  

## :star:缺陷  
+ 仅支持TCP，不支持UDP
+ Socks5代理仅支持IPv4，不支持IPv6

## :star:如何配置  


<details>
<summary>local端配置`config/config_local.py`</summary>



```py

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
        "port": 443,                        # 远程端口
        "ssl": True,                        # 与remote建立的连接是否套上ssl
        "verify": False,
        "server_hostname": 'youdomain',     # remote.ssl 为true时生效，发送的sni名称
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
```
</details>

<details>
<summary>remote端配置`config/config_remote.py`</summary>



```py
hosts = {                                   # 自定义域名ip映射, 可以为{}
    "www.baidu.com": "14.215.177.38",
}

server_remote = {
    "addr": '0.0.0.0',                      # 监听ip 127.0.0.1 仅监听本地; 0.0.0.0表示监听来自网络的ip
    "port": 443,                            # 监听端口
    "ssl": False,                           # 代理服务器是否开启ssl(套了nginx后建议关闭)
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
```
</details>








## :star:如何运行  
+ 运行本地端  
```
python server_local.py
```

+ 运行远程端
```
python server_remote.py
```