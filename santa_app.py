import mysql.connector
import random

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ns322044@@",  # <= update this
            database="santas_secretary"    # <= update this
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        exit(1)

def get_random_quote(cursor):
    cursor.execute("SELECT Quote, Author FROM christmas_quotes ORDER BY RAND() LIMIT 1")
    row = cursor.fetchone()
    if row:
        quote, author = row
        return f'\n🎅 "{quote}"\n   — {author}\n'
    else:
        return "\n(No quotes found in the database!)\n"

def main():
    db = connect_db()
    cursor = db.cursor()

    while True:
        print("\n🎄 Welcome to Santa's Quote Generator 🎄")
        print("1. Get Quote of the Day")
        print("2. Exit")
        choice = input("\nChoose an option 1 or 2: ")

        if choice == "1":
            print(get_random_quote(cursor))
        elif choice == "2":
            print("\nGoodbye! May your days be merry and bright! 🎁\n")
            break
        else:
            print("\nInvalid choice. Please enter 1 or 2.\n")

    cursor.close()
    db.close()

if __name__ == "__main__":
    main()