import tkinter as tk
from tkinter import messagebox, ttk
import fastf1  # type: ignore
from PIL import Image, ImageTk  # type: ignore
import requests  # type: ignore
from io import BytesIO

# Sample driver data (you can expand this list)
drivers = [
    {'name': 'Lewis Hamilton', 'team': 'Mercedes', 'image': 'https://financialexpresswpcontent.s3.amazonaws.com/uploads/2017/11/new-f1-logo.jpg'},
    {'name': 'Max Verstappen', 'team': 'Red Bull Racing', 'image': 'https://images.ps-aws.com/c?url=https%3A%2F%2Fd3cm515ijfiu6w.cloudfront.net%2Fwp-content%2Fuploads%2F2022%2F12%2F28143438%2Fformula-one-2022-drivers-abu-dhabi-grand-prix-planet-f1.jpg'},
    {'name': 'Charles Leclerc', 'team': 'Ferrari', 'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/F%C3%A9d%C3%A9ration_Internationale_de_l%27Automobile_wordmark.svg/1200px-F%C3%A9d%C3%A9ration_Internationale_de_l%27Automobile_wordmark.svg.png'},
    # Add more drivers as needed...
]

class F1App:
    def __init__(self, root):
        self.root = root
        self.root.title("F1 Session Data")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.session_type = tk.StringVar(value='R')  # Default to Race
        self.year = tk.StringVar(value='2023')  # Default year
        self.gp = tk.StringVar(value='Bahrain')  # Default GP
        self.driver_names = tk.StringVar()  # Driver names input

        self.create_login_frame()

    def create_login_frame(self):
        login_frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        login_frame.pack(pady=50)

        tk.Label(login_frame, text="Username:", bg="#ffffff", font=("Arial", 12)).grid(row=0, column=0)
        tk.Entry(login_frame, textvariable=self.username, font=("Arial", 12)).grid(row=0, column=1)

        tk.Label(login_frame, text="Password:", bg="#ffffff", font=("Arial", 12)).grid(row=1, column=0)
        tk.Entry(login_frame, textvariable=self.password, show='*', font=("Arial", 12)).grid(row=1, column=1)

        tk.Button(login_frame, text="Login", command=self.login, bg="#007bff", fg="white", font=("Arial", 12), padx=10).grid(row=2, columnspan=2)

    def login(self):
        if self.username.get() == "lewis44" and self.password.get() == "2020":
            self.show_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        dashboard_frame = tk.Frame(self.root, bg="#ffffff")
        dashboard_frame.pack(pady=20)

        tk.Label(dashboard_frame, text="F1 Session Data", font=("Arial", 24), bg="#ffffff").pack(pady=10)

        # Input for Year
        year_label = tk.Label(dashboard_frame, text="Year:", bg="#ffffff", font=("Arial", 12))
        year_label.pack(pady=(10, 0))
        
        year_entry = tk.Entry(dashboard_frame, textvariable=self.year, font=("Arial", 12))
        year_entry.pack(pady=(0, 10))

        # Input for Grand Prix
        gp_label = tk.Label(dashboard_frame, text="Grand Prix:", bg="#ffffff", font=("Arial", 12))
        gp_label.pack(pady=(10, 0))

        gp_entry = tk.Entry(dashboard_frame, textvariable=self.gp, font=("Arial", 12))
        gp_entry.pack(pady=(0, 10))

        # Input for Driver Names (for comparison)
        driver_label = tk.Label(dashboard_frame, text="Driver Names (comma separated):", bg="#ffffff", font=("Arial", 12))
        driver_label.pack(pady=(10, 0))

        driver_entry = tk.Entry(dashboard_frame, textvariable=self.driver_names, font=("Arial", 12))
        driver_entry.pack(pady=(0, 10))

         # Dropdown for session selection
        session_label = tk.Label(dashboard_frame, text="Select Session Type:", bg="#ffffff", font=("Arial", 12))
        session_label.pack(pady=(10, 0))

        session_options = ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'R']  # Updated options
        session_combobox = ttk.Combobox(dashboard_frame,
                                          textvariable=self.session_type,
                                          values=session_options)
        session_combobox.pack(pady=(0, 10))
         
         # Button to load data
        load_data_button = tk.Button(dashboard_frame,
                                       text="Load Session Data",
                                       command=self.load_session_data)
        load_data_button.pack(pady=(10, 0))

         # Button to compare lap times
        compare_button = tk.Button(dashboard_frame,
                                     text="Compare Lap Times",
                                     command=lambda: self.compare_lap_times())
        compare_button.pack(pady=(10, 0))

         # Frame to display driver images throughout the application
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=20)

         # Load and display all driver images initially
        self.load_driver_images()

    def load_driver_images(self):
         """Load and display images of all drivers."""
         for driver in drivers:
             try:
                 response = requests.get(driver['image'])
                 response.raise_for_status()  # Raise an error for bad responses
                 img_data = Image.open(BytesIO(response.content))
                 img_data = img_data.resize((150, 150), Image.LANCZOS)  # Resize image
                 img = ImageTk.PhotoImage(img_data)

                 label = tk.Label(self.image_frame, image=img)
                 label.image = img  # Keep a reference to avoid garbage collection
                 label.pack(side=tk.LEFT)
             except Exception as e:
                 print(f"Error loading image for {driver['name']}: {e}")

    def load_session_data(self):
         """Load session data based on selected type and filter by driver names."""
         try:
             year = int(self.year.get())
             gp = self.gp.get()
             session_type = self.session_type.get()  # Get selected session type
             specific_driver_names = [name.strip() for name in self.driver_names.get().split(',')]  # Get specific driver names

             # Load the session
             session = fastf1.get_session(year, gp, session_type)
             session.load()

             # Sort laps by position (finishing order)
             lap_times = session.laps[['Driver', 'LapTime', 'Position']].dropna()
             lap_times.sort_values(by='Position', inplace=True)  # Sort by finishing position

             lap_times_dict = lap_times.to_dict(orient='records')

             # Clear previous results in Treeview if any
             if hasattr(self,'lap_treeview'):
                 for item in self.lap_treeview.get_children():
                     self.lap_treeview.delete(item)
             else:
                 # Create Treeview if it doesn't exist yet
                 self.lap_treeview = ttk.Treeview(self.root,
                                                   columns=("Driver", "Lap Time"),
                                                   show='headings')
                 self.lap_treeview.heading("Driver", text="Driver")
                 self.lap_treeview.heading("Lap Time", text="Lap Time")
                 self.lap_treeview.pack(pady=10)

             # Display lap times in a treeview
             for lap in lap_times_dict:
                 if not specific_driver_names or lap['Driver'] in specific_driver_names:
                     self.lap_treeview.insert("", tk.END,
                                              values=(lap['Driver'], str(lap['LapTime'])))

         except Exception as e:
             messagebox.showerror("Error loading data", str(e))

    def compare_lap_times(self):
         """Compare lap times of two specified drivers."""
         try:
             year = int(self.year.get())
             gp = self.gp.get()
             
             specific_driver_names = [name.strip() for name in self.driver_names.get().split(',')]  
             
             if len(specific_driver_names) != 2:
                 messagebox.showerror("Input Error",
                                      "Please enter exactly two driver names separated by a comma.")
                 return

             comparison_results = []

             for session_type in ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'R']:
                 try:
                     session = fastf1.get_session(year, gp, session_type)
                     session.load()

                     lap_times = session.laps[['Driver', 'LapTime']].dropna()
                     lap_times_dict = lap_times.to_dict(orient='records')

                     for lap in lap_times_dict:
                         if lap['Driver'] in specific_driver_names:
                             comparison_results.append((session_type,
                                                        lap['Driver'],
                                                        str(lap['LapTime'])))

                 except Exception as e:
                     print(f"Could not load data for {session_type}: {e}")

             if comparison_results:
                 comparison_window = tk.Toplevel(self.root)
                 comparison_window.title("Lap Time Comparison")
                 
                 comparison_treeview = ttk.Treeview(comparison_window,
                                                     columns=("Session Type", "Driver", "Lap Time"),
                                                     show='headings')
                 comparison_treeview.heading("Session Type", text="Session Type")
                 comparison_treeview.heading("Driver", text="Driver")
                 comparison_treeview.heading("Lap Time", text="Lap Time")
                 comparison_treeview.pack(fill=tk.BOTH)

                 for result in comparison_results:
                     comparison_treeview.insert("", tk.END,
                                                values=result)

         except Exception as e:
             messagebox.showerror("Error during comparison", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = F1App(root)
    root.mainloop()
