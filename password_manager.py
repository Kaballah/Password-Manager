import tkinter as tk
from tkinter import simpledialog, messagebox, Menu, ttk, filedialog, StringVar, Entry
from cryptography.fernet import Fernet
# from PIL import Image, ImageTk
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyperclip
import json
import os
import re
import string
import random
import pandas as pd
import webbrowser

# Generate a key for encryption
def generate_key():
    return Fernet.generate_key()

# Load or create a key file
def load_key():
    if not os.path.exists('key.key'):
        key = generate_key()
        with open('key.key', 'wb') as key_file:
            key_file.write(key)
    else:
        with open('key.key', 'rb') as key_file:
            key = key_file.read()
    return key

key = load_key()
cipher_suite = Fernet(key)

# Load or create a password file
def load_passwords():
    if not os.path.exists('passwords.json'):
        return {}
    with open('passwords.json', 'r') as file:
        return json.load(file)

passwords = load_passwords()

# Save passwords to the file
def save_passwords():
    with open('passwords.json', 'w') as file:
        json.dump(passwords, file)

# Convert to sentence case
def to_sentence_case(text):
    return text.capitalize()

# Flash the menu window to draw attention
def flash_window(window):
    for _ in range(5):
        window.attributes("-topmost", True)
        window.update()
        window.attributes("-topmost", False)
        window.update()

# Validate URL
def is_valid_url(url):
    return re.match(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url) is not None

# Validate if URL starts with HTTP
def is_http_url(url):
    return url.startswith("http://")

# Ensure only one menu is open at a time
menu_open = False

