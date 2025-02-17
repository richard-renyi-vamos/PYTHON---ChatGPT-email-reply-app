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
