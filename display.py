#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont, ImageOps
import epd7in5b

def display(black_image_path, red_image_path):
    epd = epd7in5b.EPD()
    epd.init()
    sleep(5)
    black_image = Image.open(black_image_path)
    red_image = Image.open(red_image_path)
    epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
    epd.sleep()

"""Main loop starts from here"""
def main():
    display(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
