import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import openai

# OpenAI API key
openai.api_key = 'your_openai_api_key'

# Email credentials
EMAIL = "your_email@example.com"
PASSWORD = "your_email_password"
IMAP_SERVER = "imap.your_email_provider.com"  # Example for Gmail: "imap.gmail.com"
SMTP_SERVER = "smtp.your_email_provider.com"  # Example for Gmail: "smtp.gmail.com"

# Read unread emails
def read_unread_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    # Search for all unread emails
    status, messages = mail.search(None, '(UNSEEN)')
    
    unread_msg_nums = messages[0].split()
    emails = []

    for e_id in unread_msg_nums:
        status, msg_data = mail.fetch(e_id, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = msg['subject']
                from_ = msg['from']
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode()
                else:
                    body = msg.get_payload(decode=True).decode()

                emails.append({
                    'from': from_,
                    'subject': subject,
                    'body': body
                })

    mail.logout()
    return emails

# Generate a reply using ChatGPT
def generate_reply(prompt):
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=150
    )
    return response.choices[0].text.strip()

# Send reply email
def send_reply(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg['Subject'] = f"Re: {subject}"

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, to_email, msg.as_string())
    server.quit()

# Main function to handle the email reading and replying
def main():
    unread_emails = read_unread_emails()

    for email_data in unread_emails:
        prompt = f"Reply to the following email:\n\nSubject: {email_data['subject']}\nFrom: {email_data['from']}\nEmail Body: {email_data['body']}\n\nReply with a polite response."
        reply = generate_reply(prompt)
        
        # Send the generated reply
        send_reply(email_data['from'], email_data['subject'], reply)
        print(f"Replied to: {email_data['from']}")

if __name__ == "__main__":
    main()
