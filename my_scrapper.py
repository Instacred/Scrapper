import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime

# -------------------------- PRE-REQUISITES -----------------------
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Path to your ChromeDriver
chromedriver_path = 'C:/Users/LENOVO/Pictures/chromedriver-win64/chromedriver.exe'  # Replace with your actual path
print(f"Using ChromeDriver path: {chromedriver_path}")

# Set up the driver
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the website
url = "https://www.betway.co.zm/lobby/Casino/featured/Aviator/"
print(f"✈️ Navigating to {url}")
driver.get(url)

# --------------------------- FUNCTIONS ---------------------------------

def login():
    print("🔃 logging in....")

    username = '978934162'
    password = 'Instacred'

    try:
        username_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'login-mobile'))
        )
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'login-password'))
        )
        login_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@class,"whitespace-nowrap") and contains(@class,"bg-identity") and contains(@class,"w-full")]'))
        )

        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        print("✅ Logged in successfully!")

    except Exception as e:
        print(f"unable to login{e}")
        time.sleep(30)
        driver.quit()

def get_total_bets():
    try:
        # Find the specific parent element
        parent_element = driver.find_element(By.XPATH, '//div[contains(@class, "all-bets-block") and contains(@class, "d-flex") and contains(@class, "justify-content-between") and contains(@class, "align-items-center") and contains(@class, "px-2") and contains(@class, "pb-1")]')

        # Find the value element within the parent element
        value_element = parent_element.find_element(By.XPATH, './/div[@class="text-uppercase"]/following-sibling::div')

        return value_element.text.strip()
    except Exception as e:
        print(f"❌ Failed to retrieve total bets value: {e}")
        return None


def get_multiplier_data():
    # Get all multiplier elements
    elements = driver.find_elements(By.XPATH, '//app-bubble-multiplier[contains(@class, "payout") and contains(@class, "ng-star-inserted")]')
    multipliers = [element.text for element in elements]
    return multipliers


def save_to_text(data, filename='multipliers.txt'):
    with open(filename, 'a') as file:
        file.write(f"{data}\n")

def save_to_excel(data, filename='multipliers.xlsx'):
    df = pd.DataFrame(data, columns=['Value', 'Timestamp', 'Total Bets'])
    try:
        existing_df = pd.read_excel(filename)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_excel(filename, index=False)

# ------------------------- MAIN --------------------------

#login function
login()

print("⏱️ Loading...")
time.sleep(5)

try:
    iframe = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'iframe'))
    )
    driver.switch_to.frame(iframe)
    print("🛞 Switched to iframe!")

except Exception as e:
    print("❌No iframe found.")

# Initialize set to store seen multipliers
initial_multipliers = get_multiplier_data()
seen_multipliers = list(initial_multipliers[:1])

count = 0

time.sleep(5)

while True:
    try:
        total_bets = get_total_bets()
        new_multipliers = get_multiplier_data()
        new_multipliers = new_multipliers[:1]
        new_values = [value for value in new_multipliers if value not in seen_multipliers]

        #print(new_multipliers)
        #print(seen_multipliers)

        if new_values:
            if count == 0:
                print("Initial multipliers found and ignored:", new_values)
                seen_multipliers = (seen_multipliers + new_values)[-1:]
            else:
                print(f"✅ {count} = {new_values}")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = [(value.rstrip('x'), timestamp, total_bets) for value in new_values]
                save_to_excel(data)  # Save the new multipliers
                save_to_text(data)
                seen_multipliers = (seen_multipliers + new_values)[-1:]
            count += 1


    except StaleElementReferenceException:
        print("StaleElementReferenceException encountered. Re-locating elements.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        break

driver.quit()