# Function to add a new password
def add_password():
    global menu_open
    if menu_open:
        return
    menu_open = True

    def on_cancel():
        global menu_open
        menu_open = False
        add_window.destroy()

    def on_close(event=None):
        global menu_open
        menu_open = False
        add_window.destroy()

    def on_add(event=None):
        site_name = site_name_entry.get().strip()
        website = website_entry.get().strip()
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not site_name or not website or not username or not password:
            messagebox.showwarning("Input Error", "All fields must be filled out.")
            return
        
        if is_http_url(website):
            proceed = messagebox.askyesno("Insecure URL", "The URL starts with http:// which is not secure. Do you want to continue?")
            if not proceed:
                return

        if not is_valid_url(website):
            messagebox.showwarning("Input Error", "Please enter a valid URL.")
            return

        site_name = to_sentence_case(site_name)
        encrypted_password = cipher_suite.encrypt(password.encode()).decode()

        # Save state for the undo and redo button
        save_state()

        passwords[site_name] = {'website': website, 'username': username, 'password': encrypted_password}
        save_passwords()
        refresh_password_list()
        messagebox.showinfo("Password Manager", "Password added!")
        on_cancel()

    add_window = tk.Toplevel(app)
    add_window.title("Add Password")
    add_window.geometry("400x310")
    add_window.resizable(False, False)
    add_window.protocol("WM_DELETE_WINDOW", on_close)
    add_window.bind("<Alt-F4>", on_close)
    add_window.bind("<Return>", on_add)

    # Apply a theme
    style = ttk.Style(add_window)
    style.theme_use('clam')

    ttk.Label(add_window, text="Site Name:").pack(pady=5)
    site_name_entry = tk.Entry(add_window)
    site_name_entry.pack(pady=5)

    tk.Label(add_window, text="Website:").pack(pady=5)
    website_entry = tk.Entry(add_window)
    website_entry.pack(pady=5)

    tk.Label(add_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(add_window)
    username_entry.pack(pady=5)

    tk.Label(add_window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(add_window, show="*")
    password_entry.pack(pady=5)

    # Create a frame to contain the buttons
    button_frame = ttk.Frame(add_window)
    button_frame.pack(pady=20)

    ttk.Button(button_frame, text="Add", command=on_add, style='Custom.TButton').pack(side='left', padx=10)
    ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side='left', padx=10)

    add_window.lift()

# Function to generate a secure password
def generate_password():
    global menu_open
    if menu_open:
        return
    menu_open = True

    def on_cancel():
        global menu_open
        menu_open = False
        gen_window.destroy()

    def on_close(event=None):
        global menu_open
        menu_open = False
        gen_window.destroy()

    def on_save(event=None):
        site_name = site_name_entry.get().strip()
        website = website_entry.get().strip()
        username = username_entry.get().strip()
        
        if not site_name or not website or not username:
            messagebox.showwarning("Input Error", "All fields must be filled out.")
            return
        
        if is_http_url(website):
            proceed = messagebox.askyesno("Insecure URL", "The URL starts with http:// which is not secure. Do you want to continue?")
            if not proceed:
                return

        if not is_valid_url(website):
            messagebox.showwarning("Input Error", "Please enter a valid URL.")
            return

        site_name = to_sentence_case(site_name)
        characters = string.ascii_letters + string.digits + string.punctuation
        secure_password = ''.join(random.choice(characters) for _ in range(24))  # Increase password length to 24 characters
        pyperclip.copy(secure_password)
        encrypted_password = cipher_suite.encrypt(secure_password.encode()).decode()

        save_state()
        
        passwords[site_name] = {'website': website, 'username': username, 'password': encrypted_password}
        save_passwords()
        refresh_password_list()
        messagebox.showinfo("Password Manager", f"Generated password copied to clipboard: {secure_password}")
        on_cancel()

    gen_window = tk.Toplevel(app)
    gen_window.title("Generate Password")
    gen_window.geometry("400x250")
    gen_window.resizable(False, False)
    gen_window.protocol("WM_DELETE_WINDOW", on_close)
    gen_window.bind("<Alt-F4>", on_close)
    gen_window.bind("<Return>", on_save)

    tk.Label(gen_window, text="Site Name:").pack(pady=5)
    site_name_entry = tk.Entry(gen_window)
    site_name_entry.pack(pady=5)

    tk.Label(gen_window, text="Website URL:").pack(pady=5)
    website_entry = tk.Entry(gen_window)
    website_entry.pack(pady=5)

    tk.Label(gen_window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(gen_window)
    username_entry.pack(pady=5)

    # Create a frame to contain the buttons
    button_frame = ttk.Frame(gen_window)
    button_frame.pack(pady=20)

    ttk.Button(button_frame, text="Generate & Save", command=on_save, style='Custom.TButton').pack(side='left', padx=10)
    ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side='left', padx=10)

    gen_window.lift()

# Function to filter site names for dropdown
def filter_sites(event, site_name_var, combobox):
    entered_text = site_name_var.get().strip().lower()
    matching_sites = [site for site in passwords.keys() if entered_text in site.lower()]
    combobox['values'] = matching_sites
    combobox.event_generate('<Down>')

# Retrieve a saved password
def retrieve_password():
    global menu_open
    if menu_open:
        return
    menu_open = True

    def on_cancel():
        global menu_open
        menu_open = False
        ret_window.destroy()

    def on_close(event=None):
        global menu_open
        menu_open = False
        ret_window.destroy()

    def on_retrieve(event=None):
        site_name = site_name_var.get().strip()

        if not site_name:
            messagebox.showwarning("Input Error", "Site name must be filled out.")
            return

        site_name = to_sentence_case(site_name)
        if site_name in passwords:
            save_state()

            decrypted_password = cipher_suite.decrypt(passwords[site_name]['password'].encode()).decode()
            messagebox.showinfo("Password Manager", f"Password for {site_name}: {decrypted_password}")
            pyperclip.copy(decrypted_password)
            on_cancel()
        else:
            messagebox.showerror("Password Manager", "No password found for this site.")

    ret_window = tk.Toplevel(app)
    ret_window.title("Retrieve Password")
    ret_window.geometry("400x200")
    ret_window.resizable(False, False)
    ret_window.protocol("WM_DELETE_WINDOW", on_close)
    ret_window.bind("<Alt-F4>", on_close)
    ret_window.bind("<Return>", on_retrieve)

    tk.Label(ret_window, text="Site Name:").pack(pady=5)
    site_name_var = StringVar()
    site_name_combobox = ttk.Combobox(ret_window, textvariable=site_name_var)
    site_name_combobox.pack(pady=5)
    site_name_combobox['values'] = list(passwords.keys())
    site_name_combobox.bind("<KeyRelease>", lambda event: filter_sites(event, site_name_var, site_name_combobox))

    button_frame = tk.Frame(ret_window)
    button_frame.pack(pady=50)

    ttk.Button(button_frame, text="OK", command=on_retrieve, style='Custom.TButton').pack(side=tk.LEFT, padx=5)
    ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side=tk.LEFT, padx=5)

    ret_window.lift()

