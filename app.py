from flask import Flask, render_template, request
import os
import smtplib
from datetime import date
from langchain import OpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.chains import LLMChain
from flask_httpauth import HTTPBasicAuth
from urllib.parse import parse_qs
auth = HTTPBasicAuth()

MAILERTOGO_SMTP_HOST = os.environ.get('MAILERTOGO_SMTP_HOST')
MAILERTOGO_SMTP_PASSWORD = os.environ.get('MAILERTOGO_SMTP_PASSWORD')
MAILERTOGO_SMTP_USER = os.environ.get('MAILERTOGO_SMTP_USER')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@auth.verify_password
def verify_password(username, password):
    return username == "Allow"
@app.route('/603c08641195eca0e603b1f3acabb', methods=['POST'])

def parse_email():
    print("Parsing email...")
    params = parse_qs(request.data)
    email = params["email"][0]
    subject = params["subject"][0]
    message = params["message"][0]
        # Get the request data
    data = request.data
    params = parse_qs(data.decode('utf-8'))

    # Check if the email key is present
    if 'email' not in params:
        return 'Email not found in request data'

    email = params['email'][0]
    subject = params['subject'][0]
    message = params['message'][0]
    # Parse the data to extract the email

    # Return the email
    return email




@app.route('/send_email', methods=['POST'])
@auth.login_required
def send_email():
    

    def get_current_date():
        # Get the source code of the function
        today = date.today()
        d2 = today.strftime("%B %d")
        return d2


    # Get form data
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # Set up the connection to the SMTP server
    smtp_server = MAILERTOGO_SMTP_HOST
    smtp_port = 587
    smtp_username = MAILERTOGO_SMTP_USER
    smtp_password = MAILERTOGO_SMTP_PASSWORD
    smtp_connection = smtplib.SMTP(smtp_server, smtp_port)
    smtp_connection.connect(smtp_server, smtp_port)
    smtp_connection.starttls()
    
    try:
        smtp_connection.login(smtp_username, smtp_password)
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP login error: {e}")


    current_date = get_current_date()
    

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
    user_input = message
    catchphrase = overall_chain.run(user_input)


    # Compose the email
    from_address = 'chat@mtg.chat.siegel.io'
    to_address = email
    subject = subject
    body = catchphrase
    message = f'To: {to_address}\r\nFrom: {from_address}\r\nSubject: {subject}\r\n\r\n{body}'

    try:
        # Send the email
        smtp_connection.sendmail(from_address, to_address, message)
        print("Email sent successfully!")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

    # Close the SMTP connection
    smtp_connection.quit()
    
    return "Email sent successfully!"


if __name__ == '__main__':
    app.run()

