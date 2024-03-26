import argparse
import json
import time
import subprocess

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import logging

logging.basicConfig(level=logging.INFO,
                    # filename="main.log",
                    format="%(asctime)s:%(levelname)s:%(message)s (Line: %(lineno)d [%(filename)s])"
                    )
file_post = "posts.txt"
file_path_out = "posts_text.txt"
file_link_list = "links.txt"
file_downloaded_list = "links_downloaded.txt"

option_file = "options.json"
site_name = "nohide-space"


# return 1 if created, 0 if alredy existed, -1 if error
def create_file_if_not_exists(file: str) -> int:
    try:
        with open(file, 'r'):
            return 0
    except FileNotFoundError:
        with open(file, 'w'):
            logging.info(f"File '{file}' created successfully.")
            return 1


def load_config(config_file_path: str, key: str) -> int:
    try:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            return config.get(key)
    except FileNotFoundError:
        return None


def update_config(config_file_path: str, key: str, new_value: str):
    if create_file_if_not_exists(config_file_path):
        config_data = {}
    else:
        with open(config_file_path, 'r') as config_file:
            config_data = json.load(config_file)
    try:
        config_data[key] = new_value
        with open(config_file_path, 'w') as json_file:
            json.dump(config_data, json_file, indent=4)
    except ValueError:
        logging.critical(f"Invalid value {new_value} for key {key}")


def load_config_default(config_file: str, key: str, default: str):
    is_none = load_config(config_file, key)
    if is_none is None:
        is_none = default
    return is_none


def get_post_list():
    create_file_if_not_exists(file_post)

    with open(file_post, 'r') as file:
        file.seek(0)
        lines = file.readlines()
    next_page = True
    while next_page:
        main_div = driver.find_element(By.CLASS_NAME, "p-body-main")
        leak_list = main_div.find_elements(By.CLASS_NAME, "contentRow")
        for row in leak_list:
            time_element = row.find_element(By.XPATH, '//time')
            time_attribute_value = time_element.get_attribute("data-time")
            link = row.find_element(By.CLASS_NAME, "contentRow-title").find_element(By.XPATH, './/a').get_attribute(
                "href")
            if float(time_attribute_value) > last_time_list:
                logging.info(f"{link}")
                link = link + "\n"
                if link.strip() not in lines:
                    file.write(link)
                else:
                    logging.info(f"Line {link} exists in the {file_post}.")
            else:
                next_page = False
                break
        if not next_page:
            break
        try:
            next_page_link = driver.find_element(By.XPATH,
                                                 ".//a[contains(@class, 'pageNav-jump') and contains(@class, 'pageNav-jump--next')]")
            next_page_link.click()
            logging.info("Next page loading.")
            driver.implicitly_wait(5)

        except NoSuchElementException:
            logging.info("No Next button")
            break
    update_config(option_file, "last_time_list", time.time())


def get_link_from_posts():
    create_file_if_not_exists(file_post)
    create_file_if_not_exists(file_path_out)
    create_file_if_not_exists(file_link_list)

    with open(file_post, "r") as file:
        post_links = file.readlines()

    with open(file_path_out, "w") as output_file:
        for post_link in post_links:
            driver.get(post_link.strip())
            try:
                username = driver.find_element(By.CLASS_NAME, "username ").text
                message_content = driver.find_element(By.CLASS_NAME, "message--post")
                text = message_content.text.strip()
                output_file.write(text + "\n")
                logging.info("Now:", username, ":", post_link.strip())
                data_links = message_content.find_elements(By.CLASS_NAME, "link--external")
                with open(file_link_list, "a") as file_links:
                    for data_link in data_links:
                        file_links.write(f"{site_name}:{username}:{data_link.get_attribute('href')}\n")
                input()
            except NoSuchElementException as e:
                logging.info("Element  not found:", e)
    update_config(option_file, "last_time_posts", time.time())


# read from stdin
def download_files():
    create_file_if_not_exists(file_link_list)
    create_file_if_not_exists(file_downloaded_list)

    # TODO TODO TODo
    # open link and chcek name if already in links_downloaded.txt
    # if  yes, print warning
    # if not try downloading download, also print  (create verbose for ir)

    # for downloading jump to part for solve specific links
    # if fails, skip, print warning
    # open links, detect download button, #change downloading path to rsc/nohide_space/origin/<name of user>/<name of file>, download
    # TODO here maybe create small json report
    # if error during downloading, print errors and create error.txt ( for automatiom later, maybe discord webhook now) //udelat funkci co vyise soubor na /telegram
    # append to links_downloaded.txt if succesfull


if __name__ == "__main__":
    """
        log in into no space, get post from last_time, download posts from last time
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-", "--hostname", help="Database name")
    parser.add_argument("-size", "--size", help="Size", type=int)
    parser.add_argument('--nocheck', action=argparse.BooleanOptionalAction)
    parser.add_argument('--nopostit', action=argparse.BooleanOptionalAction)
    parser.add_argument('--download', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    driver = webdriver.Firefox()
    driver.get("https://nohide.space/search/572982/?q=czech&o=date")

    # https://stackoverflow.com/questions/76575298/how-to-click-on-verify-you-are-human-checkbox-challenge-by-cloudflare-using-se
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
    time.sleep(5)

    last_time_list = load_config_default(option_file, "last_time_list", 0)
    last_time_posts = load_config_default(option_file, "last_time_list", 0)

    if not args.nocheck:
        get_post_list()
    if not args.nopostit:
        get_link_from_posts()
        subprocess.run(["sort", "-u", file_link_list, "-o", file_link_list], check=True)

    if args.download:
        download_files()  # read from stdin
