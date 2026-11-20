
import csv
import os
import smtplib
import argparse
import time
from email.message import EmailMessage
from html import escape

# ==========================================
# CONFIGURATION
# ==========================================

CSV_FILE = "students.csv"

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

SUBJECT = (
    "Reminder: Even Semester (2nd Semester) "
    "Fee Payment and NIAT Registration"
)

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


# ==========================================
# EMAIL CONTENT
# ==========================================

def create_email(student_name):

    name = escape(student_name.strip())

    plain_text = f"""Dear {student_name},

This is to inform you that the Even Semester (2nd Semester) fee payment portal is now active.

All fee payment details have been shared with you through your respective Sri Sri University email IDs. Students are advised to check their email and complete the payment process at the earliest.

IMPORTANT DATES:

- Requested Fee Payment Completion Date: 5th January 2027
- NIAT Registration Slot Activation: 10th January 2027
- Official Last Date for Fee Payment: 13th January 2027

To facilitate timely document verification, avoid any discrepancies, and ensure the smooth commencement of the 2nd semester, all students are requested to complete their fee payment by 5th January 2027.

IMPORTANT NOTICE:

Students who do not complete both the fee payment and NIAT registration process before the commencement of 2nd-semester classes may lose access to the Learning Management System (LMS), which could impact their academic activities.

We strongly encourage all students to adhere to the requested timeline and avoid last-minute complications that may affect their academic access and registration process.

For any queries or assistance, please contact the concerned administration team.

Regards,
NIAT
"""

    html_text = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">

        <p>Dear <b>{name}</b>,</p>

        <p>
        This is to inform you that the
        <b>Even Semester (2nd Semester) fee payment portal is now active.</b>
        </p>

        <p>
        All fee payment details have been shared with you through your
        respective <b>Sri Sri University email IDs.</b>
        Students are advised to check their email and complete the
        payment process at the earliest.
        </p>

        <p><b>Important Dates:</b></p>

        <ul>
            <li><b>Requested Fee Payment Completion Date:</b> 5th January 2027</li>
            <li><b>NIAT Registration Slot Activation:</b> 10th January 2027</li>
            <li><b>Official Last Date for Fee Payment:</b> 13th January 2027</li>
        </ul>

        <p>
        To facilitate timely document verification, avoid any discrepancies,
        and ensure the smooth commencement of the 2nd semester,
        all students are requested to complete their fee payment by
        <b>5th January 2027.</b>
        </p>

        <p><b>Important Notice:</b><br>
        Students who do not complete both the fee payment and NIAT
        registration process before the commencement of 2nd-semester
        classes may lose access to the Learning Management System (LMS),
        which could impact their academic activities.
        </p>

        <p>
        We strongly encourage all students to adhere to the requested
        timeline and avoid last-minute complications that may affect
        their academic access and registration process.
        </p>

        <p>
        For any queries or assistance, please contact the concerned
        administration team.
        </p>

        <p>
        Regards,<br>
        <b>SSU x NIAT</b>
        </p>

    </body>
    </html>
    """

    return plain_text, html_text


# ==========================================
# SEND EMAIL
# ==========================================

def send_email(server, student_name, receiver_email):

    email = EmailMessage()
    email["From"] = SENDER_EMAIL
    email["To"] = receiver_email
    email["Subject"] = SUBJECT

    plain_text, html_text = create_email(student_name)

    email.set_content(plain_text)
    email.add_alternative(html_text, subtype="html")

    server.send_message(email)


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    parser = argparse.ArgumentParser(
        description="Personalized student fee reminder bulk email"
    )

    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send emails. Without this, only preview."
    )

    args = parser.parse_args()

    if not os.path.exists(CSV_FILE):
        print(f"ERROR: CSV file not found: {CSV_FILE}")
        return

    students = []

    # Read CSV
    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as file:

        reader = csv.DictReader(file)

        required_columns = {"Student_Name", "Email"}

        if not reader.fieldnames or not required_columns.issubset(
            set(reader.fieldnames)
        ):
            print("ERROR: CSV must contain Student_Name and Email columns.")
            return

        for row in reader:

            student_name = (row.get("Student_Name") or "").strip()
            receiver_email = (row.get("Email") or "").strip()

            if not student_name or not receiver_email:
                print(f"Skipping incomplete row: {row}")
                continue

            students.append((student_name, receiver_email))

    if not students:
        print("No valid student records found.")
        return

    print(f"\nTotal valid students: {len(students)}")

    # Preview mode
    if not args.send:

        print("\nPREVIEW MODE: No emails will be sent.\n")

        for name, email in students:
            print(f"Student: {name} | Email: {email}")

        print("\nTo actually send emails, run:")
        print("python bulk_fee_reminder.py --send")
        return

    # Check Gmail credentials
    if not SENDER_EMAIL or not APP_PASSWORD:
        print("ERROR: Set SENDER_EMAIL and GMAIL_APP_PASSWORD first.")
        return

    successful = 0
    failed = []

    print("\nConnecting to Gmail SMTP...")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

            server.starttls()

            server.login(SENDER_EMAIL, APP_PASSWORD)

            print("Gmail login successful!\n")

            for index, (name, receiver) in enumerate(students, start=1):

                try:

                    send_email(server, name, receiver)

                    successful += 1

                    print(
                        f"[{index}/{len(students)}] "
                        f"SUCCESS: {name} - {receiver}"
                    )

                    # Avoid sending too many emails too quickly
                    time.sleep(1)

                except Exception as error:

                    failed.append((name, receiver, str(error)))

                    print(
                        f"[{index}/{len(students)}] "
                        f"FAILED: {name} - {receiver} - {error}"
                    )

    except Exception as error:

        print(f"\nSMTP ERROR: {error}")

    # Final report
    print("\n========== EMAIL REPORT ==========")
    print(f"Total students : {len(students)}")
    print(f"Successful     : {successful}")
    print(f"Failed         : {len(failed)}")

    if failed:

        with open(
            "failed_emails.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow(["Student_Name", "Email", "Error"])
            writer.writerows(failed)

        print("Failed email details saved in failed_emails.csv")

    print("==================================")


if __name__ == "__main__":
    main()
