from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from bs4 import BeautifulSoup
import re

# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--window-size=1280x1696')
# chrome_options.add_argument('--user-data-dir=/tmp/user-data')
# chrome_options.add_argument('--hide-scrollbars')
# chrome_options.add_argument('--enable-logging')
# chrome_options.add_argument('--log-level=0')
# chrome_options.add_argument('--v=99')
# chrome_options.add_argument('--single-process')
# chrome_options.add_argument('--data-path=/tmp/data-path')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('--homedir=/tmp')
# chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
# chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
# chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"

# driver = webdriver.Chrome(chrome_options=chrome_options)
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1280x1696')
chrome_options.add_argument('--user-data-dir=/tmp/user-data')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--log-level=0')
chrome_options.add_argument('--v=99')
chrome_options.add_argument('--single-process')
chrome_options.add_argument('--data-path=/tmp/data-path')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--homedir=/tmp')
chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36')
chrome_options.binary_location = os.getcwd() + "/bin/headless-chromium"

def lambda_handler(event, context):
    # TODO implement
    driver = webdriver.Chrome(chrome_options=chrome_options)
    page_data = ""
    if event["res"]["result"]["args"][0]:
        driver.get(event["res"]["result"]["args"][0])
        page_data = driver.page_source
        bs_object = BeautifulSoup(page_data, 'html.parser')
        result = bs_object.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['dining-halls-container'])
        restaurants = []
        for i in result:
            dining_div = i.find_all("div", {"class": "dining-halls-block-left desktop-only"})
            print(dining_div)
            for i in dining_div:
                dining_title = i.find("a", {"href": re.compile("/dining-near-me")})
                print(dining_title)
                restaurants.append(dining_title.contents[0])
                
    restaurants_list = ", ".join(str(x) for x in restaurants)
    event["res"]["message"] = "{} are currently open".format(restaurants_list)


    driver.close()
    return event
