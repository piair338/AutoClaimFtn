#!/usr/bin/python3
from time import sleep
from random import uniform
from re import search
import discord
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium import webdriver
import pyotp
import discord

Headless = True
Path = "/home/pi/DalyRewardsFtn/custom/data.txt"
g =  open(Path, "r" , encoding="utf-8")
data= [ x.replace("\n","") for x in g.readlines() ]
g.close()

c = [ x.split(',') for x in data[:2]]
print(c)


def FirefoxPC(Headless = Headless):
    PC_USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134')

    options = Options()
    options.set_preference("browser.link.open_newwindow", 3)
    
    if Headless :
        options.add_argument("-headless")

    options.set_preference("general.useragent.override", PC_USER_AGENT)
    return(webdriver.Firefox(options=options))

def send_keys_wait(element,keys):
    for i in keys :
        element.send_keys(i)
        sleep(uniform(0, 0.5))

def login_with_xbox(driver,id,p):
    mail = driver.find_element(By.ID,'i0116')
    send_keys_wait(mail, id)
    mail.send_keys(Keys.ENTER)

    try :
        driver.find_element(By.ID,'idChkBx_PWD_KMSI0Pwd').click()
    except :
        try :
            driver.find_element(By.CSS_SELECTOR,'''[data-bind="text: str['CT_PWD_STR_KeepMeSignedInCB_Text']"]''').click()
        except :
            pass
    pwd = driver.find_element(By.ID,'i0118')
    send_keys_wait(pwd, p)
    pwd.send_keys(Keys.ENTER)
    try :
        driver.find_element(By.ID,'iNext').click()

    except :
        assert('il y a eu une erreur dans le login_with_xbox, il faut regarder pourquoi')    #dans le cas ou ms change ses parametre de confidentialité

    try :
        driver.find_element(By.ID,'KmsiCheckboxField').click()
        driver.find_element(By.ID,'idSIButton9').click()
    except :
        print('login_with_xbox error') #dans le cas ou il faut verifier la connection


def routine(bs, id, p):
    driver = FirefoxPC()
    driver.get('https://www.epicgames.com/fortnite/fr/help-center')
    driver.implicitly_wait(15)

    element = driver.find_element(By.XPATH,"/html/body/div/div/header/nav/div/div[2]/div/div[3]/ul/li/a/span")
    driver.execute_script("arguments[0].click();", element)

    driver.find_element(By.ID,"login-with-xbl").click()
    window_before = driver.window_handles[0]
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)

    login_with_xbox(driver, id, p)
    sleep(10)

    driver.switch_to.window(window_before)

    totp = pyotp.TOTP(bs)
    A2F = totp.now()

    actions = ActionChains(driver)
    A2F = totp.now()
    actions.send_keys(A2F)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    sleep(10)

    driver.get('view-source:https://www.epicgames.com/id/api/redirect?clientId=ec684b8c687f479fadea3cb2ad83f5c6&responseType=code')
    sleep(10)
    code = search("code=([^\"]+)", driver.page_source)[1]
    
    driver.close()
    return(code)

def main(c) : 
    for i in c :
        Token = str(i[0])
        bs = str(i[1])
        id = str(i[2])
        p = str(i[3])
        channel = int(i[4])
 

        client = discord.Client()
        @client.event
        async def on_ready():
            chan = client.get_channel(channel)
            await chan.send(f".daily {routine(bs, id, p)}")
            await client.close()

        client.run(Token, bot=False)