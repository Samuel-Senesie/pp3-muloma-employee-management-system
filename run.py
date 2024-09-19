"""
Imported libraries for runing the app
"""
import gspread
from google.oauth2.service_account import Credentials
import re
import uuid #for generating unique ID
import calendar
from datetime import datetime, timedelta #date and time for shift timedtamps
import sys

#Set project scope for Google Sheets API
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

#Open relevant Google sheets
SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("employee_info")
SHIFT_SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("shift_data")
AVAILABLE_SHIFT_SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("available_shifts")
PLANNED_SHIFT_SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("planned_shifts")

#Shift definitions
FULL_TIME_FIXED_SHIFTS = { 
        'early': ('08:00', '16:30'),
        'late': ('13:30', '22:00')
    }

FULL_TIME_FLEXIBLE_SHIFTS = {
    'flexible-early': ('08:00', '16:30'),
    'flexible_late': ('13:30', '22:00')
}

PART_TIME_SHIFTS = {
        'morning': ('08:00', '13:00'),
        'afternoon': ('13:00', '18:00'),
        'evening': ('17:00', '22:00')
    }

#Validate Departments and Roles

#list of valid departments 
valid_departments = [
    "Poultry Farming",
    "Fish Farming",
    "Cattle Ranch",
    "Vegetable Farming",
    "Construction",
    "Security",
    "Logistics and Stores",
    "General Farmhands"
]

#list of valid roles
valid_roles = [
    "General Manager",
    "Director",
    "Manager",
    "Consultant",
    "Supervisor",
    "Team Leader",
    "Technician",
    "Worker(Labouer)",
    "Assistant",
    "Intern",
    "Volunteer",
]


"""
Main menu function to dispaly welcome message and login access
"""
def main_menu():
    print("Welcome to Muloma Employee Management System")
    print("\n===== Main Menu =====")
    #answer =input("Do you have an account? (YES/NO): ").strip().lower()
    print("1. Create Account")
    print("2. Log in")
    print("3. Exit")

    choice = input("Select an option (1/2/3): ").strip()

    if choice == "1":
        create_account()
    elif choice == "2":
        login()
    elif choice == "3":
        print("Exiting the system. Goodbye!")
        exit()
    else:
        print("Please select a valid option.")

    #if answer == "yes":
        #login()
    #elif answer == "no":
        #create_account()
    #else:
        #sys.exit("Thank you for using Muloma Employee Management System. Goodbye!")
"""
Login if account already exists
"""
def login():
    name = input("Enter your full Name: ").strip()
    emp_id = input("Enter your Employee ID: ").strip()

    """
    Fetch all rows from the 'Employee info' sheet(excluding headers)
    """
    #employee_info_sheet = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("employee_info")
    employee_info = SHEET.get_all_values()[1:] #skip the first row

    #loop through rows of the 'employees_info' sheet to find find an exact match

    for row in employee_info:
        full_name = row[0].strip() #Get name exactly is in the sheet
        stored_emp_id = row[2].strip()

        if name == full_name and emp_id == stored_emp_id:
            print(f"Welcome, {name}!")

            #update the last Login data 
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            row_index = employee_info.index(row) + 2
            SHEET.update_cell(row_index, 11, current_time)

            #Pass employee ID and name to shift menu
            shift_menu(emp_id, name)
            return

    print(f"Login failed. The name or ID does not match our records")
    main_menu()

#Function to validate employee name 
def validate_name(name):
    return re.fullmatch(r"[A-Za-z\s\-]+", name) is not None

#function to validate phone number (only digits allowed)
def validate_phone_number(phone_number):
    return re.fullmatch(r"\d{10,15}", phone_number) is not None

# Function to validate email address
def validate_email(email):
    return re.fullmatch(r"[^@]+[^@]+\.[^@]+", email) is not None

# Function to validate either a phone number or email
def validate_contact_info(contact_info):
    if validate_phone_number(contact_info):
        return "Phone number is valid."
    elif validate_email(contact_info):
        return "Email address is valid."
    else:
        return "The phone number or email address is invalid"

