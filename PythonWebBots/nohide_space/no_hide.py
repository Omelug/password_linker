import argparse
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import re
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)
from lib.file_format import *

logging.basicConfig(level=logging.INFO,
                    # filename="main.log",
                    format="%(asctime)s:%(levelname)s:%(message)s (Line: %(lineno)d [%(filename)s])"
                    )

option_file = "options.json"
SITE_NAME = "nohide-space"
DB_FILE = "no_hide.db"
save_mode = {"A": "all", "C": "combo", "F": "fake", "N": "nothing", "S": "separated"}

engine = create_engine(DB_FILE)
Session = sessionmaker(bind=engine)

def db_init():
    with Session() as session:
        session.execute('''CREATE TABLE IF NOT EXISTS POSTS (
                            link TEXT PRIMARY KEY,
                            date TEXT,
                            get_date TEXT
                        )''')
        session.execute('''CREATE TABLE IF NOT EXISTS LINKS (
                                link TEXT PRIMARY KEY,
                                post_link TEXT,
                                save_mode TEXT,
                                author TEXT,
                                sort_date TEXT,
                                download_date TEXT,
                                download_path TEST
                            )''')
        session.commit()

def insert_post(link, date):
    with Session() as session:
        session.execute('''INSERT OR IGNORE INTO POSTS (link, date, get_date)
                          VALUES (?,?, ?)''', (link, date, now_string()))

        inserted = session.rowcount > 0
        session.commit()
    return inserted

def insert_link_to_db(post_info, link, save_mode):
    author, post_link = post_info
    with Session() as session:
        session.execute('''INSERT OR IGNORE INTO LINKS (link, save_mode, author, post_link, sort_date)
                          VALUES (?,?,?,?,?)''', (link, save_mode, author, post_link, now_string()))
        inserted = session.rowcount > 0
        session.commit()
    return inserted


def insert_links_to_db(post_info, links, save_mode):
    for link in links:
        insert_link_to_db(post_info, link.get_attribute("href"), save_mode)

def all_items_in_list_in_db(links):
    links_set = set(links)
    placeholders = ','.join('?' * len(links_set))
    with Session() as session:
        result = session.execute(f'SELECT link FROM LINKS WHERE link IN ({placeholders})', tuple(links_set))
        rows = result.fetchall()
    return links_set.issubset({row[0] for row in rows})

def get_links():
    with Session() as session:
        link_from_posts = session.execute('SELECT link FROM POSTS')
        rows = link_from_posts.fetchall()
        links = {row[0] for row in rows}
    return links

def get_not_down_links():
    with Session() as session:
        links_sql =session.execute('SELECT * FROM LINKS WHERE download_date is NULL')
        rows = links_sql.fetchall()
        down_links = {row for row in rows}
    return down_links

def update_download_info(link, download_date, download_path):
    with Session() as session:
        session.execute('''
                    UPDATE LINKS
                    SET download_date = ?, download_path = ?
                    WHERE link = ?
                ''', (download_date, download_path, link))
        session.commit()

def get_new_posts() -> bool:  # succes?
    while True:
        for row in driver.find_elements(By.CLASS_NAME, "contentRow"):
            time_element = row.find_element(By.XPATH, '//time')
            time_attribute_value = time_element.get_attribute("data-time")
            link = row.find_element(By.CLASS_NAME, "contentRow-title").find_element(By.XPATH, './/a').get_attribute("href")
            if date_to_string(float(time_attribute_value)) > last_time_list:
                insert_post(link, date_to_string(float(time_attribute_value)))
            else:
                return True
        try:
            next_page_link = driver.find_element(By.XPATH, ".//a[contains(@class, 'pageNav-jump') and contains(@class, 'pageNav-jump--next')]")
            next_page_link.click()
            logging.info("Next page loading.")
            driver.implicitly_wait(5)
        except NoSuchElementException:
            logging.info("No Next button")
            return True


