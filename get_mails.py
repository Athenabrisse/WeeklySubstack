import imaplib
import email
import yaml
import logging
from email.header import decode_header
import datetime
import json

IMAP_SERVER = 'imap.gmail.com'  # Replace with your IMAP server
IMAP_PORT = 993  # IMAP SSL port

def load_credentials(filepath='credentials.yaml'):
    try:
        with open(filepath, 'r') as file:
            credentials = yaml.safe_load(file)
            user = credentials['user']
            password = credentials['password']
            return user, password
    except Exception as e:
        logging.error("Failed to load credentials: {}".format(e))
        raise

def connect_to_gmail_imap(user, password):
    # Connect to the server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    # Login to your account
    mail.login(user, password)
    # Select the mailbox you want to check (INBOX by default)
    mail.select('inbox')
    return mail

def get_last_week_emails(mail):
    # Calculate the date for one week ago in the format `DD-Month-YYYY`
    last_week_date = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%d-%b-%Y')

    # Search for emails from the last week
    status, messages = mail.search(None, f'SINCE {last_week_date}')

    # Convert the result to a list of email IDs
    email_ids = messages[0].split()

    # Store emails in a list of dictionaries
    email_data = []

    # Fetch emails
    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse email
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg['Subject'])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else 'utf-8')
                
                from_ = msg.get('From')
                date_ = msg.get('Date')

                # Initialize email body
                body = ""

                # If the email message is multipart
                if msg.is_multipart():
                    for part in msg.walk():
                        # Extract the content type of the email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        # Get the email body
                        try:
                            body_part = part.get_payload(decode=True).decode()
                        except:
                            body_part = None

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = body_part
                            break  # Only store plain text content
                else:
                    # If the email is not multipart
                    body = msg.get_payload(decode=True).decode()
                
                # Add the email data to the list
                email_data.append({
                    "from": from_,
                    "subject": subject,
                    "date": date_,
                    "body": body
                })

    # Close the connection and logout
    mail.close()
    mail.logout()

    return email_data

def save_emails_to_json(email_data, output_filepath='emails.json'):
    with open(output_filepath, 'w') as json_file:
        json.dump(email_data, json_file, indent=4)

def get_email():
    # Load credentials
    user, password = load_credentials('credentials.yaml')
    # Connect to the Gmail IMAP server
    mail = connect_to_gmail_imap(user, password)
    # Get last week's emails
    return get_last_week_emails(mail)
