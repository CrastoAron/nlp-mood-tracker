from fpdf import FPDF
from db import connect_db
from datetime import datetime
import matplotlib.pyplot as plt

def generate_mood_graph_image(user_id, output_path="mood_chart.png"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, emotion, confidence FROM responses WHERE user_id=? ORDER BY timestamp", (user_id,))
    data = cursor.fetchall()
    conn.close()

    if not data:
        return None

    timestamps = [d[0][:16].replace("T", "\n") for d in data]
    confidence = [d[2] for d in data]

    plt.figure(figsize=(6, 3))
    plt.plot(timestamps, confidence, marker='o', linestyle='-', color='blue')
    plt.xticks(rotation=45)
    plt.title("Mood Confidence Over Time")
    plt.ylabel("Confidence (%)")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path

def generate_pdf_report(user_id, username, filename="MentalHealth_Report.pdf"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer, sentiment, emotion, confidence, timestamp FROM responses WHERE user_id=? ORDER BY timestamp", (user_id,))
    records = cursor.fetchall()
    conn.close()

    if not records:
        return None

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Mental Health Report - {username}", ln=1, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align="C")
    pdf.ln(5)

    for i, (q, a, s, e, c, t) in enumerate(records, 1):
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"Q{i}: {q}")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, f"A: {a}")
        pdf.cell(0, 8, f"Sentiment: {s}, Emotion: {e}, Confidence: {c}%", ln=1)
        pdf.cell(0, 8, f"Timestamp: {t}", ln=1)
        pdf.ln(4)

    graph_path = generate_mood_graph_image(user_id)
    if graph_path:
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Mood Confidence Trend", ln=1)
        pdf.image(graph_path, x=10, y=30, w=190)

    pdf.output(filename)
    return filename
