# Uses a saved court configuration to track the ball

import CustomClasses as CC

validFile = False

while not validFile:
    try:
        location = input("Input the file path of your camera configuation\n")
        f = open(location, "r")
        validFile = True
    except:
        validFile = False

activeCourt = CC.Court()
activeCourt.fromTxt(f.read())
f.close()
t = input("Chose a title and recording will begin. To stop hit enter ")
t = t +".txt"
f = open(t, "w")

while not CC.keyboard.is_pressed("enter"):
    ans = activeCourt.ballPos()
    s = str(ans[0])+ " " + str(ans[1])+" " + str(ans[2]) +"\n"
    f.write(s)

    if CC.keyboard.is_pressed("p"):
        print ("recoding paused. Hit c to contiue")
        while not CC.keyboard.is_pressed("c"):
            CC.cv2.waitKey(1)

f.close()
print("Recoding is saved")
    
