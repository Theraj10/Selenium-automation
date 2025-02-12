from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, TimeoutException
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import requests
# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\\Users\\thera\\Downloads\\gmail-demo-440410-8de4b30c112d.json", scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url('https://docs.google.com/spreadsheets/d/1WOSq5ca1fC9fcNMBQcILSzraSHzsrOuNWw88bhmgu3o/edit?gid=0#gid=0')  # Replace with your Google Sheet URL
worksheet = spreadsheet.get_worksheet(0)  # Select the first sheet


# Launch Browser
driver = webdriver.Chrome()
driver.get("https://sailtenders.co.in/Home/AdvancedSearch")  # Replace with actual URL

# Click the Dropdown to Open It
dropdown = driver.find_element(By.XPATH, "//*[@id='ddlUnit_chosen']/a")  # Adjusting to target the clickable part
dropdown.click()
time.sleep(1)  # Allow options to load

# Define scroll pause time
scroll_pause_time = 2  # Time to wait for loading content

# Create a list to store options and avoid duplicates
processed_options = []

while True:
    try:
        # Find all options in the dropdown
        options = driver.find_elements(By.XPATH, "//*[@class='chosen-results']/li")  # XPath for options

        for index, option in enumerate(options):
            option_text = option.text

            # Check if the option is already processed or should be ignored
            if option_text not in processed_options and option_text not in ["All", "Corporate Office", "SAIL Safety Organisation (SSO)", "Centre for Engineering & Technology (CET)", "Management Training Institute (MTI)"]:
                # Click on the option
                option.click()
                time.sleep(1)  # Wait for the option to load

                # Locate and click the search button
                search_button = driver.find_element(By.ID, "btnTendSrch")  # Locate the search button by ID
                search_button.click()
                time.sleep(10)  # Wait for results to load

                # Click on the dropdown to select the number of records to show
                records_dropdown = driver.find_element(By.XPATH, "//*[@id='tblTendet_length']/label/select")  # Locate the dropdown
                records_dropdown.click()
                time.sleep(1)  # Wait for options to load

                # Select the "All" option
                all_option = driver.find_element(By.XPATH, "//*[@id='tblTendet_length']/label/select/option[text()='All']")
                
                # Retry clicking on the "All" option if intercepted
                retries = 3
                while retries > 0:
                    try:
                        all_option.click()
                        break  # Exit loop if click is successful
                    except ElementClickInterceptedException:
                        time.sleep(1)  # Wait a bit before retrying
                        retries -= 1
                
                time.sleep(5)  # Wait for all records to load

                # Get the table data
                table = driver.find_element(By.ID, "tblTendet")
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Prepare data for Google Sheets
                data = []
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_data = [cell.text for cell in cells]
                    if row_data:  # Avoid empty rows
                        data.append(row_data)

                # Update Google Sheet in batches
                if data:
                    try:
                        worksheet.append_rows(data)  # Append all rows at once
                        print(f"Successfully added {len(data)} rows to Google Sheets.")
                        time.sleep(2)  # Delay to avoid quota issues
                    except gspread.exceptions.APIError as e:
                        print(f"Google Sheets API Error: {e}")
                        print("Waiting 60 seconds before retrying...")
                        time.sleep(60)  # Wait and retry
                        worksheet.append_rows(data)  # Retry appending rows

                # Add the option to processed list
                processed_options.append(option_text)

                # Re-open the dropdown to select the next option
                dropdown = driver.find_element(By.XPATH, "//*[@id='ddlUnit_chosen']/a")
                dropdown.click()
                time.sleep(1)  # Allow options to load
                break  # Break the for loop to re-evaluate options

    except (StaleElementReferenceException, TimeoutException) as e:
        print(f"Exception caught: {e}. Trying to re-find elements.")
        continue  # Retry finding elements in the next iteration

    # Scroll down to the bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # Wait for new content to load
    time.sleep(scroll_pause_time)

    # Check for new content after scrolling
    new_options = driver.find_elements(By.XPATH, "//*[@class='chosen-results']/li")
    if len(new_options) == len(options):  # If no new options found, break the loop
        break

# Clean up and close the browser
driver.quit()
spreadsheet = client.open_by_url(
    'https://docs.google.com/spreadsheets/d/1WOSq5ca1fC9fcNMBQcILSzraSHzsrOuNWw88bhmgu3o/edit?gid=0#gid=0')

# Get the Google Sheet ID from the URL
spreadsheet_id = spreadsheet.id

# Define the export URL for CSV format
export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv"

# Send GET request to download CSV
response = requests.get(export_url)

# Save it as a CSV file locally
csv_filename = "output2.csv"
with open(csv_filename, "wb") as file:
    file.write(response.content)

print(f"Google Sheet successfully converted and saved as '{csv_filename}'")

