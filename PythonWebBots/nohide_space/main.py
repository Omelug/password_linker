import argparse
import pickle
import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


file_path = "nohide-space.txt"
file_path_out = "nohide-space-message.txt"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-", "--hostname", help="Database name")
    parser.add_argument("-size", "--size", help="Size", type=int)
    parser.add_argument('--nocheck', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    driver = webdriver.Firefox()
    driver.get("https://nohide.space/search/572982/?q=czech&o=date")

    #https://stackoverflow.com/questions/76575298/how-to-click-on-verify-you-are-human-checkbox-challenge-by-cloudflare-using-se
    time.sleep(5)
    WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
    time.sleep(5)
    #driver.save_screenshot("nohide-space.png")


    last_time = time.time() - 2592000*5   # TODO get from json, ted mesic dozadu

    if not args.nocheck:
        with open(file_path, 'w+') as file:
            lines = file.readlines()
        while True:
            main_div = driver.find_element(By.CLASS_NAME, "p-body-main")
            leak_list = main_div.find_elements(By.CLASS_NAME, "contentRow")
            for row in leak_list:
                time_element = row.find_element(By.XPATH, '//time')
                time_attribute_value = time_element.get_attribute("data-time")
                link = row.find_element(By.CLASS_NAME, "contentRow-title").find_element(By.XPATH, './/a').get_attribute("href")
                if float(time_attribute_value) != last_time:
                    print(f"{link} ? : {float(time_attribute_value) > last_time}")
                    link = link + "\n"

                    if link.strip() not in lines:
                        with open(file_path_out, 'a') as file:
                            file.write(link)
                    else:
                        print("Line already exists in the file.")

                else:
                    break
            try:
                next_page_link = driver.find_element(By.XPATH, ".//a[contains(@class, 'pageNav-jump') and contains(@class, 'pageNav-jump--next')]")
                next_page_link.click()

                #WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
                print("Next page loading.")
                driver.implicitly_wait(7)

            except NoSuchElementException:
                print("No Next button ")
                break

    with open(file_path, "r") as file:
        links = file.readlines()

    with open(file_path_out, "w") as output_file:
        for link in links:
            driver.get(link.strip())
            input()
            try:
                message_content = driver.find_element(By.CLASS_NAME, "message--post")
                text = message_content.text.strip()
                output_file.write(text + "\n")
                print("Text extracted and saved for:", link.strip())
            except NoSuchElementException:
                print("Element 'message-content' not found for:", link.strip())



    # if after timestemp save to json  file
    # get another list
    # posun timestemp v options.json
    #from list get message, save div with class message-main to json
