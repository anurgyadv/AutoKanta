import os
import csv
import email
import re
from email import policy
from email.parser import BytesParser

# Directory containing .eml files
ATTACHMENTS_DIR = "../Attachments/"
OUTPUT_CSV = "extracted_data.csv"

def extract_data_from_eml(file_path):
    """Extract structured data from a .eml file."""
    
    # Open and parse the email file
    with open(file_path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    
    # Get the email body
    if msg.is_multipart():
        body = "".join(part.get_payload(decode=True).decode(errors="ignore") for part in msg.iter_parts() if part.get_content_type() == "text/plain")
    else:
        body = msg.get_payload(decode=True).decode(errors="ignore")

    # Regex pattern to extract required fields
    pattern = re.compile(
        r"S\.N:\s*(\d+).*?"
        r"(\d{2}\.\d{2}\.\d{4},\d{2}:\d{2}).*?"
        r"V\.N:\s*([A-Z0-9]+).*?"
        r"V\.T:\s*([A-Z]+).*?"
        r"PRTY:\s*(.*?)\n.*?"
        r"MATR:\s*([A-Z\s]+).*?"
        r"CHG1:\s*(\d+).*?"
        r"G/W:\s*(\d+).*?"
        r"T/W:\s*(\d+).*?"
        r"N/W:\s*(\d+)",
        re.DOTALL
    )

    # Extract data
    match = pattern.search(body)
    if match:
        return {
            "S.N": match.group(1),
            "Date & Time": match.group(2),
            "Vehicle Number (V.N)": match.group(3),
            "Vehicle Type (V.T)": match.group(4),
            "Party (PRTY)": match.group(5).strip() if match.group(5).strip() else "N/A",
            "Material (MATR)": match.group(6).strip(),
            "Charge (CHG1)": match.group(7),
            "Gross Weight (G/W)": match.group(8),
            "Tare Weight (T/W)": match.group(9),
            "Net Weight (N/W)": match.group(10),
        }
    return None

def process_eml_files():
    """Process all .eml files and handle duplicate S.N values."""
    
    extracted_data = []
    seen_entries = {}  # Dictionary to track best entries per S.N

    # Loop through all .eml files in the directory
    for file_name in os.listdir(ATTACHMENTS_DIR):
        if file_name.endswith(".eml"):
            file_path = os.path.join(ATTACHMENTS_DIR, file_name)
            data = extract_data_from_eml(file_path)

            if data:
                sn = data["S.N"]

                # Check if the same S.N already exists
                if sn in seen_entries:
                    existing = seen_entries[sn]

                    # Keep the row with complete T/W, G/W, and N/W values
                    if all(data[k] for k in ["T/W", "G/W", "N/W"]):
                        seen_entries[sn] = data  # Replace with the complete one
                else:
                    seen_entries[sn] = data

    # Convert the dictionary values to a list
    extracted_data = list(seen_entries.values())

    # Save to CSV
    save_to_csv(extracted_data)

def save_to_csv(data):
    """Save extracted data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    fieldnames = ["S.N", "Date & Time", "Vehicle Number (V.N)", "Vehicle Type (V.T)", "Party (PRTY)", "Material (MATR)", "Charge (CHG1)", "Gross Weight (G/W)", "Tare Weight (T/W)", "Net Weight (N/W)"]

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print(f"Extracted data saved to {OUTPUT_CSV}")

# Run the script
process_eml_files()
