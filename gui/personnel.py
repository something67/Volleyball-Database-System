import tkinter as tk
from tkinter import messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_personnel_window():
    win = tk.Toplevel()
    win.title("Manage Personnel")

    labels = [
        "SSN", "Date of Birth (YYYY-MM-DD)", "First Name", "Last Name", "Medicare Card No",
        "Phone No", "Address", "Email", "Role", "Mandate"
    ]
    entries = {}

    # Create label-entry pairs
    for i, label in enumerate(labels):
        tk.Label(win, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def save_personnel():
        # Extract and validate values
        values = {label: entry.get().strip() for label, entry in entries.items()}

        if not all(values.values()):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Personnel (
                    SSN, dateOfBirth, firstName, lastName, medicareCardNo,
                    phoneNo, address, email, role, mandate
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                values["SSN"],
                values["Date of Birth (YYYY-MM-DD)"],
                values["First Name"],
                values["Last Name"],
                values["Medicare Card No"],
                values["Phone No"],
                values["Address"],
                values["Email"],
                values["Role"],
                values["Mandate"]
            ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Personnel added successfully.")
            win.destroy()
        except Exception as e:
            if "Duplicate" in str(e):
                messagebox.showerror("Constraint Error", "SSN or Medicare Card No already exists.")
            else:
                messagebox.showerror("Database Error", f"Failed to add personnel:\n{e}")

    tk.Button(win, text="Save", command=save_personnel).grid(row=len(labels), column=0, columnspan=2, pady=10)
