from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con
from multiprocessing import Pool, cpu_count


def get_links_history():
    """
    Function gets current full link history

    """
    cn = mysql_con("Dev")
    with cn.cursor() as cursor:
        sql = "SELECT DISTINCT url FROM album_urls"
        cursor.execute(sql)

    return [item["url"] for item in cursor.fetchall()]


def get_links(url):
    """
    Function used to retrieve available album review links from pitchfork.com/reviews/albums/...

    """

    url_hist = get_links_history()

    try:

        #driver = webdriver.Safari()  # multi will not work with safari
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
        driver.get(url)

        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "review")))  # review link data is in class=review
        sleep(3)  # wait additional (to be safe)

        soup = BeautifulSoup(driver.page_source, features="html.parser", parse_only=SoupStrainer('a'))
#        soup = BeautifulSoup(driver.page_source, features="lxml", parse_only=SoupStrainer('a'))

        cn = mysql_con("Dev")

        for link in soup.findAll('a'):

             if str(link).find("/reviews/albums/") > 0 > str(link).find("?") \
                    and str(link['href']) != "/reviews/albums/":

                href = str(link['href'])
                print(href)

                if href in url_hist:
                    print(f"Link {href} already exists.")
                else:
                    with cn.cursor() as cursor:
                        sql = "INSERT INTO album_urls (url) VALUES (%s)"
                        cursor.execute(sql, href)
                    cn.commit()  # must be o/s with

    except Exception as e:
        print(e)
        pass  # scraping should continue on fail

    finally:
        driver.quit()

    return 0


if __name__ == '__main__':

    urls = ["https://pitchfork.com/reviews/albums/?page=" + str(ix) for ix in range(1,10)]

    try:

        # run multiprocessing
        pool = Pool(2)
        results = [pool.apply_async(get_links, (url,)) for url in urls]
        print([r.get() for r in results])

    except Exception as e:
        print(e)
        pass

    finally:
        pool.close()
