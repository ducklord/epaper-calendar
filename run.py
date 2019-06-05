#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from generate import generate
from display import display

def main():
    black_file_path, red_file_path = 'output_black.bmp', 'output_red.bmp'
    generate(black_file_path, red_file_path)
    display(black_file_path, red_file_path)
    
if __name__ == '__main__':
    main()
