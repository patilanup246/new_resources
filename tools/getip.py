import urllib.request
import random

username = 'lum-customer-hl_e91f8dc5-zone-zone1-route_err-pass_dyn'
password = 'y8v32rz1hjh1'
port = 22225

import sys


def getIp():
    if sys.version_info[0] == 2:
        import six
        from six.moves.urllib import request
        import random
        username = 'lum-customer-hl_e91f8dc5-zone-zone1-route_err-pass_dyn'
        password = 'y8v32rz1hjh1'
        port = 22225
        session_id = random.random()
        super_proxy_url = ('http://%s-country-us-session-%s:%s@servercountry-US.zproxy.lum-superproxy.io:%d' %
                           (username, session_id, password, port))
        return {
            'http': super_proxy_url,
            'https': super_proxy_url,
        }
        # proxy_handler = request.ProxyHandler({
        #     'http': super_proxy_url,
        #     'https': super_proxy_url,
        # })
        # opener = request.build_opener(proxy_handler)
        # print('Performing request')
        # print(opener.open('http://lumtest.com/myip.json').read())
    if sys.version_info[0] == 3:
        import urllib.request
        import random
        username = 'lum-customer-hl_e91f8dc5-zone-static-route_err-pass_dyn'
        password = 'bbnre3p4pkd7'
        port = 22225
        session_id = random.random()
        super_proxy_url = ('http://%s-country-us-session-%s:%s@servercountry-US.zproxy.lum-superproxy.io:%d' %
                           (username, session_id, password, port))
        # proxy_handler = urllib.request.ProxyHandler({
        #     'http': super_proxy_url,
        #     'https': super_proxy_url,
        # })
        return {
            'http': super_proxy_url,
            'https': super_proxy_url,
        }
        # opener = urllib.request.build_opener(proxy_handler)
        # print('Performing request')
        # print(opener.open('http://lumtest.com/myip.json').read())

if __name__ == '__main__':
    print(getIp())
