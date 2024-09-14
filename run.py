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
SHEET = GSPREAD_CLIENT.open("muloma_employee_managment_system").sheet1

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
    emp_id = input("Enter your Employee ID: ").strip().upper()



    """
    Fetch all rows from the 'Employee info' sheet startting from the second row
    """
    employee_data = SHEET.get_all_values()[1:] #skip the first row

    for row in employee_data:
        full_name = row[0] 
        stored_emp_id = row[1].strip().upper()

        if name.lower() == full_name.lower() and emp_id == stored_emp_id:
            print(f"Welcome, {name}!")

            #update the last Login data 
            current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            row_index = employee_data.index(row) + 2
            SHEET.update_cell(row_index, 7, current_time)

            shift_menu()
            return


    print(f"Welcome, {name}!")
    shift_menu()

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

    #Display valid departments and get the user's department 
    department = input("\nSelect your department from the list below: ")
    for i, dept in enumerate(valid_departments, 1):
        print(f"{i}. {dept}")

    department_choice = input("Enter the number that corresponds with your department: ")

    #validate department input
    while not department_choice.isdigit() or int(department_choice) not in range(1, len(valid_departments) + 1):
        print("Invalid choice. Please selecte a valid department number.")
        department_choice = input("Enter the number corresponding to your department: ")
    
    department= valid_departments[int(department_choice) - 1] 

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

    #Generate a short employee ID, 5 characters long
    emp_id = str(uuid.uuid4())[0:5].upper()

    #role = "Employee"

    """
    Get the date of account creation and last login time
    """
    date_of_creation = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    last_login = "N/A"

    """
    Append new employee data to Google sheet for all fields
    """
    SHEET.append_row([full_name, emp_id, email_or_phone, department, role, date_of_creation, last_login])


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
def shift_menu():
    print("\nShift Management Menu:")
    print("1. Start/End a shift")
    print("2. Look for available shifts")
    print("3. Log out")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
            handle_shift()
    elif choice == "2":
            available_shift()
    elif choice == "3":
            main_menu()
    else:
        print("Invalid choice. Please try again.")
        shift_menu()
    
    """
    Function to handle shift (Start, Pause, Resume, End)
    """
def handle_shift():
    shift_status = ""
    start_time = None
    pause_time = None
    resume_time = None
    end_time = None

    while True:
        print("\nShift Menu:")
        print("1. Start shift")
        print("2. Pause shift")
        print("3. Resume shift")
        print("4. End shift")
        action = input("Select an action: ")

        if action == "1":
            start_time = datetime.now()
            shift_status = "Shift started"
            print(f"Shift started at {start_time.strftime('%H:%M:%S')}")
        elif action == "2" and start_time:
            pause_time = datetime.now()
            shift_status = "Shift paused"
            print(f"shift paused at {pause_time.strftime('%H:%M:%S')}") #round time to there nearest seconds
        elif action == "3" and pause_time:
            resume_time = datetime.now()
            shift_status = "Shift resumed"
            print(f"Shift resumed at {resume_time.strftime('%H:%M:%S')}")
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
        print(f"Total hours worked: {str(total_time).split('.')[0]}")
        print(f"Total brak time: {str(break_time).split('.')[0]}")
    shift_menu()
    





if __name__ == "__main__":
    main_menu()