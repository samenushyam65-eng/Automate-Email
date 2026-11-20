# SSU-NIAT Hacktoberfest Bulk Email Sender

This program sends one personalized email per student. It reads **two columns** from `students.csv`:

- Column A: `Student Name`
- Column B: `Email ID`

The email begins `Dear [Student Name],`. The script does not send anything unless you add `--send`.

## Files

- `send_bulk_email.py` — email sender
- `students.csv` — student list transcribed from the screenshot
- `requirements.txt` — no third-party packages are required

## 1. Extract the ZIP

Download and extract the ZIP file. Open the extracted folder in File Explorer.

## 2. Open PowerShell in the folder

In File Explorer, open the extracted folder, click the address bar, type `powershell`, and press Enter.

## 3. Preview the recipient list first

Run:

```powershell
python .\send_bulk_email.py
```

This is preview-only. No emails are sent. Verify every name and address against your original sheet before sending.

## 4. Configure Gmail in PowerShell

The sending account needs Gmail SMTP access. For Gmail, enable 2-Step Verification and create a Google **App Password**, if your account supports it.

In the same PowerShell window, run these commands, replacing the examples with your own details:

```powershell
$env:GMAIL_ADDRESS = "your-sending-address@gmail.com"
$env:GMAIL_APP_PASSWORD = "your16characterapppassword"
$env:SENDER_NAME = "SSU-NIAT Team"
```

Enter the App Password without spaces. Do not use your normal Gmail password. Do not share or commit the App Password. If it was exposed, revoke it and create a new one. Some work/school accounts may not allow App Passwords; ask your Google Workspace administrator if necessary.

These environment variables are temporary and will be cleared when you close PowerShell.

## 5. Send the emails

After you have checked the list and confirmed the notice is approved, run:

```powershell
python .\send_bulk_email.py --send
```

The script sends individual emails, so recipients do not see each other's email addresses. It waits one second between messages by default.

## 6. Update the student list

Edit `students.csv` in Excel or Notepad, preserving the exact headers:

```csv
Student Name,Email ID
```

Save as CSV UTF-8. To use another CSV filename:

```powershell
python .\send_bulk_email.py --csv ".\my_students.csv"
```

Add `--send` only after previewing and verifying the list.

## Email content

Subject: Update on Your Hacktoberfest Registration – SSU-NIAT Cuttack

Dear [Student Name],

Thank you for your interest in participating in the Hacktoberfest event at SSU-NIAT Cuttack.

Due to the event reaching its maximum participant capacity, we regret to inform you that your registration has been cancelled. We appreciate your enthusiasm and interest in the event.

We encourage you to stay connected for future workshops and events, and we look forward to your participation in upcoming opportunities.

Thank you for your understanding.

Regards,
SSU-NIAT Team

## Important

- The student list was transcribed from a screenshot. Check spelling and every email address against the original Google Sheet.
- Running with `--send` again will send duplicate emails.
- Gmail sending limits and organization policies apply.
