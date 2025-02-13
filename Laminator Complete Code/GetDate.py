import datetime

def getdate():
    now = datetime.datetime.now()
    date_string = now.strftime("%d%m%Y")
    return date_string