#!/usr/bin/env python
# -*- coding: utf-8 -*-
#***********************************************************************************
"""
Auto click links to get Rakuten Points™ .

## Installation
1. Requires python2.6+.
2. If you don't have pip. Intsall pip.
3. Setup selenium:
    in command type in :pip install selenium
4. Selenium requires a driver to interface with the chosen browser.
    Firefox, requires geckodriver, which needs to be installed before the below examples can be run.
    https://github.com/mozilla/geckodriver/releases
"""

#twitter : @ithurricanept
#email : ithurricane@gmail.com
#***********************************************************************************

import requests
import io
import time
import os

# Selenium
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

rt_id = 'change to your rakuten id'
rt_pw = 'change to your rakuten password'
click_url = 'https://www.rakuten-card.co.jp/e-navi/members/point/click-point/index.xhtml?l-id=enavi_mtop_pointservice_click'

# Firefox / Gecko Driver Related
FIREFOX_BIN_PATH = r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
GECKODRIVER_BIN = r"C:\geckodriver.exe"

driver = webdriver.Firefox(firefox_binary=FirefoxBinary(FIREFOX_BIN_PATH), executable_path=GECKODRIVER_BIN)
driver.implicitly_wait(10)

def check_exists_by_xpath(elm, xpath):
    try:
        elm.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

driver.get(click_url)
loginid = driver.find_element_by_id('u')
password = driver.find_element_by_id('p')
loginid.send_keys(rt_id)
password.send_keys(rt_pw)
driver.find_element_by_id('loginButton').click()

driver.implicitly_wait(10)

# wait for load
footer = driver.find_element_by_id("rce-footer-links")
element = WebDriverWait(driver,10).until(
    lambda driver : footer.is_displayed()
)

if not check_exists_by_xpath(driver, "//img[contains(@alt,'Check')]") :
    print "already have been all clicked!"
    quit()

Listlinker1 = []
Listlinker2 = []

Listlinker1 = driver.find_elements_by_xpath('//div[@class="bnrBoxInner"]/a')
Listlinker2 = driver.find_elements_by_xpath('//p[@class="middleImageBottomText"]/a')

print len(Listlinker1)
size1 = len(Listlinker1)
print len(Listlinker2)
size2 = len(Listlinker2)
#
# for a in driver.find_elements_by_xpath('//div[@class="bnrBoxInner"]/a]'):
#     print(a.get_attribute('onclick'))
#
#
for i in range(size1):
    if i % 2 == 0:
        try:
            print(Listlinker1[i-1].get_attribute('onclick'))
            Listlinker1[i-1].click()
        except StaleElementReferenceException:
            Listlinker1 = driver.find_elements_by_xpath('//div[@class="bnrBoxInner"]/a')
            print(Listlinker1[i-1].get_attribute('onclick'))
            Listlinker1[i-1].click()

        old_handle = driver.current_window_handle
        for handle in driver.window_handles:
            if old_handle != handle:
                new_handle = handle
                break
        driver.switch_to_window(new_handle)
        time.sleep(5)
        driver.close()
        driver.switch_to_window(old_handle)

for j in range(size2):
    try:
        print(Listlinker2[j-1].get_attribute('onclick'))
        Listlinker2[j-1].click()
    except StaleElementReferenceException:
        Listlinker2 = driver.find_elements_by_xpath('//p[@class="middleImageBottomText"]/a')
        print(Listlinker2[j-1].get_attribute('onclick'))
        Listlinker2[j-1].click()

    old_handle = driver.current_window_handle
    for handle in driver.window_handles:
        if old_handle != handle:
            new_handle = handle
            break
    driver.switch_to_window(new_handle)
    time.sleep(5)
    driver.close()
    driver.switch_to_window(old_handle)

