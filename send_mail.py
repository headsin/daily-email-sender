import psycopg2
import requests
import json

# ==== Database Config ====
DB_CONFIG = {
    "host": "aws-1-ap-south-1.pooler.supabase.com",
    "port": "6543",
    "dbname": "postgres",
    "user": "postgres.maxmdtidrysubfnynahz",
    "password": "Headsin@0104"
}

# ==== HeadsIn API Config ====
API_URL = "https://application-api.headsin.co/api/v1/send-email?emailType=candidate"
API_PASSWORD = "sJYlSh9xKM4K40"
EMAIL_SUBJECT = "Stop Scrolling. Start Earning — With HeadsIn🚀"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def send_bulk_mails(recipients):
    """Send one bulk request to API with multiple recipients"""
    payload = {
        "sendTo": recipients,   # ✅ must be a list of dicts
        "subject": EMAIL_SUBJECT,
        "password": API_PASSWORD
    }

    try:
        print(f"➡ Sending {len(recipients)} emails...")
        response = requests.post(
            API_URL,
            data=json.dumps(payload),   # force exact raw JSON
            headers=HEADERS,
            timeout=60
        )
        print("🔎 Response status:", response.status_code)
        print("🔎 Response body:", response.text)

        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"❌ Bulk send error: {e}")
        return False


def process_batch(batch_size=100):
    """Fetch unsent mails, send in bulk, and update status"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email FROM email_data
        WHERE is_sended = FALSE
        LIMIT %s;
    """, (batch_size,))
    rows = cursor.fetchall()

    print(f"📩 Found {len(rows)} emails to send")

    if not rows:
        cursor.close()
        conn.close()
        return

    # ✅ Build correct payload list
    recipients = [{"email": email, "userName": name} for uid, name, email in rows]
    ids = [uid for uid, _, _ in rows]

    print("📝 Preparing to mark these IDs as sent:", ids)

    if send_bulk_mails(recipients):
        try:
            cursor.execute(
                "UPDATE email_data SET is_sended = TRUE WHERE id = ANY(%s);",
                (ids,)
            )
            conn.commit()
            print(f"✅ Successfully marked {len(ids)} emails as sent")
        except Exception as db_err:
            conn.rollback()
            print(f"❌ Database update failed: {db_err}")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    process_batch(100)
