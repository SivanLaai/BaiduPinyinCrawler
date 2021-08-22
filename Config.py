import configparser
import sys
from selenium import webdriver


global config

config = configparser.ConfigParser()
config.sections()
config.read("setting.ini")


# global driver
# opt = webdriver.ChromeOptions()
# opt.add_argument("--headless")
# # opt.add_argument("--disable-gpu")
# driver = webdriver.Chrome(executable_path=config["DEFAULT"]["CHROME_DRIVER"], options=opt)




