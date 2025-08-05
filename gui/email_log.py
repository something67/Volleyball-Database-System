import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_email_log():
    win = tk.Toplevel()
    win.title("Email Log Viewer")
    win.geometry("950x500")

    tk.Label(win, text="Sent Email Logs", font=("Arial", 14, "bold")).pack(pady=10)

    # Table setup
    columns = ("Subject", "To", "From", "Date", "Body")
    tree = ttk.Treeview(win, columns=columns, show='headings')

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=180 if col != "Body" else 300)

    tree.pack(padx=10, pady=10, fill='both', expand=True)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT E.subject, E.receiver, C.sender, C.date, C.body
            FROM EmailLog E
            JOIN EmailContents C ON E.subject = C.subject
            ORDER BY C.date DESC
        """)
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

        conn.close()

    except Exception as e:
        messagebox.showerror("Database Error", f"Could not load email logs:\n{e}")