"""
Function to create account for new Employees
"""
def create_account():
    # Validate first name
    first_name = input("Enter your first name: ").strip()
    while not validate_name(first_name):
        print("Invalid first name, only letters, spaces and hyphens are allowed")
        first_name = input("Enter your first name: ").strip()
    # Validate last name
    last_name = input("Enter your last name: ").strip()
    while not validate_name(last_name):
        print("Invalid last name, only letters, spaces and hyphens are allowed")
        last_name = input("Enter your last name: ").strip()
    
    # Validate phone number or email address
    email_or_phone = input("Enter your email or phone numer: ").strip()
    while validate_contact_info(email_or_phone) != "Phone number is valid." and validate_contact_info(email_or_phone) != "Email address is valid.":
        print(validate_contact_info(email_or_phone))
        email_or_phone = input("Enter a valid phone number or email address: ").strip()

    #Get employees date of birth
    dob_input = input("Enter your date of birth (DD-MM-YYYY). ").strip()

    try:
        dob = datetime.strptime(dob_input, "%d-%m-%Y")
    except ValueError:
        print("Invalid date format. Please enter the date in the format DD-MM-YYYY.")
        return create_account()
    
    #check users age if they are 18 or older
    today = datetime.now()
    age = today.year -dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < 18:
        print("Sorry, you must be 18 years or older to create an account")
        main_menu()
        return
    
    #Retrieve and compare employee data for date of birth and email/phone number with existing data base
    employee_info = SHEET.get_all_values()[1:]
    for row in employee_info:
        if dob_input == row[1].strip() and email_or_phone == row[3].strip():
            print("An account with the same data already exists.")
            main_menu()
            return

    #Display and collect employment type
    employment_type = ""
    while employment_type not in ["full-time", "part-time"]:
        employment_type = input("Are you a full-time or part-time employee? (full-time/part-time): ").strip().lower()
    
    #Full-time employees to selecte between fixed and flexible shifts 
    shift_model = ""
    shift_type = ""
    if employment_type == "full-time":
        while shift_model not in ["fixed", "flexible"]:
            shift_model = input("Do you prefere a fixed of flexible shift? (fixed/flexible): ").strip().lower()
        if shift_model == "fixed":
            while shift_type not in ["early", "late"]:
                shift_type = input("Would you prefer an early (08:00 - 16:30) or late (13:30 - 22:00) shift? (early/late): ").strip().lower()
        elif shift_model == "flexible":
            shift_type = "flexible" #New
            print("You will be assigned 3 early and 3 late shifts each week.")
    else:
        shift_model = "fixed"
        print("\nPart-time employees can work up to 3 days per week, for a total of 20-40hours.")
        print("Shift options are: \n1. Morning: 08:00 - 13:00\n2. Afternoon: 13:00 - 18:00\n3. Evening: 17:00 - 22:00")
        shift_choice = ""
        while shift_choice not in ["1", "2", "3"]:
            shift_choice = input(f"Select shift (1/2/3): ").strip()
        shift_map = {"1": "Morning", "2": "Afternoon", "3": "Evening"}
        shift_type = shift_map[shift_choice]

    #Department selection
    print("\nSelect your department:")
    for i, dept in enumerate(valid_departments, 1):
        print(f"{1}. {dept}")
    department_choice = input("Enter the number that corresponds with your department: ")

    #Validate department input
    while not department_choice.isdigit() or int(department_choice) not in range(1, len(valid_departments) + 1):
        print("Invalid choice. Please selecte a valid department number.")
        department_choice = input("Enter the number corresponding to your department: ")
    department = valid_departments[int(department_choice) - 1] 

    # Role selection
    print("\nSelect your role from the list below: ")
    for i, role in enumerate(valid_roles, 1):
        print(f"{i}. {role}")
    role_choice = input("Enter the number that corresponds to your role: ")

    #validate role input
    while not role_choice.isdigit() or int(role_choice) not in range(1, len(valid_roles) + 1):
        print("Invalid choice. please selecte a valid role number")
        role_choice = input("Enter the number that corresponds to your role: ")
    role = valid_roles[int(role_choice) - 1] #get the selected role 

    full_name = f"{first_name} {last_name}"

    # Review data before crating the employee ID
    print("\nPlease review your information for correctness")
    print(f"Full Name: {full_name}")
    print(f"Date of Birth: {dob_input}")
    print(f"Email/Phone: {email_or_phone}")
    print(f"Department: {department}")
    print(f"Role: {role}")
    print(f"Employment Type: {employment_type}")
    print(f"Shift Model: {shift_model}")
    print(f"Shift Type: {shift_type}")

    # Ask user to confirmation
    confim = input("\nIs the above information correct? (yes/no): ").strip().lower()

    if confim == "yes":
        #Generate a short employee ID, 5 characters long in upperclass
        emp_id = str(uuid.uuid4())[0:5].upper()

        """
        Get the date of account creation and last login time
        """
        date_of_creation = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        last_login = "N/A"
        #shift_data = shift_type if employment_type == "full-time" else " , ".join(part_time_shifts)

        """
         Append new employee data to Google sheet for all fields
        """
        employee_data = [
            full_name, dob_input, emp_id, email_or_phone, department, 
            role, employment_type, shift_model, shift_type, date_of_creation, last_login
        ]
        SHEET.append_row(employee_data)

        print(f"Your account has been created! Your Employee ID is: {emp_id}")
        print("Write this ID down and keep it safe. You will need it to log in")
        print("\nReturning to main menu")
        main_menu()
    else:
        print("Please correct your information.")
        create_account() #Rsetart the process

