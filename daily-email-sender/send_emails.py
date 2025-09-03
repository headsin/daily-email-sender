import requests
import json
import datetime

# Load email data
with open("mnc_mails.json", "r") as f:
    data = json.load(f)

# Read current index from counter.txt (start from 5600 by default)
try:
    with open("counter.txt", "r") as f:
        start_index = int(f.read().strip())
except FileNotFoundError:
    start_index = 5600

# Get current time (UTC) for GitHub Actions
now_utc = datetime.datetime.utcnow()
current_hour = now_utc.hour

# Map batch times (adjust if you're not using UTC)
batch_times = {
    10: 0,
    12: 1,
    14: 2,
    16: 3
}

# Determine batch index based on time
batch_index = batch_times.get(current_hour)
if batch_index is None:
    print(f"Not a scheduled time: {current_hour}:00 UTC")
    exit()

# Compute batch start and end
emails_per_batch = 100
batch_start = start_index + (batch_index * emails_per_batch)
batch_end = batch_start + emails_per_batch

print(f"Sending emails {batch_start} to {batch_end}")

# Send emails
for i in range(batch_start, min(batch_end, len(data))):
    email = data[i]["email"]
    userName = data[i]["userName"]

    payload = {
        "email": email,
        "userName": userName
    }

    response = requests.post(
        "https://application-api.headsin.co/api/v1/send-email?emailType=candidate",
        json=payload
    )

    print(f"{i + 1}: Sent to {email} - Status Code: {response.status_code}")

# Only update the counter after last batch (4PM = index 3)
if batch_index == 3:
    with open("counter.txt", "w") as f:
        f.write(str(batch_end))
