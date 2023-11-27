import os
from RPi import GPIO
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

os.system('clear') #clear screen, this is just for the OCD purposes
 
step = 5 #linear steps for increasing/decreasing volume
 
#tell to GPIO library to use logical PIN names/numbers, instead of the physical PIN numbers
GPIO.setmode(GPIO.BCM) 
#set up the pins we have been using
clk = 17
dt = 18
back = 27
ok = 22
 
#set up the GPIO events on those pins
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ok, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
 
#get the initial states
counter = 0
clkLastState = GPIO.input(clk)
dtLastState = GPIO.input(dt)
backLastState = GPIO.input(back)
okLastState = GPIO.input(back)

 
#define functions which will be triggered on pin state changes
@socketio.on('update_value')
def update_value():
        print("Auto updtate!")
        socketio.emit('new_value', {'value': 'false'})

def clkClicked(channel):
        global counter
        global step
 
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
 
        if clkState == 0 and dtState == 1:
                counter = counter + step
                socketio.emit('new_value', {'left': 'true'})
                print ("Counter ", counter)
 
def dtClicked(channel):
        global counter
        global step
 
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
         
        if clkState == 1 and dtState == 0:
                counter = counter - step
                socketio.emit('new_value', {'right': 'true'})
                print ("Counter ", counter)
 
def backClicked(channel):
        socketio.emit('new_value', {'back': 'true'})
        print ("Back clicked")

def okClicked(channel):
        socketio.emit('new_value', {'ok': 'true'})
        print ("Ok clicked")
 
GPIO.add_event_detect(clk, GPIO.FALLING, callback=clkClicked, bouncetime=300)
GPIO.add_event_detect(dt, GPIO.FALLING, callback=dtClicked, bouncetime=300)
GPIO.add_event_detect(back, GPIO.FALLING, callback=backClicked, bouncetime=300)
GPIO.add_event_detect(ok, GPIO.FALLING, callback=okClicked, bouncetime=300)


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

 
GPIO.cleanup()