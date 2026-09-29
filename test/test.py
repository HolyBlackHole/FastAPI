import json
import hashlib
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import random


# 添加可视化运行配置
chrome_options = Options()
# 禁用无头模式，确保浏览器窗口完整弹出可见
# chrome_options.add_argument("--headless=new") 不要开启这行，否则后台静默运行看不到界面
# 禁止浏览器自动关闭
chrome_options.add_experimental_option("detach", True)
# 规避常见的运行报错
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# 在已有的chrome_options配置里加入这几行
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)


driver = webdriver.Chrome(options=chrome_options)
# 额外注入脚本覆盖navigator.webdriver属性，彻底抹除自动化痕迹
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})
driver.maximize_window()
driver.get('https://www.baidu.com/')

# 给页面留足加载时间，避免页面还没加载完成就执行刷新
driver.implicitly_wait(10)
driver.refresh()
print("页面刷新操作已执行完成")

# 创建动作链对象
actions = ActionChains(driver)
search_text = '百度翻译'
search_box = driver.find_element(By.XPATH, "//textarea[@id='chat-textarea']")
for char in search_text:
    search_box.send_keys(char)
    sleep(random.uniform(0.1, 0.3))
sleep(2)
actions.key_down(Keys.CONTROL).send_keys('a').send_keys(Keys.BACK_SPACE).perform()
sleep(2)
for char in search_text:
    search_box.send_keys(char)
    sleep(random.uniform(0.1, 0.3))
sleep(2)
search_box.send_keys(Keys.ENTER)
sleep(2)



