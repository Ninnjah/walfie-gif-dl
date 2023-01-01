import json
import logging
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

URL = "https://walfiegif.wordpress.com/"

logging.basicConfig(level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

options = Options()
options.headless = True
browser = Firefox(options=options)
browser.get(URL)

# Scroll to bottom to load all posts
logger.info("Scrolling to bottom...")
while True:
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    try:
        # Check if bottommost post is loaded
        browser.find_element(By.ID, "post-17")
    except NoSuchElementException:
        continue
    else:
        break

# Scrape data
logger.info("Scraping data...")
data = []
posts = browser.find_elements(By.CLASS_NAME, "post")
for post in posts:
    post_url = post.find_element(By.CLASS_NAME, "entry-image-link").get_attribute("href")
    gif_url = post.find_element(By.CLASS_NAME, "wp-post-image").get_attribute("src")
    gif_url = urljoin(gif_url, urlparse(gif_url).path)  # Remove query params
    title = post.find_element(By.CLASS_NAME, "entry-title").text

    try:
        tags = post.find_element(By.CLASS_NAME, "entry-tags").text.split(", ")
    except NoSuchElementException:
        if title == "crunchy marshmallow":
            tags = [
                "amelia watson",
                "hololive"
            ]
            logger.info(f"Tags added manually for post {title!r}.")
        else:
            tags = []
            logger.warning(f"No tags found for post {title!r}.")

    date = re.search(r"\d+/\d+/\d+", post_url).group()
    date = datetime.strptime(date, "%Y/%m/%d").date()

    data.append({
        "post": post_url,
        "gif": gif_url,
        "title": title,
        "date": date,
        "tags": tags
    })

with open("data.json", "w") as f:
    json.dump(data, f, indent=4, default=str)
logger.info("Stored data.")
