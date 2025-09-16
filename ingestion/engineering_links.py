from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
driver = webdriver.Chrome()
driver.get("https://jobyaari.com/category/engineering?type=graduate")

time.sleep(2)

last_height = driver.execute_script("return document.body.scrollHeight")

while True:

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


elements = driver.find_elements(By.CLASS_NAME, "drop-name")

job_links = {}
for idx, elem in enumerate(elements, start=1):
    onclick_value = elem.get_attribute("onclick")
    if onclick_value and "location.href=" in onclick_value:
        link = onclick_value.split('"')[1]
        job_links[f"job_{idx}"] = link

print(f"✅ Extracted {len(job_links)} job links")
print(job_links)
with open("engineering_jobs_links.json","w") as f:
    json.dump(job_links, f)
    
driver.quit()
