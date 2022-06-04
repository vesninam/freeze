import leds_control

def run():
    IP = '192.168.4.2'
    fpath, nbytes, size = leds_control.load_image(IP)
    if nbytes != size[0] * size[1] * 3:
        #print("The bytes load not equal image size")
        #print("Resubmit image on web and try again")
        leds_control.show_no_image_leds()
    else:
        motion={'dir': 'down', 'speed': 20}
        leds_control.show(size, delay=0.0, motion=motion)

run()    

