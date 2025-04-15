import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
from tkinter import Tk,Label,Button,Checkbutton,BooleanVar,NORMAL,DISABLED
from paddleocr import PaddleOCR
from PIL import Image,ImageTk
from time import time
from datetime import datetime
from utils import *

device = 'cuda'
yolo = YOLO('./model/yolo12n.pt').to(device)
licensePlateModel = YOLO('./model/licensePlateDetectionM2V11.pt').to(device)
ocrModel = PaddleOCR(use_angle_cls=True, use_space_char=True, lang='en', use_gpu=True)
deepsort = DeepSort(
                max_age=20,
                n_init=15,
                nms_max_overlap=0.5,
                max_cosine_distance=0.7,
                nn_budget=None,
                override_track_class=None,
                embedder="mobilenet",
                half=True,
                bgr=True,
                embedder_model_name=None,
                embedder_wts=None,
                polygon=False,
                today=None)

videoPath = './data/carsTraffic1.mp4'
video = cv2.VideoCapture(videoPath)
previousTime = currentTime = 0
trackClassList = []
vehicleClassList = (1,2,3,5,7)
objectThresHold = 0.5
licensePlateThresHold = 0.7
ocrThresHold = 0.4
countList = {
    "people":set(),
    "vehicle":set()
    }
classNames = list(countList.keys())
# vhehicleLog = {trackID : [inTime, outTime, numberPlate, textScore]}
vehicleLog = {}

def detectLicensePlate(vehicle_img,vehicle_id): 
    boxes = licensePlateModel(vehicle_img,verbose=False,conf=licensePlateThresHold)[0].boxes
    for box in boxes:
        x1,y1,x2,y2 = map(int,box.xyxy[0])
        cv2.rectangle(vehicle_img,(x1,y1),(x2,y2),(0,255,0),1)
        gray = cv2.cvtColor(vehicle_img[y1:y2,x1:x2],cv2.COLOR_BGR2GRAY)
        cv2.threshold(gray,64,255,cv2.THRESH_BINARY_INV)
        
        #read numberplate
        readNumberPlate(gray,vehicle_id)

        if(vehicleLog[vehicle_id][2] != ''):
            cv2.rectangle(vehicle_img,(x1,y1-20),(x2+10,y1),(0,0,0),cv2.FILLED)
            cv2.putText(vehicle_img,vehicleLog[vehicle_id][2],(x1,y1-2),cv2.FONT_HERSHEY_SIMPLEX,0.4,(255,255,255),1)

def readNumberPlate(grayImg,vehicleId) -> None:
    numberPlateText = ''
    textScore = -1
    result = ocrModel.ocr(grayImg)[0]
    if(result != None):
        for line in result:
            text = line[1]
            score = text[1]
            if(score > ocrThresHold):
                textScore = score
                numberPlateText += text[0] + ' '

    if(textScore > vehicleLog[vehicleId][3]):
        vehicleLog[vehicleId][2] = numberPlateText
        vehicleLog[vehicleId][3] = textScore


