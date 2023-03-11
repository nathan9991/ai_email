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
import time
import subprocess

def get_current_date():
    # Get the source code of the function
    today = date.today()
    d2 = today.strftime("%B %d")
    return d2

while True:
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    email_address = "chat@siegel.io"
    EMAIL_Password = os.environ.get('Chat_Email_App_Password')
    password = EMAIL_Password

    M.login(email_address,password)

    M.select('inbox')

    typ, data = M.search(None, 'SUBJECT "Hey"')
    if not data[0]:
        print("no email")
    else:
        try:    
            typ, data = M.fetch(data[0], '(RFC822)')   
            def get_user_input():
                M = imaplib.IMAP4_SSL('imap.gmail.com')
                email_address = "chat@siegel.io"
                EMAIL_Password = os.environ.get('Chat_Email_App_Password')
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
            
            from langchain.prompts.few_shot import FewShotPromptTemplate
            from langchain.prompts.prompt import PromptTemplate

            examples = [
            {
                "question": "I'd like to book a meeting room tomorrow at 2pm for three hours",
                "answer": 
            """
            Month Day 14:00-17:00
            """
            },
            {
                "question": "tomorrow at 3pm to 5pm",
                "answer": 
            """
            Month Day 15:00-17:00
            """
            },
            {
                "question": "8am to 10am tomorrow",
                "answer":
            """
            Month Day 08:00-10:00
            """
            },
            {
                "question": "in four days at 9am to 10 thirty",
                "answer":
            """
            Month Day 09:00-10:30
            """
            }
            ]
            temp = f"Today is: {current_date}. rewrite this with the current date: "

            llm = OpenAI(model_name='gpt-3.5-turbo-0301', temperature=0)
            example_prompt = PromptTemplate(
                input_variables=["question", "answer"], 
                template="Question: {question}\n{answer}"
            )
        
            prompt = FewShotPromptTemplate(
                examples=examples, 
                example_prompt=example_prompt, 
                input_variables=["input"],
                suffix=f"{temp}" + "{input}?"
            )
            from langchain.chains import LLMChain
            chain = LLMChain(llm=llm, prompt=prompt)

            # Run the chain only specifying the input variable.
            # print(chain.run("tommorrow at 9pm to 11pm"))

            second_prompt = PromptTemplate(
                input_variables=["company_name"],
                template="Write this {company_name}, in the form: Month day 0:00-0:00"
            )
            chain_two = LLMChain(llm=llm, prompt=second_prompt)

            # third_prompt = PromptTemplate(
            #     input_variables=["company_name"],
            #     template="Make sure that: {company_name} only includes Month day 0:00-0:00",
            # )
            # chain_three = LLMChain(llm=llm, prompt=third_prompt)

            from langchain.chains import SimpleSequentialChain
            overall_chain = SimpleSequentialChain(chains=[chain, chain_two], verbose=True)

            # Run the chain specifying only the input variable for the first chain.
            user_input = get_user_input()
            catchphrase = overall_chain.run(user_input)
            end = catchphrase


            import os
            import smtplib
            import imaplib
            import email
            from email.message import EmailMessage

            EMAIL_Password = os.environ.get('Chat_Email_App_Password')

            # Connect to IMAP server and select the inbox
            imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
            imap_server.login('chat@siegel.io', EMAIL_Password)
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
            status, response = imap_server.fetch(latest_message_id, "RFC822")

            # Parse the email message
            raw_email = response[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Create a reply message
            reply_message = EmailMessage()
            reply_message['Subject'] = f"Re: {email_message['Subject']}"
            reply_message['From'] = "chat@siegel.io"
            reply_message['To'] = email_message['From']
            reply_message['In-Reply-To'] = email_message['Message-ID']
            reply_message['References'] = email_message['Message-ID']
            reply_message.set_content(f'did you mean {end}?')
            sender = email_message['From']
            # Send the reply message
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login("chat@siegel.io", EMAIL_Password)
                smtp.send_message(reply_message)


            # Close the IMAP connection
            imap_server.close()
            imap_server.logout()
            
            # subprocess.call(['python3', 'second_script.py', sender])
        
        except imaplib.IMAP4.error as e:
            # handle the FETCH command error
            print("Error fetching email:", e)
            

    time.sleep(30) 