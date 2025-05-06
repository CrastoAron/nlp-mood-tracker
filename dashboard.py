import customtkinter as ctk

class Dashboard:
    def __init__(self, root, user_id, username, on_start, on_export, on_history):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.on_start = on_start
        self.on_export = on_export
        self.on_history = on_history

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=40, pady=40, fill="both", expand=True)

        ctk.CTkLabel(self.frame, text=f"Welcome, {username}!", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkButton(self.frame, text="📝 Start Questionnaire", command=self.start).pack(pady=10)
        ctk.CTkButton(self.frame, text="📈 View Mood History", command=self.on_history).pack(pady=10)
        ctk.CTkButton(self.frame, text="📤 Export Report", command=self.on_export).pack(pady=10)
        ctk.CTkButton(self.frame, text="🚪 Logout", command=self.logout).pack(pady=20)

    def start(self):
        self.frame.destroy()
        self.on_start()

    def logout(self):
        self.frame.destroy()
        from login import LoginScreen
        LoginScreen(self.root, self.root._app_start_callback)  # Reshow login
