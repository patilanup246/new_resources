import urllib.request
import random

username = 'lum-customer-hl_e91f8dc5-zone-zone1-route_err-pass_dyn'
password = 'y8v32rz1hjh1'
port = 22225


def getIp():

    session_id = random.random()
    super_proxy_url = ('http://%s-country-us-dns-local-session-%s:%s@servercountry-US.zproxy.lum-superproxy.io:%d' %
                       (username, session_id, password, port))
    proxy_handler = {
        'http': super_proxy_url,
        'https': super_proxy_url,
    }
    return proxy_handler


if __name__ == '__main__':
    print(getIp())

