<h1 align="center">  
    <strong>
        Freedom
    </strong>
</h1>
<p align="center">
    �˵�����������αװ�����о�
  <br/>
    <strong>����ѧϰ�о�ʹ�ã��������ڷǷ���;</strong>
</p>


## :star:���Repo
| ��Ŀ����  | ��� | 
| ------------- | ------------- |   
| [freedom4py](https://github.com/nICEnnnnnnnLee/freedom4py)  |  python3ʵ�֣�����local�ˡ�remote��  | 
| [freedom4j](https://github.com/nICEnnnnnnnLee/freedom4j)  |  javaʵ�֣�����local�ˡ�remote��  | 
| [freedom4NG](https://github.com/nICEnnnnnnnLee/freedom4NG)  | Android javaʵ�֣�������local�ˣ�����ʹ�ÿ���ΪDNS��Host�޸��� | 
 



## :star:һ�仰˵��  
�����ش�������αװ��ָ��Զ�̶˵�HTTP(S) WebSocket������

## :star:���  
+ ��������ȷ������£�python3��java��Android�汾��local�˺�remote�˿������ʹ�á�  
+ local��ʵ����HTTP(S)��SOCKS5��SNI���Զ���������һ���˿ڣ������Զ�ʶ����ִ������͡�  
+ local��֧��pac�ļ��������ɽ�������Ϊֱ������remote�����֡�  
+ local�˵�remote�˿�������һ��HTTP(S)��������Ϊ��Websocket���죬������**�ɹ�CDN��Nginx**��  
+ local�˵�remote��֧�ּ򵥵��û���������֤��  
+ ֧��һ������ģʽ����ģʽ�½�����ԭ�ⲻ������ת����remote�˽��ܺ�ʶ�������ٽ���HTTP(S)��SOCKS5��SNI���Զ�����  
+ ������һ���������DNS������ʵ�֣�����ͨ��DNS over HTTPS��ѯ���������UDP���ĵķ�ʽ���ؽ����  

## :star:ȱ��  
+ ��֧��TCP����֧��UDP
+ Socks5�����֧��IPv4����֧��IPv6

## :star:�������  


<details>
<summary>local������`config/config_local.py`</summary>



```py

hosts = {                                   # ����ipӳ�䣬���ؽ���ʱ���õ�
    "www.baidu.com": "14.215.177.38",
}
usePac = True
# pacAddr ������dict��ʽ����ַ��Ҳ�����Ǳ����ļ�
# 'https://raw.githubusercontent.com/zhiyi7/gfw-pac/master/gfw.pac'
# pacAddr = {
#     'host': 'raw.githubusercontent.com',
#     'path': '/zhiyi7/gfw-pac/master/gfw.pac',
#     'scheme': 'HTTPS',
#     'verify': True
# }
pacAddr = './gfw_pac'


server_local = {
    "addr": '0.0.0.0',                      # ���ؼ���ip
    "port": 2376,                           # ���ؼ����˿�
    "ssl": False,                           # ���ش������������ssl
    "sslConfig": {                          # ssl Ϊtrueʱ��Ч, ����server��֤��
        'certfile': r'./cert/youdomain.pem',
        'keyfile': r'./cert/youdomain.key',
    },
    "remote": {
        "addr": 'youdomain',                # Զ��ip/domain
        "port": 443,                        # Զ�̶˿�
        "ssl": True,                        # ��remote�����������Ƿ�����ssl
        "verify": False,
        "server_hostname": 'youdomain',     # remote.ssl Ϊtrueʱ��Ч�����͵�sni����
    },
}

##### ����αװ��HTTP��ͷ��, ����/�˿����ò���ȷ�����޷���������  #####
path = '/path'
http_version = '1.1'
domain = 'youdomain'  # �Զ��壬����server_local['remote']['server_hostname']
port = '443'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'

##### ���ڼ�Ȩ #####
username = 'username'                   # �û���
pwd = 'pwd'                             # ����
salt = '4567'                           # ��ֵ,���ڼ�������
cookies = {                             # ��ʼcookies, ������� αװ��HTTP��ͷ��
    "my_type":  UNKNOWN_TYPE,           # �ò�����ָʾ��������δ���������, ��֪���Ļ�ֱ��UNKNOWN_TYPE
    "my_domain":  '',                   # ��� my_type ʹ��, �������˿���Чʱ����������ֱ���Դ�����������
    "my_port":  '0',                    # ��� my_type ʹ��, �������˿���Чʱ����������ֱ���Դ�����������
}

# �Ƿ���Զ�̽���
is_parsed_remote = False
```
</details>

<details>
<summary>remote������`config/config_remote.py`</summary>



```py
hosts = {                                   # �Զ�������ipӳ��, ����Ϊ{}
    "www.baidu.com": "14.215.177.38",
}

server_remote = {
    "addr": '0.0.0.0',                      # ����ip 127.0.0.1 ����������; 0.0.0.0��ʾ�������������ip
    "port": 443,                            # �����˿�
    "ssl": False,                           # ����������Ƿ���ssl(����nginx����ر�)
    "sslConfig": {                          # ssl Ϊtrueʱ��Ч, ����server��֤��
        'certfile': r'./cert/youdomain.pem',
        'keyfile': r'./cert/youdomain.key',
    },
}

users = {                                   # ��Ч���û���
    'username': 'pwd',
    'admin': 'admin',
}
salt = '4567'                               # �û�������У�����ֵ, ��Ҫ��ͻ���һ��
```
</details>








## :star:�������  
+ ���б��ض�  
```
python server_local.py
```

+ ����Զ�̶�
```
python server_remote.py
```