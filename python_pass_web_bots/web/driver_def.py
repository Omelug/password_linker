

def get_FF():
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    options = Options()

    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", "./downloads")
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    options.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Firefox(options=options)
    return driver

def get_chrome():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": "./downloads",
        "download.prompt_for_download": False,
        "profile.default_content_settings.popups": 0,
        "profile.content_settings.exceptions.automatic_downloads.*.setting": 1
    })

    # Disable loading images for faster crawling
    options.add_argument('--blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(options=options)
    return driver