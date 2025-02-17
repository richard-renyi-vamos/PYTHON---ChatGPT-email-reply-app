CHATGPT CONVERSATION

***********

You said:
create a PYTHON code that uses OPEN AI API to reply automatically for emails
ChatGPT said:
Sure! Here's a simple Python script that uses the OpenAI API to automatically reply to emails. It assumes you're using an email service that can be accessed through IMAP (for reading emails) and SMTP (for sending emails). This script uses the openai Python package and imaplib and smtplib to interact with your email.

Before you run this, make sure to install the necessary libraries using:

bash
Copy
Edit
pip install openai
pip install secure-smtplib
You'll also need to replace placeholders with your actual API key and email details.

Python Code:
python
Copy
Edit
import openai
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email
from email.header import decode_header

# Set your OpenAI API key here
openai.api_key = 'your-openai-api-key'

# Email configuration
IMAP_SERVER = 'imap.gmail.com'  # Change this based on your email provider
SMTP_SERVER = 'smtp.gmail.com'  # Change this based on your email provider
EMAIL_ACCOUNT = 'your-email@gmail.com'  # Your email
EMAIL_PASSWORD = 'your-email-password'  # Your email password (or app-specific password)
REPLY_SUBJECT = "Re: Automatic Reply"

# Function to read unread emails
def read_unread_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    mail.select("inbox")
    result, data = mail.search(None, 'UNSEEN')  # Get unread emails
    if result == "OK":
        for num in data[0].split():
            result, msg_data = mail.fetch(num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    from_ = msg.get("From")
                    print(f"From: {from_}")
                    print(f"Subject: {subject}")
                    body = get_body(msg)
                    return from_, subject, body
    mail.logout()

# Function to extract the email body
def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

# Function to generate a reply with OpenAI API
def generate_reply(body):
    prompt = f"Reply to this email: {body}\n\nYour response:"
    response = openai.Completion.create(
        model="text-davinci-003",  # You can change the model
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Function to send an email reply
def send_email_reply(to_email, subject, reply_body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ACCOUNT
    msg['To'] = to_email
    msg['Subject'] = REPLY_SUBJECT
    msg.attach(MIMEText(reply_body, 'plain'))
    
    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ACCOUNT, to_email, msg.as_string())

# Main function to execute
def auto_reply():
    from_, subject, body = read_unread_emails()
    if body:
        print("Generating reply...")
        reply = generate_reply(body)
        print(f"Reply: {reply}")
        send_email_reply(from_, subject, reply)
        print("Reply sent!")

if __name__ == "__main__":
    auto_reply()
Explanation:
Reading Emails: The read_unread_emails function connects to your email server using IMAP to fetch unread emails.
Generating Replies: The generate_reply function uses OpenAI's GPT model to generate a response based on the email's content.
Sending Replies: The send_email_reply function sends the generated reply using the SMTP server.
Automated Process: The auto_reply function reads an email, generates a reply, and sends it back automatically.
Important Notes:
Make sure to enable "Less secure apps" in your email settings or use app-specific passwords if using Gmail or similar services.
If you're using Gmail, you may need to set up an app password if 2FA is enabled.
This script is designed for a basic use case. You may need to add error handling and further optimizations depending on your email provider and use case.
Feel free to modify and enhance the functionality as per your needs! 😄📧🤖







You said:
add a GUI for settings
ChatGPT said:
Sure! Here's a Python script that includes a GUI for settings using tkinter. The GUI allows you to enter email credentials, OpenAI API key, and configure the SMTP/IMAP settings.

🔹 Features:

GUI with input fields for email settings and OpenAI API key
Button to save settings (saved locally in a .json file)
Button to start auto-reply
Logs to display email processing in real-time
📌 Install dependencies:
bash
Copy
Edit
pip install openai
pip install secure-smtplib
📜 Full Python Script:
python
Copy
Edit
import openai
import imaplib
import smtplib
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import email
from email.header import decode_header

# Settings file
SETTINGS_FILE = "email_settings.json"

# Load settings from JSON
def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save settings to JSON
def save_settings():
    settings = {
        "email": email_entry.get(),
        "password": password_entry.get(),
        "imap_server": imap_entry.get(),
        "smtp_server": smtp_entry.get(),
        "openai_api_key": api_key_entry.get()
    }
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)
    messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")

# Read unread emails
def read_unread_emails():
    settings = load_settings()
    if not settings:
        log_message("⚠️ No settings found. Please save your settings first.")
        return None, None, None
    
    try:
        mail = imaplib.IMAP4_SSL(settings["imap_server"])
        mail.login(settings["email"], settings["password"])
        mail.select("inbox")
        result, data = mail.search(None, 'UNSEEN')  # Get unread emails

        if result == "OK":
            for num in data[0].split():
                result, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')
                        from_ = msg.get("From")
                        body = get_body(msg)
                        return from_, subject, body
        mail.logout()
    except Exception as e:
        log_message(f"Error reading emails: {e}")
    return None, None, None

# Extract email body
def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

# Generate a reply using OpenAI API
def generate_reply(body):
    settings = load_settings()
    openai.api_key = settings.get("openai_api_key", "")

    if not openai.api_key:
        log_message("⚠️ OpenAI API key is missing.")
        return ""

    prompt = f"Reply to this email: {body}\n\nYour response:"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Send an email reply
def send_email_reply(to_email, subject, reply_body):
    settings = load_settings()
    try:
        msg = MIMEMultipart()
        msg['From'] = settings["email"]
        msg['To'] = to_email
        msg['Subject'] = f"Re: {subject}"
        msg.attach(MIMEText(reply_body, 'plain'))

        with smtplib.SMTP_SSL(settings["smtp_server"], 465) as server:
            server.login(settings["email"], settings["password"])
            server.sendmail(settings["email"], to_email, msg.as_string())

        log_message(f"✅ Reply sent to {to_email}")
    except Exception as e:
        log_message(f"❌ Error sending email: {e}")

# Process an email and reply
def auto_reply():
    from_, subject, body = read_unread_emails()
    if body:
        log_message(f"📧 Email from: {from_}\n📌 Subject: {subject}")
        reply = generate_reply(body)
        log_message(f"🤖 AI-generated reply:\n{reply}")
        send_email_reply(from_, subject, reply)
    else:
        log_message("📭 No unread emails found.")

# Function to log messages in the UI
def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + "\n")
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

