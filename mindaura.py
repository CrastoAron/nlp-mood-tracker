import customtkinter as ctk
from tkinter import filedialog
from transformers import pipeline
from datetime import datetime

BOT_NAME = "Mental Health Check-in Bot"

# Load sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def analyze_sentiment(text):
    result = sentiment_analyzer(text)[0]
    return {
        "label": result['label'],
        "score": round(result['score'], 2)
    }

def get_questions():
    return [
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

class MentalHealthApp:
    def __init__(self, root):
        self.root = root
        self.root.title(BOT_NAME)
        self.root.geometry("600x450")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.questions = get_questions()
        self.responses = []
        self.current_question_index = 0

        self.title_label = ctk.CTkLabel(root, text="Welcome to the Mental Health Check-in Bot!", font=ctk.CTkFont(size=18, weight="bold"), wraplength=550)
        self.title_label.pack(pady=20)

        self.question_label = ctk.CTkLabel(root, text="", font=ctk.CTkFont(size=16), wraplength=550)
        self.question_label.pack(pady=10)

        self.entry = ctk.CTkEntry(root, width=500)
        self.entry.pack(pady=10)

        self.submit_button = ctk.CTkButton(root, text="Submit", command=self.handle_response)
        self.submit_button.pack(pady=10)

        self.start_questionnaire()

    def start_questionnaire(self):
        self.display_question()

    def display_question(self):
        if self.current_question_index < len(self.questions):
            self.question_label.configure(text=self.questions[self.current_question_index])
            self.entry.delete(0, 'end')
        else:
            self.end_questionnaire()

    def handle_response(self):
        user_response = self.entry.get().strip()
        if not user_response:
            ctk.CTkMessagebox.show_warning("Input Error", "Please enter a response.")
            return

        question = self.questions[self.current_question_index]
        self.responses.append((question, user_response))
        self.current_question_index += 1
        self.display_question()

    def end_questionnaire(self):
        analysis_results = [analyze_sentiment(f"Q: {q}\nA: {a}") for q, a in self.responses]

        positive = sum(1 for r in analysis_results if r["label"] == "POSITIVE")
        negative = len(analysis_results) - positive

        summary = "----- Mental Health Summary -----\n\n"
        for i, ((question, answer), result) in enumerate(zip(self.responses, analysis_results), 1):
            summary += f"Q{i}: {question}\n"
            summary += f"A: {answer}\n"
            summary += f"   Sentiment: {result['label']} (Confidence: {result['score'] * 100}%)\n\n"

        if negative > positive:
            summary += "🧠 It seems you're going through a tough time. Don't hesitate to talk to someone you trust or seek professional support."
        else:
            summary += "😊 You're doing pretty well overall! Keep up the self-care and positivity!"

        self.show_summary_window(summary)

    def show_summary_window(self, summary_text):
        summary_window = ctk.CTkToplevel(self.root)
        summary_window.title("Your Mental Health Summary")
        summary_window.geometry("650x500")

        summary_label = ctk.CTkLabel(summary_window, text="Your Summary", font=ctk.CTkFont(size=18, weight="bold"))
        summary_label.pack(pady=10)

        text_box = ctk.CTkTextbox(summary_window, width=600, height=350, wrap="word", corner_radius=10)
        text_box.insert("1.0", summary_text)
        text_box.configure(state="disabled")  # Make it read-only
        text_box.pack(padx=10, pady=10, expand=True, fill="both")

        button_frame = ctk.CTkFrame(summary_window)
        button_frame.pack(pady=10)

        save_button = ctk.CTkButton(button_frame, text="💾 Save to File", command=lambda: self.save_summary_to_file(summary_text))
        save_button.pack(side="left", padx=10)

        close_button = ctk.CTkButton(button_frame, text="❌ Close", command=summary_window.destroy)
        close_button.pack(side="right", padx=10)

    def save_summary_to_file(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"Mental_Health_Summary_{timestamp}.txt"
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_filename, filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text)
            ctk.CTkMessagebox.show_info("Saved", f"Summary saved successfully:\n{filepath}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = MentalHealthApp(root)
    root.mainloop()
