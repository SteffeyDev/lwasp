#!/usr/bin/env python
import pygame
import sys

try:
    pygame.init()
    pygame.mixer.init()
except:
    exit()

if sys.agrv[0] == "new" or sys.argv[0] == "both":
    pygame.mixer.music.load("/usr/share/sounds/useless/success.wav")
    pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    continue
if sys.argv[0] == "penalty" or sys.argv[0] == "both":
    pygame.mixer.music.load("/usr/share/sounds/useless/error.mp3")
    pygame.mixer.music.play()
#waits until sound is finished playing to end script
while pygame.mixer.music.get_busy():
    continue