# Update an existing password
def update_password():
    global menu_open
    if menu_open:
        return
    menu_open = True

    def on_cancel():
        global menu_open
        menu_open = False
        update_window.destroy()

    def on_close(event=None):
        global menu_open
        menu_open = False
        update_window.destroy()

    def on_update(event=None):
        site_name = site_name_var.get().strip()
        password = password_entry.get().strip()

        if not site_name or not password:
            messagebox.showwarning("Input Error", "Both fields must be filled out.")
            return

        site_name = to_sentence_case(site_name)
        if site_name in passwords:
            save_state()

            encrypted_password = cipher_suite.encrypt(password.encode()).decode()
            passwords[site_name]['password'] = encrypted_password
            save_passwords()
            refresh_password_list()
            messagebox.showinfo("Password Manager", "Password updated!")
            on_cancel()
        else:
            messagebox.showerror("Password Manager", "No password found for this site.")

    def suggest_password():
        characters = string.ascii_letters + string.digits + string.punctuation
        secure_password = ''.join(random.choice(characters) for _ in range(24))
        password_entry.delete(0, tk.END)
        password_entry.insert(0, secure_password)
        pyperclip.copy(secure_password)

    update_window = tk.Toplevel(app)
    update_window.title("Update Password")
    update_window.geometry("550x200")
    update_window.resizable(False, False)
    update_window.protocol("WM_DELETE_WINDOW", on_close)
    update_window.bind("<Alt-F4>", on_close)
    update_window.bind("<Return>", on_update)

    fields_frame = ttk.Frame(update_window)
    fields_frame.pack(pady=20, padx=20)

    tk.Label(fields_frame, text="Site Name:").pack(side='left', pady=5, padx=5)
    site_name_var = StringVar()
    site_name_combobox = ttk.Combobox(fields_frame, textvariable=site_name_var)
    site_name_combobox.pack(side='left', pady=5, padx=5)
    site_name_combobox['values'] = list(passwords.keys())
    site_name_combobox.bind("<KeyRelease>", lambda event: filter_sites(event, site_name_var, site_name_combobox))

    tk.Label(fields_frame, text="New Password:").pack(side='left', pady=5, padx=5)
    password_entry = tk.Entry(fields_frame, show="*")
    password_entry.pack(side='left', pady=5, padx=5)

    # suggest_frame = tk.Frame(update_window)
    # suggest_frame.pack(anchor="e", padx=50, pady=0)

    ttk.Button(update_window, text="Suggest Password", command=suggest_password, style='Custom.TButton').pack(anchor="e", padx=50, pady=0)

    button_frame = tk.Frame(update_window)
    button_frame.pack(pady=20)

    ttk.Button(button_frame, text="OK", command=on_update, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=10)
    ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=10)
    
    update_window.lift()

# Find functionality
def find_record(event):
    query = find_entry.get().strip().lower()
    for row in tree.get_children():
        tree.delete(row)
    for site_name, details in passwords.items():
        if query in site_name.lower() or query in details['website'].lower() or query in details['username'].lower():
            tree.insert("", tk.END, values=(site_name, details['website'], details['username'], details['password']))

