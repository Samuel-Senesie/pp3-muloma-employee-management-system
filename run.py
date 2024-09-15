"""
Imported libraries for runing the app
"""
import gspread
from google.oauth2.service_account import Credentials
import uuid #for generating unique ID
from datetime import datetime #date and time for shift timedtamps
import sys

#Set project scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("employee_info")
SHIFT_SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").worksheet("shift_data")

"""
Main menu to dispaly welcome message and login access
"""
def main_menu():
    print("Welcome to Muloma Employee Management System")
    answer =input("Do you have an account? (YES/NO): ").strip().lower()

    if answer == "yes":
        login()
    elif answer == "no":
        create_account()
    else:
        sys.exit("Thank you for using Muloma Employee Management System. Goodbye!")
"""
Login if account already exists
"""
def login():
    name = input("Enter your full Name: ").strip()
    emp_id = input("Enter your Employee ID: ").strip()

    """
    Fetch all rows from the 'Employee info' sheet startting from the second row
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
            SHEET.update_cell(row_index, 8, current_time)

            #pass employee ID and name to shift menu
            shift_menu(emp_id, name)
            return


    print(f"Login failed. The name or ID does not match our records")
    main_menu()

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
Function to create account for new Employees
"""
def create_account():
    first_name = input("Enter your first name: ").strip()
    last_name = input("Enter your last name: ").strip()
    email_or_phone = input("Enter your email or phone numer: ").strip()

    #Get employees date of birtf
    dob_input = input("Enter your date of birth (DD-MM-YYYY). ").strip()

    try:
        dob = datetime.strptime(dob_input, "%d-%m-%Y")
    except ValueError:
        print("Invalid date format. Please enter the date in the format DD-MM-YYYY.")
        return(create_account)
    
    #check users age, should be 18 or older
    today = datetime.now()
    age = today.year -dob.year - ((today.month, today.day) < (dob.month, dob.day))

    if age < 18:
        print("Sorry, you must be 18 years or older to create an account")
        main_menu()
        return
    
    #Retrieve existing employee data from database
    employee_info = SHEET.get_all_values()[1:]

    #Compare employee data for date of birth and email/phone number with existing data base
    for row in employee_info:
        stored_dob = row[1].strip()
        stored_email_or_phone = row[3].strip()

        if dob_input == stored_dob and email_or_phone == stored_email_or_phone:
            print("An account with the same data already exists.")
            main_menu()
            return

    #Display and collect employment type
    employment_type = ""
    while employment_type not in ["full-time", "part-time"]:
        employment_type = input("Are you a full-time or part-time employee? (full-time/part-time): ").strip().lower()
    
    #Full-time employees to selecte between fixed and flexible shifts 
    shift_type = ""
    if employment_type == "full-time":
        while shift_type not in ["fixed", "flexible"]:
            shift_type = input("Do you prefere a fixed of flexible shift? (fixed/flexible): ").strip().lower()
        
        if shift_type == "fixed":
            shift_time = ""
            while shift_time not in ["early", "late"]:
                shift_time = input("Would you prefer an early (08:00 - 16:30) or late (13:30 - 22:00) shift? (early/late): ").strip().lower()
        elif shift_type == "flexible":
            print("You will be assigned 3 early and 3 late shifts each week.")
    else:
        print("\nPart-time employees can work up to 3 days per week, for a total of 20-40hours.")
        print("Shift options are:")
        print("1. Morning: 08:00 - 13:00")
        print("2. Afternoon: 13:00 -16:00")
        print("3. Evening: 16:00 - 21:00")

        part_time_shifts = []
        while len(part_time_shifts) < 3:
            shift_choice = input(f"Select shift {len(part_time_shifts) + 1} (1/2/3): ").strip()
            if shift_choice in ["1", "2", "3"]:
                shift_map = {"1": "Morning: 08:00 - 13:00", "2": "Afternoon: 13:00 - 16:00", "3": "Evening: 16:00 - 21:30"}
                part_time_shifts.append(shift_map[shift_choice])
            else:
                print("Invalid choice. Please try again.")

    #Display valid departments and get the user's department 
    department = input("\nSelect your department from the list below: ")
    for i, dept in enumerate(valid_departments, 1):
        print(f"{i}. {dept}")

    department_choice = input("Enter the number that corresponds with your department: ")

    #validate department input
    while not department_choice.isdigit() or int(department_choice) not in range(1, len(valid_departments) + 1):
        print("Invalid choice. Please selecte a valid department number.")
        department_choice = input("Enter the number corresponding to your department: ")
    
    department = valid_departments[int(department_choice) - 1] 

    print("\nSelect your role from the list below: ")
    for i, role in enumerate(valid_roles, 1):
        print(f"{i}. {role}")
    role_choice = input("Enter that corresponds to your role: ")

    #validate role input
    while not role_choice.isdigit() or int(role_choice) not in range(1, len(valid_roles) + 1):
        print("Invalid choice. please selecte a valid role number")
        role_choice = input("Enter the number that corresponds to your role: ")
    
    role = valid_roles[int(role_choice) - 1] #get the selected role 


    full_name = f"{first_name} {last_name}"
    #Generate a short employee ID, 5 characters long in upperclass
    emp_id = str(uuid.uuid4())[0:5].upper()

    """
    Get the date of account creation and last login time
    """
    date_of_creation = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    last_login = "N/A"

    """
    Append new employee data to Google sheet for all fields
    """
    employee_data = [full_name, dob_input, emp_id, email_or_phone, department, role, employment_type, shift_type if employment_type == "full-time" else ", ".join(part_time_shifts), date_of_creation, last_login]
    SHEET.append_row(employee_data)

    print(f"Your account has been created! Your Employee ID is: {emp_id}")
    print("Write this ID down and keep it safe. You will need it to log in")
    main_menu()


    """
    Function to handle shift menu
    """
    #def shift_menu():
       # print("\nWhat would you like to do?")
       # print("1. Start/End a shift")
       # print("2. Look for available shifts")
        #choice = input("Enter your choice: ").strip()

        #if choice == "1":
           # handle_shift()
        #elif choice == "2":
           # available_shift()
        #elif choice == "3":
            #main_menu()
        #else:
            #print("Invalid choice. Return to main menu.")
           # main_menu()
    """
    Function to display shift menu
    """
def shift_menu(emp_id, emp_name):
    print("\nShift Management Menu:")
    print("1. Start/End a shift")
    print("2. Look for available shifts")
    print("3. Log out")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
            handle_shift(emp_id, emp_name)
    elif choice == "2":
            available_shift()
    else:
        print("Invalid choice. Please try again.")
        main_menu()
    
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

        #SHEET.append_row([emp_id, emp_name, department, role, date_of_creation, last_login])

        #print(f"Shift data to be added: {shift_data}")

        #try:
        SHIFT_SHEET.append_row(shift_data)
        print("Shift data updated successfully!")
        #except Exception as e:
            #print(f"Error appending shift data to Google Sheet: {e}")
"""
Function to display available shifts
"""
def available_shift():
    shifts = ["Morning Shifts: 9AM - 1PM", "Afternoon Shift: 1PM - 5PM", "Night Shift: 5PM - 9PM"]
    print("Available Shifts:")
    for i, shift in enumerate(shifts):
        print(f"{i+1}. {shifts}")
    choice = input("Select a shift: ")

    try: 
        shift_choice = shifts[int(choice) - 1]
        print(f"Shift confirmed: {shift_choice}")
    except (IndexError, ValueError):
        print("Invalid shift selection")



    main_menu()
    





if __name__ == "__main__":
    main_menu()