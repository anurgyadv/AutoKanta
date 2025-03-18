import imaplib
import email
import csv
from config import USER_EMAIL, USER_PASSWORD, FROM_EMAIL

# Email credentials
EMAIL = USER_EMAIL
PASSWORD = USER_PASSWORD
IMAP_SERVER = "imap.gmail.com" 

# Connect to IMAP server
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)
mail.select("inbox") 

status, email_ids = mail.search(None, '(FROM "{FROM_EMAIL}")')
email_ids = email_ids[0].split()

# Prepare CSV file
csv_file = "emails.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Date", "From", "Subject", "Body"])  # CSV Headers

    # Loop through emails
    for e_id in email_ids[:10]:  # Limit to first 10 emails (change as needed)
        status, data = mail.fetch(e_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract required fields
        email_date = msg["Date"]
        email_from = msg["From"]
        email_subject = msg["Subject"]

        # Extract email body
        email_body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            email_body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # Write to CSV
        writer.writerow([email_date, email_from, email_subject, email_body])

# Close connection
mail.logout()
print(f"Emails saved to {csv_file}")
