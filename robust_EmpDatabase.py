from logging import raiseExceptions

print("*" * 80)
print("*" + "Rudy's Employee DataBase".center(78, " ") + "*")
print("*" * 80)


def checkForDigit(input):
    for i in input:
        if i.isdigit():
            return True
        else:
            pass
    return False

# This will print the menu to give user 3 options
def displayMenu():
    print(" " * 20 + "*" * 40 + " " * 20)
    print(" " * 20 + "*" + "HOME".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Add Employee: Type '1'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Remove Employee: Type '2'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Print Database: Type '3'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" * 40 + " " * 20)

def displayRemoveSearch():
    print(" " * 20 + "*" * 40 + " " * 20)
    print(" " * 20 + "*" + "Remove by EmpID: Type '1'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Remove by Employee Name: Type '2'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" * 40 + " " * 20)

# custom function to display any message in fancy box
def displayMessage(message):
    print(" " * 20 + "*" * 40 + " " * 20)
    print(" " * 20 + "*" + f"{message}".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" * 40 + " " * 20)


# Menu at the end of every add or remove or print
def displayAction():
    print(" " * 20 + "*" * 40 + " " * 20)
    print(" " * 20 + "*" + "MENU".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "WARNING! N or No will QUIT Program".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Back to Home?: Y/N".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" + "Print Database: Type 'P'".center(38, " ") + "*" + " " * 19)
    print(" " * 20 + "*" * 40 + " " * 20)

def displayError(input):
    print(f" {input} ".center(80,"*"))



## PROGRAM STARTS HERE! ##
#Have 1 employee by default
DataBase = {'emp1': {'name': 'John Pork', 'job': 'Head Chef', 'salary': 60000},
            }


# numEmployees will be used as the Key
numEmployees = 1
goHome = False
INVALID_input = False
## Program Starts Here ##
while(True):
    displayMenu()
    # get user's choice
    choiceInput = input("Input: ")

    # User Choses to "ADD"
    if choiceInput == '1':
        try:
            # Get Employee info from user
            displayMessage("Enter Employee Name")
            empName = input("Input Name: ")
            if checkForDigit(empName) == True:
                raise Exception
            displayMessage(f"Job Title for {empName}")
            empJob = input("Input Job: ")
            displayMessage("Enter their Salary (Yearly)")
            empSalary = input("Input Salary: ")
            #raise an error if the user trying to put a non digit number as a salary
            if not empSalary.isdigit():
                raise TypeError
        except TypeError:
            displayError(" Error: You can only input Integer (Whole) Numbers.")
        except:
            displayError("Error: Invalid Input.")

        else:
            # Put Employee into Database if no problems occur
            empKey = "emp" + str(numEmployees + 1)
            numEmployees += 1
            newEmployee = {empKey: {'name': empName, 'job': empJob, 'salary': empSalary}}
            DataBase.update(newEmployee)
            print(f"{empName} has been added to the database!")

    # User Chose "REMOVE"
    elif choiceInput == '2':
        #display menu
        displayRemoveSearch()
        #get user user choice
        removeInput = input("Input: ")
        if removeInput == "1":
            displayMessage("Enter emp'ID'")
            #get empID from User
            removeInput = input("Input: ")
            person = DataBase.get(removeInput)
            #If user input empID not in DataBase. Give an error message
            if person is None:
                displayError("Error. Employee not found.")
            #If empID is found. Remove them from the Database
            else:
                print(person)
                DataBase.pop(removeInput)
                print(f"{removeInput} has been removed!")
        #User chose to remove by name
        elif removeInput == "2":
            displayMessage("Enter Employee Name: ")
            #Get emp name from user
            removeInput = input("Enter Employee Name: ")
            resultCounter = 0
            #iterate through database to find emp with user name given
            for id, people in DataBase.items():
                #if name found in data base, ask to remove them (In case multiple employees have the same name)
                #Will keep iterating until user says "yes" (to remove) or until there is no one else with that name
                if DataBase[id].get('name') == removeInput:
                    #result counter to see if anyone was even found. Zero means no one of that name is in tne database
                    resultCounter += 1
                    print("Result " + str(resultCounter) + ":")
                    print(DataBase[id].get('name'))
                    print(DataBase[id].get('job'))
                    print(DataBase[id].get('salary'))
                    print()
                    displayMessage("Is this who you want to remove?(Y/N)")
                    yesOrNoRemove = input("Input: ").strip().lower()
                    if yesOrNoRemove == "y" or yesOrNoRemove == "yes":
                        print(f"{DataBase[id].get('name')} has been removed!")
                        del DataBase[id]
                        break
                    elif yesOrNoRemove == "n" or yesOrNoRemove == "no":
                        pass
                    else:
                        displayError("Invalid Input")
                        break
            if resultCounter == 0:
                displayMessage("We couldn't find someone by the name:")
                displayMessage(removeInput)
                print()
            else :
                displayMessage("End of Search")
                print()
        else:
            displayError("Invalid Input.")
    # User chose "PRINT DATABASE"
    elif choiceInput == '3':
        print(DataBase)

    #User put in an INVALID input
    else:
        displayError("Invalid Input")

    #Find out of User wants to QUIT to Continue doing stuff
    while (choiceInput != 'y' and choiceInput != 'yes' and choiceInput != 'n' and choiceInput != 'no'):
        displayAction()
        choiceInput = input("Input: ").strip().lower()
        if choiceInput == 'p':
            print(DataBase)
        elif choiceInput != 'y' and choiceInput != 'yes' and choiceInput != 'n' and choiceInput != 'no':
            displayError("Invalid Input")
    #This will quit the program
    if choiceInput == 'n' or choiceInput == 'no':
        break
    else:
        pass