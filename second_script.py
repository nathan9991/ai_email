import imaplib
import email
import os
import time
import sys
time.sleep(30) 
# Set up the email parameters
imap_server = 'imap.gmail.com'
imap_port = 993
email_address = 'chat@siegel.io'
EMAIL_Password = os.environ.get('Chat_Email_App_Password')
expected_subject = 'Re: Hey'
sender = sys.argv[1]  # get sender email address passed in as argument

expected_subject = 'Re: Hey'
expected_sender = sender
print(expected_sender)

# Set up the IMAP server and login credentials
mail = imaplib.IMAP4_SSL(imap_server, imap_port)
mail.login(email_address, EMAIL_Password)

while True:
    # Select the inbox folder and search for emails with a specific subject line
    mail.select('inbox')
    typ, data = mail.search(None, f'SUBJECT "{expected_subject}" FROM "{expected_sender}"')

    # If a response email is found, retrieve its content and process it
    if data[0]:
        mail_ids = data[0].split()
        for i in mail_ids:
            typ, data = mail.fetch(i, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract the content of the email and process it as needed
            content = email_message.get_payload()
            print(content)

        # Mark the response email as read
        mail.store(mail_ids, '+FLAGS', '\\Seen')

    # Wait for 10 seconds before checking for new emails again
    time.sleep(10)

# Close the IMAP connection
mail.close()
mail.logout()
