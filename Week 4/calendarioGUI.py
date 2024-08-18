import tkinter as tk
from tkcalendar import DateEntry
import datetime

def get_date_time():
    selected_date = cal.get_date()
    selected_time = time_hour.get() + ":" + time_minute.get()
    print(f"Selected Date and Time: {selected_date} {selected_time}")

# Get today's date and time
today = datetime.date.today()
now = datetime.datetime.now()
current_hour = now.hour
current_minute = now.minute

# Create the main window
root = tk.Tk()
root.title("Selecciona una fecha y hora")

# Create a DateEntry widget with Spanish locale and restrict dates
cal = DateEntry(root, width=12, background='darkblue',
                foreground='white', borderwidth=2, year=2024, 
                locale='es_ES', maxdate=today)
cal.pack(pady=10)

# Create Spinboxes for time selection
time_hour = tk.Spinbox(root, from_=0, to=current_hour, width=2, format="%02.0f", justify='center')
time_hour.pack(side='left', padx=(10, 5))

time_minute = tk.Spinbox(root, from_=0, to=current_minute, width=2, format="%02.0f", justify='center')
time_minute.pack(side='left', padx=(5, 10))

# Create a button to get the selected date and time
button = tk.Button(root, text="Obtener fecha y hora", command=get_date_time)
button.pack(pady=10)

# Run the application
root.mainloop()
