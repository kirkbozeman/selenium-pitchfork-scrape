from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con
from mttkinter import mtTkinter as tk  # use multithread tkinter

# tkinter progress window
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

    cn = mysql_con()
    with cn.cursor() as cursor:
        sql = 'SELECT url FROM pitchfork_reviews WHERE error IS NULL /*OR error IS True*/'
        cursor.execute(sql)
        urls = [item["url"] for item in cursor.fetchall()]

    urlfails = []

    for ix, url in enumerate(urls):
        get_review_data(str(url), urlfails)
        status = str(ix + 1) + " of " + str(len(urls)) + " complete"

        # update tkinter window
        progress.set(status)
        failed.set(str(len(urlfails)) + (" failures" if len(urlfails) != 1 else " failure"))
        window.update()


def get_review_data(url, urlfails):
    # Function used to scrape review page info for an album review link

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

        urlfails.append(str(url))

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




if __name__ == '__main__':

    window.after(1, get_urls)  # needed to run tkinter alongside program
    window.mainloop()




# exception in tkinter callback