# Replace text in password manager
def replace_text():
    global menu_open, replace_window, match_indices, current_index, site_name_var, username_var, url_var
    if menu_open:
        return
    menu_open = True
    match_indices = []
    current_index = 0

    def on_cancel():
        global menu_open
        menu_open = False
        replace_window.destroy()

    def on_close(event=None):
        global menu_open
        menu_open = False
        replace_window.destroy()

    def search_matches():
        global match_indices
        search_text = search_entry.get().strip()
        match_indices = []

        if not search_text:
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return

        for site_name, details in passwords.items():
            if site_name_var.get() and search_text.lower() in site_name.lower():
                match_indices.append((site_name, "site_name"))
            elif username_var.get() and search_text.lower() in details['username'].lower():
                match_indices.append((site_name, "username"))
            elif url_var.get() and search_text.lower() in details['website'].lower():
                match_indices.append((site_name, "website"))

        if not match_indices:
            messagebox.showinfo("No Matches", "No matching records found.")
            return

        current_index = 0
        highlight_match()

    def highlight_match():
        if not match_indices:
            return

        site_name, field = match_indices[current_index]
        details = passwords[site_name]
        
        record_text = f"Site Name: {site_name}\nUsername: {details['username']}\nURL: {details['website']}\n"
        record_label.config(text=record_text, padx=50)

        highlight_field(field, details)

    def highlight_field(field, details):
        search_text = search_entry.get().strip()
        site_name, field = match_indices[current_index]

        if field == "site_name":
            start_idx = site_name.lower().index(search_text.lower())
            end_idx = start_idx + len(search_text)
            site_name_entry.delete(0, tk.END)
            site_name_entry.insert(0, site_name)
            site_name_entry.selection_range(start_idx, end_idx)
        elif field == "username":
            start_idx = details['username'].lower().index(search_text.lower())
            end_idx = start_idx + len(search_text)
            username_entry.delete(0, tk.END)
            username_entry.insert(0, details['username'])
            username_entry.selection_range(start_idx, end_idx)
        elif field == "website":
            start_idx = details['website'].lower().index(search_text.lower())
            end_idx = start_idx + len(search_text)
            url_entry.delete(0, tk.END)
            url_entry.insert(0, details['website'])
            url_entry.selection_range(start_idx, end_idx)

    def next_match():
        global current_index
        if match_indices:
            current_index = (current_index + 1) % len(match_indices)
            highlight_match()

    def previous_match():
        global current_index
        if match_indices:
            current_index = (current_index - 1) % len(match_indices)
            highlight_match()

    def replace_current():
        if not match_indices:
            return

        new_text = replace_entry.get().strip()
        if not new_text:
            messagebox.showwarning("Input Error", "Please enter a replacement value.")
            return

        site_name, field = match_indices[current_index]

        if field == "site_name":
            passwords[new_text] = passwords.pop(site_name)
        elif field == "username":
            passwords[site_name]['username'] = new_text
        elif field == "website":
            passwords[site_name]['website'] = new_text

        save_passwords()
        refresh_password_list()
        messagebox.showinfo("Password Manager", f"{field.capitalize()} replaced successfully!")
        search_matches()

    replace_window = tk.Toplevel(app)
    replace_window.title("Replace Password")
    replace_window.geometry("500x250")
    replace_window.resizable(False, False)
    replace_window.protocol("WM_DELETE_WINDOW", on_close)
    replace_window.bind("<Alt-F4>", on_close)

    # Frame for search and replace fields
    search_replace_frame = tk.Frame(replace_window)
    search_replace_frame.pack(pady=10, padx=10)

    tk.Label(search_replace_frame, text="Search For:").grid(row=0, column=0, padx=5, pady=5)
    search_entry = tk.Entry(search_replace_frame, width=20)
    search_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(search_replace_frame, text="Replace With:").grid(row=0, column=2, padx=5, pady=5)
    replace_entry = tk.Entry(search_replace_frame, width=20)
    replace_entry.grid(row=0, column=3, padx=5, pady=5)

    # Frame for search in option and search button
    search_button_frame = tk.Frame(replace_window)
    search_button_frame.pack(pady=10)

    tk.Label(search_button_frame, text="Search in:").pack(side=tk.LEFT, padx=5, pady=0)

    # Variables to store checkbox states
    site_name_var = tk.BooleanVar()
    username_var = tk.BooleanVar()
    url_var = tk.BooleanVar()

    # Checkboxes for multiple selection
    site_name_check = ttk.Checkbutton(search_button_frame, text="Site Name", variable=site_name_var)
    username_check = ttk.Checkbutton(search_button_frame, text="Username", variable=username_var)
    url_check = ttk.Checkbutton(search_button_frame, text="URL", variable=url_var)

    # Pack checkboxes
    site_name_check.pack(side=tk.LEFT, padx=5, pady=0)
    username_check.pack(side=tk.LEFT, padx=5, pady=5)
    url_check.pack(side=tk.LEFT, padx=5, pady=5)

    # Search button
    ttk.Button(search_button_frame, text="Search", command=search_matches, style='Custom.TButton').pack(side=tk.RIGHT, padx=20, pady=5)

    record_label = tk.Label(replace_window, text="", justify=tk.LEFT, anchor="w")
    record_label.pack(pady=5, fill="x")

    site_name_entry = tk.Entry(replace_window)
    username_entry = tk.Entry(replace_window)
    url_entry = tk.Entry(replace_window)

    button_frame = ttk.Frame(replace_window)
    button_frame.pack(padx=10, pady=10, fill='x')

    # Create spacer frames
    ttk.Frame(button_frame).pack(side=tk.LEFT, expand=True)

    ttk.Button(button_frame, text="Previous", command=previous_match, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=0)
    ttk.Button(button_frame, text="Next", command=next_match, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=0)
    ttk.Button(button_frame, text="Replace", command=replace_current, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=0)
    ttk.Button(button_frame, text="Cancel", command=on_cancel, style='Custom.TButton').pack(side=tk.LEFT, padx=5, pady=0)

    ttk.Frame(button_frame).pack(side=tk.LEFT, expand=True)

    replace_window.lift()

