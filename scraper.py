from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
import pymysql
import json
from tkinter import *


# tkinter progress window
window = Tk()
window.title("Scrape Progress")
progress = StringVar()
progress.set("Initializing...")
label = Label(window, fg="blue", width=30, textvariable=progress)
label.pack()


def mysql_con():

    with open('config.json', 'r') as cf:
        config = json.load(cf)
        host = config["config"]["mysql_host"]
        user = config["config"]["mysql_user"]
        pw = config["config"]["mysql_password"]

    conn = pymysql.connect(host=host,
                         user=user,
                         password=pw,
                         db='Dev',
                         charset='utf8mb4',
                         cursorclass=pymysql.cursors.DictCursor)
    return conn


def get_urls():

    cn = mysql_con()
    with cn.cursor() as cursor:
        sql = 'SELECT url FROM pitchfork_reviews WHERE error IS NULL /*OR error IS True*/'
        cursor.execute(sql)
        urls = [item["url"] for item in cursor.fetchall()]

    for ix, url in enumerate(urls):
        get_review_data(str(url))
        status = str(ix + 1) + " of " + str(len(urls)) + " complete"
        progress.set(status)
        window.update()  # updates tkinter window


def get_review_data(url):

    # initialize selenium
    driver = webdriver.Safari()
    driver.get(url)

    try:
        # wait for Doc1 to be available (up to 20 sec before error)
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "review-detail")))
        sleep(2)  # wait additional (to be safe)

        # get artist / title (always first <title>)
        title1 = driver.find_element_by_xpath("//title[1]")
        title = title1.get_attribute("innerHTML")

        # get album score
        score_class = driver.find_element_by_class_name("score")
        score = score_class.get_attribute("innerHTML")

        # get album genre
        genre_class = driver.find_element_by_class_name("genre-list__link")
        genre = genre_class.get_attribute("innerHTML")

        # get album review (roughly 500 chars)
        body = driver.find_element_by_class_name("review-detail")
        review = body.get_attribute("innerHTML")
        soup = BeautifulSoup(review, features="lxml")
        ptags_list = [str(p) for p in soup.findAll('p') if str(p).find(r'class="title"') < 0]
        ptags = ''.join(ptags_list)


        sql = """
        UPDATE pitchfork_reviews
        SET title = %s
        ,score = %s
        ,genre = %s
        ,review = %s
        ,get_date = NOW()
        ,error = False
        WHERE url = '""" + url + "'"

        cn = mysql_con()
        with cn.cursor() as cursor:
            cursor.execute(sql, (title, score, genre, ptags))
            cn.commit()

    except:  # for now, just mark errors and continue

        print("there was an error with " + str(url))

        sql = """
        UPDATE pitchfork_reviews
        SET get_date = NOW()
        ,error = True
        WHERE url = '""" + url + "'"

        cn = mysql_con()
        with cn.cursor() as cursor:
            cursor.execute(sql)
            cn.commit()
        pass

    finally:
        driver.quit()


def get_links():

    for ix in range(0, 2000):  # force retry certain # times? # 1754 was last page on 2.28.19

        print(ix)

        url = "https://pitchfork.com/reviews/albums/?page=" + str(ix)
        driver = webdriver.Safari()
        driver.get(url)

        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "review")))
            sleep(3)  # wait additional (to be safe)

            soup = BeautifulSoup(driver.page_source, features="lxml", parse_only=SoupStrainer('a'))

            cn = mysql_con()  # correct place for this?
            for link in soup:
                if link.has_attr('href') \
                        and str(link).find("/reviews/albums/") > 0\
                        and str(link).find("?") < 0\
                        and str(link['href']) != "/reviews/albums/":

                    with cn.cursor() as cursor:  # correct place for this?
                        sql = "INSERT INTO popular_album_urls (url) VALUES (%s)"
                        cursor.execute(sql, (str(link['href'])))
                        cn.commit()

        finally:
            driver.quit()


if __name__ == '__main__':

    window.after(0, get_urls)  # needed to run tkinter alongside program
    window.mainloop()




