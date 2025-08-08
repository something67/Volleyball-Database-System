import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db import get_connection  # pyright: ignore[reportMissingImports]

def _render_result(tree: ttk.Treeview, rows, cols):
    # reset
    for i in tree.get_children():
        tree.delete(i)
    tree["columns"] = cols
    tree["show"] = "headings"
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120, anchor="w")
    for r in rows:
        tree.insert("", "end", values=[("" if v is None else v) for v in r])
    # crude autosize
    for idx, c in enumerate(cols):
        maxlen = max([len(str(c))] + [len(str(r[idx])) for r in rows] if rows else [len(c)])
        tree.column(c, width=min(12 * maxlen + 24, 320))

def open_query_window():
    win = tk.Toplevel()
    win.title("Run SQL Queries")
    win.geometry("950x580")

    # ---- queries dictionary (your SQLs, with Q16/Q17 syntax fixed) ----
    queries = {
        "Q8 - Location Details and Member/Team Count": """
            SELECT Locations.address, Residences.city, Residences.province, Residences.postalCode,
                   Reach.phoneNo, Locations.webAddress, Locations.type, Locations.maxCapacity,
                   CONCAT(Personnel.firstName, ' ', Personnel.lastName) AS generalManagerName,
                   COUNT(DISTINCT Minor.memberNo) AS numMinorMembers,
                   COUNT(DISTINCT Major.memberNo) AS numMajorMembers,
                   COUNT(DISTINCT HomeTo.teamName) AS numTeams
            FROM Locations
            LEFT JOIN Residences ON Locations.address = Residences.address
            LEFT JOIN Reach ON Locations.name = Reach.locationName
            LEFT JOIN Employ ON Employ.locationName = Locations.name
            LEFT JOIN Personnel ON Employ.SSN = Personnel.SSN AND Personnel.role = 'administrator'
            LEFT JOIN Belongs ON Belongs.locationName = Locations.name
            LEFT JOIN Minor ON Belongs.memberNo = Minor.memberNo
            LEFT JOIN Major ON Belongs.memberNo = Major.memberNo
            LEFT JOIN HomeTo ON HomeTo.locationName = Locations.name
            GROUP BY Locations.address, Residences.city, Residences.province, Residences.postalCode,
                     Reach.phoneNo, Locations.webAddress, Locations.type, Locations.maxCapacity,
                     Personnel.firstName, Personnel.lastName
            ORDER BY Residences.province ASC, Residences.city ASC;
        """,

        "Q9 - Designated Family Members of Minors": """
            SELECT Designates.firstName, Designates.lastName, Designates.phoneNo,
                   Members.memberNo, Members.firstName, Members.lastName,
                   Members.dateOfBirth, Members.SSN, Members.medicareCardNo,
                   Members.phoneNo, Members.address, Residences.city,
                   Residences.province, Residences.postalCode, Registers.relationship
            FROM Designates
            JOIN Registers ON Designates.majorNo = Registers.majorNo
            JOIN Members ON Registers.minorNo = Members.memberNo
            JOIN Residences ON Members.address = Residences.address;
        """,

        "Q10 - Session Schedule with Coaches and Players": """
            SELECT Personnel.firstName AS headCoachFirstName, Personnel.lastName AS headCoachLastName,
                   Play.time AS sessionStartTime, Play.address AS sessionAddress,
                   Play.activityType AS sessionNature, Play.teamName,
                   CASE WHEN Play.date > CURDATE() THEN NULL ELSE Play.scoreT1 END AS scoreT1,
                   CASE WHEN Play.date > CURDATE() THEN NULL ELSE Play.scoreT2 END AS scoreT2,
                   Members.firstName AS playerFirstName, Members.lastName AS playerLastName, Form.role AS playerRole
            FROM Play
            JOIN Form ON Play.teamName = Form.teamName
            JOIN Members ON Form.memberNo = Members.memberNo
            JOIN Teams ON Play.teamName = Teams.name
            JOIN HomeTo ON Teams.name = HomeTo.teamName
            JOIN Employ ON TRIM(LOWER(Employ.locationName)) = TRIM(LOWER(HomeTo.locationName))
            JOIN Personnel ON Employ.SSN = Personnel.SSN AND Personnel.role = 'Coach'
            ORDER BY Play.time ASC;
        """,

        "Q11 - Members Belonging to 2+ Locations, No Current Renewal": """
            SELECT DISTINCT Members.memberNo, Members.firstName, Members.lastName
            FROM Members
            JOIN Belongs ON Members.memberNo = Belongs.memberNo
            WHERE Members.memberNo IN (
                SELECT Belongs.memberNo FROM Belongs
                GROUP BY Belongs.memberNo
                HAVING COUNT(DISTINCT Belongs.locationName) >= 2
            )
            AND Members.memberNo NOT IN (
                SELECT Renew.memberNo FROM Renew
                WHERE YEAR(Renew.membershipStartDate) = YEAR(CURDATE())
            )
            AND Members.memberNo IN (
                SELECT Renew.memberNo FROM Renew
                WHERE Renew.membershipStartDate <= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
            )
            ORDER BY Members.memberNo ASC;
        """,

        "Q12 - Locations with >=4 Games and Session Stats": """
            SELECT HomeTo.locationName,
                   COUNT(CASE WHEN Play.activityType = 'Training Session' THEN 1 END) AS totalTrainingSessions,
                   COUNT(DISTINCT CASE WHEN Play.activityType = 'Training Session' THEN Form.memberNo END) AS totalTrainingPlayers,
                   COUNT(CASE WHEN Play.activityType = 'Game' THEN 1 END) AS totalGameSessions,
                   COUNT(DISTINCT CASE WHEN Play.activityType = 'Game' THEN Form.memberNo END) AS totalGamePlayers
            FROM Play
            JOIN HomeTo ON Play.teamName = HomeTo.teamName
            JOIN Form ON Form.teamName = Play.teamName
            GROUP BY HomeTo.locationName
            HAVING totalGameSessions >= 4
            ORDER BY totalGameSessions DESC;
        """,

        "Q13 - Members with no games but all fees paid": """
            SELECT Members.memberNo, Members.firstName, Members.lastName,
                   YEAR(CURDATE()) - YEAR(Members.dateOfBirth) AS age,
                   Members.phoneNo, Belongs.locationName
            FROM Members
            LEFT JOIN Form ON Members.memberNo = Form.memberNo
            JOIN Belongs ON Members.memberNo = Belongs.memberNo
            WHERE Form.memberNo IS NULL
              AND (Belongs.endDate IS NULL OR Belongs.endDate > CURDATE())
              AND NOT EXISTS (
                SELECT * FROM Installments
                WHERE Installments.recipientNo = Members.memberNo
                  AND NOT EXISTS (
                      SELECT * FROM Payments
                      WHERE Payments.recipientNo = Installments.recipientNo
                        AND Payments.installmentNo = Installments.installmentNo
                  )
              )
            ORDER BY Belongs.locationName ASC, age ASC;
        """,

        "Q14 - Majors who were previously minors and paid": """
            SELECT
              Members.memberNo,
              Members.firstName,
              Members.lastName,
              Renew.membershipStartDate,
              YEAR(CURDATE()) - YEAR(Members.dateOfBirth) AS age,
              Members.phoneNo,
              Belongs.locationName
            FROM Members
            JOIN Major   ON Major.memberNo  = Members.memberNo
            JOIN Belongs ON Belongs.memberNo = Members.memberNo
            JOIN Renew   ON Renew.recipientNo = Members.memberNo
            WHERE Members.memberNo IN (
                SELECT Payments.recipientNo
                FROM Payments
                WHERE Payments.membershipType = 'Minor'
            )
            AND (Belongs.endDate IS NULL OR Belongs.endDate > CURDATE())
            ORDER BY Belongs.locationName, age;
        """,

        "Q15 - Setters who paid dues and only played as Setters": """
            SELECT Members.memberNo, Members.firstName, Members.lastName,
                   YEAR(CURDATE()) - YEAR(Members.dateOfBirth) as age,
                   Members.phoneNo, Personnel.email, Belongs.locationName
            FROM Members
            JOIN Form ON Members.memberNo = Form.memberNo
            JOIN Belongs ON Belongs.memberNo = Members.memberNo
            JOIN Personnel ON Personnel.SSN = Members.SSN
            WHERE Members.memberNo NOT IN (SELECT memberNo FROM Form WHERE role <> 'Setter')
              AND Members.memberNo IN (SELECT memberNo FROM Form WHERE role = 'Setter')
              AND Members.memberNo NOT IN (
                  SELECT memberNo
                  FROM Payments
                  WHERE amount IS NULL OR amount = 0
              )
            ORDER BY Belongs.locationName, Members.memberNo;
        """,

        # ---- your Q16 (keep if you want; consider replacing with the COUNT-DISTINCT version we discussed) ----
        "Q16 - Members with all 4 roles": """
            SELECT DISTINCT M.memberNo, M.firstName, M.lastName,
                   YEAR(CURDATE()) - YEAR(M.dateOfBirth) AS age,
                   M.phoneNo, P.email, B.locationName
            FROM Members M
            JOIN Belongs B ON M.memberNo = B.memberNo
            JOIN Personnel P ON M.SSN = P.SSN
            WHERE (B.endDate IS NULL OR B.endDate > CURDATE())
              AND M.memberNo IN (
                SELECT memberNo
                FROM Form
                WHERE role IN ('Setter','Libero','Outside Hitter','Opposite Hitter')
                GROUP BY memberNo
                HAVING COUNT(DISTINCT role) = 4
              )
            ORDER BY B.locationName, M.memberNo;
        """,

        
        "Q17 - Family Members who are also Head Coaches": """
            SELECT DISTINCT 
    FamilyMembers.firstName, 
    FamilyMembers.lastName, 
    FamilyMembers.phoneNo
FROM FamilyMembers
JOIN Members 
    ON FamilyMembers.firstName = Members.firstName 
   AND FamilyMembers.lastName = Members.lastName 
   AND FamilyMembers.phoneNo = Members.phoneNo
JOIN Belongs 
    ON Members.memberNo = Belongs.memberNo
JOIN Personnel 
    ON FamilyMembers.firstName = Personnel.firstName 
   AND FamilyMembers.lastName = Personnel.lastName 
   AND FamilyMembers.phoneNo = Personnel.phoneNo
JOIN HouseSite 
    ON Belongs.locationName = HouseSite.locationName
JOIN Play 
    ON Play.address = HouseSite.address
WHERE Belongs.endDate IS NULL
  AND Personnel.role = 'Coach'
  AND Personnel.mandate = 'Volunteer'
ORDER BY 
    FamilyMembers.firstName, 
    FamilyMembers.lastName;

        """,

        "Q18 - Members who never lost a game": """
            SELECT DISTINCT M.memberNo, M.firstName, M.lastName,
                            YEAR(CURDATE()) - YEAR(M.dateOfBirth) AS age,
                            M.phoneNo, P.email, B.locationName
            FROM Members M
            JOIN Form F ON M.memberNo = F.memberNo
            JOIN Belongs B ON M.memberNo = B.memberNo
            JOIN Personnel P ON P.SSN = M.SSN
            WHERE NOT EXISTS (
                SELECT 1
                FROM Play
                WHERE Play.teamName = F.teamName
                  AND ((Play.teamName = F.teamName AND Play.scoreT1 < Play.scoreT2)
                       OR (Play.teamName <> F.teamName AND Play.scoreT2 < Play.scoreT1))
            )
            AND (B.endDate IS NULL OR B.endDate > CURDATE())
            ORDER BY B.locationName, M.memberNo;
        """,

        "Q19 - Volunteer family members of minors": """
            SELECT 
              Personnel.firstName, 
              Personnel.lastName, 
              COUNT(DISTINCT Minor.memberNo) AS minorCount,
              Personnel.phoneNo, 
              Personnel.email, 
              Belongs.locationName, 
              Personnel.role
            FROM Personnel
            JOIN FamilyMembers ON Personnel.phoneNo = FamilyMembers.phoneNo
            JOIN Members ON FamilyMembers.phoneNo = Members.phoneNo
            JOIN Minor   ON Members.memberNo = Minor.memberNo
            JOIN Belongs ON Minor.memberNo = Belongs.memberNo
            WHERE Personnel.mandate = 'Volunteer'
              AND (Belongs.endDate IS NULL OR Belongs.endDate > CURDATE())
            GROUP BY Personnel.firstName, Personnel.lastName, Personnel.phoneNo,
                     Personnel.email, Belongs.locationName, Personnel.role
            ORDER BY Belongs.locationName, Personnel.role, Personnel.firstName, Personnel.lastName;
        """,
    }

    # ---- controls
    top = tk.Frame(win)
    top.pack(fill="x", padx=8, pady=8)
    tk.Label(top, text="Select Query:").pack(side="left")
    query_box = ttk.Combobox(top, values=list(queries.keys()), state="readonly", width=70)
    query_box.pack(side="left", padx=8)
    query_box.current(0)
    run_btn = ttk.Button(top, text="Run")
    run_btn.pack(side="left")

    # table with scrollbars
    table_frame = tk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=8, pady=8)
    tree = ttk.Treeview(table_frame, show="headings")
    yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
    tree.grid(row=0, column=0, sticky="nsew")
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll.grid(row=1, column=0, sticky="ew")
    table_frame.rowconfigure(0, weight=1)
    table_frame.columnconfigure(0, weight=1)

    # export to CSV (optional but nice)
    def export_csv():
        if not tree.get_children():
            messagebox.showinfo("Export", "No rows to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        cols = tree["columns"]
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for iid in tree.get_children():
                w.writerow(tree.item(iid, "values"))
        messagebox.showinfo("Export", f"Saved to {path}")

    bottom = tk.Frame(win)
    bottom.pack(fill="x", padx=8, pady=4)
    ttk.Button(bottom, text="Export CSV", command=export_csv).pack(side="right")

    def run():
        key = query_box.get()
        sql = queries.get(key)
        if not sql:
            messagebox.showwarning("Select a Query", "Please select a query to run.")
            return
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            conn.close()
            _render_result(tree, rows, cols)
            if not rows:
                messagebox.showinfo("No Results", "Query returned 0 rows.")
        except Exception as e:
            messagebox.showerror("Query Error", str(e))

    run_btn.configure(command=run)