def get_link_from_posts():
    for post_link in get_links():
        driver.get(post_link.strip())
        try:
            author = driver.find_element(By.CLASS_NAME, "username ").text
            message_content = driver.find_element(By.CLASS_NAME, "message--post")
            logging.info(f"Now: {author}:{post_link.strip()}")
            data_links = message_content.find_elements(By.CLASS_NAME, "link--external")

            try:
                for index, data_link in enumerate(data_links):
                    print(f"{index} {author}\t{data_link.get_attribute('href')}")
                flist = [data_link.get_attribute('href') for data_link in data_links]
            except Exception:
                continue

            if all_items_in_list_in_db(flist):
                logging.info(f"File {post_link} already contains all links.")
                continue

            while True:
                in_save = input("Save: [A]ll, To [C]ombo list, [F]ake, [N]othing, number separated with S,,,, :")
                post_info = (author, post_link.strip())

                try:
                    if 'S' not in in_save:
                        for link in flist:
                            insert_link_to_db(post_info, link, save_mode[in_save])
                    else:
                        indexes = list(map(int, in_save[1].split(",")))
                        for index, link in enumerate(data_links):
                            if index in indexes:
                                insert_link_to_db(post_info, link.get_attribute("href"), save_mode["S"])
                    break
                except KeyError:
                    logging.warning(f"Invalid input value")
        except NoSuchElementException:
            logging.info("Element  not found")
            return False
    return True

#  download files from stdin and print only what wasnt downloaded
def download_files(driver):
    for link in get_not_down_links():
        if re.compile("^https://www.upload.ee/files/.*?$").match(link[0]):
            driver.get(link[0])

            name = re.compile("^.*/(.*)\..*\..*$").match(link[0]).group(1)
            f_name = re.compile("^.*/(.*)\..*$").match(link[0]).group(1)

            try:
                download_link = driver.find_element(By.ID, "d_l").get_attribute("href")
            except NoSuchElementException:
                try:
                    td_element = driver.find_element(By.CSS_SELECTOR, 'td.textbody[valign="top"]')
                    if 'There is no such file.' in td_element.text:
                        update_download_info(link[0], now_string(), "NOT VALID LINK")
                        logging.info(f"There is no such file {link[0]}")
                finally:
                    continue
        elif re.compile("^https://pixeldrain.com/u/.*?$").match(link[0]):
            driver.get(link[0])
            meta_tag = driver.find_element(By.CSS_SELECTOR, 'meta[property="og:title"]')
            f_name = meta_tag.get_attribute("content").replace(" ", "_")
            name = re.compile("^(.*)\..*$").match(f_name).group(1)
            download_link = link[0].replace("/u/", "/api/file/")
        else:
            logging.warning(f"{link[0]} is not supported, skipped")
            continue

        #TODO
        if link[2] != "all" and link[2] != "separated":
            continue

        path = f"../../rsc/nohide_space/original/{name}"
        absolute_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))
        f_path = f"{absolute_path}/{f_name}"

        if os.path.exists(path):
            logging.warning(f"{link[0]} already exists")
            update_download_info(link[0], "EXISTS", path)
            continue

        os.makedirs(path)

        if download_with_wget(download_link, f_path):
            update_download_info(link[0], now_string(), path)
        else:
            logging.error(f"Error wget {link}")


def cloudfare_wait_checkbox(driver):
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.cb-lb"))).click()
    time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--get_new_post', action=argparse.BooleanOptionalAction)
    parser.add_argument('--get_links', action=argparse.BooleanOptionalAction)
    parser.add_argument('--download', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "./downloads")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

    db_init()

    driver = webdriver.Firefox()

    if args.get_new_post or args.get_links:
        driver.get("https://nohide.space/search/572982/?q=czech&o=date")
        cloudfare_wait_checkbox(driver)
    if args.get_new_post:
        last_time_list = load_config(option_file, "last_time_list", "0001-01-01 00:00:00")
        logging.info(f"last_time_list: {last_time_list}")
        if get_new_posts():  # load posts links to post_file
            update_config(option_file, "last_time_list", now_string())
        logging.info("CHECK finished")
    if args.get_links:
        last_time_posts = load_config(option_file, "last_time_list", "0001-01-01 00:00:00")
        if get_link_from_posts():  #load resource links from posts
            update_config(option_file, "last_time_list", now_string())
        logging.info("GET LINKS finished")
    if args.download:
        download_files(driver=driver)
        logging.info("DOWNLOAD finished.")
