"""Campus Transit desktop application."""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser

import database
from tracking_server import run_server

BG = "#f3f6fb"
NAVY = "#17345c"
ACCENT = "#2878d0"


class CampusTransitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Transit")
        self.root.geometry("900x620")
        self.root.minsize(760, 520)
        self.root.configure(bg=BG)
        self.server_started = False
        database.init_db()
        self.show_login()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()
        panel = tk.Frame(self.root, bg="white", padx=42, pady=34, highlightthickness=1,
                         highlightbackground="#dce4ef")
        panel.place(relx=.5, rely=.5, anchor="center")
        tk.Label(panel, text="CAMPUS TRANSIT", bg="white", fg=NAVY,
                 font=("Segoe UI", 23, "bold")).pack(pady=(0, 5))
        tk.Label(panel, text="Campus bus management portal", bg="white", fg="#64748b",
                 font=("Segoe UI", 10)).pack(pady=(0, 22))
        tk.Label(panel, text="Username", bg="white", anchor="w").pack(fill="x")
        self.username = tk.Entry(panel, font=("Segoe UI", 11), width=32)
        self.username.pack(pady=(5, 14), ipady=7)
        tk.Label(panel, text="Password", bg="white", anchor="w").pack(fill="x")
        self.password = tk.Entry(panel, show="•", font=("Segoe UI", 11), width=32)
        self.password.pack(pady=(5, 18), ipady=7)
        tk.Button(panel, text="Sign in", command=self.login, bg=ACCENT, fg="white",
                  activebackground=NAVY, activeforeground="white", relief="flat",
                  font=("Segoe UI", 11, "bold"), padx=20, pady=9).pack(fill="x")
        tk.Label(panel, text="Demo: admin/admin123  |  driver1/driver123  |  student1/student123",
                 bg="white", fg="#64748b", font=("Segoe UI", 8)).pack(pady=(17, 0))
        self.password.bind("<Return>", lambda _event: self.login())
        self.username.focus_set()

    def login(self):
        user = database.authenticate(self.username.get(), self.password.get())
        if not user:
            messagebox.showerror("Sign in failed", "Username or password is incorrect.")
            return
        self.user = user
        self.show_dashboard()

    def header(self, title):
        bar = tk.Frame(self.root, bg=NAVY, padx=24, pady=17)
        bar.pack(fill="x")
        tk.Label(bar, text=title, bg=NAVY, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        tk.Label(bar, text=f"{self.user['full_name']}  ·  {self.user['role'].title()}",
                 bg=NAVY, fg="#d7e6fa", font=("Segoe UI", 10)).pack(side="right")

    def show_dashboard(self):
        self.clear()
        self.header("Campus Transit Dashboard")
        body = tk.Frame(self.root, bg=BG, padx=26, pady=24)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Welcome, {self.user['full_name']}", bg=BG, fg=NAVY,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w")
        tk.Label(body, text="Manage campus journeys and view bus activity.",
                 bg=BG, fg="#64748b").pack(anchor="w", pady=(3, 20))

        if self.user["role"] == "admin":
            data = database.dashboard_data()
            cards = tk.Frame(body, bg=BG)
            cards.pack(fill="x", pady=(0, 18))
            for label, value in (("Students", data["students"]), ("Drivers", data["drivers"]), ("Buses", data["buses"])):
                card = tk.Frame(cards, bg="white", padx=24, pady=18, highlightthickness=1,
                                highlightbackground="#e1e8f0")
                card.pack(side="left", fill="x", expand=True, padx=(0, 12))
                tk.Label(card, text=str(value), bg="white", fg=ACCENT,
                         font=("Segoe UI", 24, "bold")).pack(anchor="w")
                tk.Label(card, text=label, bg="white", fg="#64748b").pack(anchor="w")
            self.table(body, "Bus fleet", ("Bus", "Route", "Driver"),
                       [(r["bus_number"], r["route_name"], r["driver"] or "Unassigned") for r in data["bus_rows"]])
            self.table(body, "Student list", ("Student ID", "Name", "Assigned bus"),
                       [(r["student_code"], r["full_name"], r["bus"]) for r in data["student_rows"]])
        elif self.user["role"] == "driver":
            bus = database.bus_for_driver(self.user["id"])
            if bus:
                tk.Label(body, text=f"Assigned bus: {bus['bus_number']}  |  Route: {bus['route_name']}",
                         bg="white", fg=NAVY, padx=18, pady=18,
                         font=("Segoe UI", 12, "bold")).pack(fill="x", pady=8)
                tk.Button(body, text="Open driver GPS page", command=self.open_driver,
                          bg=ACCENT, fg="white", relief="flat", padx=16, pady=10).pack(anchor="w", pady=12)
            else:
                tk.Label(body, text="No bus is assigned to your account yet.", bg=BG, fg="#64748b").pack(anchor="w")
        else:
            tk.Label(body, text="Your student account is active. Ask the administrator to confirm your bus assignment.",
                     bg="white", fg=NAVY, padx=18, pady=18, wraplength=700,
                     justify="left").pack(fill="x")

        actions = tk.Frame(body, bg=BG)
        actions.pack(side="bottom", fill="x", pady=(18, 0))
        tk.Button(actions, text="Open live bus map", command=self.open_map,
                  bg=ACCENT, fg="white", relief="flat", padx=16, pady=10).pack(side="left")
        tk.Button(actions, text="Sign out", command=self.show_login,
                  bg="#e2e8f0", fg=NAVY, relief="flat", padx=16, pady=10).pack(side="right")

    def table(self, parent, title, columns, rows):
        tk.Label(parent, text=title, bg=BG, fg=NAVY,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(8, 5))
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=min(4, max(2, len(rows))))
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=210, anchor="w")
        for row in rows:
            tree.insert("", "end", values=row)
        tree.pack(fill="x", pady=(0, 8))

    def start_server(self):
        if not self.server_started:
            thread = threading.Thread(target=run_server, daemon=True)
            thread.start()
            self.server_started = True

    def open_map(self):
        self.start_server()
        webbrowser.open("http://127.0.0.1:8765/map")

    def open_driver(self):
        self.start_server()
        webbrowser.open("http://127.0.0.1:8765/driver")

if __name__ == "__main__":
    root = tk.Tk()
    CampusTransitApp(root)
    root.mainloop()
