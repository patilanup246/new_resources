import requests
import random

username = 'lum-customer-hl_e91f8dc5-zone-static'
password = 'bbnre3p4pkd7'
port = 22225


def getIp():
    session_id = random.random()
    super_proxy_url = ('http://%s-country-us-session-%s:%s@servercountry-US.zproxy.lum-superproxy.io:%d' %
                       (username, session_id, password, port))
    proxy_handler = {
        'http': super_proxy_url,
        'https': super_proxy_url,
    }
    return proxy_handler


if __name__ == '__main__':
    print(getIp())
