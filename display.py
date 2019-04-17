#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from time import sleep
from PIL import Image, ImageDraw, ImageFont, ImageOps
import epd7in5b


"""Main loop starts from here"""
def main():
    epd = epd7in5b.EPD()
    epd.init()
    sleep(5)
    HBlackimage = Image.open(sys.argv[1])
    HRedimage = Image.open(sys.argv[2])
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
    epd.sleep()

if __name__ == '__main__':
    main()
