import pdb
import pandas as pd
import numpy as np
import time
# import schedule
import re
import random
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from datetime import datetime


def open_driver(url, headless=True):
    op = webdriver.FirefoxOptions()
    if headless:
        op.add_argument('headless')
        op.add_argument("window-size=1400,600")
        op.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36")
    driver = webdriver.Firefox(options=op)
    driver.get(url)
    return driver


def login_email(driver, my_email, my_password):
    # login
    driver.implicitly_wait(10)
    elem = driver.find_element_by_name("j_username")
    elem.clear()
    elem.send_keys(my_email)
    driver.implicitly_wait(10)  # seconds
    elem = driver.find_element_by_name("j_password")
    elem.send_keys(my_password)
    driver.implicitly_wait(10)  # seconds
    elem.send_keys(Keys.RETURN)
    driver.implicitly_wait(10)  # seconds


def write_email(driver, recipient_mail, subject, text_body):
    button = driver.find_element(By.CSS_SELECTOR, "[aria-label^='Verfassen']")
    ActionChains(driver).click(button).perform()

    # to_field = driver.find_element(By.CLASS_NAME, "select")
    # driver.find_element_by_xpath("//div[@class='select']").get_attribute("message-to-field")
    driver.find_element(By.ID, "message-to-field").send_keys(recipient_mail)

    driver.find_element(By.CSS_SELECTOR, "[aria-label^='Betreff']").send_keys(subject)
    textbox = driver.find_element(By.ID, 'editor-container')
    driver.find_element(By.CSS_SELECTOR, "[role^='textbox']").send_keys(text_body)
    send_button = driver.find_element(By.XPATH, "//span[.='Senden']")
    ActionChains(driver).click(send_button).perform()


url = "https://tum-conf.zoom.us/signin/"
my_email = 'ge43sif@mytum.de'
my_password = '\dfrac{%L/G}'


from selenium import webdriver
from selenium.webdriver.common.keys import Keys



driver = open_driver(url, headless=False)
wait = WebDriverWait(driver, 5)
login_email(driver, my_email, my_password)

#reject cookies
button = driver.find_element(By.ID, 'onetrust-reject-all-handler')
button.click()
#naviagte to meetings and select first
driver.get("https://tum-conf.zoom.us/meeting#/upcoming")
button = driver.find_element_by_class_name('topic') #something is not working here!
button.click()
# Navigate to emails setting and open template
button = driver.find_element_by_id("showemailSettingsTab")
button.click()
button = driver.find_element_by_id("meeting_email_confirmation_edit_button")
button.click()
# Edit title and text body
title_text = "Invitation to Kipoi Seminar Series with Benjamin Schubert from HMGU"
title = driver.find_element_by_id("confirm_email_form_subject")
title.clear()
title.send_keys(title_text)

body_text = "I am happy to announce Benjamin Schubert from Helmholtz Zentrum Munich at our next Kipoi Seminar on the topic:\n\n"\
"Advanced Machine Learning Approaches to Dissect the T cell Immune Response \n\n"\
"Abstract: \nT lymphocytes play a crucial role in the progression of infectious diseases. They recognize pathogenic peptides, so-called epitopes, through a unique antigen T cell receptor sequence (TCR). Although the specificity and affinity of the TCR to its epitope determine the functionality, phenotypic and cellular differentiation in the context of the cell’s TCR, and therefore also the fate of a T cell as well as the interaction of a TCR and its cognate epitope are still poorly understood. \nIn this talk, I will present machine learning models that can leverage new advances in single-cell immune profiling to help us in unraveling the T cell-based immune response. A good understanding and accurate prediction of what the T cell can recognize and how it will change its cellular program upon recognition would have a tremendous impact on many biomedical fields, including basic immunology, virology, cancer biology, autoimmunity, and inflammatory diseases research, as well as immunotherapy development."\
"\n\nPlease also follow our social media channels:\n"\
"- Website: http://kipoi.org/seminar/\n"\
"- Twitter: @KipoiZoo\n"\
"- YouTube: https://www.youtube.com/channel/UCL_iKCHUxepOi7_Wk010--g\n\n"\
"Best,\nLaura"

body = driver.find_element_by_id("confirm_email_form_body_branding1")
body.clear()
body.send_keys(body_text)
#button = driver.find_element_by_class_name("btn btn-primary submit")
#button.click()
driver.close()

