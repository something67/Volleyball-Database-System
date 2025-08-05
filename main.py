import tkinter as tk

# Import GUI window functions (updated - no more 'gui.' prefix)
from gui.location import open_location_window
from gui.personnel import open_personnel_window
from gui.family import open_family_window
from gui.member import open_member_window
from gui.team_formation import open_team_window
from gui.payment import open_payment_window
from gui.email_log import open_email_log

# Create the main application window
root = tk.Tk()
root ['bg'] = 'lightblue'
root.title("Volleyball Club System")
root.geometry("400x450")

# Welcome Label
tk.Label(root, text="Welcome to MVC Management System", bg='pink' ,font=("Arial", 14, "bold")).pack(pady=15)

# Add feature buttons
tk.Button(root, text="Manage Locations", width=30, command=open_location_window,bg='cyan').pack(pady=5)
tk.Button(root, text="Manage Personnel", width=30, command=open_personnel_window,bg='cyan').pack(pady=5)
tk.Button(root, text="Manage Family Members", width=30, command=open_family_window,bg='cyan').pack(pady=5)
tk.Button(root, text="Manage Club Members", width=30, command=open_member_window,bg='cyan').pack(pady=5)
tk.Button(root, text="Manage Team Formation", width=30, command=open_team_window,bg='cyan').pack(pady=5)
tk.Button(root, text="Make Payments", width=30, command=open_payment_window,bg='cyan').pack(pady=5)
tk.Button(root, text="View Email Logs", width=30, command=open_email_log,bg='cyan').pack(pady=5)

tk.Label(root, text="By Kevin, Pamela, Jasmine, Patricia",bg='lightblue',font=("Arial", 14, "italic")).pack(side='bottom',pady=15)

root.mainloop()