import mysql.connector
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

def connect_db():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ns322044@@",
            database="santas_secretary"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"{err}")
        exit(1)

def get_random_quote(cursor):
    cursor.execute("SELECT Quote, Author FROM christmas_quotes ORDER BY RAND() LIMIT 1")
    row = cursor.fetchone()
    return f'🎅 "{row[0]}"\n— {row[1]}' if row else "(No quotes found!)"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db = connect_db()
cursor = db.cursor()

root = tk.Tk()
root.title("Santa's Secretary 🎄")
root.geometry("700x550")
root.resizable(False, False)

def load_image(filename, size):
    img = Image.open(os.path.join(BASE_DIR, filename)).resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)

header_bg = load_image("header_bg.png", (700, 100))
results_bg = load_image("results_bg.png", (700, 450))

header_frame = tk.Frame(root, width=700, height=100)
header_frame.place(x=0, y=0)
tk.Label(header_frame, image=header_bg).place(x=0, y=0)

tk.Label(
    header_frame,
    text="🎄 Santa's Christmas Assistant 🎄",
    font=("Georgia", 24, "bold"),
    fg="white",
    bg="black"
).place(relx=0.5, rely=0.5, anchor="center")

results_frame = tk.Frame(root, width=700, height=450)
results_frame.place(x=0, y=100)
tk.Label(results_frame, image=results_bg).place(x=0, y=0)

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
current_user_id = None
current_wishlist_id = None
current_shopping_list_id = None

def log_shopping_list_action(list_id, item_name, action_type):
    cursor.execute(
        "INSERT INTO shopping_list_audit (UserID, ListID, ItemName, ActionType) "
        "VALUES (%s, %s, %s, %s)",
        (current_user_id, list_id, item_name, action_type)
    )
    db.commit()

def show_main_menu():
    print_out("\n---------- MAIN MENU ----------")
    print_out("1) Sign in")
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
        user_input.bind("<Return>", login_account_username)

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
        print_out("❌ Invalid choice.")
        show_main_menu()

def login_account_username(event=None):
    global temp_username
    temp_username = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (temp_username,))
    if cursor.fetchone():
        print_out("🔑 Enter password:")
        user_input.bind("<Return>", login_account_password)
    else:
        print_out("❌ No such user.")
        show_main_menu()

def login_account_password(event=None):
    global current_user, current_user_id
    password = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT UserID FROM users WHERE Username=%s AND PasswordHash=%s",
        (temp_username, password)
    )
    row = cursor.fetchone()

    if row:
        current_user = temp_username
        current_user_id = row[0]
        print_out(f"🎉 Welcome back, {current_user}!")
        show_user_menu()
    else:
        print_out("❌ Incorrect password.")
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

    cursor.execute(
        "INSERT INTO users (Username, PasswordHash, QuoteID) VALUES (%s, %s, NULL)",
        (temp_new_username, password)
    )
    db.commit()

    print_out(f"🎉 Account '{temp_new_username}' created.")
    temp_new_username = None
    show_main_menu()

def delete_account_fn(event=None):
    username = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT UserID FROM users WHERE Username=%s", (username,))
    if cursor.fetchone():
        cursor.execute("DELETE FROM users WHERE Username=%s", (username,))
        db.commit()
        print_out(f"🗑 User '{username}' deleted.")
    else:
        print_out("❌ User not found.")

    show_main_menu()

def search_for_users(event=None):
    term = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute("SELECT Username FROM users WHERE Username LIKE %s", (f"%{term}%",))
    rows = cursor.fetchall()

    if not rows:
        print_out("❌ No matching users found.")
    else:
        for r in rows:
            print_out(f" - {r[0]}")

    show_main_menu()

