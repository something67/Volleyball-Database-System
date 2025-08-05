import tkinter as tk
from tkinter import messagebox
from db import get_connection # pyright: ignore[reportMissingImports]

def open_location_window():
    win = tk.Toplevel()
    win.title("Manage Locations")

    # --- Input Fields ---
    tk.Label(win, text="Location Name:").grid(row=0, column=0, padx=10, pady=5)
    name_entry = tk.Entry(win)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(win, text="Location Type (Head/Branch):").grid(row=1, column=0, padx=10, pady=5)
    type_entry = tk.Entry(win)
    type_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Label(win, text="Address:").grid(row=2, column=0, padx=10, pady=5)
    address_entry = tk.Entry(win)
    address_entry.grid(row=2, column=1, padx=10, pady=5)

    tk.Label(win, text="Web Address:").grid(row=3, column=0, padx=10, pady=5)
    web_entry = tk.Entry(win)
    web_entry.grid(row=3, column=1, padx=10, pady=5)

    tk.Label(win, text="Max Capacity:").grid(row=4, column=0, padx=10, pady=5)
    capacity_entry = tk.Entry(win)
    capacity_entry.grid(row=4, column=1, padx=10, pady=5)

    # --- Save Button ---
    def save_location():
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Locations (name, type, address, webAddress, maxCapacity)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                name_entry.get(),
                type_entry.get(),
                address_entry.get(),
                web_entry.get(),
                int(capacity_entry.get())
            ))

            conn.commit()
            messagebox.showinfo("Success", "Location saved successfully!")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(win, text="Save Location", command=save_location).grid(row=5, column=1, pady=15)
