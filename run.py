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
    emp_id = input("Enter your Employee ID: ").strip()
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



if __name__ == "__main__":
    main_menu()