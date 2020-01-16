import pygame
import time

pygame.init()
x=5
while x:
    pygame.mixer.music.load("2.mp3")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()
    time.sleep(5)
    x-=1

dataAsInt = 17.5
dataAsString = str(dataAsInt)

fb = open('/share/test.csv','a+')
fb.write(dataAsString) 
fb.write('\n')
fb.close()
