import datetime

def gettime():
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return current_time