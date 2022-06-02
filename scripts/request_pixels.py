import time

SYSTEM='!micro'
IP = '0.0.0.0'
PORT = '5000'
FILE = 'pixels.pix'
LINES = 10


if SYSTEM == 'micro':
    import urequests as req
else:
    import requests as req

with open('pixels.pix', 'wb') as f:
    pass

while True:
    resp = req.get(f'http://{IP}:{PORT}/get_portion')
    if resp.status_code == 500:
        print('Probably image is not loaded to server')
        print(resp.json()['message'])
        time.sleep(1)
    elif resp.status_code == 200:
        data = resp.content
        if len(data) == 0:
            break
        with open(FILE, 'ab') as f:
            f.write(data)
        while True:
            resp = req.post(f'http://{IP}:{PORT}/next_portion')
            if resp.status_code == 200:
                break
    else:
        print('Unknow error, see server logs')
        time.sleep(1)


if SYSTEM == 'micro':
    #DRIVE STEPPERS AND CONTROL LEDS
    from machine import Pin
    from neopixel import NeoPixel
    import utime
    resp = req.get(f'http://{IP}:{PORT}/get_size')
    s = resp.json()['size']
    NLEDS = s[0]
    HEIGHT = s[1]
    pix = NeoPixel(Pin(2), NLEDS)
    with open(FILE, 'rb') as f:
        lastline = 0
        while lastline <= HEIGHT:
            data = f.read(LINES * NLEDS * 3)
            if NLEDS * 3 >= len(data):
                break
            for line in range(LINES):
                if (line + 1) * NLEDS * 3 >= len(data):
                    break
                for iled in range(NLEDS):
                    ind = (i + line * NLEDS * 3)
                    #r, g, b = data[ind:ind+3]
                    pix[iled] = data[ind:ind+3]
                pix.write()
                utime.sleep(0.1)
                lastline += 1

if SYSTEM != 'micro':
    from PIL import Image
    import io
    image_data = None
    with open('pixels.pix', 'rb') as f:
        image_data = f.read()
    resp = req.get(f'http://{IP}:{PORT}/get_size')
    s = resp.json()['size']
    print(s)
    image = Image.frombytes('RGB', s, image_data, 'raw')
    image.show()
