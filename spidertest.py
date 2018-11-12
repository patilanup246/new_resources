# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

driver = webdriver.Chrome()
driver.get("http://www.baidu.com")
time.sleep(3)
print(driver.current_window_handle)  #打印当前页面的句柄
print(driver.title)  #打印页面标题

#通过执行js语句为元素添加target="_blank"属性
js = 'document.getElementsByName("tj_trnews")[0].target="_blank"'
driver.execute_script(js)


news = driver.find_element_by_name('tj_trnews')
news.click()
time.sleep(3)

handles = driver.window_handles  #获取所有打开窗口的句柄
print(handles)
for i in ["https://www.hao123.com","https://www.youtube.com"]:
    driver.get(i)
    print(driver.page_source)
    # driver.switch_to.window(handles[0])
    # print(driver.current_window_handle)
    # print(driver.title)
    # news = driver.find_element_by_name('tj_trnews')
    # news.click()