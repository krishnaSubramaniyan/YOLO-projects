from datetime import datetime
from csv import DictWriter
from tkinter import NORMAL,DISABLED


def getColor(cls) -> tuple:
    if(cls == 0):
        return (255,0,0)
    else:
        return (0,0,255)

#disable checkbox
def checkboxChangeState(checkbox, buttonState=False) -> None:
    if(buttonState == False):
        checkbox.configure(state=DISABLED)
        checkbox.deselect()

# write csv file
def writeLog(vehicleLog):
    vehicleCount = 1
    with open(f"./log/{datetime.now().strftime('%d-%m-%y %I.%M.%S%P')}.csv", 'w') as csvFile:
        column = ["Vehicle Count","ID","In Time","Out Time","Number Plate", "OCR Score"]
        writer = DictWriter(csvFile,fieldnames=column)
        writer.writeheader()
        
        for car_id,logdata in vehicleLog.items():
            if(logdata[1] != '' and logdata[2] != ''):
                writer.writerow(
                    {
                        column[0]:vehicleCount,
                        column[1]:car_id,
                        column[2]:logdata[0],
                        column[3]:logdata[1],
                        column[4]:logdata[2],
                        column[5]:f'{logdata[3]:.6f}'
                    }
                )
                vehicleCount += 1
        print("vehicle log file wroted")

# modify tracking class list
def modifyTrackingObject(cls,trackClassList,checkbox_list):
    if(cls == 0):
        if(0 in trackClassList):
            trackClassList.remove(0)
            checkboxChangeState(checkbox_list[0],False)
        else:
            trackClassList.append(0)
            checkbox_list[0].configure(state=NORMAL)
    else:
        if(2 in trackClassList):
            for i in (1,2,3,5,7): trackClassList.remove(i)
            checkboxChangeState(checkbox_list[1],False)
            checkboxChangeState(checkbox_list[2],False)
        else:
            for i in (1,2,3,5,7): trackClassList.append(i)
            checkbox_list[1].configure(state=NORMAL)
            checkbox_list[2].configure(state=NORMAL)
