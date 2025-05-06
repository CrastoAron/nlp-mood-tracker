# login.py

import customtkinter as ctk
from tkinter import messagebox
from db import login_user, register_user

class LoginScreen:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=40, pady=40, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text="🧠 Mental Health Bot Login", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self.frame, placeholder_text="Username")
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(self.frame, placeholder_text="Password", show="*")
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self.frame, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(self.frame, text="Register", command=self.register).pack()

    def login(self):
        u, p = self.username_entry.get(), self.password_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "Please enter all fields.")
            return
        uid = login_user(u, p)
        if uid:
            self.frame.destroy()
            self.on_login_success(uid, u)  # Crucial: Call the callback
        else:
            messagebox.showerror("Failed", "Incorrect credentials.")

    def register(self):
        u, p = self.username_entry.get(), self.password_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "Please enter all fields.")
            return
        if register_user(u, p):
            messagebox.showinfo("Success", "Registered successfully.")
        else:
            messagebox.showerror("Failed", "Username already exists.")