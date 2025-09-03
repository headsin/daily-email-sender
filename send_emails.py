import requests
import json
import datetime
import os

def send_emails():
    # Load email data
    try:
        with open("mnc_mails.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("mnc_mails.json not found!")
        return
    except json.JSONDecodeError:
        print("Invalid JSON in mnc_mails.json!")
        return

    if not data:
        print("No emails left to send!")
        return

    print(f"Loaded {len(data)} email addresses")

    # Your email credentials
    subject = "Stop Scrolling. Start Earning — With HeadsIn🚀"
    password = "sJYlSh9xKM4K40"

    # Get current Indian Time (IST = UTC+5:30)
    utc_now = datetime.datetime.utcnow()
    ist_time = utc_now + datetime.timedelta(hours=5, minutes=30)
    current_hour = ist_time.hour

    print(f"Current Indian Time: {ist_time.strftime('%H:%M')}")

    # Define batch schedule (Indian Time - IST)
    batch_times = {10: 100, 12: 100, 14: 100, 16: 100}  # 100 emails per batch at 10AM, 12PM, 2PM, 4PM IST

    # Determine how many emails to send in this batch
    emails_to_send = batch_times.get(current_hour)
    if emails_to_send is None:
        print(f"Not a scheduled time: {current_hour}:00 IST")
        return

    # Take only the number of emails for this batch
    batch_recipients = data[:emails_to_send]
    remaining_emails = data[emails_to_send:]

    print(f"Sending {len(batch_recipients)} emails this batch")
    print(f"Will remain {len(remaining_emails)} emails after sending")

    # Prepare payload
    payload = {
        "sendTo": batch_recipients,
        "subject": subject,
        "password": password
    }

    try:
        print("Sending batch...")
        
        response = requests.post(
            "https://application-api.headsin.co/api/v1/send-email",
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30
        )

        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Successfully sent {len(batch_recipients)} emails")
            
            # Remove sent emails from the list and update mnc_mails.json
            with open("mnc_mails.json", "w") as f:
                json.dump(remaining_emails, f, indent=2)
            
            print(f"Removed sent emails. {len(remaining_emails)} emails remaining.")
                
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            # Don't remove emails if sending failed
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")

    print("Batch processing completed!")

if __name__ == "__main__":
    send_emails()