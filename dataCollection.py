import time
from datetime import datetime
import sqlite3

from gpiozero import Button, LED, PWMLED, Servo
import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep

# tensorflow image recognition model
from lobe import ImageModel

# custom google sheets API
from Sheets_API import Sheets_Logging

dbname='sensorData.db'

# create camera, LED, servo, and ir sensor objects
button = Button(2)

red_led = LED(17) # bin state LED
white_led = PWMLED(24) # camera state LED

general_ir = Button(23)
recycling_ir = Button(22)

servo = Servo(19)
servo.value = 0  # initate servo to mid point

# count that records row number for google sheets writing
global count
count = 133 # change to current position of last entry

camera = PiCamera()

# Load Lobe TF model
model = ImageModel.load('/home/pi/Lobe')


# run after button press
def get_data(count):   
    white_led.blink(0.1,0.1)
    sleep(1)
    print("Pressed")
    white_led.on()
    # Start the camera preview
    camera.start_preview(alpha=200)
    # wait 0.5s for light adjustment
    sleep(0.5) 
    # image rotation for camera
    camera.rotation = 90
    # new image file path
    camera.capture('/home/pi/Sensors_Database/dhtWebServer/static/image.jpg')
    camera.stop_preview()
    white_led.off()
    sleep(1)
    
    # Run photo through Lobe TF model
    result = model.predict_from_file('/home/pi/Sensors_Database/dhtWebServer/static/image.jpg')
    packaging = result.prediction
    
    # check which bin chosen through ir sensors
    general = 0
    recycling = 0
    
    # start 10 second timer
    timeout = time.time() + 10 
    print('waiting for bin...')
    # turn on red LED to tell user bin is ready
    red_led.on() 
    # start while loop waiting for IR sensor to be tripped or until 10 seconds have passed
    while time.time() < timeout:
        if general_ir.is_pressed is False:
            general = 1
            print('general')
            break
        if recycling_ir.is_pressed is False:
            recycling = 1
            print('recycling')
            break
        time.sleep(0.1)
    
    red_led.off()

    # log data on local SQlite database AND cloud google sheets API
    log_data(packaging, general, recycling, count)

    
# log sensor data
def log_data (packaging, general, recycling, count):
    print("logging data...")
    
    # log data on local SQlite database
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    
    curs.execute("INSERT INTO trash_data values(datetime('now'), (?), (?), (?))", (packaging, general, recycling))
    conn.commit()
    conn.close()
    
    # log data on cloud through google sheets API
    doc = Sheets_Logging()
    date = datetime.now() # get current date and time
    
    # assign g/co2 variable
    if packaging == "Aluminium Can":
        co2 = 164
    if packaging == "Cardboard Brown":
        co2 = 10
    if packaging == "Cardboard White":
        co2 = 10
    if packaging == "Egg Carton":
        co2 = 33
    if packaging == "Foil":
        co2 = 55
    if packaging == "Glass Bottle Opaque":
        co2 = 1722
    if packaging == "Long Tin Can":
        co2 = 575
    if packaging == "Plastic Bottle Clear":
        co2 = 458
    if packaging == "Plastic Film Clear":
        co2 = 4
    if packaging == "Plastic Milk Bottle":
        co2 = 118
    if packaging == "Plastic Tray Opaque":
        co2 = 115
    if packaging == "Plastic Tray Transparent":
        co2 = 96
    if packaging == "Plastic Tub Small":
        co2 = 46
    if packaging == "Pringles Can":
        co2 = 44
    if packaging == "Short Tin Can":
        co2 = 196
        
    # write data to google sheets
    data = [str(date).split('.')[0], packaging, general, recycling, co2]
    print(data)
    doc.write_data(data, count)
    
    # auto sort mode
    auto_sort(packaging) # uncomment to enable auto sort mode

# optional display database data
def display_data():
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    print ("\nEntire database contents:\n")
    for row in curs.execute("SELECT * FROM trash_data"):
        print (row)
    conn.close()

# auto sort mode
def auto_sort(packaging):
    print('auto sorting...')
    
    # whcih bin to throw away in: 1 = recycling, 0 = general
    which_bin = 1 

    if packaging == "Aluminium Can":
        which_bin = 0
    if packaging == "Cardboard Brown":
        which_bin = 0
    if packaging == "Cardboard White":
        which_bin = 0
    if packaging == "Egg Carton":
        which_bin = 0
    if packaging == "Foil":
        which_bin = 0
    if packaging == "Glass Bottle Opaque":
        which_bin = 0
    if packaging == "Long Tin Can":
        which_bin = 0
    if packaging == "Plastic Bottle Clear":
        which_bin = 0
    if packaging == "Plastic Film Clear":
        which_bin = 1
    if packaging == "Plastic Milk Bottle":
        which_bin = 0
    if packaging == "Plastic Tray Opaque":
        which_bin = 1
    if packaging == "Plastic Tray Transparent":
        which_bin = 0
    if packaging == "Plastic Tub Small":
        which_bin = 1
    if packaging == "Pringles Can":
        which_bin = 1
    if packaging == "Short Tin Can":
        which_bin = 0
        
    # actuate servo accordingly
    if which_bin == 1:
        servo.value = 1 # push trash left to recycling 
    if which_bin == 0:
        servo.value = -1 # push trash right to general
        
    sleep(2)
    servo.value = 0
    
# wait for button press    
while True:
    if button.is_pressed:
        count += 1 # increment to write to next row on google sheets
        get_data(count)
        #display_data()
    else:
        # pulse status light
        white_led.pulse(2,1)
    sleep(1)

