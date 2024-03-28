import argparse
import json
import time
import subprocess
import os
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
import logging

logging.basicConfig(level=logging.INFO,
                    # filename="main.log",
                    format="%(asctime)s:%(levelname)s:%(message)s (Line: %(lineno)d [%(filename)s])"
                    )

# check -> posts.txt (sort) -> postit -> links.txt -> awk only_links.txt (sort) -> download_link.txt
posts_file = "posts.txt"
links_file = "links.txt"
only_links_file = "only_links.txt"
combo_links_file = "combo_links.txt"
links_downloaded_file = "links_downloaded.txt"

option_file = "options.json"
SITE_NAME = "nohide-space"


def create_file_if_not_exists(file: str) -> int:
    """
        @return 1 if created, 0 if already existed, -1 if error
    """
    try:
        with open(file, 'r'):
            return 0
    except FileNotFoundError:
        try:
            with open(file, 'w'):
                logging.info(f"File '{file}' created successfully.")
            return 1
        except FileNotFoundError:
            return -1


def load_config(config_file_path: str, key: str) -> int | None:
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
                if float(time_attribute_value) > last_time_list:
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
    logging.info("get_post_list() finished.")


# TODO make unit test
def all_items_in_list_in_file(data_links, file_path):
    grep_command = ["grep", "-Ec", "-w"]
    for link in data_links:
        grep_command.extend(["-e", link])
    grep_command.append(file_path)
    # print(grep_command)
    result = subprocess.run(grep_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        stdout_str = result.stdout.strip()
        if stdout_str:
            num_matches = int(stdout_str)
            return num_matches == len(data_links)
        else:
            # No matches found
            return False
    else:
        print("Error:", result.stderr.decode())
        return False


def get_link_from_posts():
    create_file_if_not_exists(posts_file)
    create_file_if_not_exists(only_links_file)
    create_file_if_not_exists(combo_links_file)

    with open(posts_file, "r") as file:
        post_links = file.readlines()

    for post_link in post_links:
        driver.get(post_link.strip())
        try:
            username = driver.find_element(By.CLASS_NAME, "username ").text
            message_content = driver.find_element(By.CLASS_NAME, "message--post")
            # text = message_content.text.strip()
            # output_file.write(text + "\n")
            logging.info(f"Now: {username}:{post_link.strip()}")
            data_links = message_content.find_elements(By.CLASS_NAME, "link--external")

            with (open(file_links, "a") as file_links):
                for index, data_link in enumerate(data_links):
                    print(f"{index} {username}\t{data_link.get_attribute('href')}")
                # already in file, skip input
                flist = [data_link.get_attribute('href') for data_link in data_links]
                if all_items_in_list_in_file(flist, file_links) or \
                        all_items_in_list_in_file(flist, combo_links_file):
                    logging.info(f"File {file_links} already contains all links.")
                    continue
                inp = input("Save: [A]ll, To [C]ombo list,  [N]othing, number separated with , :")
                if inp == "A" or inp == "":
                    for data_link in data_links:
                        line = f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}"
                        file_links.write(f"{line}\n")
                elif inp == "N":
                    pass
                elif inp == "C":
                    with open(combo_links_file, "a") as file_combo_links:
                        line = f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}"
                        file_combo_links.write(f"{line}\n")
                else:
                    try:
                        indexes = list(map(int, inp.split(",")))
                    except ValueError:
                        logging.warning(f"Invalid value {inp}, added all")
                    for index, data_link in enumerate(data_links):
                        if index in indexes:
                            file_links.write(
                                f"{SITE_NAME}\t{username}\t{data_link.get_attribute('href')}\t{post_link.strip()}\n")
        except NoSuchElementException as e:
            logging.info("Element  not found:", e)
    update_config(option_file, "last_time_posts", time.time())
    logging.info("get_link_from_posts()")
#TODo uniot test
def download_with_wget(url, output_directory):
    try:
        subprocess.run(['wget', url, '-P', output_directory], check=True)
        logging.info(f"{url} downloaded successful!")
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Error downloading file:", e)
        return False

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
                        else:
                            logging.warning(f"{link.strip()} is unsupported, skip")
                    except Exception as e:
                        logging.error(f"Error downloading {e}")
    print()
    # TODO TODO TODo
    # if not try downloading , also print  (create verbose for ir)

    # for downloading jump to part for solve specific links
    # if fails, skip, print warning
    # open links, detect download button, #change downloading path to rsc/nohide_space/origin/<name of user>/<name of file>, download
    # TODO here maybe create small json report
    # if error during downloading, print errors and create error.txt ( for automatiom later, maybe discord webhook now) //udelat funkci co vyise soubor na /telegram
    # append to links_downloaded.txt if succesfull


def get_main_page(driver):
    driver.get("https://nohide.space/search/572982/?q=czech&o=date")

    # https://stackoverflow.com/questions/76575298/how-to-click-on-verify-you-are-human-checkbox-challenge-by-cloudflare-using-se
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
    time.sleep(5)


if __name__ == "__main__":
    """
        log in into no space, get post from last_time, download posts from last time
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-", "--hostname", help="Database name")
    parser.add_argument("-size", "--size", help="Size", type=int)
    parser.add_argument('--check', action=argparse.BooleanOptionalAction)
    parser.add_argument('--postit', action=argparse.BooleanOptionalAction)
    parser.add_argument('--download', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "./downloads")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

    driver = webdriver.Firefox(options=options)

    if args.check:
        get_main_page(driver)
        last_time_list = load_config_default(option_file, "last_time_list", 0)
        get_post_list()
        subprocess.run(["sort", "-u", posts_file, "-o", posts_file], check=True)
    if args.postit:
        get_main_page(driver)
        last_time_posts = load_config_default(option_file, "last_time_list", 0)
        get_link_from_posts()
        subprocess.run(["sort", "-u", links_file, "-o", links_file], check=True)
        subprocess.run(["sort", "-u", combo_links_file, "-o", combo_links_file], check=True)
    if args.download:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        links = os.path.join(script_dir, 'links.txt')
        only_links = os.path.join(script_dir, 'only_links.txt')

        command = f"cat {links} | awk -F'\t' '{{print $3}}' | sort -u > {only_links}"
        subprocess.run(command, shell=True)

        download_files(driver=driver)
