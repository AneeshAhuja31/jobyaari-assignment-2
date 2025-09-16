from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
url = "https://jobyaari.com/jobdetails/2634"
driver.get(url)
time.sleep(2)

job_data = {}


company_elem = driver.find_element(By.CLASS_NAME, "drop__profession")
job_data['company'] = company_elem.text.strip() if company_elem else None


title_elem = driver.find_element(By.CLASS_NAME, "post-name")
job_data['title'] = title_elem.text.strip() if title_elem else None


age_elem = driver.find_element(By.CLASS_NAME, "job-location")
job_data['age_limit'] = age_elem.text.strip() if age_elem else None


location_elem = driver.find_element(By.CLASS_NAME, "location-list")
job_data['location'] = location_elem.text.strip() if location_elem else None


for elem in driver.find_elements(By.CLASS_NAME, "job-post-info-text"):
    label = elem.find_element(By.TAG_NAME, "h5").text.strip()
    value = elem.text.replace(label, "").strip()
    job_data[label.lower()] = value


for elem in driver.find_elements(By.CLASS_NAME, "job-post-info-text.edu"):
    label = elem.find_element(By.TAG_NAME, "h5").text.strip()
    value = elem.text.replace(label, "").strip()
    job_data[label.lower()] = value


rich_elem = driver.find_elements(By.CLASS_NAME, "rich-text.w-richtext")
all_texts = []

for elem in rich_elem:

    ol_items = elem.find_elements(By.TAG_NAME, "li")
    if ol_items:
        for li in ol_items:
            all_texts.append(li.text.strip())
    else:

        p_items = elem.find_elements(By.TAG_NAME, "p")
        for p in p_items:
            text = p.text.strip()
            if text:
                all_texts.append(text)

job_data['details_list'] = all_texts

print(job_data)
driver.quit()
