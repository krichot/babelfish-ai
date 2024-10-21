import psycopg2
import datetime
from bs4 import BeautifulSoup

def upload_html_to_postgres(html_content, title, db_config):
    """Uploads HTML content to a PostgreSQL database.

    Args:
        html_content: The HTML content to upload as a string.
        db_config: A dictionary containing the database connection details:
                   {"host": "...", "database": "...", "user": "...", "password": "..."}

    Returns:
        The UID of the inserted row, or None if an error occurred.
    """

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()

        # Prepare the SQL query
        query = """
            INSERT INTO translations (uid, contents_original, title, status, timestamp)
            VALUES (gen_random_uuid(), %s, %s, 'UPLOADED', NOW())
            RETURNING uid;
        """

        # Execute the query
        cur.execute(query, (html_content, title,))

        # Get the generated UID
        uid = cur.fetchone()[0]

        # Commit the transaction
        conn.commit()

        return uid

    except (Exception, psycopg2.Error) as error:
        print(f"Error uploading HTML to PostgreSQL: {error}")
        return None

    finally:
        # Close the cursor and connection
        if cur:
            cur.close()
        if conn:
            conn.close()

# Example usage:
if __name__ == "__main__":
    # 1. Load HTML content from "report.html"
    with open("raport.html", "r") as file:
        html_content = file.read()

    # 2. Define your database connection details
    db_config = {
        "host": "localhost",
        "database": "babelfish-ai",
        "user": 'postgres',
        "password": 'ZHC`kiCKq~gY2",8'
    }

    title = "Raport testowy " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. Upload the HTML content
    inserted_uid = upload_html_to_postgres(html_content, title, db_config)

    if inserted_uid:
        print(f"HTML content uploaded successfully with UID: {inserted_uid}")
    else:
        print("Failed to upload HTML content.")
