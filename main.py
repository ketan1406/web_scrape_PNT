import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setting up Selenium WebDriver
# Updated to the driver available in the same directory
driver_path = './chromedriver.exe'
# The use of Selenium service for easier management
service = Service(driver_path)
driver = webdriver.Chrome(service=service)  # Webdriver init

# Function to fetch project details from the dialog box


def fetch_project_details():
    details = {}
    # Get Name of the Project owner
    try:
        details['Name'] = driver.find_element(
            By.XPATH, '//*[@id="project-menu-html"]/div[2]/div[1]/div/table/tbody/tr[1]/td[2]').text.strip()
    except Exception as e:
        print(f"Error fetching Name: {e}")
        details['Name'] = 'N/A'
    # Get GSTIN of the Project owner
    try:
        gstin_element = driver.find_element(
            By.XPATH, '//*[text()="GSTIN No."]/following-sibling::td/span')
        gstin_text = gstin_element.text.strip()
        details['GSTIN No'] = gstin_text if gstin_text and gstin_text != '-NA-' else 'N/A'
    except Exception as e:
        print(f"Error fetching GSTIN No.: {e}")
        details['GSTIN No'] = 'N/A'
    # Get PAN No. of the Project owner
    try:
        pan_element = driver.find_element(
            By.XPATH, '//*[text()="PAN No."]/following-sibling::td/span')
        details['PAN No'] = pan_element.text.strip()
    except Exception as e:
        print(f"Error fetching PAN No.: {e}")
        details['PAN No'] = 'N/A'
    # Get Permanent Address of the Project owner
    try:
        address_element = driver.find_element(
            By.XPATH, '//*[text()="Permanent Address"]/following-sibling::td/span').text.strip()
        details['Permanent Address'] = address_element
    except Exception as e:
        print(f"Error fetching Permanent Address: {e}")
        details['Permanent Address'] = 'N/A'

    return details

# Main function to scrape the project list and details


def scrape_projects():
    base_url = 'https://hprera.nic.in/PublicDashboard'
    driver.get(base_url)

    # Waiting for the Registered Projects section to load
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="reg-Projects"]/div/div')))
        print("Registered Projects section loaded.")
    except Exception as e:
        print(f"Error waiting for Registered Projects section: {e}")
        driver.quit()
        return

    # Locating the Registered Projects cards and get the first 6 project cards
    try:
        project_cards = driver.find_elements(
            By.XPATH, '//*[@id="reg-Projects"]/div/div/div')
        print(f"Found {len(project_cards)} project cards.")
    except Exception as e:
        print(f"Error finding project cards: {e}")
        driver.quit()
        return

    projects = []

    for i, card in enumerate(project_cards[:6], 1):
        try:
            print(f"Clicking project card {i}.")
            link = card.find_element(
                By.XPATH, f'//*[@id="reg-Projects"]/div/div/div[{i}]/div/div/a')
            link.click()  # Click to open the dialog box
            time.sleep(2)  # Wait for the dialog box to open

            project_details = fetch_project_details()
            projects.append(project_details)

            # Closing the dialog box
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="modal-data-display-tab_project_main"]/div/div/div[1]/button/span')))
            close_button.click()
            time.sleep(1)  # Wait for the dialog box to close
        except Exception as e:
            print(f"Error processing project card {i}: {e}")

    # Saving the details to a CSV file
    with open('project_details.csv', 'w', newline='') as csvfile:
        fieldnames = ['Name', 'GSTIN No', 'PAN No', 'Permanent Address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for project in projects:
            writer.writerow(project)

    driver.quit()


if __name__ == '__main__':
    scrape_projects()
