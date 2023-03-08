from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
import re
from datetime import date
from langchain.prompts import BasePromptTemplate
from pydantic import BaseModel, validator
import email
from langchain.chains import PALChain
from langchain import OpenAI
import os
import smtplib
import imaplib
from email.message import EmailMessage
import inspect

def get_current_date():
    # Get the source code of the function
    today = date.today()
    d2 = today.strftime("%B %d")
    return d2


def get_user_input():
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    email_address = "liam@siegel.io"
    EMAIL_Password = os.environ.get('Email_App_Password')
    password = EMAIL_Password

    M.login(email_address,password)

    M.select('inbox')

    typ, data = M.search(None, 'SUBJECT "Hey"')

    email_id = data[0]

    result , email_data = M.fetch(email_id, '(RFC822)')

    raw_email = email_data[0][1]

    raw_email_string = raw_email.decode('utf-8')

    email_message = email.message_from_string(raw_email_string)

    for part in email_message.walk():
        
        if part.get_content_type() == 'text/plain':
            body = part.get_payload(decode=True)
            text_email = body

    # bytes object
    b_name = text_email

    # convert to string and remove b''
    name = b_name.decode()
    name = re.sub("^b'|'$", '', name)

    print(name)
    
    return name


current_date = get_current_date()
temp = f"Today is: {current_date}. Reword this to have in account for the current date: "

llm = OpenAI(model_name='gpt-3.5-turbo-0301', temperature=0)
prompt = PromptTemplate(
    input_variables=["product"],
    template = f"{temp}" + "{product}?",
)

from langchain.chains import LLMChain
chain = LLMChain(llm=llm, prompt=prompt)

# Run the chain only specifying the input variable.
# print(chain.run("tommorrow at 9pm to 11pm"))

second_prompt = PromptTemplate(
    input_variables=["company_name"],
    template="Write this {company_name}, in the form: (Month day 0:00-0:00)",
)
chain_two = LLMChain(llm=llm, prompt=second_prompt)

third_prompt = PromptTemplate(
    input_variables=["company_name"],
    template="Make sure that: {company_name} only includes (Month day 0:00-0:00)",
)
chain_four = LLMChain(llm=llm, prompt=third_prompt)

fourth_prompt = PromptTemplate(
    input_variables=["company_name"],
    template="Make sure there are no commas or periods in: {company_name}",
)
chain_three = LLMChain(llm=llm, prompt=fourth_prompt)

from langchain.chains import SimpleSequentialChain
overall_chain = SimpleSequentialChain(chains=[chain, chain_two, chain_three, chain_four], verbose=True)

# Run the chain specifying only the input variable for the first chain.
user_input = get_user_input()
catchphrase = overall_chain.run(user_input)
end = catchphrase


import os
import smtplib
import imaplib
import email
from email.message import EmailMessage

EMAIL_Password = os.environ.get('Email_App_Password')

# Connect to IMAP server and select the inbox
imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
imap_server.login('liam@siegel.io', EMAIL_Password)
imap_server.select('inbox')

# Search for emails with the subject "Hey"
status, response = imap_server.search(None, 'SUBJECT "Hey"')

# Get the message IDs of the matching emails
message_ids = response[0].split()

if not message_ids:
    print("No matching emails found.")
    exit()

# Select the last matching email (most recent)
latest_message_id = message_ids[-1]
status, response = imap_server.fetch(latest_message_id, "(RFC822)")

# Parse the email message
raw_email = response[0][1]
email_message = email.message_from_bytes(raw_email)

# Create a reply message
reply_message = EmailMessage()
reply_message['Subject'] = f"Re: {email_message['Subject']}"
reply_message['From'] = "Liam@siegel.io"
reply_message['To'] = email_message['From']
reply_message['In-Reply-To'] = email_message['Message-ID']
reply_message['References'] = email_message['Message-ID']
reply_message.set_content(f'did you mean {end}?')

# Send the reply message
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login("liam@siegel.io", EMAIL_Password)
    smtp.send_message(reply_message)

# Close the IMAP connection
imap_server.close()
imap_server.logout()
