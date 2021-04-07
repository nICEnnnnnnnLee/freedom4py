from .config_basic import *
import sys
# print(sys.argv)
if len(sys.argv) < 2:
    if sys.argv[0].endswith('server_remote.py'):
        run = REMOTE
    elif sys.argv[0].endswith('server_local.py'):
        run = LOCAL
    elif sys.argv[0].endswith('dns.py'):
        run = DNS
    else:
        #print(f'please input {LOCAL}/{REMOTE}')
        #exit(-1)
        pass
else:
    run = sys.argv[1]

if 'run' in locals():
    if run == LOCAL:
        from .config_local import *
    elif run == REMOTE:
        from .config_remote import *
    elif run == DNS:
        from .config_dns import *
    else:
        #print(f'inupt invalid args, please input {LOCAL}/{REMOTE}')
        #exit(-1)
        pass
