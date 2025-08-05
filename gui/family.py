import tkinter as tk
from tkinter import messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_family_window():
    win = tk.Toplevel()
    win.title("Manage Family Members")

    labels = [
        "Major Member ID (FK)", "First Name", "Last Name",
        "Relationship", "Phone Number"
    ]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(win, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def save_family():
        values = {label: entry.get().strip() for label, entry in entries.items()}
        if not all(values.values()):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Designates (
                    majorNo, firstName, lastName, relationship, phoneNo
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                values["Major Member ID (FK)"],
                values["First Name"],
                values["Last Name"],
                values["Relationship"],
                values["Phone Number"]
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Family member added successfully.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add family member:\n{e}")

    tk.Button(win, text="Save", command=save_family).grid(row=len(labels), column=0, columnspan=2, pady=10)
