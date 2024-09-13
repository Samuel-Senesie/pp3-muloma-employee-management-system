"""
Imported libraries for runing the app
"""
import gspread
from google.oauth2.service_account import Credentials
import uuid #for generating unique ID
import datetime #date and time for shift timedtamps
import sys

#Set project scope
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_services_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("muloma-employee-management-system")

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
    name = input("Enter your full Name: ")
    emp_id = input("Enter your Employee ID: ")
    print(f"Welcome, {name}!")
    shift_menu()

"""
Function to create account for new Employees
"""
def create_account():
    first_name = input("Enter your first name: ")
    last_name = input("Enter your last name: ")
    email_or_phone = input("Enter your email or phone numer: ")
    department = input("Enter your department/unit: ")
    full_name = f"{first_name} {last_name}"

    #Generate a short employee ID, 5 characters long
    emp_id = str(uuid.uuid4())[0:5].upper()
    print(f"Your account has been created! Your Employee ID is: {emp_id}")
    print("Write this ID down and keep it safe. You will need it to log in")
    main_menu()



if __name__ == "__main__":
    main_menu()