# Create GUI
root = tk.Tk()
root.title("Auto Email Reply Bot")
root.geometry("500x550")

# Labels and Entry Fields
tk.Label(root, text="Email Address:").pack()
email_entry = tk.Entry(root, width=40)
email_entry.pack()

tk.Label(root, text="Email Password:").pack()
password_entry = tk.Entry(root, width=40, show="*")
password_entry.pack()

tk.Label(root, text="IMAP Server:").pack()
imap_entry = tk.Entry(root, width=40)
imap_entry.pack()

tk.Label(root, text="SMTP Server:").pack()
smtp_entry = tk.Entry(root, width=40)
smtp_entry.pack()

tk.Label(root, text="OpenAI API Key:").pack()
api_key_entry = tk.Entry(root, width=40, show="*")
api_key_entry.pack()

# Load saved settings if available
saved_settings = load_settings()
email_entry.insert(0, saved_settings.get("email", ""))
password_entry.insert(0, saved_settings.get("password", ""))
imap_entry.insert(0, saved_settings.get("imap_server", "imap.gmail.com"))
smtp_entry.insert(0, saved_settings.get("smtp_server", "smtp.gmail.com"))
api_key_entry.insert(0, saved_settings.get("openai_api_key", ""))

# Buttons
save_button = tk.Button(root, text="Save Settings", command=save_settings)
save_button.pack(pady=5)

start_button = tk.Button(root, text="Start Auto-Reply", command=auto_reply)
start_button.pack(pady=5)

# Log Display
log_text = scrolledtext.ScrolledText(root, width=60, height=15, state=tk.DISABLED)
log_text.pack(pady=10)

# Run GUI
root.mainloop()
🎨 How the GUI Works:
Enter Email Credentials & OpenAI API Key
Save Settings (stored in email_settings.json)
Click 'Start Auto-Reply'
The bot fetches unread emails, generates AI replies, and sends them.
Logs are displayed in the window.
🔥 Why This is Awesome?
✅ User-friendly GUI 🎨
✅ Saves settings locally for convenience 📂
✅ Logs real-time email processing 💬
✅ Secured with app passwords support 🔐

Now, just enter your email details, save settings, and start auto-replying to emails like a pro! 🚀📧🤖
