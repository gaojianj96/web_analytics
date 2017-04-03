from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from unidecode import unidecode
import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean
import sys
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from dateutil import parser
from sklearn import preprocessing


def scrape_general(start_date, from_place, to_place):
    driver = webdriver.Chrome()
    driver.get('https://www.google.com/flights/explore/')

    ele_f = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[2]/div/div')
    ele_f.click()
    actions = ActionChains(driver)
    actions.send_keys(from_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(1)

    ele_t = driver.find_element_by_xpath('//*[@id="root"]/div[3]/div[3]/div/div[4]/div/div')
    ele_t.click()
    actions = ActionChains(driver)
    actions.send_keys(to_place)
    actions.send_keys(Keys.ENTER)
    actions.perform()
    time.sleep(1)

    url = driver.current_url
    url = url[:url.find("d=") + 2] + start_date.strftime('%Y-%m-%d')
    driver.get(url)
    time.sleep(1)

    return driver


# TODO ******************************* Task 1 ************************************

def scrape_data(start_date, from_place, to_place, city_name):
    driver = scrape_general(start_date, from_place, to_place)

    ele_eles = driver.find_elements_by_class_name('LJTSM3-v-m')
    ele_result = [ele for ele in ele_eles if
                  city_name.lower() in unidecode(ele.find_element_by_class_name('LJTSM3-v-c').text).lower()]
    if ele_result == []:
        print 'Something wrong within scrapping data. Please avoid move of mouse within chrome!\nPlease check start_date which should not later than today. Please check whther from and destination exist.\nIf nothing wrong, please try again.'
        return None
    ele_result = ele_result[0]

    bars = ele_result.find_elements_by_class_name('LJTSM3-w-x')

    data = []

    for bar in bars:
        ActionChains(driver).move_to_element(bar).perform()
        time.sleep(0.001)
        try:
            ele_find = ele_result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')
            if len(ele_find) > 1:
                data.append([parser.parse(ele_find[1].text.split('-')[0].strip()),
                             int(ele_find[0].text.replace(',', '')[1:])])
        except:
            pass

    df_data = pd.DataFrame(data=data, columns=['Date_of_Flight', 'Price'])
    driver.quit()

    return df_data


# TODO **************** Task 2 ***************
def scrape_data_90(start_date, from_place, to_place, city_name):
    driver = scrape_general(start_date, from_place, to_place)
    sleep_time = 0.5

    data = []

    while True:
        ele_eles = driver.find_elements_by_class_name('LJTSM3-v-m')
        ele_result = [ele for ele in ele_eles if
                      city_name.lower() in unidecode(ele.find_element_by_class_name('LJTSM3-v-c').text).lower()]
        if ele_result == []:
            print 'Something wrong within scrapping data. Please avoid move of mouse within chrome!\nPlease check start_date which should not later than today. Please check whther from and destination exist.\nIf nothing wrong, please try again.'
            return None
        ele_result = ele_result[0]

        bars = ele_result.find_elements_by_class_name('LJTSM3-w-x')
        for bar in bars:
            ActionChains(driver).move_to_element(bar).perform()
            time.sleep(0.0001)
            try:
                ele_find = ele_result.find_element_by_class_name('LJTSM3-w-k').find_elements_by_tag_name('div')
                if len(ele_find) > 1 and len(data) < 90:
                    data.append([parser.parse(ele_find[1].text.split('-')[0].strip()),
                                 int(ele_find[0].text.replace(',', '')[1:])])
                elif len(data) >= 90:
                    break
            except:
                pass

        # next
        if len(data) < 90:
            ActionChains(driver).click(ele_result.find_element_by_class_name('LJTSM3-w-D')).perform()
            time.sleep(sleep_time)
            ele_eles = driver.find_elements_by_class_name('LJTSM3-v-m')
            ele_result = [ele for ele in ele_eles if
                          city_name.lower() in unidecode(ele.find_element_by_class_name('LJTSM3-v-c').text).lower()][0]
            ActionChains(driver).click(ele_result.find_element_by_class_name('LJTSM3-w-D')).perform()
            time.sleep(sleep_time)
        else:
            break

    df_data = pd.DataFrame(data=data, columns=['Date_of_Flight', 'Price'])
    driver.quit()

    return df_data


# TODO ************* Task 3-1 ********************

# Date_of_Flight of flight_data is a datetime object
def task_3_dbscan(flight_data):
    df_90_cv = pd.DataFrame(
        [[row.Date_of_Flight, (row.Date_of_Flight - flight_data.Date_of_Flight[0]).days, row.Price] for
         index, row in flight_data.iterrows()],
        columns=['Date_of_Flight', 'Date_Label', 'Price'])
    X = preprocessing.MinMaxScaler((0, 10)).fit_transform(df_90_cv[['Date_Label', 'Price']])
    mad_date = (abs(X[:, 0] - X[:, 0].mean())).mean()
    mad_price = (abs(X[:, 1] - X[:, 1].mean())).mean()
    # print mad_date, mad_price
    X[:, 0] = X[:, 0] / mad_date * mad_price * 2
    mad_date = (abs(X[:, 0] - X[:, 0].mean())).mean()
    # mad_price = (abs(X[:, 1] - X[:, 1].mean())).mean()
    # print '2mad:', mad_date, mad_price

    eps = float('%4.2f' % euclidean([0, 0], [mad_date, mad_price])) / 6
    print 'Task3_DBSCAN eps:', eps
    db = DBSCAN(eps=eps, min_samples=4).fit(X)

    df_90_cv['dbscan_labels'] = db.labels_

    # plot
    labels = db.labels_
    # Number of cluster, ignoring noises
    clusters_len = len(set(labels)) - 1
    unique_labels = set(labels)
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))

    plt.subplots(figsize=(12, 8))

    for k, c in zip(unique_labels, colors):
        class_member_mask = (labels == k)
        xy = df_90_cv[['Date_Label', 'Price']][class_member_mask].values
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=c,
                 markeredgecolor='k', markersize=12)

    plt.title("Total Clusters: {}".format(clusters_len), fontsize=14,
              y=1.01)

    plt.savefig('task_3_dbscan.png')
    plt.ion()
    plt.show()
    plt.draw()
    plt.pause(0.001)

    df_90_cv['Date_Label'] = X[:, 0]
    df_90_cv['Price_Label'] = X[:, 1]
    # find noise_points as outliers
    noises = df_90_cv[df_90_cv['dbscan_labels'] == -1]
    if len(noises) < 1:
        raise Exception("No noises")
    noises['nearest_Cluster'] = np.full((len(noises), 1), -2)
    clusters = []
    for label_db in df_90_cv.dbscan_labels.unique() - [-1]:
        clusters.append(df_90_cv[df_90_cv.dbscan_labels == label_db])

    noise_point_ret = []
    for index_noise, noy_p in noises.iterrows():
        distance_clusters_min = sys.maxsize
        cluster_min = clusters[0]
        for cluster in clusters:
            mean_tmp = cluster[['Date_Label', 'Price']].mean()
            dist_tmp = euclidean(noy_p[['Date_Label', 'Price']].values, mean_tmp.values)
            if dist_tmp < distance_clusters_min:
                distance_clusters_min = dist_tmp
                cluster_min = cluster
        mean_cluster = cluster_min.Price.mean()
        std_cluster = cluster_min.Price.std() * 2
        std_cluster = std_cluster if std_cluster > 50 else 50
        if noy_p.Price < mean_cluster - std_cluster:
            print  noy_p.Date_of_Flight, noy_p.Price, mean_cluster, std_cluster, mean_cluster - std_cluster, \
            cluster_min.iloc[0].dbscan_labels
            noy_p.nearest_Cluster = cluster_min.iloc[0].dbscan_labels
            noise_point_ret.append(noy_p[['Date_of_Flight', 'Price', 'nearest_Cluster']].values.tolist())
    noise_point_ret = pd.DataFrame(noise_point_ret, columns=['Date_of_Flight', 'Price', 'nearest_Cluster'])
    return noise_point_ret

