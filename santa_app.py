import mysql.connector
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ns322044@@",
            database="santas_secretary"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"❌ {err}")
        exit(1)

def get_random_quote(cursor):
    cursor.execute("SELECT Quote, Author FROM christmas_quotes ORDER BY RAND() LIMIT 1")
    row = cursor.fetchone()
    if row:
        quote, author = row
        return f'🎅 "{quote}"\n— {author}'
    else:
        return "(No quotes found!)"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

db = connect_db()
cursor = db.cursor()

root = tk.Tk()
root.title("Santa's Christmas Assistant 🎄")
root.geometry("700x550")
root.resizable(False, False)

def load_image(filename, size):
    img = Image.open(os.path.join(BASE_DIR, filename))
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

header_bg = load_image("header_bg.png", (700, 100))
results_bg = load_image("results_bg.png", (700, 450))

header_frame = tk.Frame(root, width=700, height=100)
header_frame.place(x=0, y=0)

header_label = tk.Label(header_frame, image=header_bg)
header_label.place(x=0, y=0)

title_label = tk.Label(
    header_frame,
    text="🎄 Santa's Christmas Assistant 🎄",
    font=("Georgia", 24, "bold"),
    fg="white",
    bg="black"
)
title_label.place(relx=0.5, rely=0.5, anchor="center")

results_frame = tk.Frame(root, width=700, height=450)
results_frame.place(x=0, y=100)

results_label = tk.Label(results_frame, image=results_bg)
results_label.place(x=0, y=0)

results_text = tk.Text(
    results_frame,
    width=65,
    height=20,
    font=("Consolas", 12),
    wrap="word",
    bd=0,
    bg="white"
)
results_text.place(x=20, y=40)
results_text.config(state="disabled")

user_input = tk.Entry(root, font=("Consolas", 14), width=40)
user_input.place(relx=0.5, y=525, anchor="center")

def print_out(text):
    results_text.config(state="normal")
    results_text.insert(tk.END, text + "\n")
    results_text.config(state="disabled")
    results_text.see(tk.END)

current_user = None

def show_main_menu():
    print_out("\n---------- MAIN MENU ----------")
    print_out("1) I have an account")
    print_out("2) Create a new account")
    print_out("3) Delete an account")
    print_out("4) Search for users")
    print_out("--------------------------------")
    print_out("Enter your choice:")
    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_main_menu)

def handle_main_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        print_out("🔐 Enter username:")
        user_input.bind("<Return>", login_account)

    elif choice == "2":
        print_out("📝 Enter NEW username:")
        user_input.bind("<Return>", create_account)

    elif choice == "3":
        print_out("🗑 Enter username to DELETE:")
        user_input.bind("<Return>", delete_account_fn)

    elif choice == "4":
        print_out("🔍 Enter part of a username to search:")
        user_input.bind("<Return>", search_for_users)

    else:
        print_out("❌ Invalid choice. Try 1–4.")
        show_main_menu()

def login_account(event=None):
    global current_user
    username = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (username,))
    row = cursor.fetchone()

    if row:
        current_user = username
        print_out(f"🎉 Welcome back, {username}!")
        show_user_menu()
    else:
        print_out("❌ No such user.")
        show_main_menu()

def create_account(event=None):
    global temp_new_username
    temp_new_username = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (temp_new_username,))
    if cursor.fetchone():
        print_out("❌ Username already exists.")
        show_main_menu()
        return

    print_out("🔐 Enter a password for this account:")
    user_input.bind("<Return>", finish_create_account)

def finish_create_account(event=None):
    global temp_new_username
    password = user_input.get().strip()
    user_input.delete(0, tk.END)

    password_hash = password  

    cursor.execute(
        "INSERT INTO users (Username, PasswordHash, QuoteID) VALUES (%s, %s, NULL)",
        (temp_new_username, password_hash)
    )
    db.commit()

    print_out(f"🎉 Account '{temp_new_username}' created successfully!")
    temp_new_username = None
    show_main_menu()

def delete_account_fn(event=None):
    username = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (username,))
    if not cursor.fetchone():
        print_out("❌ User not found.")
    else:
        cursor.execute("DELETE FROM users WHERE Username=%s", (username,))
        db.commit()
        print_out(f"🗑 User '{username}' deleted.")

    show_main_menu()

def search_for_users(event=None):
    term = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT Username FROM users WHERE Username LIKE %s", (f"%{term}%",))
    rows = cursor.fetchall()

    if not rows:
        print_out("❌ No matching users found.")
    else:
        print_out("🔍 Matching users:")
        for r in rows:
            print_out(f" - {r[0]}")

    show_main_menu()

def show_user_menu():
    print_out("\n-------- USER MENU --------")
    print_out(f"Logged in as: {current_user}")
    print_out("1) Change Username")
    print_out("2) Sign Out")
    print_out("---------------------------")
    print_out("Enter your choice:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_user_menu)

def handle_user_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        print_out("✏️ Enter new username:")
        user_input.bind("<Return>", change_username)

    elif choice == "2":
        print_out("👋 Signed out.")
        global current_user
        current_user = None
        show_main_menu()

    else:
        print_out("❌ Invalid choice.")
        show_user_menu()

def change_username(event=None):
    global current_user
    new_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (new_name,))
    if cursor.fetchone():
        print_out("❌ Username already exists.")
        show_user_menu()
        return

    cursor.execute("UPDATE users SET Username=%s WHERE Username=%s", (new_name, current_user))
    db.commit()

    print_out(f"🎉 Username changed from '{current_user}' to '{new_name}'")
    current_user = new_name
    show_user_menu()

print_out(get_random_quote(cursor))
show_main_menu()

root.mainloop()

cursor.close()
db.close()
