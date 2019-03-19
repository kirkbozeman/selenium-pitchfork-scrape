"""
Process used to scrape review data from pitchfork.com for use in Natural Language Processing -
multiprocessing version

"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup, SoupStrainer
from time import sleep
from mysql_con import mysql_con
from multiprocessing import Pool, cpu_count


def get_urls():

    cn = mysql_con("Dev")
    with cn.cursor() as cursor:
        sql = f"""SELECT url 
                 FROM pitchfork_reviews 
                 LIMIT 10
                /* WHERE error IS NULL OR error IS True */"""
        cursor.execute(sql)

    return [item["url"] for item in cursor.fetchall()]


def get_review_data(url):

    try:
        # initialize selenium
#        driver = webdriver.Safari()
        options = webdriver.ChromeOptions()
#        options.add_argument("headless")
        driver = webdriver.Chrome(options=options)
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

        sql = """
        UPDATE pitchfork_reviews
        SET get_date = NOW()
        ,error = True
        WHERE url = '""" + url + "'"

        cn = mysql_con("Dev")
        with cn.cursor() as cursor:
            cursor.execute(sql)
            cn.commit()

        pass

    finally:

        driver.quit()

    return 0


if __name__ == '__main__':

    try:

        urls = get_urls()
        print(urls)

        # run multiprocessing
        pool = Pool(cpu_count())
        results = [pool.apply_async(get_review_data, (url,)) for url in urls]
        # note the odd behavior, the x, is necessary to avoid the string being interpreted as a list
        print([r.get() for r in results])

    except Exception as e:
        print(e)
        pass

    finally:
        pool.close()
