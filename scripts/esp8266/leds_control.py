from machine import Pin
from neopixel import NeoPixel
import utime 
import urequests as req
from stepper import STEPPER

#IP = '0.0.0.0'
FILE = 'pixels.pix'
LINES = 10
STEPPER_CONFIG = {'In1':5, 
                  'In2':4, 
                  'In3':12, 
                  'In4':14, 
                  'power_pin': 13,
                  'number_of_steps': 400,
                  'max_speed': 20 } 
MOVE_LINE_STEPS = 17.6367
NLEDS_STRIP = 144
stepper = STEPPER(STEPPER_CONFIG) 
pix = NeoPixel(Pin(2), NLEDS_STRIP)

def show_no_image_leds():
    for _ in range(3):
        for i in range(NLEDS_STRIP):
            pix[i] = (0,64,0)
        pix.write()
        utime.sleep(1)
        for i in range(NLEDS_STRIP):
            pix[i] = (0,0,0)
        pix.write()

    

def load_image(IP, PORT = '5000', fname=FILE):
    with open(fname, 'wb') as f:
        pass
    size = 0
    while True:
        resp = req.get('http://'+IP+':'+PORT+'/get_portion')
        if resp.status_code == 500:
            print('Probably image is not loaded to server')
            print(resp.json()['message'])
            utime.sleep(1)
        elif resp.status_code == 200:
            data = resp.content
            if len(data) == 0:
                break
            size += len(data)   
            with open(fname, 'ab') as f:
                f.write(data)
            while True:
                resp = req.post('http://'+IP+':'+PORT+'/next_portion')
                if resp.status_code == 200:
                    break
        else:
            print('Unknow error, see server logs')
            utime.sleep(1)
    resp = req.get('http://'+IP+':'+PORT+'/get_size')
    aspect = resp.json()['size']
    return fname, size, aspect
    
def move(steps, speed,  moveup=False):
    stepper.on()
    start = utime.time()
    #TODO check 1 and -1 for directions
    stepper.step((1 if moveup else -1) * steps, speed, hold = True) 
    stepper.off()
    return utime.time() - start

def show(size, delay=0.02, motion={}, lines=LINES, scaler=8):
    s = size
    NLEDS = s[0]
    HEIGHT = s[1]
    
    with open(FILE, 'rb') as f:
        lastline = 0
        while lastline <= HEIGHT:
            data = f.read(lines * NLEDS * 3)
            if NLEDS * 3 >= len(data):
                break
            for line in range(lines):
                if (line + 1) * NLEDS * 3 >= len(data):
                    break
                for iled in range(NLEDS):
                    ind = (iled + line * NLEDS) * 3
                    r, g, b = data[ind:ind+3]
                    pix[iled] = (int(g/scaler), int(r/scaler), int(b/scaler)) #data[ind:ind+3]
                pix.write()
                if motion:
                    moveup = True if motion['dir'] == 'up' else  False
                    steps = int(MOVE_LINE_STEPS)
                    move(steps, motion['speed'], moveup=moveup)
                else:
                    utime.sleep(delay)
                lastline += 1

