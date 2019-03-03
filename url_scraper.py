from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con


def get_links():
    """
    Function used to retrieve available album review links from pitchfork.com/reviews/albums/...
    Used to scrape links thru 2/28/19 (any site design changes may require code adjustments or rebuild)

    """

    for ix in range(1, 2000):  # force retry certain # times? # 1754 was last page on 2.28.19

        print(ix)  # debug print page num
        url = "https://pitchfork.com/reviews/albums/?page=" + str(ix)

        driver = webdriver.Safari()
        driver.get(url)

        try:
            element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "review")))  # review link data is in class=review
            sleep(3)  # wait additional (to be safe)

            soup = BeautifulSoup(driver.page_source, features="lxml", parse_only=SoupStrainer('a'))

            cn = mysql_con("Dev")

            for link in soup:

                if link.has_attr('href') \
                        and str(link).find("/reviews/albums/") > 0 > str(link).find("?") \
                        and str(link['href']) != "/reviews/albums/":

                    with cn.cursor() as cursor:
                        sql = "INSERT INTO album_urls (url) VALUES (%s)"
                        cursor.execute(sql, (str(link['href'])))
                        cn.commit()

        finally:
            driver.quit()


if __name__ == '__main__':
    get_links()