def main():
    global frame,previousTime,currentTime
    currentTime = time()
    
    ret,frame = video.read()
    frame = cv2.resize(frame,(1080,600))
    if(ret is False):
        close()
        return
    detect = yolo(frame,classes=trackClassList,conf=objectThresHold,verbose=False)[0]
    objects = []

    for box in detect.boxes:
        conf,cls = box.conf[0],int(box.cls[0])
        x1,y1,x2,y2 = map(int,box.xyxy[0])
        objects.append([[x1,y1,x2-x1,y2-y1],conf,cls])
    tracker = deepsort.update_tracks(objects,frame=frame)
    
    
    if(len(trackClassList) != 0):
        for track in tracker:
            if not track.is_confirmed():
                continue
            id,cls = track.track_id, track.get_det_class()
            color = getColor(cls)
            tx1,ty1,tx2,ty2 = map(int,track.to_ltrb())

            # check vehicle inside at lane
            if(checkVarList[2].get() and (tx1 > 160 and tx2 < 915)):

                if((vehicleLog.get(id)==None)):
                    vehicleLog[id] = [datetime.now().strftime("%I:%M:%S"), '', '', 0]
                
                if((ty2 > 550 and vehicleLog[id][1] == '')):
                        vehicleLog[id][1] = datetime.now().strftime("%I:%M:%S")

                if(cls in vehicleClassList):
                    carImg = frame[ty1:ty2, tx1:tx2]
                    if(carImg.size != 0):
                        detectLicensePlate(carImg,id)
            
            #draw boundingBox putText object-name
            cv2.rectangle(frame,(tx1,ty1),(tx2,ty2),color,1)
            cv2.putText(frame,detect.names[cls],(tx1,ty1),cv2.FONT_HERSHEY_SIMPLEX,0.7,color,1)
            
            #count object
            if(cls == 0):
                countList["people"].add(id)
            elif(cls in vehicleClassList):
                countList["vehicle"].add(id)
        
        #Print Count
        countTextYAxis = 80
        for i in range(0,len(countList)):
            if(checkVarList[i].get()):
                key = classNames[i]
                cv2.putText(frame,f'{key} count: {len(countList[key])}',(10,countTextYAxis),cv2.FONT_HERSHEY_SIMPLEX,1,(0,120,255),2)
                countTextYAxis += 50
    #FPS
    fps = 1/(currentTime-previousTime)
    previousTime = currentTime
    fps = f'FPS : {fps:.2f}'
    cv2.putText(frame,fps,(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,120,255),3)
    
    #draw lane blue-line
    cv2.line(frame,(160,550),(915,550),(255,0,0),1)

    photo = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)))
    imgLabel.img = photo
    imgLabel.configure(image=photo)
    root.after(10,main)

def close() -> None:
    writeLog(vehicleLog)
    root.quit()

def modifyclassList(trackClassList,cls):
    if(cls == 0):
        if(cls in trackClassList):
            trackClassList.remove(0)
            checkboxChangeState(personCountCheckBox,False)
        else:
            trackClassList.append(0)
            personCountCheckBox.configure(state=NORMAL)
    
    else:
        if( 2 in trackClassList):
           trackClassList = [0]
           checkboxChangeState(vehicleCountCheckBox,False)
           checkboxChangeState(licensePlateCheckBox,False)
        else:
            vehicleCountCheckBox.configure(state=NORMAL)
            licensePlateCheckBox.configure(state=NORMAL)
            for classID in vehicleClassList:
                trackClassList.append(classID)




root = Tk()
imgLabel = Label()

closeBtn = Button(text="Close",command=close,width=6,height=1)
personBtn = Button(text="Person",command=lambda: modifyclassList(trackClassList,0),width=10,height=1)
vehicleBtn = Button(text="vhicle",command=lambda: modifyclassList(trackClassList,[1,2,3,5,7]),width=10,height=1)
checkVarList = [BooleanVar(),BooleanVar(),BooleanVar()]
personCountCheckBox = Checkbutton(text="count person", variable=checkVarList[0], onvalue=True,offvalue=False)
vehicleCountCheckBox = Checkbutton(text="count vehicle",variable=checkVarList[1], onvalue=True, offvalue=False)
licensePlateCheckBox = Checkbutton(text="detect licensePlate",variable=checkVarList[2],onvalue=True,offvalue=False)

#checkbox state
personCountCheckBox.configure(state=DISABLED)
vehicleCountCheckBox.configure(state=DISABLED)
licensePlateCheckBox.configure(state=DISABLED)

#layout
imgLabel.grid(row=0,column=0,columnspan=4)
closeBtn.grid(row=1,column=2)
personBtn.grid(row=1,column=0)
vehicleBtn.grid(row=1,column=1)
personCountCheckBox.grid(row=2,column=0)
vehicleCountCheckBox.grid(row=2,column=1)
licensePlateCheckBox.grid(row=3,column=1,columnspan=1)

main()

cv2.destroyAllWindows()
root.mainloop()