"""
Function to display shift menu
"""
def shift_menu(emp_id, emp_name):
    print("\nShift Management Menu:")
    print("1. Start/End a shift")
    print("2. View my Shifts")
    print("3. Select Available Shifts")
    print("4. Log out")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
            handle_shift(emp_id, emp_name)
    elif choice == "2":
        view_shifts(emp_id, emp_name)        
    elif choice == "3":
            select_shift(emp_id, emp_name)
    elif choice == "4":
        main_menu()
    else:
        print("Invalid choice. Please try again.")
        shift_menu(emp_id, emp_name)

# Function to handle shift start/end

"""
Function to handle shift (Start, Pause, Resume, End)
"""
def handle_shift(emp_id, emp_name):
    shift_status = ""
    start_time = None
    pause_time = None
    resume_time = None
    end_time = None
    pause_time_str = "N/A"
    resume_time_str = "N/A"

    while True:
        print("\nShift Menu:")
        print("1. Start shift")
        print("2. Pause shift")
        print("3. Resume shift")
        print("4. End shift")
        action = input("Select an action: ")

        if action == "1" and not start_time:
            start_time = datetime.now()
            shift_status = "Shift started"
            print(f"Shift started at {start_time.strftime('%H:%M:%S')}")
        elif action == "2" and start_time and not pause_time:
            pause_time = datetime.now()
            pause_time_str = pause_time.strftime('%H:%M:%S')
            shift_status = "Shift paused"
            print(f"shift paused at {pause_time_str}") #round time to there nearest seconds
        elif action == "3" and pause_time:
            resume_time = datetime.now()
            resume_time_str = resume_time.strftime('%H:%M:%S')
            shift_status = "Shift resumed"
            print(f"Shift resumed at {resume_time_str}")
        elif action == "4" and start_time:
            end_time = datetime.now()
            shift_status = "Shift_ended"
            print(f"Shift ended at {end_time.strftime('%H:%M:%S')}")
            break
        else:
            print("Invalid action")

    if start_time and end_time:
        total_time = end_time - start_time
        break_time = resume_time - pause_time if pause_time and resume_time else 0
        total_time_str = str(total_time).split('.')[0]
        break_time_str = str(break_time).split('.')[0]

        print(f"Total hours worked: {total_time_str}")
        print(f"Total break time: {break_time_str}")

        #Get shift date
        shift_date = start_time.strftime('%d-%m-%Y')

        receipt_issued = "Yes"

        """
        Append shift data to Google Sheet
        """
        shift_data = [
            emp_name,
            emp_id,
            shift_date,
            start_time.strftime('%H:%M:%S'),
            end_time.strftime('%H:%M:%S'),
            pause_time_str,
            resume_time_str,
            total_time_str,
            break_time_str,
            receipt_issued
        ]

        SHIFT_SHEET.append_row(shift_data)
        print("Shift data updated successfully!")



