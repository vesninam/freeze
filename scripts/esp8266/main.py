import os
import leds_control

def run(local=False, do_move=True):
    IP = '192.168.4.2'
    motion={'dir': 'down', 'speed': 20}
    fpath, nbytes, size = leds_control.load_image(IP)
    if not local:
        if nbytes != size[0] * size[1] * 3:
            #print("The bytes load not equal image size")
            #print("Resubmit image on web and try again")
            leds_control.show_no_image_leds()
        else:
            if do_move:
                leds_control.show(size, delay=0.0, motion=motion)
            else:
                leds_control.show(size, delay=0.0, motion={})
    else:
        if leds_control.FILE in os.listdir():
            if do_move:
                leds_control.show(size, delay=0.0, motion=motion)
            else:
                leds_control.show(size, delay=0.0, motion={})

while True:
    run()    
    

