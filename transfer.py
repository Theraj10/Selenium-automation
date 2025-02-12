import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    , scope)
client = gspread.authorize(creds)

# Open the source Google Sheet (Sheet 1)
source_sheet = client.open_by_url("")  # Replace with actual URL
source_worksheet = source_sheet.get_worksheet(0)  # First sheet

# Open the destination Google Sheet (Sheet 2)
destination_sheet = client.open_by_url("")  # Replace with actual URL
destination_worksheet = destination_sheet.get_worksheet(0)  # First sheet

# Define the new header order
header = ["Date", "Status", "Item", "Company", "Closing Date", "Tender ID", "Tender No"]

# Clear the destination sheet and set the header
destination_worksheet.clear()
destination_worksheet.append_row(header)

# Read data from source sheet (excluding header row)
source_data = source_worksheet.get_all_values()[1:]  # Skip the first row (header)

# Prepare new data format for the destination sheet
rearranged_data = []
for row in source_data:
    if len(row) >= 5:  # Ensure at least 5 columns exist
        new_row = [
            row[3],  # Date → Column 1 in destination
            "",      # Status (No data provided, keeping empty)
            row[0],  # Item → Column 3 in destination
            row[2],  # Company → Column 4 in destination
            row[4],  # Closing Date → Column 5 in destination
            "",      # Tender ID (No data provided, keeping empty)
            row[1]   # Tender No → Column 7 in destination
        ]
        rearranged_data.append(new_row)

# Append the formatted data to destination sheet
if rearranged_data:
    destination_worksheet.append_rows(rearranged_data)

print("Data successfully transferred and reformatted!")

data = destination_worksheet.get_all_values()

header = data[0]
filtered_data = [header] 
# Loop through rows and filter based on Column 3 content
for row in data[1:]:  # Skip header
    if len(row) > 2 :
        item_column = row[2].lower()
        if ("fan" in row[2].lower() or "blower" in row[2].lower()) and ("ceiling" not in item_column and "exhaust" not in item_column):
            filtered_data.append(row)

# Clear sheet and update with filtered data
destination_worksheet.clear()
destination_worksheet.append_rows(filtered_data)