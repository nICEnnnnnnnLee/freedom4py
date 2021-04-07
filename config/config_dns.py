
# domain -> (ip, time to die)
# 0: stay alive forever
hosts = {                                   
    #"www.baidu.com": ("127.0.0.1", 0),
}

# udp address to bind.
# 127.0.0.1 means only receive data from local PC
# 0.0.0.0 means receive any from the network
addr = ('0.0.0.0', 53)

'''
   # dnsforge.de
   # dns.edgy.network
   #  jp.tiar.app
   #  jp.tiarap.org
   ##  doh.post-factum.tk
   ##  doh.crypto.sx
   ##  freedom.mydns.network
   ##?  ibuki.cgnat.net
   ? 网页可以，但是py返回404 resolver-eu.lelux.fi
   ? 网页可以，但是py不行 ordns.he.net
    https://rdns.faelix.net/?
    https://doh.applied-privacy.net/query?

    dns64.cloudflare-dns.com
    doh.pub
    dns.google
    dns.alidns.com
    dns.rubyfish.cn
    cloudflare-dns.com
DoH server defines in https://tools.ietf.org/html/rfc1035
https://{domain}/dns-query?dns={ base64(DNS wire data) }
https://cloudflare-dns.com/dns-query?dns=AAIBAAABAAAAAAAAA3d3dwViYWlkdQNjb20AAAEAAQ
'''
DoH = 'odvr.nic.cz'
# you should better configure this before you set this dns server as the local server  
DoH_ip = DoH
# DoH_ip = None
# check the SSL cert or not
verify = False