def show_help_window():
    help_window = tk.Toplevel(app)
    help_window.title("Help")
    help_window.geometry("400x450")
    help_window.resizable(False, False)

    notebook = ttk.Notebook(help_window)

    def setup_text_styles(text_widget):
        text_widget.tag_configure('bold', font=('Arial', 12, 'bold'))
        text_widget.tag_configure('italic', font=('Arial', 9, 'italic'))
        text_widget.tag_configure('underline', underline=True)
        text_widget.tag_configure('center', justify='center')
        text_widget.tag_configure('right', justify='right')

    def insert_text_with_styles(text_widget):
        text_widget.insert('1.0', "Getting Started\n", 'bold center')
        text_widget.insert('end', "1. Launch the Application: Double-click the application icon to open the Password Manager.\n")
        text_widget.insert('end', "2. Initial Setup: Upon first launch, you will see the main window with a list of stored password records, if any.\n\n")
        
        text_widget.insert('end', "\nMain Window\n", 'bold center')
        text_widget.insert('end', "The main window contains the following components:\n")
        text_widget.insert('end', "1. Tree View: ")
        text_widget.insert('end', "Displays all password records in a tabular format with columns for Site Name, Username, URL, and Password\n\n")
        text_widget.insert('end', "2. Buttons:\n")
        text_widget.insert('end', "     • Add: Opens a window to add a new password record.\n")
        text_widget.insert('end', "     • Edit: Opens a window to edit the selected record.\n")
        text_widget.insert('end', "     • Delete: Deletes the selected record after confirmation.\n")
        text_widget.insert('end', "     • Search: Searches for records based on the entered search term.\n")
        text_widget.insert('end', "     • Replace: Opens a window to search and replace text in the records.\n\n")
        text_widget.insert('end', "3. Menu Bar:\n")
        text_widget.insert('end', "     • File: Contains options like Help.\n")
        text_widget.insert('end', "     • Theme: Allows you to change the application's theme.\n")

        text_widget.insert('end', "\nAdding a New Record\n", 'bold center')
        text_widget.insert('end', "1. Open Add Window: Click the 'Add' button or press Alt + A.\n")
        text_widget.insert('end', "2. Enter Details: Fill in the Site Name, Username, Password, and URL.\n")
        text_widget.insert('end', "3. Save Record: Click the 'Save' button to store the new record.\n\n")

        text_widget.insert('end', "\nEditing a Record\n", 'bold center')
        text_widget.insert('end', "1. Select a Record: Click on a record in the tree view to select it.\n")
        text_widget.insert('end', "2. Open Edit Window: Click the 'Edit' button or press Alt + E.\n")
        text_widget.insert('end', "3. Edit Details: Modify the Site Name, Username, and URL. The Password field is not editable.\n")
        text_widget.insert('end', "4. Save Changes: Click the 'Save' button to update the record.\n\n")

        text_widget.insert('end', "\nDeleting a Record\n", 'bold center')
        text_widget.insert('end', "1. Select a Record: Click on a record in the tree view to select it.\n")
        text_widget.insert('end', "2. Delete Record: Click the 'Delete' button or press Alt + D.\n")
        text_widget.insert('end', "3. Confirm Deletion: A prompt will appear asking for confirmation. Click 'Yes' to delete the record.\n\n")

        text_widget.insert('end', "\nSearching Records\n", 'bold center')
        text_widget.insert('end', "1. Enter Search Term: Type the search term in the search box.\n")
        text_widget.insert('end', "2. Initiate Search: Click the 'Search' button or press Enter.\n")
        text_widget.insert('end', "3. View Results: The tree view will display only the records that match the search term.\n\n")

        text_widget.insert('end', "\nReplacing Text in Records\n", 'bold center')
        text_widget.insert('end', "1. Open Replace Window: Click the 'Replace' button or press Alt + R.\n")
        text_widget.insert('end', "2. Enter Search Term: Type the text you want to search for.\n")
        text_widget.insert('end', "3. Enter Replacement Text: Type the text you want to replace the search term with.\n")
        text_widget.insert('end', "4. Search and Replace:\n")
        text_widget.insert('end', "     • Previous: Click to view the previous match.\n")
        text_widget.insert('end', "     • Next: Click to view the next match.\n")
        text_widget.insert('end', "     • Replace: Click to replace the current match with the replacement text.\n")
        text_widget.insert('end', "     • Cancel: Click to close the replace window without making any changes.\n\n")

        text_widget.insert('end', "\nCopying and Editing Records\n", 'bold center')
        text_widget.insert('end', "1. Right-Click Context Menu:\n")
        text_widget.insert('end', "     • Copy: Right-click on a record and select 'Copy' to copy the selected cell's content to the clipboard.\n")
        text_widget.insert('end', "     • Edit: Right-click on a record and select 'Edit' to open the edit window with the selected record's details pre-filled.\n\n")

        text_widget.insert('end', "\nChanging Themes\n", 'bold center')
        text_widget.insert('end', "1. Open Theme Menu: Click on the 'Theme' menu.\n")
        text_widget.insert('end', "2. Select a Theme: Choose a theme from the list. The application's appearance will change based on the selected theme.\n\n")
        
        text_widget.insert('end', "\nHelp Menu\n", 'bold center')
        text_widget.insert('end', "1. Open Help Menu: Click on the 'File' menu and select 'Help' or press F1.\n")
        text_widget.insert('end', "2. Help Window: The help window contains three tabs:\n")
        text_widget.insert('end', "     • About: Provides an overview of the application.\n")
        text_widget.insert('end', "     • Usage Guide: Describes how to use the application and what each button does.\n")
        text_widget.insert('end', "     • Contact: Displays contact information including email, GitHub, Twitter, WhatsApp, and telephone number.\n")

        text_widget.config(state='disabled')

    # Function to send email
    def send_email():
        sender_email = email_entry.get()
        subject = email_subject_entry.get()
        message = email_message_entry.get("1.0", tk.END)

        # Validate input fields
        if not sender_email or not subject or not message.strip():
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        # Email configuration
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'snowdendoug07@gmail.com'
        smtp_password = 'ejqwhcmuohlxmowz'

        # Create a MIMEText object to represent the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'kabzkabala6@gmail.com'
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        try:
            # Establish a secure session with the Gmail SMTP server using TLS
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)

            # Send email
            server.sendmail(sender_email, 'kabzkabala6@gmail.com', msg.as_string())
            server.quit()

            messagebox.showinfo("Success", "Email sent successfully!")
            # Clear fields after sending
            email_entry.delete(0, tk.END)
            email_subject_entry.delete(0, tk.END)
            email_message_entry.delete("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email. Error: {str(e)}")

    def open_github():
        webbrowser.open_new("https://github.com/kaballah")

    def open_twitter():
        webbrowser.open_new("https://twitter.com/mckaballah")

    def open_whatsapp():
        webbrowser.open_new("https://wa.me/254769692554")

    def open_tel():
        webbrowser.open_new("tel:+254769692554")

    # Tab 1: About
    about_frame = ttk.Frame(notebook)
    notebook.add(about_frame, text="Overview")
    about_text = tk.Text(about_frame, wrap='word', height=15, width=50)
    about_text.pack(expand=True, fill='both', padx=10, pady=10)
    about_text.insert('1.0', "This application, a comprehensive password manager, is a project I've always been passionate about creating. As someone who constantly juggles multiple online accounts, I recognized the need for a secure and efficient way to manage passwords. The application provides a user-friendly interface where users can store, edit, and manage their passwords securely. It features a robust search and replace functionality, making it easy to update passwords and other details. Additionally, it offers a theming option, allowing users to customize the look and feel of the application to suit their preferences.\n\n\n\n")
    about_text.insert('2.0', "\n")
    about_text.insert('3.0', "Developing this password manager has been an exciting journey as it is my first major project. It represents my foray into creating practical, real-world applications that solve everyday problems. By integrating features such as the help menu with comprehensive guidance, and ensuring ease of use with functionalities like copy, edit, and context-aware search, I've aimed to make password management less of a chore and more of a streamlined process. This project not only showcases my programming skills but also my dedication to creating tools that enhance digital security and user experience.")
    about_text.insert('4.0', "\n")
    about_text.insert('5.0', "Thank you for downloading this software. Your use is greatly appreciated.")
    about_text.config(state='disabled')

    # Tab 2: How To
    howto_frame = ttk.Frame(notebook)
    notebook.add(howto_frame, text="How to")
    howto_text = tk.Text(howto_frame, wrap='word', height=15, width=50)
    howto_text.pack(expand=True, fill='both', padx=10, pady=10)

    setup_text_styles(howto_text)
    insert_text_with_styles(howto_text)

    # Tab 3: Contact
    contact_frame = ttk.Frame(notebook)
    notebook.add(contact_frame, text="Contact Me")

    # Email Form
    email_label = ttk.Label(contact_frame, text="Email Form", font=("Arial", 12, "bold"))
    email_label.pack(pady=10)

    email_entry_frame = ttk.Frame(contact_frame)
    email_entry_frame.pack(pady=(20, 10))

    # Email Entry
    email_label = ttk.Label(email_entry_frame, text="Your Email:")
    email_label.grid(row=0, column=0, padx=10, pady=5)

    email_entry = ttk.Entry(email_entry_frame, width=40)
    email_entry.grid(row=0, column=1, padx=10, pady=5)

    # Contact Form
    email_subject_frame = ttk.Frame(contact_frame)
    email_subject_frame.pack(pady=(20, 10))

    email_subject_label = ttk.Label(email_subject_frame, text="Subject:")
    email_subject_label.pack(side=tk.LEFT, padx=10, pady=5)
    email_subject_entry = ttk.Entry(email_subject_frame, width=40)
    email_subject_entry.pack(side=tk.LEFT, padx=10, pady=5)

    email_message_frame = ttk.Frame(contact_frame)
    email_message_frame.pack(pady=(20, 10))

    email_message_label = ttk.Label(email_message_frame, text="Message:")
    email_message_label.pack(side=tk.LEFT, padx=10, pady=5)
    email_message_entry = tk.Text(email_message_frame, wrap='word', height=5, width=30)
    email_message_entry.pack(side=tk.LEFT, padx=10, pady=5)

    send_email_button = ttk.Button(contact_frame, text="Send Email", command=send_email)
    send_email_button.pack(pady=10)

    # Other Contact Options
    other_contacts_label = ttk.Label(contact_frame, text="You can also reach me through:")
    other_contacts_label.pack(pady=10)

    # Frame to contain the buttons side by side
    button_frame = ttk.Frame(contact_frame)
    button_frame.pack()

    github_button = ttk.Button(button_frame, text="GitHub", command=open_github)
    github_button.pack(side=tk.LEFT, padx=10, pady=5)

    twitter_button = ttk.Button(button_frame, text="Twitter", command=open_twitter)
    twitter_button.pack(side=tk.LEFT, padx=10, pady=5)

    whatsapp_button = ttk.Button(button_frame, text="WhatsApp", command=open_whatsapp)
    whatsapp_button.pack(side=tk.LEFT, padx=10, pady=5)

    tel_button = ttk.Button(button_frame, text="Tel", command=open_tel)
    tel_button.pack(side=tk.LEFT, padx=10, pady=5)

    # Function to send email (not fully implemented, you would need to implement this according to your needs)
    def send_email(subject, message):
        # Implement email sending logic here
        print(f"Subject: {subject}")
        print(f"Message: {message}")
        messagebox.showinfo("Email Sent", "Your email has been sent successfully.")

    notebook.pack(expand=True, fill='both')

