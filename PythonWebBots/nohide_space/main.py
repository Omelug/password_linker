import argparse
import json
import time
import subprocess
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import re
import logging
import sys
import datetime

lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')
sys.path.append(lib_dir)
from lib.file_format import *

logging.basicConfig(level=logging.INFO,
                    # filename="main.log",
                    format="%(asctime)s:%(levelname)s:%(message)s (Line: %(lineno)d [%(filename)s])"
                    )

# check -> posts.txt (sort) -> postit -> links.txt -> awk only_links.txt (sort) -> download_link.txt
posts_file = "posts.txt"
links_file = "links.txt" #for download <source> <username> <link> <post_link>
only_links_file = "only_links.txt" #link list from  links_file <link>
combo_links_file = "combo_links.txt" #for combos which are better to sort by hand <source> <username> <link> <post_link>
fake_links_file = "fake_links.txt"  #for fake list of <source> <username> <link> <post_link>
links_downloaded_file = "links_downloaded.txt" #downloaded links <link>

option_file = "options.json"
SITE_NAME = "nohide-space"




def get_new_posts() -> bool: # succes?
    create_file_if_not_exists(posts_file)

    with open(posts_file, 'r') as file:
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
                #print(f"{date_to_string(float(time_attribute_value))} > {last_time_list}")
                if date_to_string(float(time_attribute_value)) > last_time_list:
                    #TODO save only if not already saved
                    logging.info(f"{link}")
                    link = link + "\n"
                    if link.strip() not in lines:
                        with open(posts_file, 'a') as file2:
                            file2.write(link)
                    else:
                        logging.info(f"Line {link} exists in the {posts_file}.")
                else:
                    next_page = False
                    break
            if not next_page:
                return True
            try:
                next_page_link = driver.find_element(By.XPATH,
                                                     ".//a[contains(@class, 'pageNav-jump') and contains(@class, 'pageNav-jump--next')]")
                next_page_link.click()
                logging.info("Next page loading.")
                driver.implicitly_wait(5)

            except NoSuchElementException:
                logging.info("No Next button")
                return True


# TODO make unit test
def all_items_in_list_in_file(data_links, *args):
    grep_command = ["grep", "-Ec", "-w"]
    for link in data_links:
        grep_command.extend(["-e", link])
    for file_path in args:
        grep_command.append(f" {file_path}")
    result = subprocess.run(grep_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        stdout_str = result.stdout.strip()
        if stdout_str:
            num_matches = int(stdout_str)
            return num_matches == len(data_links)
        else:
            return False
    else:
        print("Error:", result.stderr.decode())
        print(data_links)
        return False


def get_link_from_posts():
    create_file_if_not_exists(posts_file)
    create_file_if_not_exists(only_links_file)
    create_file_if_not_exists(combo_links_file)
    create_file_if_not_exists(fake_links_file)

    with open(posts_file, "r") as file:
        post_links = file.readlines()

    for post_link in post_links:
        driver.get(post_link.strip())
        try:
            username = driver.find_element(By.CLASS_NAME, "username ").text
            message_content = driver.find_element(By.CLASS_NAME, "message--post")
            logging.info(f"Now: {username}:{post_link.strip()}")
            data_links = message_content.find_elements(By.CLASS_NAME, "link--external")

            with (open(links_file, "a") as file_links_f):
                for index, data_link in enumerate(data_links):
                    print(f"{index} {username}\t{data_link.get_attribute('href')}")
                # already in file, skip input
                flist = [data_link.get_attribute('href') for data_link in data_links]
                #TODO muzou byt ruzne, ale aspon v jednom listu
                #FIXME COMBO listy se porad nabyzeji, i kdyz uz jsou v listech
                if all_items_in_list_in_file(flist, links_file) or \
                        all_items_in_list_in_file(flist, combo_links_file) or \
                        all_items_in_list_in_file(flist, fake_links_file):
                    logging.info(f"File {links_file} already contains all links.")
                    continue
                inp = input("Save: [A]ll, To [C]ombo list, [F]ake, [N]othing, number separated with , :")

                match inp.lower():
                    case "a" | "": #
                        for data_link in data_links:
                            line = f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}"
                            file_links_f.write(f"{line}\n")
                    case "n":
                        pass
                    case "c":
                        with open(combo_links_file, "a") as file_combo_links:
                            line = f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}"
                            file_fake_links.write(f"{line}\n")
                    case "f":
                        with open(fake_links_file, "a") as file_fake_links:
                            line = f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}"
                            file_fake_links.write(f"{line}\n")
                    case _:
                        try:
                            indexes = list(map(int, inp.split(",")))
                        except ValueError:
                            logging.warning(f"Invalid value {inp}, added all")
                        for index, data_link in enumerate(data_links):
                            if index in indexes:
                                file_links_f.write(
                                    f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}\n")
        except NoSuchElementException as e:
            logging.info("Element  not found:", e)
            return False
    update_config(option_file, "last_time_posts", time.time())


