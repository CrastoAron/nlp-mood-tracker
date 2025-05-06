import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk
from db import connect_db
from datetime import datetime

def show_mood_graph(root, user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            DATE(timestamp) as date,
            AVG(confidence)
        FROM responses
        WHERE user_id = ? AND sentiment = 'POSITIVE'
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp)
    """, (user_id,))
    records = cursor.fetchall()
    conn.close()

    if not records:
        ctk.CTkMessagebox.show_info("No Data", "No positive mood records found.")
        return

    dates = [datetime.strptime(r[0], '%Y-%m-%d') for r in records]
    avg_confidence = [r[1] for r in records]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(dates, avg_confidence, marker='o', linestyle='-', color='green')  # Changed color to green
    ax.set_title("Daily Average Positive Mood Confidence")  # Updated title
    ax.set_ylabel("Average Confidence (%)")
    ax.set_xlabel("Date")  # Simplified x-axis label
    ax.set_ylim(0, 100)
    ax.grid(True)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format x-axis as dates
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    # Popup window
    graph_win = ctk.CTkToplevel(root)
    graph_win.title("Daily Mood Trend")  # Updated window title
    graph_win.geometry("700x500")

    chart = FigureCanvasTkAgg(fig, master=graph_win)
    chart.draw()
    chart.get_tk_widget().pack(fill="both", expand=True)