# Function to refresh the password list display
def refresh_password_list():
    for row in tree.get_children():
        tree.delete(row)
    
    for site_name, details in passwords.items():
        tree.insert("", tk.END, values=(site_name, details['website'], details['username'], details['password']))

# Sort the password list display
def sort_tree(column, reverse):
    try:
        # Print column names for debugging
        print(f"Sorting column: {column}")

        # Verify if column exists in the Treeview
        column_exists = False
        for col in tree["columns"]:
            if col == column:
                column_exists = True
                break

        if not column_exists:
            raise ValueError(f"Column '{column}' does not exist in the Treeview.")

        # Create a list of tuples (column value, item ID) and sort it
        l = [(tree.set(k, column), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        # Adjust the column header for next sort
        tree.heading(column, command=lambda: sort_tree(column, not reverse))
    except Exception as e:
        print(f"Error in sort_tree: {e}")

# Create a context menu for right-click options
def on_right_click(event):
    item = tree.selection()
    if not item:
        return

    def copy_record():
        col = tree.identify_column(event.x)
        col_name = col[1:]  # Remove '#' prefix
        values = tree.item(item[0], 'values')
        pyperclip.copy(values[int(col_name) - 1])
        messagebox.showinfo("Copied", f"{col_name.capitalize()} copied to clipboard.")

    def edit_record():
        def on_save():
            new_values = [site_entry.get(), website_entry.get(), username_entry.get(), password_entry.get()]
            tree.item(item[0], values=new_values)
            edit_window.destroy()

        values = tree.item(item[0], 'values')
        edit_window = tk.Toplevel(app)
        edit_window.title("Edit Record")
        edit_window.geometry("300x200")
        edit_window.resizable(False, False)

        tk.Label(edit_window, text="Site:").grid(row=0, column=0, padx=5, pady=5)
        site_entry = tk.Entry(edit_window, width=35)
        site_entry.grid(row=0, column=1, padx=5, pady=5)
        site_entry.insert(0, values[0])

        tk.Label(edit_window, text="Website:").grid(row=1, column=0, padx=5, pady=5)
        website_entry = tk.Entry(edit_window, width=35)
        website_entry.grid(row=1, column=1, padx=5, pady=5)
        website_entry.insert(0, values[1])

        tk.Label(edit_window, text="Username:").grid(row=2, column=0, padx=5, pady=5)
        username_entry = tk.Entry(edit_window, width=35)
        username_entry.grid(row=2, column=1, padx=5, pady=5)
        username_entry.insert(0, values[2])

        tk.Label(edit_window, text="Password:").grid(row=3, column=0, padx=5, pady=5)
        password_entry = tk.Entry(edit_window, width=35, state='disabled')
        password_entry.grid(row=3, column=1, padx=5, pady=5)
        password_entry.insert(0, values[3])

        ttk.Button(edit_window, text="Save", command=on_save, style='Custom.TButton').grid(row=4, columnspan=2, pady=10)

    menu = Menu(app, tearoff=0)
    menu.add_command(label="Copy", command=copy_record)
    menu.add_command(label="Edit", command=edit_record)
    menu.post(event.x_root, event.y_root)

# Create undo and redo stacks
undo_stack = []
redo_stack = []

# Function to save the current state to the undo stack
def save_state():
    undo_stack.append(passwords.copy())
    if len(undo_stack) > 100:  # Limit the undo stack to 100 entries
        undo_stack.pop(0)
    redo_stack.clear()  # Clear the redo stack whenever a new state is saved

# Function to undo the last change
def undo():
    if undo_stack:
        redo_stack.append(passwords.copy())
        passwords.clear()
        passwords.update(undo_stack.pop())
        save_passwords()
        refresh_password_list()

# Function to redo the last undone change
def redo():
    if redo_stack:
        undo_stack.append(passwords.copy())
        passwords.clear()
        passwords.update(redo_stack.pop())
        save_passwords()
        refresh_password_list()

# Theme function
def change_theme(theme):
    style.theme_use(theme)

# Create the main application window
app = tk.Tk()
app.title("Password Manager")

# Create a custom style for the button
style = ttk.Style(app)
style.configure('Custom.TButton', background='#f0f0f0', borderwidth=1, relief='raised', foreground='black')

# Create a menu bar
menu_bar = Menu(app)
app.config(menu=menu_bar)

# Add "File" menu with options
file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Add Password", command=add_password, accelerator="F2")
file_menu.add_command(label="Generate Password", command=generate_password, accelerator="F3")
file_menu.add_command(label="Retrieve Password", command=retrieve_password, accelerator="F4")
file_menu.add_command(label="Update Password", command=update_password, accelerator="F6")
file_menu.add_separator()
file_menu.add_command(label="Help", command=show_help_window, accelerator="F1")
menu_bar.add_cascade(label="File", menu=file_menu)

# Add "Edit" menu with options
edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Undo", accelerator="Ctrl+Z")
edit_menu.add_command(label="Redo", accelerator="Ctrl+Y")
edit_menu.add_separator()
edit_menu.add_command(label="Find", command=lambda: find_entry.focus(), accelerator="Ctrl+F")
edit_menu.add_command(label="Replace", command=replace_text, accelerator="Ctrl+H")
menu_bar.add_cascade(label="Edit", menu=edit_menu)

# Theme Menu
theme_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Theme", menu=theme_menu)

# Add available themes to the Theme menu
available_themes = style.theme_names()
for theme in available_themes:
    theme_menu.add_command(label=theme, command=lambda t=theme: change_theme(t))

# Find and Replace Frame
find_replace_frame = tk.Frame(app)
find_replace_frame.pack(fill='x')

find_label = tk.Label(find_replace_frame, text="Find:")
find_label.pack(side='left', padx=5)

find_entry = tk.Entry(find_replace_frame)
find_entry.pack(side='left', fill='x', expand=False, padx=5)
find_entry.bind("<KeyRelease>", find_record)

# replace_label = tk.Label(find_replace_frame, text="Replace:")
# replace_label.pack(side='left', padx=5)

# replace_entry = tk.Entry(find_replace_frame)
# replace_entry.pack(side='left', fill='x', expand=True, padx=5)
# replace_entry.bind("<Return>", replace_text)

# Create a treeview to list the passwords
columns = ('Site', 'Website', 'Username', 'Password')
tree = ttk.Treeview(app, columns=columns, show='headings')
tree.heading('Site', text='Site', command=lambda: sort_tree("Site", False))
tree.heading('Website', text='Website')
tree.heading('Username', text='Username', command=lambda: sort_tree("Username", False))
tree.heading('Password', text='Password')
tree.pack(fill='both', expand=True)

# Bind right-click event to show context menu
tree.bind("<Button-3>", on_right_click)

# Initialize the password list
refresh_password_list()

save_state()

# Add keyboard shortcuts
app.bind("<F2>", lambda event: add_password())
app.bind("<F3>", lambda event: generate_password())
app.bind("<F4>", lambda event: retrieve_password())
app.bind("<F6>", lambda event: update_password())
app.bind('<F1>', lambda event: show_help_window())
app.bind("<Control-f>", lambda event: find_entry.focus())
app.bind("<Control-h>", lambda event: replace_text())

app.mainloop()