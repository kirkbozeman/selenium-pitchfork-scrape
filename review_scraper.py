from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con
from mttkinter import mtTkinter as tk  # use multithread tkinter
#import sys

# define / set up tkinter progress window
window = tk.Tk()
window.title("Scrape Progress")

progress = tk.StringVar()
progress.set("Initializing...")
label1 = tk.Label(window, fg="blue", width=30, textvariable=progress)
label1.pack()

failed = tk.StringVar()
failed.set("")
label2 = tk.Label(window, fg="red", width=30, textvariable=failed)
label2.pack()


def get_urls():
    # Function that loops through retrieved urls and runs review scrape

    cn = mysql_con("Dev")
    with cn.cursor() as cursor:
        sql = f"""SELECT url 
                 FROM pitchfork_reviews 
                 WHERE error IS NULL OR error IS True"""
        cursor.execute(sql)
        urls = [str(item["url"]) for item in cursor.fetchall()]

    urlfails = []

    for ix, url in enumerate(urls):
        get_review_data(url, urlfails)

        try:
            # update tkinter window
            status = str(ix + 1) + " of " + str(len(urls)) + " complete (" + str(round(100*(ix + 1)/len(urls), 2)) + "%)"
            progress.set(status)
            failed.set(str(len(urlfails)) + (" failures" if len(urlfails) != 1 else " failure"))
            window.update()
        finally:
            pass


def get_review_data(url, urlfails):
    # Function used to scrape review page info for an album review link

    try:
        # initialize selenium
        driver = webdriver.Safari()
        driver.get(url)

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

        # get pub date
        try:
            pub_class = driver.find_element_by_class_name("pub-date")
            pub_date = pub_class.get_attribute("datetime")
        except NoSuchElementException:
            pub_date = "N/A"
            pass

        # get genre if exists
        try:
            genre_class = driver.find_element_by_class_name("genre-list__link")
            genre = genre_class.get_attribute("innerHTML")
        except NoSuchElementException:
            genre = "N/A"
            pass

        # get record label if exists
        try:
            reclabel_class = driver.find_element_by_class_name("labels-list__item")
            reclabel = reclabel_class.get_attribute("innerHTML")
        except NoSuchElementException:
            reclabel = "N/A"
            pass

        # get release dt if exists
        try:
            releasedt_class = driver.find_element_by_class_name("single-album-tombstone__meta-year")
            releasedt = releasedt_class.get_attribute("innerHTML")
        except NoSuchElementException:
            releasedt = "N/A"
            pass

        # get author if exists
        try:
            author_class = driver.find_element_by_class_name("authors-detail__display-name")
            author = author_class.get_attribute("innerHTML")
        except NoSuchElementException:
            author = "N/A"
            pass


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
        ,pub_date = %s
        ,release_dt = %s
        ,label = %s
        ,author = %s
        WHERE url = '""" + url + "'"

        cn = mysql_con("Dev")
        with cn.cursor() as cursor:
            cursor.execute(sql, (title, score, genre, ptags, pub_date, releasedt, reclabel, author))
            cn.commit()

    except Exception as e:  # for now, just mark errors and continue

        print("there was an error with " + str(url))
#        print(str(e))

        urlfails.append(str(url))

        sql = """
        UPDATE pitchfork_reviews
        SET get_date = NOW()
        ,error = True
        WHERE url = '""" + url + "'"

        cn = mysql_con("Dev")
        with cn.cursor() as cursor:
            cursor.execute(sql)
            cn.commit()

        window.update()

        pass

    finally:
        driver.quit()


if __name__ == '__main__':

    window.after(2, get_urls)  # needed to run tkinter alongside program
#    window.after(2, get_urls(int(sys.argv[1])*5000))  # needed to run tkinter alongside program
    window.mainloop()