from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from bs4 import BeautifulSoup
# Set up Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://hajj.gov.bd/agency-profile")
driver.implicitly_wait(10)

data = []

# Loop through all pagination indices from 1 to 39
for idx in range(0, 39):
    try:
        # Click the page link
        page_link = driver.find_element(By.CSS_SELECTOR, f'a[data-dt-idx="8"]')
        driver.execute_script("arguments[0].click();", page_link)

        # Wait for table to update
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#agencyListTable tbody tr"))
        )

        # Extract table rows


        rows = driver.find_elements(By.CSS_SELECTOR, "#agencyListTable tbody tr")
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            row_data = []
            for i, col in enumerate(cols):
                if i == len(cols) - 1:  # last column
                    # Look for the <a> tag and get href
                    try:
                        link = col.find_element(By.TAG_NAME, "a").get_attribute("href")
                        row_data.append(link.strip())
                    except:
                        row_data.append("")  # if no link present
                else:
                    # Get raw HTML for normal columns
                    html_content = col.get_attribute("innerHTML")
                    soup = BeautifulSoup(html_content, "html.parser")
                    for br in soup.find_all("br"):
                        br.replace_with("\n")
                    parts = [part.strip() for part in soup.get_text().split("\n") if part.strip()]
                    row_data.extend(parts)

            if row_data:
                data.append(row_data)



        time.sleep(0.5)  # small delay to avoid issues

    except Exception as e:
        print(f"Error on page {idx}: {e}")

# Create DataFrame
df = pd.DataFrame(data)

# Optional: Add headers if you know them
df.columns = ["SL", "H/L", "Agency", "Email", "Address", "Contact Info","Pre Reg. Pilgrim",	"Own Reg. Pilgrim","Details"]
# Save to Excel
df.to_excel("hajj_agencies_full5.xlsx", index=False)

driver.quit()
print("Data saved to hajj_agencies_full5.xlsx")
