import json                    #call jason file
import random                   #for random callng
import string                    #for string
from pathlib import Path           # we need to know path of jason file,and we will acess again again 
class Bank:
    database = 'data.json'      # To access data.json data
    data = []                  #for dummy data save in string format

    try:                       #for except handling
        if Path(database).exists():
           with open(database) as fs:    #To open file which is part of file handling
              data = json.loads(fs.read()) 
        else:
            print("No such file exists")
           
    except Exception as err:
        print(f"an exception occured as {err}")

    @classmethod
    def __update(cls):
        with open(cls.database,'w') as fs:
            fs.write(json.dumps(Bank.data))

    @classmethod
    def __accountgenerate(cls):       #using cls method so that anyone cannot acces that
        alpha = random.choices(string.ascii_letters,k=3)
        num = random.choices(string.digits,k = 3)
        spchar = random.choices("!@#$%^&*",k=1)
        id = alpha + num + spchar
        random.shuffle(id)
        return "".join(id)

    def Createaccount(self):   # We are create all user data here
        info = {
            "name":input("Tell your name :- "),
            "age":int(input("tell your age :- ")),
            "email": (input("tell your email :- ")),
            "pin": int(input("tell me your 4 number pin :- ")),
            "accountNo." : Bank.__accountgenerate(),
            "balance" : 0
        }
        if info['age'] < 18 or len(str(info['pin'])) != 4:
            print("sorry you can not create your account")
        else:
            print("account has been created successfully")
            for i in info:
                print(f"{i}:{info[i]}")   # To show all details after create account
            print("please note down your account number")

            Bank.data.append(info)

            Bank.__update()


    def depositmoney(self):
        accnumber = input("please tell me your account number:-")    #To deposite money function
        pin = int(input("Please enter your pin :-"))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if userdata == False:
            print("Sorry no data found")

        else:
            amount = int(input("How much you want to deposit :-"))
            if amount > 10000 or amount < 0:
                print("sorry your amount is too much , you can not deposit below 10000 and above 0")
            else:
                userdata[0]['balance'] += amount
                Bank.__update()            # we call update function
                print("Amount deposit successfull")



    def withdrawmoney(self):
            accnumber = input("please tell me your account number:-")    #To withdraw money function
            pin = int(input("Please enter your pin :-"))

            userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

            if userdata == False:
                print("Sorry no data found")

            else:
                amount = int(input("How much you want to withdraw :-"))
                if userdata[0]['balance'] < amount:
                    print("sorry your amount is too much , you do not have that much ")
                else:
                    userdata[0]['balance'] -= amount
                    Bank.__update()            # we call update function
                    print("Amount withdrew successfull")




    #To see details

    def showdetails(self):
        accnumber = input("please tell me your account number:-")    #To withdraw money function
        pin = int(input("Please enter your pin :-"))

        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]
        print("Your information are \n\n\n")
        for i in userdata[0]:
            print(f"{i}:{userdata[0][i]}")

    #To update details
    def updatedetails(self):
        accnumber = input("please tell me your account number:-")
        pin = int(input("Please enter your pin :-"))
        userdata = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin]

        if not userdata:
            print("No such user found")
        else:
            print("you can not change age , account number ,balance")

            print("Fill the details for change or leave it empty if no change")

            newdata = {
                "name":input("Please tell me name or press enter : "),
                "email":input("Please tell me new email or press enter to skip : "),
                "pin":input("Enter new Pin or enter to skip :")
            }

            if newdata["name"] =="":
                newdata["name"] = userdata[0]['name']
            if newdata["email"] =="":
                newdata["email"] = userdata[0]['email']
            if newdata["pin"] =="":
                newdata["pin"] = userdata[0]['pin']

            newdata['age'] = userdata[0]['age']

            newdata['accountNo.'] = userdata[0]['accountNo.']
            newdata['balance'] = userdata[0]['balance']

            if type(newdata['pin']) == str:
                newdata['pin'] = int(newdata['pin'])

            for i in newdata:
                if newdata[i] == userdata[0][i]:
                    continue
                else:
                    userdata[0][i] = newdata[i]
            Bank.__update()
            print("Details update sucessful")
           





user = Bank()

print("press 1 for create an account")
print("press 2 for Deposittiting the money in tha bank")
print("press 3 for withdrawing the money")
print("press 4 for details")
print("press 5 for updating the details")
print("press 6 for deleting your account")


check = int(input("tell your responce :- "))


if check == 1:
    user.Createaccount()   
if check ==2:
    user.depositmoney()     
if check == 3:
      user.withdrawmoney()
if check == 4:
    user.showdetails()
if check == 5:
    user.updatedetails()