"""
Function to generate shifts based on employment type and shift model
"""
def generate_planned_shifts():
    employee_info = SHEET.get_all_records()

    planned_shifts = []

    shift_timings = {**FULL_TIME_FIXED_SHIFTS, **FULL_TIME_FLEXIBLE_SHIFTS, **PART_TIME_SHIFTS}

    # Generate shifts for the next 60 days (approx. two months)
    start_date = datetime.today()
    end_date = start_date + timedelta(days=60)

    for employee in employee_info:
        emp_id = employee.get("Employee ID")
        name = employee.get("Full Name")
        employment_type = employee.get("Employment Type")
        shift_model = employee.get("Shift Model")
        shift_type = employee.get("Shift Type")
        department = employee.get("Department")

        # Start the shift loop over the data range
        current_date = start_date

        while current_date <= end_date:
            #skip Sunday 
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue

            #shift_key = None
            shift_start_str, shift_end_str = '00:00', '00:00'

            if employment_type == 'full-time':
                if shift_model == 'fixed':
                    shift_key = shift_type.lower()
                    shift_start_str, shift_end_str = shift_timings.get(shift_key, ('00:00', '00:00')) 

                elif shift_model == 'flexible':
                    days_since_start = (current_date - start_date).days
                    days_in_cycle = days_since_start % 7

                    if days_in_cycle < 3:
                        shift_key = 'flexible-early'
                        shift_start_str, shift_end_str = shift_timings['flexible-early']
                    else:
                        shift_key = 'flexible-late'
                        shift_start_str, shift_end_str = shift_timings['flexible_late']

            elif employment_type == 'part-time':
                shift_key = shift_type.lower() 
                shift_start_str, shift_end_str = shift_timings.get(shift_key, ('00:00', '00:00'))  

            if shift_start_str == '00:00' and shift_end_str == '00:00':  
                current_date += timedelta(days=1)
                continue      

            #Get current date
            shift_date = current_date.strftime('%Y-%m-%d')
            
            #Calculate number of hours in each shift
            shift_start_time = datetime.strptime(shift_start_str, "%H:%M")
            shift_end_time = datetime.strptime(shift_end_str, "%H:%M")
            duration = shift_end_time - shift_start_time
            number_of_hours = duration.seconds / 3600

            planned_shifts.append([
                emp_id,
                name,
                employment_type,
                shift_model,
                department,
                shift_date,
                shift_key if shift_key else 'Not Assigned',
                number_of_hours,
                shift_start_str,
                shift_end_str
            ])

            current_date += timedelta(days=1)
    if planned_shifts:
        existing_data = PLANNED_SHIFT_SHEET.get_all_records()
        if existing_data:
            header = list(existing_data[0].keys())
            PLANNED_SHIFT_SHEET.clear()
            PLANNED_SHIFT_SHEET.append_row(header)
        PLANNED_SHIFT_SHEET.append_rows(planned_shifts)

generate_planned_shifts()

"""
Function to display all available shifts for the month
"""
def view_shifts(emp_id, emp_name):
    #Get current date
    today = datetime.now()

    # First and last days of the current month 
    first_day_of_current_month = today.replace(day=1)

    last_day_of_current_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    next_month = (today.month % 12) + 1
    year_increment = today.year if today.month != 12 else today.year + 1
    #year_increment = today.year + (today.month == 12)
    first_day_of_next_month = datetime(year_increment, next_month, 1)

    last_day_of_next_month = first_day_of_next_month.replace(day=calendar.monthrange(year_increment, next_month)[1])

    # Fetch shifts from planned shift sheet
    shift_records = PLANNED_SHIFT_SHEET.get_all_values()[1:]

    # Filter shift for the employees
    current_month_shifts = []
    next_month_shifts = []

    for record in shift_records:
        if record[0] == emp_id:
            # Parse the shift date from the record
            shift_date = datetime.strptime(record[5], '%Y-%m-%d')

            # Group shifts by current and next month 
            if first_day_of_current_month <= shift_date <= last_day_of_current_month:
                current_month_shifts.append(record)
            elif first_day_of_next_month <= shift_date <= last_day_of_next_month:
                next_month_shifts.append(record)

    # Display shifts for current month     
    if not current_month_shifts:
        print(f"\nNo Shifts found for {emp_name} ({emp_id}) in {today.strftime('%B')}.")
    else:
        print(f"\nShifts for {emp_name} ({emp_id}) in {today.strftime('%B')}:")
        for shift in current_month_shifts:
            print(f"Date: {shift[5]}, Shift Type: {shift[6]}, Start Time: {shift[8]}, End Time: {shift[9]}, Hours: {shift[7]}")
    
    #Display shifts for the following month
    next_month_name = first_day_of_next_month.strftime('%B')
    if not next_month_shifts:
        print(f"\nNo Shifts found for {emp_name} ({emp_id}) in {next_month_name}.")
    else:
        print(f"\nShifts for {emp_name} ({emp_id}) in {next_month_name}:")
        for shift in next_month_shifts:
            print(f"Date: {shift[5]}, Shift Type: {shift[6]}, Start Time: {shift[8]}, End Time: {shift[9]}, Hours: {shift[7]}")

    shift_menu(emp_id, emp_name)

if __name__ == "__main__":
    main_menu()