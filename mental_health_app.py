import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from textblob import TextBlob
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
import sqlite3

# Database setup
DB_NAME = "mental_health.db"
def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT,
            answer TEXT,
            sentiment TEXT,
            emotion TEXT,
            confidence REAL,
            timestamp TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

class MentalHealthBot:
    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.root.title("AuraMind")
        self.root.geometry("700x550")

        self.questions = [
            "How have you been feeling emotionally in the past few days?",
            "Do you feel overwhelmed or under pressure lately?",
            "Are you sleeping well and feeling rested?",
            "Have you had interest in activities you usually enjoy?",
            "How has your appetite been recently?",
            "Do you feel supported by friends or family?",
            "Do you feel anxious or worried about things?",
            "Are you able to concentrate on tasks or studies?",
            "Do you feel hopeful about the future?",
            "Would you like to share anything else about your mental well-being?"
        ]
        self.current_question_index = 0
        self.responses = []

        self.frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.frame.pack(padx=30, pady=30, fill="both", expand=True)

        self.header = ctk.CTkLabel(
            self.frame,
            text="Mental Health Check-In",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="center"
        )
        self.header.pack(pady=(20, 10))

        self.subheader = ctk.CTkLabel(
            self.frame,
            text=f"Welcome, {self.username}! Please answer the following questions as honestly as possible.",
            font=ctk.CTkFont(size=14),
            wraplength=600,
            justify="center"
        )
        self.subheader.pack(pady=(0, 20))

        self.question_label = ctk.CTkLabel(
            self.frame,
            text="",
            font=ctk.CTkFont(size=16),
            wraplength=600,
            justify="center"
        )
        self.question_label.pack(pady=10)

        self.entry = ctk.CTkEntry(self.frame, width=550, height=35, placeholder_text="Type your response here...")
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', lambda event: self.handle_response())

        button_row = ctk.CTkFrame(self.frame)
        button_row.pack(pady=20)

        self.button = ctk.CTkButton(button_row, text="Next", width=120, command=self.handle_response)
        self.button.pack(side="left", padx=10)

        self.history_button = ctk.CTkButton(button_row, text="Mood History", width=150, command=self.show_mood_graph)
        self.history_button.pack(side="left", padx=10)

        self.export_button = ctk.CTkButton(button_row, text="Export Report", width=150, command=self.export_report)
        self.export_button.pack(side="left", padx=10)

        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            self.question_label.configure(text=f"Q{self.current_question_index+1}: {self.questions[self.current_question_index]}")
            self.entry.delete(0, tk.END)
        else:
            self.show_quiz_results()  #  Show results instead of "Completed" message

    def handle_response(self):
        user_response = self.entry.get().strip()
        if not user_response:
            messagebox.showwarning("Input Error", "Please enter a response.")
            return
        if len(user_response.split()) < 3:
            messagebox.showwarning("Try to elaborate", "Your answer is a bit short. Could you share a little more detail?")
            return

        question = self.questions[self.current_question_index]
        blob = TextBlob(user_response)
        sentiment_score = blob.sentiment.polarity
        sentiment_label = "POSITIVE" if sentiment_score > 0.1 else "NEGATIVE" if sentiment_score < -0.1 else "NEUTRAL"
        emotion_label = "Joy" if sentiment_score > 0.3 else "Sadness" if sentiment_score < -0.3 else "Neutral"
        confidence = round(abs(sentiment_score) * 100, 1)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO responses (user_id, question, answer, sentiment, emotion, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.user_id, question, user_response, sentiment_label, emotion_label, confidence, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        self.responses.append({  # Store the response with score
            "question": question,
            "answer": user_response,
            "sentiment": sentiment_label,
            "emotion": emotion_label,
            "confidence": confidence,
            "sentiment_score": sentiment_score # Store numerical score for analysis
        })

        self.current_question_index += 1
        self.display_question()

    def show_quiz_results(self):
        # Clear the existing frame
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.results_header = ctk.CTkLabel(
            self.frame,
            text="Quiz Results",
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="center"
        )
        self.results_header.pack(pady=(20, 10))

        results_text = ""
        overall_sentiment_score = 0
        for i, response in enumerate(self.responses):
            results_text += f"Q{i + 1}: {response['question']}\n"
            results_text += f"  Your Answer: {response['answer']}\n"
            results_text += f"  Sentiment: {response['sentiment']}, Emotion: {response['emotion']}, Confidence: {response['confidence']}%\n\n"
            overall_sentiment_score += response['sentiment_score']

        self.results_textbox = ctk.CTkTextbox(self.frame, wrap="word", font=ctk.CTkFont(size=14))
        self.results_textbox.insert("0.0", results_text)
        self.results_textbox.configure(state="disabled")  # Make it read-only
        self.results_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        num_responses = len(self.responses)
        if num_responses > 0:
            average_sentiment_score = overall_sentiment_score / num_responses

            if average_sentiment_score > 0.2:
                conclusion = "Overall, your responses indicate a generally positive mood."
                tip = "Continue to engage in activities that bring you joy and maintain your positive outlook. Consider sharing your positive experiences with others."
            elif average_sentiment_score < -0.2:
                conclusion = "Overall, your responses suggest you may be experiencing some negative feelings."
                tip = "It might be helpful to engage in self-care activities, talk to a trusted friend or family member, or consider exploring resources for mental well-being. Remember, it's okay to seek support."
            else:
                conclusion = "Overall, your responses indicate a relatively neutral emotional state."
                tip = "Pay attention to your feelings throughout the day. If you notice any shifts, try to identify the triggers and engage in healthy coping mechanisms."

            self.conclusion_label = ctk.CTkLabel(self.frame, text=conclusion, font=ctk.CTkFont(size=16, weight="bold"))
            self.conclusion_label.pack(pady=(10, 5))

            self.tip_label = ctk.CTkLabel(self.frame, text=tip, wraplength=580, justify="center")
            self.tip_label.pack(pady=(5, 20))
        else:
            self.conclusion_label = ctk.CTkLabel(self.frame, text="No responses recorded.", font=ctk.CTkFont(size=16, weight="bold"))
            self.conclusion_label.pack(pady=(10, 5))

            self.tip_label = ctk.CTkLabel(self.frame, text="", wraplength=580, justify="center")
            self.tip_label.pack(pady=(5, 20))

        self.close_button = ctk.CTkButton(self.frame, text="Close", command=self.close_results)
        self.close_button.pack(pady=20)

    def close_results(self):
        self.root.destroy()  # Close the quiz window

    def show_mood_graph(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, emotion, confidence FROM responses WHERE user_id = ? ORDER BY timestamp", (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("No Data", "No previous mood records found.")
            return

        timestamps = [d[0][:16].replace("T", "\n") for d in data]
        confidence = [d[2] for d in data]

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(timestamps, confidence, marker='o', linestyle='-', color='blue')
        ax.set_title("Mood Confidence Over Time")
        ax.set_ylabel("Confidence (%)")
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45)

        chart_window = ctk.CTkToplevel(self.root)
        chart_window.title("Mood History")
        chart = FigureCanvasTkAgg(fig, master=chart_window)
        chart.draw()
        chart.get_tk_widget().pack(fill="both", expand=True)

    def export_report(self):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT question, answer, sentiment, emotion, confidence, timestamp FROM responses WHERE user_id=?", (self.user_id,))
        data = cursor.fetchall()
        conn.close()

        if not data:
            messagebox.showinfo("No Data", "No responses to export.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"Mental Health Report - {self.username}", ln=1, align="C")
        pdf.set_font("Arial", size=12)

        for i, (q, a, s, e, c, t) in enumerate(data, 1):
            pdf.multi_cell(0, 10, f"Q{i}: {q}\nA: {a}\nSentiment: {s}, Emotion: {e}, Confidence: {c}%\nDate: {t}\n")

        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if path:
            pdf.output(path)
            messagebox.showinfo("Saved", f"Report saved to {path}")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    create_tables()

    root = ctk.CTk()
    # Replace with actual user ID and username after login
    app = MentalHealthBot(root, user_id=1, username="demo_user")
    root.mainloop()