# Classes and methods used to track the ball

import sys, os
import cv2
import cvzone 
from cvzone.ColorModule import ColorFinder
import math
import keyboard

class Camera:
    
    def __init__(self, xPos = 0, yPos = 0, zPos = 0, xAngle = 0, yAngle = 0, zAngle = 0 , scale = [1,2], hsvVals = {'hmin': 0, 'smin': 0, 'vmin': 0, 'hmax': 179, 'smax': 255, 'vmax': 255}, camNumb = 0, camName = "My Cam"):

        self.pos = [xPos, yPos, zPos]
        self.angle = [xAngle, yAngle, zAngle]
        self.scale = scale #scale = [distacne from camera(m)/width(m), distacne from camera(m)/height(m)]
        self.hsvVals = hsvVals
        self.camNumb = camNumb
        self.camName = camName
        self.video = cv2.VideoCapture(camNumb)

    def __repr__(self):
        ans = str(self.pos[0])+" "+str(self.pos[1])+" "+str(self.pos[2])+" "+str(self.angle[0])+" "+str(self.angle[1])+" "+str(self.angle[2])+" "+str(self.scale[0])+" "+str(self.scale[1])+" "
        ans = ans + str(self.hsvVals["hmin"])+" "+str(self.hsvVals["smin"])+" "+str(self.hsvVals["vmin"])+" "+str(self.hsvVals["hmax"])+" "+str(self.hsvVals["smax"])+" "+str(self.hsvVals["vmax"])+" "+ str(self.camNumb)+" "+self.camName
        return ans

    def fromStr(self, cam):
        temp = cam.split(" ",15)
        self.pos[0] = float(temp[0])
        self.pos[1] = float(temp[1])
        self.pos[2] = float(temp[2])
        self.angle[0] = float(temp[3])
        self.angle[1] = float(temp[4])
        self.angle[2] = float(temp[5])
        self.scale[0] = float(temp[6])
        self.scale[1] = float(temp[7])
        self.hsvVals["hmin"] = int(temp[8])
        self.hsvVals["smin"] = int(temp[9])
        self.hsvVals["vmin"] = int(temp[10])
        self.hsvVals["hmax"] = int(temp[11])
        self.hsvVals["smax"] = int(temp[12])
        self.hsvVals["vmax"] = int(temp[13])
        self.camNumb = int(temp[14])
        self.camName = temp[15]
        self.video = cv2.VideoCapture(self.camNumb)
    
    def __str__(self):

        ans = self.camName + " Positioned at " + str(self.pos[0]) + ", " + str(self.pos[1]) + ", " + str(self.pos[2])     
        ans = ans + "\nScale = " + str(self.scale[0])+", " + str(self.scale[1])+ ". Camera is rotated " + str(self.angle) + ". Camera number " + str(self.camNumb) + "."
        ans = ans + "\nhsvVals " + str(self.hsvVals)
        exists, tempFrame = self.video.read()

        if exists:            
            cv2.imshow("Current view", tempFrame)
        else:
            ans = ans + "\nNo video found"
            
        return ans

    def changeCam(self, cam = 0):
        self.camNumb = cam
        self.video = cv2.VideoCapture(cam)
        exists, tempFrame = self.video.read()
        return exists
    
    def checkCam(self):
        exists, tempFrame = self.video.read()
        return exists

    def changeWidth(self, width):
        self.video.set(3,width)

    def changeHeight(self, height):
        self.video.set(4,height)

    def getFrame(self):
        exists, tempFrame = self.video.read()
        return tempFrame

    def changeHue(self, lower, upper):
        self.hsvVals["hmin"] = lower
        self.hsvVals["hmax"] = upper

    def changeSat(self, lower, upper):
        self.hsvVals["smin"] = lower
        self.hsvVals["smax"] = upper

    def changeVal(self, lower, upper):
        self.hsvVals["vmin"] = lower
        self.hsvVals["vmax"] = upper
    

    def getRelativePosition(self):
        ans = None        
        exists, tempFrame = self.video.read()

        if exists:
            imgColor, mask = ColorFinder(False).update(tempFrame, self.hsvVals) 
            imgContour, contours = cvzone.findContours(tempFrame, mask, 150)
            if contours:
                ans = [contours[0]['center'][0], contours[0]['center'][1], int(contours[0]['area'])]

        return ans

    def getTruePosition(self, ballRadius): #returns the postions of the ball in meters WRT the origin [X, Y, Z]
        relative = self.getRelativePosition()
        if relative == None:
            return None
        ans = self.pos.copy()
        
        #finding distance from camera
        metersPerPixle = ballRadius/(math.sqrt(relative[2]/math.pi)) #m/pixles ratio of constant ball radius to aproximat radius in pixles of the ball in the frame
        widthInMeters = metersPerPixle*self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        heightInMeters = metersPerPixle*self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        distanceInMeters = (widthInMeters*self.scale[0] + heightInMeters*self.scale[1])/2 # average of 2 for more accuracy

        zAdjust = (metersPerPixle*relative[0] - widthInMeters/2)*math.cos(math.radians(self.angle[0]) + (metersPerPixle*relative[1] - heightInMeters/2)*math.sin(math.radians(self.angle[0]))) #width distance for z moment adjustment
        yAdjust = (heightInMeters/2 - metersPerPixle*relative[1])*math.cos(math.radians(self.angle[0])) - (metersPerPixle*relative[0] - widthInMeters/2)*math.sin(math.radians(self.angle[0]))  

        camToPoint = math.sqrt((distanceInMeters**2) + (zAdjust**2) + (yAdjust**2))
        
        zAdjust = math.atan(zAdjust/distanceInMeters)
        yAdjust = math.atan(yAdjust/distanceInMeters)

        ans[0] = ans[0] + camToPoint*math.cos(math.radians(self.angle[1]) + yAdjust)*math.cos(math.radians(self.angle[2]) + zAdjust)
        ans[1] = ans[1] + camToPoint*math.cos(math.radians(self.angle[1]) + yAdjust)*math.sin(math.radians(self.angle[2]) + zAdjust)
        ans[2] = ans[2] + camToPoint*math.cos(math.radians(self.angle[0]))*math.sin(math.radians(self.angle[1]) + yAdjust)
        
        return ans
        
    def saveConfig(self):
        self.video = None

    def prepCam(self):
        self.video = cv2.VideoCapture(self.camNumb)

    def HSVSlider(self, key, lower, upper):

        cv2.waitKey(1000)
        exists, img = self.video.read() # Read the value of the camera
        if exists:

            while exists and not keyboard.is_pressed("enter"):
                
                exists, img = self.video.read()
                imgColor, mask = ColorFinder(False).update(img, self.hsvVals) 
                imgContour, contours = cvzone.findContours(img, mask)

                imgStack = cvzone.stackImages([img, imgColor, mask, imgContour], 2, 0.5)
                cv2.imshow("Image", imgStack) # Show the image filmed by the camera
                cv2.waitKey(1)

                if keyboard.is_pressed("left") and self.hsvVals[key] > lower:
                    self.hsvVals[key] = self.hsvVals[key] - 1
                elif keyboard.is_pressed("right") and self.hsvVals[key] < upper:
                    self.hsvVals[key] = self.hsvVals[key] + 1

    def findHSV(self):
        key = ['hmin','hmax','smin','smax','vmin','vmax']
        self.HSVSlider(key[0], 0, 179)
        cv2.waitKey(1000)
        print("done 1")
        self.HSVSlider(key[1], self.hsvVals[key[0]], 179)
        cv2.waitKey(1000)
        print("done 2")
        self.HSVSlider(key[2], 0, 255)
        cv2.waitKey(1000)
        print("done 3")
        self.HSVSlider(key[3], self.hsvVals[key[2]], 255)
        cv2.waitKey(1000)
        print("done 4")
        self.HSVSlider(key[4], 0, 179)
        cv2.waitKey(1000)
        print("done 5")
        self.HSVSlider(key[5], self.hsvVals[key[4]], 179)
        cv2.waitKey(1000)
        print("done 6")

    def findHSVFast(self):

        myColorFinder = ColorFinder(True)
        temp = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        try:
            while True:
                success, img = self.video.read() # Read the value of the camera
                imgColor, mask = myColorFinder.update(img, self.hsvVals) 
                imgContour, contours = cvzone.findContours(img, mask, 150)
                imgStack = cvzone.stackImages([img, imgColor, mask, imgContour], 2, 0.5)
                cv2.imshow("Image", imgStack) # Show the image filmed by the camera
                self.hsvVals = myColorFinder.getTrackbarValues()
                cv2.waitKey(1)
        except:
            sys.stdout = temp
            print("done with HSV vals")

    def findScale(self, ballRadius):
        exists, img = self.video.read() # Read the value of the camera

        if exists:
            print("To calibrate the camera place the ball 1m from the lense in the center of the cameras vision")
            print("When the ball is place and higlited in blue hit the enter key")
            while exists and not keyboard.is_pressed("enter"):
                
                exists, img = self.video.read()
                imgColor, mask = ColorFinder(False).update(img, self.hsvVals) 
                imgContour, contours = cvzone.findContours(img, mask, 150)

                imgStack = cvzone.stackImages([img, imgColor, mask, imgContour], 2, 0.5)
                cv2.imshow("Image", imgStack) # Show the image filmed by the camera
                cv2.waitKey(1)
        
        temp = self.getRelativePosition()
        
        if not (temp == None):
            metersPerPixle = ballRadius/(math.sqrt(temp[2]/math.pi))
            self.scale[0] = 1/(metersPerPixle*self.video.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.scale[1] = 1/(metersPerPixle*self.video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
        

class Court: #stores court config
    
    def __init__(self, ballRadius = 0.03, courtName = "My Court"):
        self.courtName = courtName
        self.ballRadius = ballRadius
        self.allCams = []

    def __repr__(self):
        ans = str(self.courtName) + "," + str(self.ballRadius)

        for i in self.allCams:
            ans = ans +","+i.__repr__()

        return ans

    def fromTxt(self, txt):
        temp = txt.split(",")

        self.courtName = temp[0]
        self.ballRadius = float(temp[1])

        for i in temp[2:]:
            self.allCams.append(Camera())
            self.allCams[-1].fromStr(i)

    def __str__(self):
        ans = self.courtName + "\n" +  "Ball has radius " + str(self.ballRadius) + "m" + "\n"

        for i in self.allCams:
            ans = ans + i.__repr__() + "\n"

        return ans

    def saveCourt(self):
        for i in self.allCams:
            i.saveConfig()
            
    def loadCourt(self):
        for i in self.allCams:
            i.prepCam()

    def ballPos(self):

        ans = None
        total = 0
        for i in self.allCams:
            temp = i.getTruePosition(self.ballRadius)

            if not temp == None:

                if total == 0:
                    ans = temp
                else:
                    ans[0] = ans[0] + temp[0]
                    ans[1] = ans[1] + temp[1]
                    ans[2] = ans[2] + temp[2]

                total = total + 1

        if total == 0:
            return [0,0,-1]
        
        ans[0] = round(ans[0]/total, 3)
        ans[1] = round(ans[1]/total, 3)
        ans[2] = round(ans[2]/total, 3)

        return ans

    def addCam(self):
        xPos = float(input("X positon of the camera "))
        yPos = float(input("Y positon of the camera "))
        zPos = float(input("Z positon of the camera "))
        xM = int(input("Rotation of the camera about the X axis un degrees "))
        yM = int(input("Rotation of the camera about the Y axis un degrees "))
        zM = int(input("Rotation of the camera about the Z axis un degrees "))
        camName = input("camera name ")
        camNumb = int(input("camera Number "))
        self.allCams.append(Camera(xPos, yPos, zPos, xM, yM, zM, [1,1], {'hmin': 0, 'smin': 0, 'vmin': 0, 'hmax': 179, 'smax': 255, 'vmax': 255}, camNumb, camName))
        self.allCams[-1].findHSVFast()
        self.allCams[-1].findScale(self.ballRadius)
        cv2.destroyAllWindows()
        print ("addition compleat")       


class Ball:

    def __init__(self, radius, hsvVals):
        self.radius = radius
        self.hsvVals = hsvVals

    def __repr__(self):
        ans = "radius is " + str(radius)
        ans = ans + "\nhsvVals " + str(hsvVals)

    
    
        