# read from stdin
def download_files(driver):
    """
        download files from stdin and print only what wasnt downloaded
    """
    create_file_if_not_exists(links_file)
    create_file_if_not_exists(links_downloaded_file)
    with open(links_downloaded_file, 'r') as links_downloaded:
        links_down_list = links_downloaded.readlines()
    with open(links_downloaded_file, 'a+') as links_downloaded:
        with open(only_links_file, 'r') as only_links_f:
            for link in only_links_f:
                if link in links_down_list:
                    logging.info(f"{link.strip()} already in {links_downloaded_file}")
                else:
                    try:
                        if re.compile("^https://www.upload.ee/files/.*?$").match(link):

                            driver.get(link.strip())
                            download_link = driver.find_element(By.ID, "d_l").get_attribute("href")
                            if download_with_wget(download_link, "../../rsc/nohide_space/original"):
                                links_downloaded.write(f"{link}")
                        elif re.compile("^https://pixeldrain.com/u/.*?$").match(link):
                            download_link = link.strip().replace("/u/", "/api/file/")
                            if download_with_wget(download_link, "../../rsc/nohide_space/original"):
                                links_downloaded.write(f"{link}")
                        else:
                            logging.warning(f"{link.strip()} is unsupported, skipped")
                    except Exception as e:
                        logging.error(f"Error downloading {e}")
    # TODO TODO TODo
    # if not try downloading , also print  (create verbose for ir)

    # for downloading jump to part for solve specific links
    # if fails, skip, print warning
    # open links, detect download button, #change downloading path to rsc/nohide_space/origin/<name of user>/<name of file>, download
    # TODO here maybe create small json report
    # if error during downloading, print errors and create error.txt ( for automatiom later, maybe discord webhook now) //udelat funkci co vyise soubor na /telegram
    # append to links_downloaded.txt if succesfull


def cloudfare_wait_checkbox(driver):
    # https://stackoverflow.com/questions/76575298/how-to-click-on-verify-you-are-human-checkbox-challenge-by-cloudflare-using-se
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
    time.sleep(5)


if __name__ == "__main__":
    """
        
    """
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

    driver = webdriver.Firefox()

    # bypass cloudflare checkbox
    if args.get_new_post or args.get_links:
        driver.get("https://nohide.space/search/572982/?q=czech&o=date")
        cloudfare_wait_checkbox(driver)

    if args.get_new_post:
        last_time_list = load_config(option_file, "last_time_list", "0001-01-01 00:00:00")
        logging.info(f"last_time_list: {last_time_list}")
        if get_new_posts(): # load posts links to post_file
            subprocess.run(["sort", "-u", posts_file, "-o", posts_file], check=True)
            update_config(option_file, "last_time_list", now_string())
            logging.info("get_post_list() finished.")
        logging.info("CHECK finished succesfully")
    if args.get_links:
        last_time_posts = load_config(option_file, "last_time_list", "0001-01-01 00:00:00")
        if get_link_from_posts(): #load resource links from posts
            subprocess.run(["sort", "-u", links_file, "-o", links_file], check=True)
            subprocess.run(["sort", "-u", combo_links_file, "-o", combo_links_file], check=True)
            subprocess.run(["sort", "-u", fake_links_file, "-o", fake_links_file], check=True)
            update_config(option_file, "last_time_list", now_string())
            logging.info("get_link_from_posts() finished succesfully")
        logging.info("POST IT finished.")
    if args.download:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        links = os.path.join(script_dir, 'links.txt')
        only_links = os.path.join(script_dir, 'only_links.txt')

        command = f"cat {links} | awk -F'\t' '{{print $3}}' | sort -u > {only_links}"
        subprocess.run(command, shell=True)

        download_files(driver=driver)
        logging.info("DOWNLOAD finished.")