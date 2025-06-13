import tkinter as tk
from tkinter import messagebox
import mysql.connector
import hashlib
import subprocess
import sys

import model
from model import open_db

# Global variables
current_user_level = None
current_user_pseudo = None

# --- Database Connection ---
#open_db() #moved to where it is needed

# --- Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Registration Function ---
def register():
    username = entry_register_username.get()
    password1 = entry_register_password1.get()
    password2 = entry_register_password2.get()

    if password1 != password2:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    hashed = hash_password(password1)

    conn = None # Initialize conn to None
    try:
        conn = open_db()
        if conn is None:
            messagebox.showerror("Error", "Failed to connect to the database.")
            return

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pilots (Pseudo, Pw_hash, level) VALUES (%s, %s, %s)",
            (username, hashed, 0)
        )
        conn.commit()
        messagebox.showinfo("Success", "Registration successful.")
        show_login()  # Redirige vers la page de connexion après inscription
    except mysql.connector.errors.IntegrityError:
        messagebox.showerror("Error", "Username already taken.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if conn: # Check if conn is not None before attempting to close
            if conn.is_connected():
                cursor = conn.cursor() #create cursor
                cursor.close()
                conn.close()

# --- Login Function ---
def login():
    global current_user_level, current_user_pseudo
    username = entry_login_username.get()
    password = entry_login_password.get()
    hashed = hash_password(password)

    conn = None
    try:
        conn = open_db()
        if conn is None:
            messagebox.showerror("Error", "Failed to connect to the database.")
            return

        cursor = conn.cursor()
        cursor.execute("SELECT Pw_hash, level FROM pilots WHERE pseudo = %s", (username,))
        result = cursor.fetchone()

        if result and result[0] == hashed:
            current_user_level = result[1]
            current_user_pseudo = username
            messagebox.showinfo("Login successful", f"Welcome {username}!")

            # Fermer la fenêtre login
            root.destroy()

            # Importer main.py et ouvrir la fenêtre principale
            import main
            main.open_main_window(current_user_pseudo, current_user_level)

        else:
            messagebox.showerror("Error", "Incorrect username or password.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        if conn:
            cursor.close()
            conn.close()


def get_current_user():
    return current_user_pseudo, current_user_level

def set_current_user_pseudo(new_pseudo):
    global current_user_pseudo
    current_user_pseudo = new_pseudo

# --- Page Navigation ---
def show_register():
    frame_login.pack_forget()
    frame_register.pack(padx=10, pady=10, fill="x")

def show_login():
    frame_register.pack_forget()
    frame_login.pack(padx=10, pady=10, fill="x")

# --- Tkinter UI ---
root = tk.Tk()
root.title("Login / Register")

# --- Register Frame ---
frame_register = tk.LabelFrame(root, text="Register")

tk.Label(frame_register, text="Username:").pack()
entry_register_username = tk.Entry(frame_register)
entry_register_username.pack()

tk.Label(frame_register, text="Password:").pack()
entry_register_password1 = tk.Entry(frame_register, show="*")
entry_register_password1.pack()

tk.Label(frame_register, text="Repeat password:").pack()
entry_register_password2 = tk.Entry(frame_register, show="*")
entry_register_password2.pack()

tk.Button(frame_register, text="Register", command=register).pack(pady=5)
tk.Button(frame_register, text="Back to Login", command=show_login).pack()

# --- Login Frame ---
frame_login = tk.LabelFrame(root, text="Login")

tk.Label(frame_login, text="Username:").pack()
entry_login_username = tk.Entry(frame_login)
entry_login_username.pack()

tk.Label(frame_login, text="Password:").pack()
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.pack()

tk.Button(frame_login, text="Login", command=login).pack(pady=5)
tk.Button(frame_login, text="Create an account", command=show_register).pack()

# --- Start with Login Page ---
show_login()

# --- Main Loop ---
root.mainloop()
