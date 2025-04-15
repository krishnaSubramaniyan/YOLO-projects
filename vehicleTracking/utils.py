from datetime import datetime
from csv import DictWriter

#get a color based on classID
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
    with open(f"./log/{datetime.now().strftime('%d-%m-%y %I.%M.%S')}.csv", 'w') as csvFile:
        column = ["Vehicle Count","ID","In Time","Out Time","Number Plate", "OCR Score"]
        writer = DictWriter(csvFile,fieldnames=column)
        writer.writeheader()
        
        for car_id,logdata in vehicleLog.items():
            if(logdata[1] != '' and logdata[2] != ''):
                print(f"{vehicleCount} | {car_id} | {logdata[0]} | {logdata[1]} | {logdata[2]} | {logdata[3]}")
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