# TODO ************* Task 3-2**********************
def task_3_IQR(flight_data):
    Q1 = flight_data["Price"].quantile(0.25)
    Q3 = flight_data["Price"].quantile(0.75)
    IQR = Q3 - Q1

    IQR_min = Q1 - 1.5 * IQR

    color = dict(boxes='DarkGreen', whiskers='DarkOrange', medians='DarkBlue', caps='Gray')
    flight_data['Price'].plot.box(color=color, sym='r+')

    plt.savefig('task_3_iqr.png')

    return flight_data[flight_data["Price"] < IQR_min]


# TODO ****************** Task 4 **********************
def task_4_dbscan(flight_data):
    # datelabel is date_of_flight scale to start:0, step:25,
    # select 25 as scale is avoid same price but two days away directly include in same cluster
    # scale based on former reason should be 20<scale<eps
    df_90_cv = pd.DataFrame(
        [[row.Date_of_Flight, (row.Date_of_Flight - flight_data.Date_of_Flight[0]).days * 25, row.Price]
         for index, row in flight_data.iterrows()],
        columns=['Date_of_Flight', 'Date_Label', 'Price'])

    # due to one day difference is 25, wants diff between Price <20,
    # euclidean([0,0],[25,20])=32.0156, euclidean([0,0],[25,21])=32.6496
    # thus, 32.0156<=eps<32.6496
    db = DBSCAN(eps=32.5, min_samples=3).fit(df_90_cv[['Date_Label', 'Price']])
    df_90_cv['dbscan_labels'] = db.labels_

    clusters_5 = []
    for label_db in df_90_cv.dbscan_labels.unique() - [-1]:
        cluster = df_90_cv[df_90_cv.dbscan_labels == label_db]
        cluster_len = len(cluster)
        if cluster_len >= 5:

            cluster_div_min = sys.maxsize
            cluster_div_ret = []

            # find 5 day period with the lowest average price
            for start in range(0, cluster_len - 4):
                cluster_div = cluster[start:start + 5]
                avg = cluster_div.Price.mean()
                if avg < cluster_div_min:
                    cluster_div_ret = cluster_div
                    cluster_div_min = avg
            clusters_5.append(cluster_div_ret[['Date_of_Flight', 'Price', 'dbscan_labels']])

    # only return periods where the difference between minimum price and the maximum price is also <= $20.
    for cluster in clusters_5:
        if cluster.Price.max() - cluster.Price.min() > 20:
            clusters_5.remove(cluster)
    return clusters_5


# TODO ************* Test Code **************
def test():
    df_60 = scrape_data(parser.parse('2017-04-01'), 'NYC', 'Scandinavia', 'Gothenburg')
    df_90 = scrape_data_90(parser.parse('2017-04-01'), 'NYC', 'Scandinavia', 'Gothenburg')

    print task_3_dbscan(df_90)
    print task_3_IQR(df_90)

    print task_4_dbscan(df_90)
    print df_90

# test()

