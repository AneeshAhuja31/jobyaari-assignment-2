import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


with open("science_jobs_links.json", "r") as f:
    job_links = json.load(f)


results_dir = r"C:\Users\HP\OneDrive\Desktop\jobyaari-assignements\ASSIGNMENT2\science_jobs_results"
os.makedirs(results_dir, exist_ok=True)

driver = webdriver.Chrome()

for job_key, url in job_links.items():
    driver.get(url)
    time.sleep(2)
    job_data = {}

    try:
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

    except Exception as e:
        job_data['error'] = str(e)


    out_path = os.path.join(results_dir, f"{job_key}.json")
    with open(out_path, "w", encoding="utf-8") as out_f:
        json.dump(job_data, out_f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {out_path}")

driver.quit()