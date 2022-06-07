import os
import leds_control
import utime

IP = '192.168.4.2'
        
while True:
    leds_control.run(IP, local=True, do_move=False, RGB=False)
    utime.sleep(1)
    leds_control.show_no_image_leds()
    
    

