#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, sys, re, ctypes

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        f'CHCP 65001 && {cmd}',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    print(f'[{cmd!r} exited with {proc.returncode}]')
    if stdout:
        #print(f'[stdout]\n{stdout.decode("utf-8")}')
        return stdout.decode("utf-8")
    if stderr:
        print(f'[stdout]\n{stdout.decode("utf-8")}')

async def getNetworkInterface():
    answer = await run('netsh interface ip show subinterfaces')
    interfaces = []
    max = (0, 0)
    for line in answer.splitlines():
        search = re.search(r'\s*\d+\s+\d+\s+(\d+)\s+\d+\s+(.*)', line)
        if search:
            bytesIn, interface = int(search.group(1)), search.group(2).strip()
            # 记录找出最大的那一个interface
            maxIndex, maxBytesIn = max
            if bytesIn > maxBytesIn:
                max = (len(interfaces),  bytesIn)
            # 将所有interface 放入list
            interfaces.append(interface)
    return interfaces[ max[0] ]

    
def is_admin():
    try:
        print(sys.version_info[0])
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
def authAdmin():
    if sys.version_info[0] == 3:
        print("无管理员权限")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        
async def setDNSServer(dns_server_ip: str or 'dhcp', interface = None):
    if interface is None:
        interface = await getNetworkInterface()
    if dns_server_ip == 'dhcp':
        cmd = f'netsh interface ip set dnsservers name="{interface}" source=dhcp'
    else:
        cmd = f'netsh interface ip set dnsservers name="{interface}" source=static addr={dns_server_ip} register=primary'
    if is_admin():
        result = await run(cmd)
    else:
        print('请以管理员权限运行!!!')

async def getDNSServerInfo(interface=None):
    if interface is None:
        interface = await getNetworkInterface()
    cmd = f'netsh interface ip show dnsservers name="{interface}"'
    result = await run(cmd)
    print(result)
    return result
    
if __name__ == '__main__':
    #asyncio.run(setDNSServer('127.0.0.1'))
    asyncio.run(setDNSServer('dhcp'))
    asyncio.run(getDNSServerInfo())
