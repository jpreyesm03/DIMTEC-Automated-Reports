import tkinter as tk
from tkcalendar import DateEntry  # type: ignore
from datetime import datetime, timedelta, timezone
import re
import argparse



def widget_calendario(min_date_given = ""):

    def corrected_date(date_str):
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
        if not pattern.match(date_str):
            raise ValueError(f"Date string '{date_str}' does not match format '{date_format}'")
        
        try:
            return datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error parsing date: {e}")
            raise




    selected_date = None
    selected_time = None

    def get_date_time():
        nonlocal selected_date, selected_time
        try:
            selected_date = cal.get_date()  # Get the selected date from the DateEntry widget
            selected_time = time_hour.get() + ":" + time_minute.get()  # Get the selected time from the Spinbox widgets
        except Exception as e:
            print(f"Error getting date and time: {e}")
        finally:
            root.destroy()  # Ensure the GUI window is destroyed

    today = datetime.today().date()  # Use datetime.today().date() to get the current date
    now = datetime.now()  # Use datetime.now() to get the current datetime
    max_date = today - timedelta(days = 1)
    
    if not min_date_given:
        min_date = today - timedelta(days = 91)
        fecha_a_mostrar = min_date
        titulo_a_mostrar = "Seleccione una fecha y hora inicial:"
    else:
        try:
            min_date = corrected_date(min_date_given)
            min_date += timedelta(days = 1)
        except ValueError as e:
            return f"Error: {e}"
        
        fecha_a_mostrar = max_date
        titulo_a_mostrar = "Seleccione una fecha y hora final:"
    
    root = tk.Tk()
    root.title(titulo_a_mostrar)

    # Set the DateEntry widget to start at max_date
    cal = DateEntry(root, width = 12, background = 'darkblue', foreground = 'white', borderwidth = 2, 
                    year = fecha_a_mostrar.year, month = fecha_a_mostrar.month, day = fecha_a_mostrar.day,
                    locale = 'es_ES', maxdate = max_date, mindate = min_date, 
                    weekendbackground = 'white', weekendforeground = 'black')
    cal.pack(pady = 10)

    # Initialize Spinbox widgets for time with full range and default to current time
    time_hour = tk.Spinbox(root, from_ = 0, to = 23, width = 2, format = "%02.0f", justify = 'center')
    time_hour.pack(side = 'left', padx = (10, 5))
    time_hour.delete(0, 'end')
    time_hour.insert(0, f"{now.hour:02d}")
    
    time_minute = tk.Spinbox(root, from_ = 0, to = 59, width = 2, format = "%02.0f", justify = 'center')
    time_minute.pack(side = 'left', padx = (5, 10))
    time_minute.delete(0, 'end')
    time_minute.insert(0, f"{now.minute:02d}")

    button = tk.Button(root, text = "Obtener fecha y hora", command = get_date_time)
    button.pack(pady = 10)

    root.mainloop()

    # Capture the return values after the window is closed
    root.quit()
    if selected_date is not None and selected_time is not None:
        
        return str(selected_date) + "T" + str(selected_time) + ":00Z"
    else:
        return "No date and time selected"

def obtener_fechas_GUI():
    first_run = widget_calendario()
    print(first_run)
    second_run = widget_calendario(first_run)
    print(second_run)
    return first_run, second_run

def main():
    parser = argparse.ArgumentParser(description="Calendar program")
    parser.add_argument('min_date_given', type=str, help='Minimum date as an ISO 8601 string')
    args = parser.parse_args()

    min_date_given = args.min_date_given
    selected_date_time = widget_calendario(min_date_given)
    print(str(selected_date_time))
    # print("Este programa sólo existe como ayuda para funciones_cortas.py, que a su vez depende de programa_principal.py")

if __name__ == "__main__":
    main()
