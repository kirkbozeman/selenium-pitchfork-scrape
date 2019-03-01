from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con



def get_links():
    # Function used to retrieve available album review links from pitchfork.com/reviews/albums/...

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
