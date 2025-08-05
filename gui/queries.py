import tkinter as tk
from tkinter import ttk, messagebox
from db import get_connection  # pyright: ignore[reportMissingImports]

def open_query_window():
    win = tk.Toplevel()
    win.title("Predefined Queries")
    win.geometry("800x500")

    # --- Query Options ---
    tk.Label(win, text="Select Query:").pack(pady=10)
    query_options = [
        "1. List all members of a team",
        "2. Personnel by role",
        "3. Members with unpaid membership fees",
        "4. Designated family contacts of a major member"
    ]
    query_box = ttk.Combobox(win, values=query_options, state="readonly", width=60)
    query_box.pack()

    tk.Label(win, text="Enter Search Value (if needed):").pack(pady=5)
    value_entry = tk.Entry(win, width=40)
    value_entry.pack()

    result_table = ttk.Treeview(win)
    result_table.pack(pady=10, fill='both', expand=True)

    def run_query():
        selected = query_box.get()
        user_input = value_entry.get().strip()

        for i in result_table.get_children():
            result_table.delete(i)

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # --- Query 1: Members of a team ---
            if selected.startswith("1."):
                cursor.execute("""
                    SELECT M.memberNo, M.firstName, M.lastName, F.role
                    FROM Members M
                    JOIN Form F ON M.memberNo = F.memberNo
                    WHERE F.teamName = %s
                """, (user_input,))
                result_table["columns"] = ("Member No", "First Name", "Last Name", "Role")

            # --- Query 2: Personnel by role ---
            elif selected.startswith("2."):
                cursor.execute("""
                    SELECT SSN, firstName, lastName
                    FROM Personnel
                    WHERE role = %s
                """, (user_input,))
                result_table["columns"] = ("SSN", "First Name", "Last Name")

            # --- Query 3: Members with unpaid fees ---
            elif selected.startswith("3."):
                cursor.execute("""
                    SELECT M.memberNo, M.firstName, M.lastName
                    FROM Members M
                    WHERE M.memberNo NOT IN (
                        SELECT DISTINCT memberNo
                        FROM Payments
                        WHERE YEAR(date) = YEAR(CURDATE())
                    )
                """)
                result_table["columns"] = ("Member No", "First Name", "Last Name")

            # --- Query 4: Family contacts from Designates table ---
            elif selected.startswith("4."):
                cursor.execute("""
                    SELECT firstName, lastName, relationship, phoneNo
                    FROM Designates
                    WHERE majorNo = %s
                """, (user_input,))
                result_table["columns"] = ("First Name", "Last Name", "Relationship", "Phone No")

            else:
                messagebox.showwarning("Invalid", "Select a valid query.")
                return

            # Display column headings
            for col in result_table["columns"]:
                result_table.heading(col, text=col)
                result_table.column(col, anchor="center")

            # Populate results
            for row in cursor.fetchall():
                result_table.insert("", "end", values=row)

            conn.close()

        except Exception as e:
            messagebox.showerror("Query Error", f"Error executing query:\n{e}")

    tk.Button(win, text="Run Query", command=run_query).pack(pady=10)
