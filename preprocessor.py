import re
import pandas as pd

def preprocess(data):
    pattern = r'\d{2}/\d{2}/\d{2}, \d{1,2}:\d{2}\s?[ap]m -'
    messages = re.split(pattern, data)[1:]
    messages = [msg.lstrip() for msg in messages if msg.lstrip()]     # To remove space before a message (can also use .strip())
    dates = re.findall(pattern, data)
    df = pd.DataFrame({'Date': dates, 'Message': messages})
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y, %I:%M %p -')

    users = []
    messages = []
    for message in df['Message']:
        entry = re.split(r'([\w\W]+?):\s', message, maxsplit=1)
        if entry[1:]: # user name
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('Group Notification')
            messages.append(entry[0])
        
    df['user'] = users
    df['message'] = messages
    df.drop(columns=['Message'], inplace=True)
    df['Year'] = df['Date'].dt.year 
    df['Month_num'] = df['Date'].dt.month   
    df['Only_date'] = df['Date'].dt.date
    df['Month'] = df['Date'].dt.month_name()
    df['Day'] = df['Date'].dt.day
    df['Day_name'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour
    df['Minute'] = df['Date'].dt.minute

    return df