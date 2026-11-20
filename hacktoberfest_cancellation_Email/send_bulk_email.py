#!/usr/bin/env python3
"""Send personalized SSU-NIAT Hacktoberfest registration emails.

CSV format:
Student Name,Email ID

By default the script only previews the recipient list.
Use --send only after reviewing the list.
"""

import argparse
import csv
import os
import smtplib
import ssl
import sys
import time
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SUBJECT = "Update on Your Hacktoberfest Registration – SSU-NIAT Cuttack"

EMAIL_TEMPLATE = """Dear {name},

Thank you for your interest in participating in the Hacktoberfest event at SSU-NIAT Cuttack.

Due to the event reaching its maximum participant capacity, we regret to inform you that your registration has been cancelled. We appreciate your enthusiasm and interest in the event.

We encourage you to stay connected for future workshops and events, and we look forward to your participation in upcoming opportunities.

Thank you for your understanding.

Regards,
SSU-NIAT Team
"""


def load_recipients(csv_path):
    recipients = []
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {"Student Name", "Email ID"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(
                'CSV headers must be exactly: "Student Name" and "Email ID".'
            )

        for row_number, row in enumerate(reader, start=2):
            name = (row.get("Student Name") or "").strip()
            email = (row.get("Email ID") or "").strip()
            if not name and not email:
                continue
            if not name or not email:
                print(f"Skipping row {row_number}: name or email is blank.")
                continue
            if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
                print(f"Skipping row {row_number}: email looks invalid: {email}")
                continue
            recipients.append((name, email))
    return recipients


def main():
    parser = argparse.ArgumentParser(description="SSU-NIAT Hacktoberfest bulk email sender")
    parser.add_argument("--csv", default="students.csv", help="CSV file path (default: students.csv)")
    parser.add_argument("--send", action="store_true", help="Actually send emails; without this, preview only")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between emails in seconds (default: 1)")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.is_file():
        print(f"ERROR: Cannot find CSV file: {csv_path.resolve()}")
        sys.exit(1)

    try:
        recipients = load_recipients(csv_path)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}")
        sys.exit(1)

    if not recipients:
        print("No valid recipients found. Please check students.csv.")
        sys.exit(1)

    print(f"\nFound {len(recipients)} recipient(s):")
    for index, (name, email) in enumerate(recipients, start=1):
        print(f"{index:>2}. {name} <{email}>")

    if not args.send:
        print("\nPREVIEW ONLY — no emails were sent.")
        print("If the list is correct, configure Gmail and run: python send_bulk_email.py --send")
        return

    sender_email = os.getenv("GMAIL_ADDRESS", "").strip()
    app_password = os.getenv("GMAIL_APP_PASSWORD", "").replace(" ", "").strip()
    sender_name = os.getenv("SENDER_NAME", "SSU-NIAT Team").strip() or "SSU-NIAT Team"

    if not sender_email or not app_password:
        print(
            "\nERROR: Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD environment variables "
            "in this same terminal window before sending."
        )
        sys.exit(1)

    sent_count = 0
    failed_count = 0
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(sender_email, app_password)
            for name, email in recipients:
                message = EmailMessage()
                message["From"] = formataddr((sender_name, sender_email))
                message["To"] = email
                message["Subject"] = SUBJECT
                message.set_content(EMAIL_TEMPLATE.format(name=name))

                try:
                    server.send_message(message)
                    sent_count += 1
                    print(f"SENT: {name} <{email}>")
                except Exception as error:
                    failed_count += 1
                    print(f"FAILED: {name} <{email}> — {error}")

                if args.delay > 0:
                    time.sleep(args.delay)
    except smtplib.SMTPAuthenticationError:
        print(
            "Gmail authentication failed. Check the sending address and App Password. "
            "Use a Google App Password, not your normal Gmail password."
        )
        sys.exit(1)
    except Exception as error:
        print(f"SMTP ERROR: {error}")
        sys.exit(1)

    print(f"\nFinished. Sent: {sent_count}; Failed: {failed_count}.")


if __name__ == "__main__":
    main()
