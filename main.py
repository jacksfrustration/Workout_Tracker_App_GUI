from tkinter import *
from tkinter import messagebox, simpledialog
import json
from datetime import datetime, timedelta


class WorkoutTracker:
    def __init__(self, window: Tk, canvas: Canvas):
        self.window = window
        self.canvas = canvas
        self.cur_row = 0
        self.count = 0
        self.dates_list = self.generate_dates_list()
        self.pic_file = PhotoImage(file="./workout.png")

        # Lists to store widgets and their variables
        self.day_vars = []
        self.act_vars = []
        self.widgets = []
        #GUI setup
        self.setup_gui()
        #add the first row of widgets
        self.add_entry_row()

    def generate_dates_list(self, days: int = 10, date_format: str = "%a %d %B %Y") -> list:
        '''Generates a list of dates starting from 5 days ago to 5 days in the future.'''
        start_date = datetime.now() - timedelta(days=5)
        return [(start_date + timedelta(days=i)).strftime(date_format) for i in range(days)]

    def add_entry_row(self):
        '''Adds a row of entry widgets for user input.'''
        self.cur_row += 1

        # Variables to store user selections
        day_var = StringVar(self.window, value="Choose a date")
        act_var = StringVar(self.window, value="Choose a workout")

        # Create and place widgets
        widgets = [
            (Label(self.window, text="On"), 0),
            (OptionMenu(self.window, day_var, *self.dates_list), 1),
            (Label(self.window, text="I did"), 2),
            (OptionMenu(self.window, act_var, "Aerobics", "Cycling", "Running", "Swimming", "Walking"), 3),
            (Label(self.window, text="for:"), 4),
            (Entry(self.window), 5),
            (Label(self.window, text="minutes"), 6)
        ]

        for widget, col in widgets:
            widget.grid(row=self.cur_row, column=col)
            self.widgets.append(widget)

        self.day_vars.append(day_var)
        self.act_vars.append(act_var)
        self.count += 1

    def setup_gui(self):
        '''Sets up the initial GUI with buttons and canvas.'''
        self.canvas.grid(row=0, column=1, columnspan=11)
        self.canvas.create_image(240, 135, image=self.pic_file)

        # Buttons
        buttons = [
            ("Remove Last Entry", self.remove_last_entry, 1, 7),
            ("Add Entry", self.add_entry_row, 1, 8),
            ("Register Activities", self.register_activities, 1, 9),
            ("Display Saved Activities", self.display_activities, 1, 10),
            ("Erase Saved Data", self.erase_all_data, 1, 11),
            ("Erase Specific Day Data", self.erase_specific_day_data, 1, 12)
        ]

        for text, command, row, col in buttons:
            Button(self.window, text=text, command=command).grid(row=row, column=col)

    def remove_last_entry(self):
        '''Removes the last row of entry widgets.'''
        if self.count > 1:
            for _ in range(7):
                widget = self.widgets.pop()
                widget.grid_forget()
                widget.grid_forget()
            self.count -= 1
            self.cur_row -= 1
            self.day_vars.pop()
            self.act_vars.pop()
        else:
            messagebox.showerror(title="Ooooops", message="No more entries to delete")

    def register_activities(self):
        '''Saves the entered activities to a JSON file.'''
        try:
            with open("saved_data.json", "r") as file:
                saved_data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            saved_data = {}

        for i in range(self.count):
            day = self.day_vars[i].get()
            activity = self.act_vars[i].get().title()
            try:
                duration = float(self.widgets[i * 7 + 5].get())
            except ValueError:
                messagebox.showerror(title="Oooops", message="Invalid duration entered")
                return

            if messagebox.askokcancel(title=f"{day} Workout Information", message=f"Activity: {activity} for {duration} minutes. Save this activity?"):
                if day in saved_data:
                    saved_data[day]["activity"].append(activity)
                    saved_data[day]["unit"].append(duration)
                else:
                    saved_data[day] = {"activity": [activity], "unit": [duration]}

        with open("saved_data.json", "w") as file:
            json.dump(saved_data, file, indent=4)

    def display_activities(self):
        '''Displays the saved activities from the JSON file.'''
        try:
            with open("saved_data.json", "r") as file:
                saved_data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            messagebox.showerror(title="Ooooops", message="No saved data found")
            return

        if saved_data:
            for day, details in saved_data.items():
                activities = "\n".join(f"On {day} you did {act.lower()} for {unit} minutes." for act, unit in zip(details["activity"], details["unit"]))
                messagebox.showinfo(title=f"{day} Workout Information", message=activities)
        else:
            messagebox.showerror(title="Oooops", message="No saved data available")

    def erase_all_data(self):
        '''Erases all saved data from the JSON file.'''
        if messagebox.askokcancel(title="Erase All Data", message="Are you sure you want to erase all saved data?"):
            with open("saved_data.json", "w") as file:
                json.dump({}, file)
            messagebox.showinfo(title="Erase All Data", message="All data erased successfully")

    def erase_specific_day_data(self):
        '''Erases data for a specific day from the JSON file.'''
        try:
            with open("saved_data.json", "r") as file:
                saved_data = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            saved_data = {}
            with open("saved_data.json", "w") as file:
                json.dump(saved_data, file)
            messagebox.showerror(title="Ooooops", message="No saved data available")
            return

        if saved_data:
            saved_dates = list(saved_data.keys())
            messagebox.showinfo(title="Available Saved Data", message=f"Available dates: {', '.join(saved_dates)}")
            entry = simpledialog.askstring(title="Delete Data", prompt="Enter the date to delete (format: Day DD Month YYYY)")

            if entry and entry in saved_data:
                saved_data.pop(entry)
                with open("saved_data.json", "w") as file:
                    json.dump(saved_data, file)
                messagebox.showinfo(title="Delete Data", message="Data deleted successfully")
            else:
                messagebox.showerror(title="Ooooops", message="Date not found in saved data")
        else:
            messagebox.showerror(title="Oooops", message="No saved data available")


if __name__ == "__main__":
    window = Tk()
    window.title("Workout Tracker")
    canvas = Canvas(window, width=400, height=227)
    tracker = WorkoutTracker(window, canvas)
    window.mainloop()