import tkinter as tk
from tkinter import messagebox
import mysql.connector
import hashlib
import model
from model import open_db
# Variable globale pour stocker le niveau de l'utilisateur connecté
current_user_level = None
current_user_pseudo = None

# --- Connexion à la base MySQL ---
open_db()

# --- Fonction pour hacher un mot de passe ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- Fonction d'inscription ---
def register():
    username = entry_register_username.get()
    password1 = entry_register_password1.get()
    password2 = entry_register_password2.get()

    if password1 != password2:
        messagebox.showerror("Error", "Passwords do not match.")
        return

    hashed = hash_password(password1)

    try:
        conn = open_db()
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
        cursor.close()
        conn.close()

# --- Fonction de connexion ---
def login():
    global current_user_level, current_user_pseudo
    username = entry_login_username.get()
    password = entry_login_password.get()
    hashed = hash_password(password)

    try:
        conn = open_db()
        cursor = conn.cursor()
        cursor.execute("SELECT Pw_hash, level FROM pilots WHERE pseudo = %s", (username,))
        result = cursor.fetchone()

        if result and result[0] == hashed:
            current_user_level = result[1]
            current_user_pseudo = username
            messagebox.showinfo("Login successful", f"Welcome {username}!")
            import subprocess
            import sys

            root.destroy()
            # Launch main.py as a separate process
            subprocess.Popen([sys.executable, "main.py"])

        else:
            messagebox.showerror("Error", "Incorrect username or password.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cursor.close()
        conn.close()


def get_current_user():
    return current_user_pseudo, current_user_level

def set_current_user_pseudo(new_pseudo):
    global current_user_pseudo
    current_user_pseudo = new_pseudo


# --- Fonctions pour changer de page ---
def show_register():
    frame_login.pack_forget()
    frame_register.pack(padx=10, pady=10, fill="x")

def show_login():
    frame_register.pack_forget()
    frame_login.pack(padx=10, pady=10, fill="x")

def get_current_user():
    return current_user_pseudo, current_user_level
# --- Interface tkinter ---
root = tk.Tk()
root.title("Login / Register")

# --- Frame d'inscription ---
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

# --- Frame de connexion ---
frame_login = tk.LabelFrame(root, text="Login")

tk.Label(frame_login, text="Username:").pack()
entry_login_username = tk.Entry(frame_login)
entry_login_username.pack()

tk.Label(frame_login, text="Password:").pack()
entry_login_password = tk.Entry(frame_login, show="*")
entry_login_password.pack()

tk.Button(frame_login, text="Login", command=login).pack(pady=5)
tk.Button(frame_login, text="Create an account", command=show_register).pack()

# --- Démarrer avec la page de connexion ---
show_login()

root.mainloop()
