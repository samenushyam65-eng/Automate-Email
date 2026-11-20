
import csv
import smtplib
import os
import argparse
from email.message import EmailMessage

# Configuration
REQUIRED_ATTENDANCE = 85.0
CSV_FILE = "attendance.csv"

# Gmail credentials from environment variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(receiver, student_name, attendance):
    msg = EmailMessage()

    msg["Subject"] = f"Attendance Shortage Alert - {student_name}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver

    msg.set_content(f"""
Dear Parent/Guardian,

We would like to inform you that your ward, {student_name}, currently has an attendance of {attendance}%, which is below the required minimum of 85%.

If {student_name} is unable to improve their attendance and meet this requirement, they will not be permitted to participate in any NIAT activities or events.

We kindly request your support in ensuring regular attendance going forward.

Regards,
NIAT Team
""")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--send",
        action="store_true",
        help="Actually send emails. Without this, only preview."
    )
    args = parser.parse_args()

    if not os.path.exists(CSV_FILE):
        print(f"CSV file not found: {CSV_FILE}")
        return

    if args.send and (not SENDER_EMAIL or not APP_PASSWORD):
        print("Please configure SENDER_EMAIL and GMAIL_APP_PASSWORD.")
        return

    sent = 0
    skipped = 0

    with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "Student_Name",
            "Attendance_Percentage",
            "Email"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            print("CSV is missing one or more required columns.")
            return

        for row in reader:
            try:
                name = row["Student_Name"].strip()
                attendance = float(
                    row["Attendance_Percentage"].strip().replace("%", "")
                )
                receiver = row["Email"].strip()

                if not name or not receiver:
                    print("Skipping row with missing name or email.")
                    skipped += 1
                    continue

                if attendance >= REQUIRED_ATTENDANCE:
                    print(f"SKIPPED: {name} - {attendance}%")
                    skipped += 1
                    continue

                if args.send:
                    send_email(receiver, name, attendance)
                    print(f"EMAIL SENT: {name} - {attendance}%")
                    sent += 1
                else:
                    print(
                        f"PREVIEW: {name} | {attendance}% | {receiver}"
                    )
                    sent += 1

            except (ValueError, AttributeError, KeyError) as error:
                print(f"Invalid row: {row} | Error: {error}")
                skipped += 1

            except Exception as error:
                print(f"Failed to process {row}: {error}")
                skipped += 1

    print("\n========== SUMMARY ==========")
    print(f"Emails sent / ready: {sent}")
    print(f"Rows skipped: {skipped}")
    print("=============================")


if __name__ == "__main__":
    main()
