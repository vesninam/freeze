from machine import Pin
from neopixel import NeoPixel
import utime 
import urequests as req
import os
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
last_size = (NLEDS_STRIP, 1)
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
    size = 0
    aspect = [0, 0]
    first = True
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
            if first:
                with open(fname, 'wb') as f:
                    pass
                resp_size = req.get('http://'+IP+':'+PORT+'/get_size')
                aspect = resp_size.json()['size']
                first = False
            size += len(data)   
            with open(fname, 'ab') as f:
                f.write(data)
            while True:
                resp_next = req.post('http://'+IP+':'+PORT+'/next_portion')
                if resp_next.status_code == 200:
                    break
            
        else:
            print('Unknow error, see server logs')
            utime.sleep(1)
    return fname, size, aspect

def get_local_size(nleds):
    height = 0
    with open(FILE, 'rb') as f:
        while True:
            data = f.read(nleds * 3)
            if data == nleds * 3:
                height += 1
            else:
                break
    return (nleds, height)
    
def move(steps, speed,  moveup=False):
    stepper.on()
    start = utime.time()
    #TODO check 1 and -1 for directions
    stepper.step((1 if moveup else -1) * steps, speed, hold = True) 
    stepper.off()
    return utime.time() - start

def show(size, delay=0.02, motion={}, lines=LINES, scaler=8, RGB=True):
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
                    if RGB:
                        pix[iled] = (int(r/scaler), int(g/scaler), int(b/scaler))
                    else:
                        pix[iled] = (int(g/scaler), int(r/scaler), int(b/scaler)) #data[ind:ind+3]
                pix.write()
                if motion:
                    moveup = True if motion['dir'] == 'up' else  False
                    steps = int(MOVE_LINE_STEPS)
                    move(steps, motion['speed'], moveup=moveup)
                else:
                    utime.sleep(delay)
                lastline += 1


def run(IP, local=False, do_move=False, RGB=True):    
    global last_size
    motion={'dir': 'down', 'speed': 20}
    fpath, nbytes, size = load_image(IP)
    size_ok = (nbytes == size[0] * size[1] * 3) and size[1] > 1

    if (not size_ok) and local:
        image_exists = False
        _bytes = last_size[0] * last_size[1] * 3
        for f in os.listdir():
            if f == FILE:
                image_exists = os.stat(f)[-4] == _bytes
                break
        if image_exists:
            if do_move:
                show(last_size, delay=0.0, motion=motion, RGB=RGB)
            else:
                show(last_size, RGB=RGB)
    else:
        last_size = size if size_ok else last_size
        if do_move:
            show(size, delay=0.0, motion=motion, RGB=RGB)
        else:
            show(size, delay=0.0, motion={}, RGB=RGB)
