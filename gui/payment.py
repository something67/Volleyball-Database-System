import tkinter as tk
from tkinter import messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_payment_window():
    win = tk.Toplevel()
    win.title("Record Membership Payment")

    labels = [
        "Recipient No (Member ID)", "Installment No", "Payment Date (YYYY-MM-DD)",
        "Membership Payment Date (YYYY-MM-DD)", "Amount", "Payment Method"
    ]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(win, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def save_payment():
        values = {label: entry.get().strip() for label, entry in entries.items()}
        if not all(values.values()):
            messagebox.showerror("Input Error", "All fields are required.")
            return
        
        try:
            amount = float(values["Amount"])
            if amount < 0:
                messagebox.showerror("Validation Error", "Amount must be non-negative.")
                return
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a number.")
            return


        try:

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Payments (
                    recipientNo, installmentNo, date, memberNo,
                    membershipPaymentDate, amount, method
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                values["Recipient No (Member ID)"],
                values["Installment No"],
                values["Payment Date (YYYY-MM-DD)"],
                values["Recipient No (Member ID)"],  # memberNo == recipientNo
                values["Membership Payment Date (YYYY-MM-DD)"],
                values["Amount"],
                values["Payment Method"]
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Payment recorded successfully.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to record payment:\n{e}")

    tk.Button(win, text="Record Payment", command=save_payment).grid(row=len(labels), column=0, columnspan=2, pady=10)
