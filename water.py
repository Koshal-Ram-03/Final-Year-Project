import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import serial
import time
import re
import warnings
import requests #for thingspeak
api = "B81ZJ29V89LGGJMK" #thingspeak api key
warnings.filterwarnings("ignore")

ser = serial.Serial('COM21', baudrate=9600)  # Adjust COM port and baudrate as needed
print("Serial connection opened successfully!")

# Load data from an Excel sheet and split into features and labels
data = pd.read_excel("water.xlsx", engine="openpyxl")


feature_1 = data['Turbuidity_val']
feature_2 = data['ph_val']
feature_3 = data['tds_val']
feature_4 = data['temperature']

label_1 = data['label_turbu']
label_2 = data['label_ph']
label_3 = data['label_tds']
label_4 = data['label_temp']




# Split the data into training and testing sets for each parameter
X_train_1, X_test_1, y_train_1, y_test_1 = train_test_split(feature_1, label_1, test_size=0.2, random_state=42)
X_train_2, X_test_2, y_train_2, y_test_2 = train_test_split(feature_2, label_2, test_size=0.2, random_state=42)
X_train_3, X_test_3, y_train_3, y_test_3 = train_test_split(feature_3, label_3, test_size=0.2, random_state=42)
X_train_4, X_test_4, y_train_4, y_test_4 = train_test_split(feature_4, label_4, test_size=0.2, random_state=42)






# Build Random Forest models for each parameter
model_1 = RandomForestClassifier(random_state=42)
model_1.fit(X_train_1.values.reshape(-1, 1), y_train_1)

model_2 = RandomForestClassifier(random_state=42)
model_2.fit(X_train_2.values.reshape(-1, 1), y_train_2)

model_3 = RandomForestClassifier(random_state=42)
model_3.fit(X_train_3.values.reshape(-1, 1), y_train_3)

model_4 = RandomForestClassifier(random_state=42)
model_4.fit(X_train_4.values.reshape(-1, 1), y_train_4)


# Initialize 6 variables (t, u, v, w, x, y)
t, u, v, w, x, y = 0, 0, 0, 0, 0, 0
def readData():
    global t, u, v, w, x, y 
    time.sleep(1)
    serial_data = ser.readline().decode().strip()
    
    #while not serial_data.startswith('a'):
        #serial_data = ser.readline().decode().strip()

    print("\n----------------------------")
    print("     -= Data Received =- ")
    print("----------------------------\n")
    print("Data:", serial_data, "\n")
    time.sleep(1)

    a = serial_data.find("a")
    b = serial_data.find("b")
    a = a +1
    Turbuidity_val = int(serial_data[a:b])
    print("Turbidity Val:",Turbuidity_val)

    b = serial_data.find("b")
    c = serial_data.find("c")
    b = b + 1
    ph_val= int(serial_data[b:c])
    print("ph Val:",ph_val)

    c = serial_data.find("c")
    d = serial_data.find("d")
    c = c + 1
    tds_val = int(serial_data[c:d])
    print("tds_Val:",tds_val)

    d = serial_data.find("d")
    a = serial_data.find("e")
    d = d + 1
    temperature = int(serial_data[d:a])
    print("Temperature_Val:",temperature)

    


    
            
    return Turbuidity_val,ph_val,tds_val,temperature

while True:


     Turbuidity_val,ph_val,tds_val,temperature= readData() #map(float, input_data.split(','))
     time.sleep(1)
     print("Uploading data to webserver....")
     time.sleep(2)
       
     queries = {"api_key": api, "field1":Turbuidity_val , "field2": ph_val, "field3" :tds_val,"field4" :temperature}
     r = requests.get('https://api.thingspeak.com/update', params=queries)
       
     if r.status_code == requests.codes.ok:
            print("Data Successfully Uploaded!")
     else:
            print("Error Code: " + str(r.status_code))
            time.sleep(1)


 
     x_prediction = model_1.predict([[Turbuidity_val]])[0]
     z_prediction = model_2.predict([[ph_val]])[0]
     w_prediction = model_3.predict([[tds_val]])[0]
     y_prediction = model_4.predict([[temperature]])[0]

     print("\nPredictions:")
     print(f'X Prediction: {x_prediction}')
     print(f'Y Prediction: {z_prediction}')
     print(f'Z Prediction: {w_prediction}')
     print(f'W Prediction: {y_prediction}')
   
      

    

     time.sleep(1)

     if x_prediction == 1:
       print("Feature 1 is normal")
	#ser.write(str('0').encode())
     else:
        print("Abnormal Feature 1 detected")

     if z_prediction == 1:
        print("Feature 2 is normal")
     else:
        print("Abnormal Feature 2 detected")

     if  w_prediction  == 1:
        print("Feature 3 is normal")
     else:
        print("Abnormal Feature 3 detected")
     if  y_prediction  == 1:
        print("Feature 4 is normal")
     else:
        print("Abnormal Feature 4 detected")

     

     values_string =f"t{x_prediction:.2f}u{z_prediction:.2f}v{w_prediction:.2f}w{ y_prediction:.2f}x"
     time.sleep(2)
     print(values_string)
     time.sleep(3)
     ser.write(bytes(values_string,'utf-8'))
     time.sleep(3)
     print("completed")
     time.sleep(3)



