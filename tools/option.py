from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile


def getOption(headless):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            # "javascript":2,  # facebook无法禁止加载javascript
            'automatic_downloads': 1,
        }
    }
    # options.add_experimental_option('prefs', prefs)
    # 默认中文
    options.add_argument("–lang=zh-CN")
    options.add_argument("–start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    # options.add_argument("--no-gpu")
    # options.add_argument("--disable-software-rasterizer")
    options.add_argument(
        "--user-agent={}".format(UserAgent().random))
    # 关闭不安全的认证
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--ignore-urlfetcher-cert-requests")
    options.add_argument("--auto-ssl-client-auth")
    options.add_argument("--allow-http-background-page")
    # 进入无痕模式
    options.add_argument("--incognito")
    options.add_argument("--disable-web-security")
    # options.add_argument('window-size=1920x1080')
    # options.add_argument('--remote-debugging-targets="0.0.0.0:10000"')
    options.add_argument("--non-secure")
    # options.add_argument("--user-data-dir=./ChromeUserData/{}".format(workId))
    options.add_argument("--window-position=0,0")
    # options.add_argument("--disk-cache-dir=./ChromeUserCache")#windows not error,temp # this
    # if len(g_proxy_address) > 0:
    #     options.add_argument("--proxy-server={}".format(g_proxy_address))
    # options.add_argument("--proxy-server={}".format())
    options.add_argument("--liclc_work")

    # if len(g_proxy_address) <= 0:
    #     options.add_extension(get_chrome_proxy_extension(proxy=proxy))
    # 禁止加载图片
    return options
