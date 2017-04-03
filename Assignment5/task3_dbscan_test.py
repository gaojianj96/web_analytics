from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from unidecode import unidecode
import copy
import datetime
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
import sys
from sklearn.cluster import DBSCAN
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.parser import parse as dateparse
from sklearn import preprocessing
from flight_outliers import task_3_dbscan

def scrape_general(start_date,from_place, to_place):
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/flights/explore/')

    ele_f = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/div/div')
    ele_f.click()
    actions = ActionChains(driver)
    actions.send_keys(from_place)
    actions.send_keys(Keys.ENTER)
    time.sleep(0.001)
    actions.perform()

    ele_t = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/div/div')
    ele_t.click()
    actions = ActionChains(driver)
    actions.send_keys(to_place)
    actions.send_keys(Keys.ENTER)
    time.sleep(0.001)
    actions.perform()
    time.sleep(0.5)

    url = driver.current_url
    url = url[:url.find("d=") + 2] + start_date.strftime('%Y-%m-%d')
    driver.get(url)
    time.sleep(1)

    return driver

def scrape_data_90(driver,ele_result,data):
    bars = ele_result.find_elements_by_class_name('LJTSM3-w-x')
    for bar in bars:
        ActionChains(driver).move_to_element(bar).perform()
        time.sleep(0.0001)
        try:
            ele_find=ele_result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')
            if len(ele_find)>1 and len(data)<90:
                data.append([dateparse(ele_find[1].text.split('-')[0].strip()),
                                  int(ele_find[0].text.replace(',','')[1:])])
            elif len(data)>=90:
                break
        except:
            print "Unexpected error in scrap data:", sys.exc_info()
    return data

def scrape_all(start_date, from_place, to_place):
    driver = scrape_general(start_date,from_place, to_place)
    sleep_time=0.5
    ele_eles=driver.find_elements_by_class_name('LJTSM3-v-m')
    datas=[]
    for ele in ele_eles:
        city=unidecode(ele.find_element_by_class_name('LJTSM3-v-c').text).split(',')[0]
        data=[]
        data=scrape_data_90(driver,ele,data)
        datas.append((city,data))
    #next
    ActionChains(driver).click(driver.find_element_by_class_name('LJTSM3-w-D')).perform()
    time.sleep(sleep_time)
    ActionChains(driver).click(driver.find_element_by_class_name('LJTSM3-w-D')).perform()
    time.sleep(sleep_time)
    ret_data=[]
    ele_eles=driver.find_elements_by_class_name('LJTSM3-v-m')
    for data_ele in datas:
        ele_result=[ele for ele in ele_eles if data_ele[0].lower() in unidecode(ele.find_element_by_class_name('LJTSM3-v-c').text).lower()][0]
        data=scrape_data_90(driver,ele_result,data_ele[1])
        df_data=pd.DataFrame(data,columns=['Date_of_Flight','Price'])
        ret_data.append(df_data)
    driver.quit()
    return ret_data


df_90s=scrape_all(dateparse('2017-04-02'),'NYC','Scandinavia')
count=1
for df in df_90s:
    print '******************** Figure ',count,' ***************************'
    nyp = task_3_dbscan(df)
    print nyp
    count+=1
while True:
    plt.pause(0.001)