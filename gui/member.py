import tkinter as tk
from tkinter import messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_member_window():
    win = tk.Toplevel()
    win.title("Manage Club Members")

    labels = [
        "Member Number", "First Name", "Last Name", "Date of Birth (YYYY-MM-DD)",
        "Height (cm)", "Weight (kg)", "SSN", "Medicare Card No",
        "Phone Number", "Address", "Gender (M/F)"
    ]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(win, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def save_member():
        values = {label: entry.get().strip() for label, entry in entries.items()}
        if not all(values.values()):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Members (
                    memberNo, firstName, lastName, dateOfBirth,
                    height, weight, SSN, medicareCardNo,
                    phoneNo, address, gender
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                values["Member Number"],
                values["First Name"],
                values["Last Name"],
                values["Date of Birth (YYYY-MM-DD)"],
                values["Height (cm)"],
                values["Weight (kg)"],
                values["SSN"],
                values["Medicare Card No"],
                values["Phone Number"],
                values["Address"],
                values["Gender (M/F)"]
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Member added successfully.")
            win.destroy()
        except Exception as e:
            if "Duplicate" in str(e) or "SSN" in str(e):
                messagebox.showerror("Constraint Error", "MemberNo, SSN or Medicare Card No already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to add member:\n{e}")

    tk.Button(win, text="Save", command=save_member).grid(row=len(labels), column=0, columnspan=2, pady=10)
