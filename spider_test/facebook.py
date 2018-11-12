# coding:utf-8
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from lxml import etree
import traceback

from logs.loggerDefine import loggerDefine

logging = loggerDefine("./../logs/facebook.log")


def getOption(headless):
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless")

    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-gpu")
    # options.add_argument("--disable-software-rasterizer")
    options.add_argument("--ignore-certificate-errors")
    # options.add_argument("--ignore-urlfetcher-cert-requests")
    options.add_argument("--auto-ssl-client-auth")
    options.add_argument("--allow-http-background-page")
    # 进入无痕模式
    options.add_argument("--incognito")
    options.add_argument("--disable-web-security")
    options.add_argument('window-size=1920x1080')
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
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            'automatic_downloads': 1,
        }
    }
    options.add_experimental_option('prefs', prefs)
    return options


def login(driver):
    driver.get("https://www.facebook.com/login")
    # 输入用户名
    driver.find_element_by_id("email").send_keys("tanya.beleutova.beleutova@mail.ru")
    # 输入密码
    driver.find_element_by_id("pass").send_keys("yoan6SNoer")
    # 点击登录
    driver.find_element_by_id("loginbutton").click()

def search(driver, keyword):
    # 输入关键字
    driver.find_element_by_xpath('//input[@placeholder="搜索"]').send_keys(keyWord)
    # 点击搜索
    driver.find_element_by_xpath('//button[@data-testid="facebar_search_button"]').click()
    time.sleep(5)
    # 点击小组
    driver.find_element_by_link_text("小组").click()

    # targetElem = driver.find_element_by_xpath('//div[@class="phm _64f"]')
    # driver.execute_script("arguments[0].scrollIntoView();", targetElem)    # 拖动到可见的元素去

    cc = 1
    js = 'window.scrollTo(0, document.body.scrollHeight)'
    flag = True
    while flag and cc < 12:
        driver.execute_script(js)
        try:
            driver.find_element_by_xpath('//div[contains(text(),"已经到底啦~")]')
            flag = False
            print("已经到底啦")
        except NoSuchElementException:
            flag = True
        cc += 1
        time.sleep(5)
    responseBody = driver.page_source
    selector = etree.HTML(responseBody)

    titleNode = selector.xpath('//div[@class="_gll"]')
    numberNode = selector.xpath('//div[@class="_glm"]')
    textNode = selector.xpath('//div[@class="_glo"]')
    countryNode = selector.xpath('//div[@class="_glp"]')
    for title,number,text,country in zip(titleNode,numberNode,textNode,countryNode):
        try:
            # 标题
            titleName = title.xpath("./div//a/text()")[0]
            # 链接
            link = "https://www.facebook.com" + title.xpath("./div//a/@href")[0]
            # 21 万位成员 · 一天发布超过 10 篇帖子
            textDetail = number.xpath('./div/text()')[0] + number.xpath('./div/span/text()')[0]
            print(textDetail)
        except Exception as e:
            logging.error(traceback.format_exc())


if __name__ == '__main__':
    options = getOption(True)
    driver = webdriver.Chrome(chrome_options=options)
    login(driver)

    keyWord = "xiaomi"
    search(driver,keyWord)

    driver.quit()