def show_user_menu():
    print_out("\n-------- USER MENU --------")
    print_out(f"Logged in as: {current_user}")
    print_out("1) Change Username")
    print_out("2) Naughty or Nice Check")
    print_out("3) Christmas Wishlists")
    print_out("4) See Shopping Lists")
    print_out("5) Christmas Tree Finder")
    print_out("6) Sign Out")
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
        print_out("🎅 Enter your FIRST NAME:")
        user_input.bind("<Return>", naughty_or_nice_check)

    elif choice == "3":
        show_wishlist_menu()

    elif choice == "4":
        show_shopping_list_menu()

    elif choice == "5":
        start_tree_finder()

    elif choice == "6":
        print_out("👋 Signed out.")
        global current_user, current_user_id
        current_user = None
        current_user_id = None
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

    cursor.execute(
        "UPDATE users SET Username=%s WHERE Username=%s",
        (new_name, current_user)
    )
    db.commit()

    print_out(f"🎉 Username changed from '{current_user}' to '{new_name}'")
    current_user = new_name
    show_user_menu()

def naughty_or_nice_check(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT Naughty_or_Nice FROM naughty_or_nice_list WHERE Name=%s",
        (name,)
    )
    row = cursor.fetchone()

    if not row:
        print_out(f"❌ No record found for '{name}'.")
    else:
        status = row[0].strip().lower()
        if status == "nice":
            print_out(f"😇 {name}, you are NICE!")
        elif status == "naughty":
            print_out(f"😈 {name}, you are NAUGHTY!")
        else:
            print_out(f"{name}'s record: {row[0]}")

    show_user_menu()

