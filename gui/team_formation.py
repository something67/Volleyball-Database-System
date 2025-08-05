import tkinter as tk
from tkinter import messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_team_window():
    win = tk.Toplevel()
    win.title("Team Formation")

    labels = ["Team Name", "Member ID", "Start Date (YYYY-MM-DD)", "End Date (YYYY-MM-DD)", "Role"]
    entries = {}

    for i, label in enumerate(labels):
        tk.Label(win, text=label + ":").grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entry = tk.Entry(win)
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[label] = entry

    def assign_member():
        values = {label: entry.get().strip() for label, entry in entries.items()}
        if not all(values.values()):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # --- Gender Constraint ---
            cursor.execute("SELECT gender FROM Members WHERE memberNo = %s", (values["Member ID"],))
            member_gender = cursor.fetchone()
            if not member_gender:
                raise Exception("Member not found.")
            
            cursor.execute("SELECT gender FROM Teams WHERE name = %s", (values["Team Name"],))
            team_gender = cursor.fetchone()
            if not team_gender:
                raise Exception("Team does not exist.")
            
            if member_gender[0] != team_gender[0]:
                raise Exception("Incompatible genders: Cannot assign member to this team.")

            # --- Assign Member to Team ---
            cursor.execute("""
                INSERT INTO Form (memberNo, teamName, startDate, role, endDate)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                values["Member ID"], values["Team Name"], values["Start Date (YYYY-MM-DD)"],
                values["Role"], values["End Date (YYYY-MM-DD)"]
            ))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Member {values['Member ID']} assigned to team '{values['Team Name']}'.")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    tk.Button(win, text="Assign Member", command=assign_member).grid(row=len(labels), column=0, columnspan=2, pady=10)
