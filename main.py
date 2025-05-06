import customtkinter as ctk
from mental_health_app import MentalHealthBot
from graph_viewer import show_mood_graph
from report_generator import generate_pdf_report
from tkinter import messagebox, filedialog
from db import connect_db
from db import create_tables
from datetime import datetime
from login import LoginScreen

class MainMenuScreen:
    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username

        for widget in self.root.winfo_children():
            widget.destroy()

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=40, pady=40, fill="both", expand=True)

        self.title = ctk.CTkLabel(self.frame, text=f"Welcome, {username} 👋", font=ctk.CTkFont(size=26, weight="bold"))
        self.title.pack(pady=(10, 5))

        self.last_checkin = self.get_last_checkin_date()
        subtitle_text = f"Last check-in: {self.last_checkin}" if self.last_checkin else "No check-ins yet"
        self.subtitle = ctk.CTkLabel(self.frame, text=subtitle_text, font=ctk.CTkFont(size=14), text_color="gray")
        self.subtitle.pack(pady=(0, 20))

        self.prompt = ctk.CTkLabel(self.frame, text="What would you like to do today?", font=ctk.CTkFont(size=16))
        self.prompt.pack(pady=10)

        self.quiz_btn = ctk.CTkButton(self.frame, text="📝 Take Mental Health Quiz", width=300, height=40, command=self.start_quiz)
        self.quiz_btn.pack(pady=15)

        self.graph_btn = ctk.CTkButton(self.frame, text="📊 View Mood History Graph", width=300, height=40, command=self.view_graph)
        self.graph_btn.pack(pady=15)

        self.report_btn = ctk.CTkButton(self.frame, text="📄 Export PDF Report", width=300, height=40, command=self.export_report)
        self.report_btn.pack(pady=15)

        self.logout_btn = ctk.CTkButton(self.frame, text="🔓 Log Out", fg_color="gray30", hover_color="gray40", command=self.logout, width=150)
        self.logout_btn.pack(pady=30)

    def get_last_checkin_date(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM responses WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (self.user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            dt = datetime.fromisoformat(result[0])
            return dt.strftime("%b %d, %Y at %I:%M %p")
        return None

    def start_quiz(self):
        self.frame.destroy() 
        self.frame = None 
        self.quiz_instance = MentalHealthBot(self.root, self.user_id, self.username)
        
    def view_graph(self):
        show_mood_graph(self.root, self.user_id)

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="Mental_Health_Report.pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            result = generate_pdf_report(self.user_id, self.username, filename=path)
            if result:
                messagebox.showinfo("Success", f"Report saved to:\n{result}")
            else:
                messagebox.showerror("Error", "Could not generate report.")

    def logout(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        LoginScreen(self.root, on_login_success=MainMenuScreen)

    def logout(self):
        print("MainMenuScreen.logout() called")
        print("Destroying MainMenuScreen widgets...")
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.frame:
            print("Destroying MainMenuScreen frame...")
            self.frame.destroy()
        print("Creating LoginScreen...")
        LoginScreen(
            self.root,
            on_login_success=self.on_login_success
        )
        print("MainMenuScreen.logout() completed")

    def on_login_success(self, user_id, username):
        print(f"MainMenuScreen.on_login_success() called with user_id={user_id}, username={username}")
        print("Destroying existing widgets in preparation for MainMenuScreen...")
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.frame:  # Add this check
           self.frame.destroy()
        print("Creating MainMenuScreen...")
        MainMenuScreen(self.root, user_id, username)
        print("MainMenuScreen.on_login_success() completed")

class WelcomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x500")
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=30, pady=30, fill="both", expand=True)

        self.title = ctk.CTkLabel(
            self.frame,
            text="Welcome to AuraMind 🌿",
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.title.pack(pady=40)

        self.subtitle = ctk.CTkLabel(
            self.frame,
            text="Your personal mental health check-in and mood companion.",
            font=ctk.CTkFont(size=16),
            wraplength=600,
            justify="center"
        )
        self.subtitle.pack(pady=10)

        self.start_button = ctk.CTkButton(self.frame, text="Get Started", command=self.show_login)
        self.start_button.pack(pady=20)

    def show_login(self):
        print("WelcomeScreen.show_login() called")
        print("Destroying WelcomeScreen widgets...")
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.frame:
            print("Destroying WelcomeScreen frame...")
            self.frame.destroy()
        print("Creating LoginScreen...")
        LoginScreen(
            self.root,
            on_login_success=self.on_login_success
        )
        print("WelcomeScreen.show_login() completed")

    def on_login_success(self, user_id, username):
        print(f"WelcomeScreen.on_login_success() called with user_id={user_id}, username={username}")
        print("Destroying existing widgets...")
        for widget in self.root.winfo_children():
            widget.destroy()
        if self.frame:  # Add this check
           self.frame.destroy()
        print("Creating MainMenuScreen...")
        MainMenuScreen(self.root, user_id, username)
        print("WelcomeScreen.on_login_success() completed")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.title("AuraMind -Your Mental Health Companion")
    create_tables()
    WelcomeScreen(root)
    root.mainloop()