def show_wishlist_menu():
    print_out("\n------ CHRISTMAS WISHLISTS ------")
    print_out("1) See all wishlists")
    print_out("2) Select a wishlist")
    print_out("3) Add a wishlist")
    print_out("4) Delete a wishlist")
    print_out("5) Exit to User Menu")
    print_out("---------------------------------")
    print_out("Enter your choice:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_wishlist_menu)

def handle_wishlist_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        see_all_wishlists()

    elif choice == "2":
        print_out("Enter wishlist name to select:")
        user_input.bind("<Return>", select_wishlist)

    elif choice == "3":
        print_out("Enter name for new wishlist:")
        user_input.bind("<Return>", add_wishlist)

    elif choice == "4":
        print_out("Enter wishlist name to delete:")
        user_input.bind("<Return>", delete_wishlist)

    elif choice == "5":
        show_user_menu()

    else:
        print_out("❌ Invalid choice.")
        show_wishlist_menu()

def see_all_wishlists():
    cursor.execute(
        "SELECT WishlistName FROM wishlists WHERE UserID=%s",
        (current_user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print_out("❌ You have no wishlists.")
    else:
        print_out("🎁 Your Wishlists:")
        for r in rows:
            print_out(f" - {r[0]}")

    show_wishlist_menu()

def select_wishlist(event=None):
    global current_wishlist_id
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT WishlistID FROM wishlists WHERE UserID=%s AND WishlistName=%s",
        (current_user_id, name)
    )
    row = cursor.fetchone()

    if not row:
        print_out(f"❌ No wishlist named '{name}'.")
        show_wishlist_menu()
        return

    current_wishlist_id = row[0]
    print_out(f"🎁 Selected wishlist: {name}")
    show_wishlist_item_menu()

def add_wishlist(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "INSERT INTO wishlists (UserID, WishlistName, CreatedAt) VALUES (%s, %s, NOW())",
        (current_user_id, name)
    )
    db.commit()

    print_out(f"🎁 Wishlist '{name}' added.")
    show_wishlist_menu()

def delete_wishlist(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "DELETE FROM wishlists WHERE UserID=%s AND WishlistName=%s",
        (current_user_id, name)
    )
    db.commit()

    print_out(f"🗑 Wishlist '{name}' deleted.")
    show_wishlist_menu()


def show_wishlist_item_menu():
    print_out("\n------ WISHLIST ITEMS ------")
    print_out("1) See all items")
    print_out("2) Mark item as purchased")
    print_out("3) Add item to wishlist")
    print_out("4) Delete an item")
    print_out("5) See total cost")
    print_out("6) Add wishlist item to a shopping list")
    print_out("7) Exit to Wishlist Menu")
    print_out("----------------------------")
    print_out("Enter your choice:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_wishlist_item_menu)

def handle_wishlist_item_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        see_all_wishlist_items()

    elif choice == "2":
        print_out("Enter item name to mark purchased:")
        user_input.bind("<Return>", wishlist_mark_purchased)

    elif choice == "3":
        print_out("Enter new item name:")
        user_input.bind("<Return>", add_item_step1)

    elif choice == "4":
        print_out("Enter item name to delete:")
        user_input.bind("<Return>", delete_wishlist_item)

    elif choice == "5":
        see_wishlist_total()

    elif choice == "6":
        print_out("Enter wishlist item name to add to a shopping list:")
        user_input.bind("<Return>", wishlist_item_add_to_shopping_step1)

    elif choice == "7":
        show_wishlist_menu()

    else:
        print_out("❌ Invalid choice.")
        show_wishlist_item_menu()


def see_all_wishlist_items():
    cursor.execute(
        "SELECT ItemName, Description, Price, Priority, Purchased "
        "FROM wishlist_items WHERE WishlistID=%s",
        (current_wishlist_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print_out("❌ No items in this wishlist.")
    else:
        print_out("🎁 Items:")
        for item in rows:
            purchased = "✔️" if item[4] else "❌"
            print_out(f"- {item[0]} (${item[2]}): {item[1]} | Priority: {item[3]} | Purchased: {purchased}")

    show_wishlist_item_menu()


def wishlist_mark_purchased(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "UPDATE wishlist_items SET Purchased=1 WHERE WishlistID=%s AND ItemName=%s",
        (current_wishlist_id, name)
    )
    db.commit()

    print_out(f"✔️ Marked '{name}' as purchased.")
    show_wishlist_item_menu()


def add_item_step1(event=None):
    global temp_item_name
    temp_item_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter description:")
    user_input.bind("<Return>", add_item_step2)

def add_item_step2(event=None):
    global temp_item_description
    temp_item_description = user_input.get().strip()
    user_input.delete(0, tk.END)

    add_item_price_menu()

def add_item_price_menu(event=None):
    print_out("1) Enter your own price")
    print_out("2) See price recommendation")
    print_out("Choose an option:")
    user_input.delete(0, tk.END)
    user_input.bind("<Return>", add_item_price_choice)

def add_item_price_choice(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        print_out("Enter price:")
        user_input.bind("<Return>", add_item_manual_price)

    elif choice == "2":
        cursor.execute(
            "SELECT UnitPrice FROM christmassales WHERE ProductName=%s",
            (temp_item_name,)
        )
        row = cursor.fetchone()

        if not row:
            print_out("No recommendation found. Enter price manually:")
            user_input.bind("<Return>", add_item_manual_price)
        else:
            global temp_item_price
            temp_item_price = row[0]
            print_out(f"Recommended Price: ${temp_item_price}")
            print_out("Press Enter to accept or type a different price:")
            user_input.bind("<Return>", add_item_price_override)

    else:
        print_out("Invalid choice.")
        add_item_price_menu()

def add_item_manual_price(event=None):
    global temp_item_price
    temp_item_price = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter priority (Low, Medium, High):")
    user_input.bind("<Return>", finish_add_item)

def add_item_price_override(event=None):
    global temp_item_price
    override = user_input.get().strip()
    user_input.delete(0, tk.END)

    if override != "":
        temp_item_price = override

    print_out("Enter priority (Low, Medium, High):")
    user_input.bind("<Return>", finish_add_item)

def finish_add_item(event=None):
    priority = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "INSERT INTO wishlist_items (WishlistID, ItemName, Description, Price, Priority, Purchased) "
        "VALUES (%s, %s, %s, %s, %s, 0)",
        (current_wishlist_id, temp_item_name, temp_item_description, temp_item_price, priority)
    )
    db.commit()

    print_out(f"🎁 Added item '{temp_item_name}'!")
    show_wishlist_item_menu()


def delete_wishlist_item(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "DELETE FROM wishlist_items WHERE WishlistID=%s AND ItemName=%s",
        (current_wishlist_id, name)
    )
    db.commit()

    print_out(f"🗑 Deleted item '{name}'.")
    show_wishlist_item_menu()


def see_wishlist_total():
    cursor.execute(
        "SELECT SUM(Price) FROM wishlist_items WHERE WishlistID=%s",
        (current_wishlist_id,)
    )
    total = cursor.fetchone()[0]

    print_out(f"Total cost: ${total:.2f}" if total else "Total cost: $0.00")
    show_wishlist_item_menu()


def wishlist_item_add_to_shopping_step1(event=None):
    global temp_wishlist_item_name
    temp_wishlist_item_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT WishlistItemID, ItemName, Description, Price, Priority "
        "FROM wishlist_items WHERE WishlistID=%s AND ItemName=%s",
        (current_wishlist_id, temp_wishlist_item_name)
    )
    row = cursor.fetchone()

    if not row:
        print_out("❌ Item not found.")
        show_wishlist_item_menu()
        return

    global temp_wishlist_item_id, temp_wishlist_item_desc, temp_wishlist_item_price, temp_wishlist_item_priority
    temp_wishlist_item_id = row[0]
    temp_wishlist_item_name = row[1]
    temp_wishlist_item_desc = row[2]
    temp_wishlist_item_price = row[3]
    temp_wishlist_item_priority = row[4]

    print_out("Enter shopping list name to add this item into:")
    user_input.bind("<Return>", wishlist_item_add_to_shopping_step2)

def wishlist_item_add_to_shopping_step2(event=None):
    list_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT ListID FROM shoppinglists WHERE UserID=%s AND ListName=%s",
        (current_user_id, list_name)
    )
    row = cursor.fetchone()

    if not row:
        print_out("❌ No such shopping list.")
        show_wishlist_item_menu()
        return

    list_id = row[0]

    cursor.execute(
        "INSERT INTO shopping_list_items "
        "(ListID, WishlistItemID, ItemName, Description, Price, Priority, Purchased, Quantity) "
        "VALUES (%s, %s, %s, %s, %s, %s, 0, 1)",
        (
            list_id,
            temp_wishlist_item_id,
            temp_wishlist_item_name,
            temp_wishlist_item_desc,
            temp_wishlist_item_price,
            temp_wishlist_item_priority
        )
    )
    db.commit()

    log_shopping_list_action(list_id, temp_wishlist_item_name, "ADD")

    print_out(f"🛒 Added '{temp_wishlist_item_name}' to shopping list '{list_name}'.")
    show_wishlist_item_menu()

def show_shopping_list_menu():
    print_out("\n------ SHOPPING LISTS ------")
    print_out("1) See all shopping lists")
    print_out("2) Select a shopping list")
    print_out("3) Add a shopping list")
    print_out("4) Delete a shopping list")
    print_out("5) Exit to User Menu")
    print_out("----------------------------")
    print_out("Enter your choice:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_shopping_list_menu)

def handle_shopping_list_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        see_all_shopping_lists()

    elif choice == "2":
        print_out("Enter shopping list name to select:")
        user_input.bind("<Return>", select_shopping_list)

    elif choice == "3":
        print_out("Enter new shopping list name:")
        user_input.bind("<Return>", add_shopping_list)

    elif choice == "4":
        print_out("Enter shopping list name to delete:")
        user_input.bind("<Return>", delete_shopping_list)

    elif choice == "5":
        show_user_menu()

    else:
        print_out("❌ Invalid choice.")
        show_shopping_list_menu()

def see_all_shopping_lists():
    cursor.execute(
        "SELECT ListName FROM shoppinglists WHERE UserID=%s",
        (current_user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print_out("❌ You have no shopping lists.")
    else:
        print_out("🛒 Your Shopping Lists:")
        for r in rows:
            print_out(f" - {r[0]}")

    show_shopping_list_menu()

def select_shopping_list(event=None):
    global current_shopping_list_id
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT ListID FROM shoppinglists WHERE UserID=%s AND ListName=%s",
        (current_user_id, name)
    )
    row = cursor.fetchone()

    if not row:
        print_out("❌ No such shopping list.")
        show_shopping_list_menu()
        return

    current_shopping_list_id = row[0]
    print_out(f"🛒 Selected shopping list: {name}")
    show_shopping_list_item_menu()

def add_shopping_list(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "INSERT INTO shoppinglists (UserID, ListName, Budget) VALUES (%s, %s, 0)",
        (current_user_id, name)
    )
    db.commit()

    print_out(f"🛒 Shopping list '{name}' created.")
    show_shopping_list_menu()

def delete_shopping_list(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "DELETE FROM shoppinglists WHERE UserID=%s AND ListName=%s",
        (current_user_id, name)
    )
    db.commit()

    print_out(f"🗑 Shopping list '{name}' deleted.")
    show_shopping_list_menu()


def show_shopping_list_item_menu():
    print_out("\n------ SHOPPING LIST ITEMS ------")
    print_out("1) See all items")
    print_out("2) Add manual item")
    print_out("3) Change quantity")
    print_out("4) Mark item purchased")
    print_out("5) Remove item")
    print_out("6) See total estimated cost")
    print_out("7) View audit log")
    print_out("8) Exit to Shopping Lists Menu")
    print_out("---------------------------------")
    print_out("Enter your choice:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_shopping_list_item_menu)

def handle_shopping_list_item_menu(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        see_shopping_list_items()

    elif choice == "2":
        print_out("Enter new item name:")
        user_input.bind("<Return>", shopping_add_item_step1)

    elif choice == "3":
        print_out("Enter item name to change quantity:")
        user_input.bind("<Return>", change_shopping_quantity_item)

    elif choice == "4":
        print_out("Enter item name to mark purchased:")
        user_input.bind("<Return>", shopping_mark_purchased)

    elif choice == "5":
        print_out("Enter item name to remove:")
        user_input.bind("<Return>", remove_shopping_item)

    elif choice == "6":
        see_shopping_total()

    elif choice == "7":
        show_shopping_audit_log()

    elif choice == "8":
        show_shopping_list_menu()

    else:
        print_out("❌ Invalid choice.")
        show_shopping_list_item_menu()


def see_shopping_list_items():
    cursor.execute(
        "SELECT ItemName, Description, Price, Priority, Purchased, Quantity "
        "FROM shopping_list_items WHERE ListID=%s",
        (current_shopping_list_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print_out("🛒 No items in this shopping list.")
    else:
        print_out("🛍 Items:")
        for r in rows:
            purchased = "✔️" if r[4] else "❌"
            print_out(
                f"- {r[0]} x{r[5]} @ ${r[2]} | {r[1]} | Priority: {r[3]} | Bought: {purchased}"
            )

    show_shopping_list_item_menu()


def shopping_add_item_step1(event=None):
    global shop_item_name
    shop_item_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter description:")
    user_input.bind("<Return>", shopping_add_item_step2)

def shopping_add_item_step2(event=None):
    global shop_item_description
    shop_item_description = user_input.get().strip()
    user_input.delete(0, tk.END)

    shopping_price_menu()

def shopping_price_menu(event=None):
    print_out("1) Enter your own price")
    print_out("2) See price recommendation")
    print_out("Choose an option:")
    user_input.delete(0, tk.END)
    user_input.bind("<Return>", shopping_price_choice_handler)

def shopping_price_choice_handler(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        print_out("Enter price:")
        user_input.bind("<Return>", shopping_price_manual)

    elif choice == "2":
        cursor.execute(
            "SELECT UnitPrice FROM christmassales WHERE ProductName=%s",
            (shop_item_name,)
        )
        row = cursor.fetchone()

        if not row:
            print_out("No recommendation found. Enter price:")
            user_input.bind("<Return>", shopping_price_manual)
        else:
            global shop_item_price
            shop_item_price = row[0]
            print_out(f"Recommended price: ${shop_item_price}")
            print_out("Press Enter to accept or type your own price:")
            user_input.bind("<Return>", shopping_price_accept_override)

    else:
        print_out("Invalid choice.")
        shopping_price_menu()

def shopping_price_manual(event=None):
    global shop_item_price
    shop_item_price = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter priority (Low, Medium, High):")
    user_input.bind("<Return>", shopping_priority_step)

def shopping_price_accept_override(event=None):
    global shop_item_price
    override = user_input.get().strip()
    user_input.delete(0, tk.END)

    if override != "":
        shop_item_price = override

    print_out("Enter priority (Low, Medium, High):")
    user_input.bind("<Return>", shopping_priority_step)

def shopping_priority_step(event=None):
    global shop_item_priority
    shop_item_priority = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter quantity:")
    user_input.bind("<Return>", shopping_finish_add)

def shopping_finish_add(event=None):
    qty = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "INSERT INTO shopping_list_items "
        "(ListID, ItemName, Description, Price, Priority, Purchased, Quantity, WishlistItemID) "
        "VALUES (%s, %s, %s, %s, %s, 0, %s, NULL)",
        (
            current_shopping_list_id,
            shop_item_name,
            shop_item_description,
            shop_item_price,
            shop_item_priority,
            qty
        )
    )
    db.commit()

    log_shopping_list_action(current_shopping_list_id, shop_item_name, "ADD")

    print_out(f"🛒 Added '{shop_item_name}' to shopping list.")
    show_shopping_list_item_menu()


def change_shopping_quantity_item(event=None):
    global item_to_change_qty
    item_to_change_qty = user_input.get().strip()
    user_input.delete(0, tk.END)

    print_out("Enter new quantity:")
    user_input.bind("<Return>", apply_new_quantity)

def apply_new_quantity(event=None):
    qty = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "UPDATE shopping_list_items SET Quantity=%s "
        "WHERE ListID=%s AND ItemName=%s",
        (qty, current_shopping_list_id, item_to_change_qty)
    )
    db.commit()

    print_out(f"Updated '{item_to_change_qty}' to quantity {qty}.")
    show_shopping_list_item_menu()


def shopping_mark_purchased(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "UPDATE shopping_list_items SET Purchased=1 "
        "WHERE ListID=%s AND ItemName=%s",
        (current_shopping_list_id, name)
    )
    db.commit()

    print_out(f"✔️ Marked '{name}' as purchased.")
    show_shopping_list_item_menu()


def remove_shopping_item(event=None):
    name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "DELETE FROM shopping_list_items WHERE ListID=%s AND ItemName=%s",
        (current_shopping_list_id, name)
    )
    db.commit()

    log_shopping_list_action(current_shopping_list_id, name, "DELETE")

    print_out(f"🗑 Removed '{name}' from shopping list.")
    show_shopping_list_item_menu()


def see_shopping_total():
    cursor.execute(
        "SELECT SUM(Price * Quantity) FROM shopping_list_items WHERE ListID=%s",
        (current_shopping_list_id,)
    )
    total = cursor.fetchone()[0]

    print_out(f"Total estimated cost: ${total:.2f}" if total else "Total estimated cost: $0.00")
    show_shopping_list_item_menu()

def show_shopping_audit_log():
    cursor.execute(
        "SELECT ItemName, ActionType, ActionTimestamp "
        "FROM shopping_list_audit WHERE UserID=%s ORDER BY ActionTimestamp DESC",
        (current_user_id,)
    )
    rows = cursor.fetchall()

    if not rows:
        print_out("📘 No audit logs yet.")
    else:
        print_out("📘 Shopping List Audit Log:")
        for r in rows:
            print_out(f"{r[2]} - {r[1]} '{r[0]}'")

    show_shopping_list_item_menu()


def start_tree_finder():
    print_out("\n🎄 CHRISTMAS TREE FINDER 🎄")
    print_out("1) Cheapest tree")
    print_out("2) Most popular tree")
    print_out("Choose an option:")

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_tree_finder_option)

def handle_tree_finder_option(event=None):
    choice = user_input.get().strip()
    user_input.delete(0, tk.END)

    if choice == "1":
        get_cheapest_tree()

    elif choice == "2":
        get_most_popular_tree()

    else:
        print_out("❌ Invalid choice.")
        show_user_menu()

def get_cheapest_tree():
    cursor.execute(
        "SELECT `Type of tree`, `Year`, `Average Tree Price`, `Sales`, `Number of trees sold` "
        "FROM christmastrees ORDER BY `Average Tree Price` ASC LIMIT 1"
    )
    row = cursor.fetchone()

    recommend_tree(row)

def get_most_popular_tree():
    cursor.execute(
        "SELECT `Type of tree`, `Year`, `Average Tree Price`, `Sales`, `Number of trees sold` "
        "FROM christmastrees ORDER BY `Number of trees sold` DESC LIMIT 1"
    )
    row = cursor.fetchone()

    recommend_tree(row)

def recommend_tree(row):
    tree_type = row[0]
    year = row[1]
    avg_price = row[2]

    print_out(f"\n🎄 Recommended Tree: {tree_type}")
    print_out(f"📅 Year: {year}")
    print_out(f"💲 Average Price: ${avg_price}")
    print_out("\nAdd to shopping list? (yes/no)")

    global recommended_tree_type, recommended_tree_price, recommended_tree_year
    recommended_tree_type = tree_type
    recommended_tree_price = avg_price
    recommended_tree_year = year

    user_input.delete(0, tk.END)
    user_input.bind("<Return>", handle_tree_add_choice)

def handle_tree_add_choice(event=None):
    choice = user_input.get().strip().lower()
    user_input.delete(0, tk.END)

    if choice == "yes":
        print_out("Enter shopping list name:")
        user_input.bind("<Return>", add_recommended_tree_to_list)

    else:
        print_out("Returning to User Menu.")
        show_user_menu()

def add_recommended_tree_to_list(event=None):
    list_name = user_input.get().strip()
    user_input.delete(0, tk.END)

    cursor.execute(
        "SELECT ListID FROM shoppinglists WHERE UserID=%s AND ListName=%s",
        (current_user_id, list_name)
    )
    row = cursor.fetchone()

    if not row:
        print_out("❌ No such shopping list.")
        show_user_menu()
        return

    list_id = row[0]

    cursor.execute(
        "INSERT INTO shopping_list_items "
        "(ListID, ItemName, Description, Price, Priority, Purchased, Quantity, WishlistItemID) "
        "VALUES (%s, %s, %s, %s, 'Medium', 0, 1, NULL)",
        (
            list_id,
            f"{recommended_tree_type} Christmas Tree",
            f"Recommended Christmas tree for {recommended_tree_year}",
            recommended_tree_price
        )
    )
    db.commit()

    log_shopping_list_action(list_id, f"{recommended_tree_type} Christmas Tree", "ADD")

    print_out(f"🎄 Added {recommended_tree_type} Christmas Tree to '{list_name}'.")
    show_user_menu()


print_out(get_random_quote(cursor))
show_main_menu()

root.mainloop()

cursor.close()
db.close()
