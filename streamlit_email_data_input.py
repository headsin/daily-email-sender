import streamlit as st
import pandas as pd
import psycopg2

# Database credentials
DB_CONFIG = {
    "host": "aws-1-ap-south-1.pooler.supabase.com",
    "port": "6543",
    "dbname": "postgres",
    "user": "postgres.maxmdtidrysubfnynahz",
    "password": "Headsin@0104"
}

def insert_data(df):
    """Insert data from DataFrame into Postgres"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO sample_data (name, email, is_sended)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING;
        """

        for _, row in df.iterrows():
            cursor.execute(insert_query, (row['userName'], row['email'], False))

        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error inserting data: {e}")
        return False


# Streamlit UI
st.title("Anant Mail System(Mail Loader)")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # ✅ Detect duplicates by email
        duplicate_df = df[df.duplicated(subset=["email"], keep=False)]
        unique_df = df.drop_duplicates(subset=["email"], keep="first")

        st.write("### Preview of uploaded data (after removing duplicates)")
        st.dataframe(unique_df)

        if not duplicate_df.empty:
            st.warning("⚠️ Duplicate emails found! They will not be inserted.")
            st.write("### Duplicate Emails:")
            st.dataframe(duplicate_df)

        # ✅ Button to insert only unique rows
        if st.button("🚀 Insert Unique Emails into Database"):
            success = insert_data(unique_df)
            if success:
                st.success("✅ Unique data inserted successfully into Postgres!")

    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
