# Allows user to create a camera configuration
# Does not check for valid inputs

import CustomClasses as CC

print("We will now begin setting up your court")

cn = input("Court Name ")
br = float(input("ball radius "))
activeCourt = CC.Court(br,cn)

n = input("would you like to add a camera y=yes anything else no ")

while n == "y":
    activeCourt.addCam()
    n = input("would you like to add another camera y=yes anything else no ")

fileName = cn + ".txt"

f = open(fileName, "w")
f.write(activeCourt.__repr__())
f.close()
print("The camera configuration is now saved")
