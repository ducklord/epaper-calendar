#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pyowm
import calendar
import locale
import math
from os import path
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps

"""
Copyright bullshit stuff.
"""

"""Settings:"""
api_key = ""
location = "Aalborg, DK"


"""Defines:"""
EPD_WIDTH = 384
EPD_HEIGHT = 640
FILE_PATH = path.dirname(path.realpath(__file__))
FONTS_PATH = path.join(FILE_PATH, 'fonts')


font_path = path.join(FONTS_PATH, 'DejaVuSans-Bold.ttf')
font_weather_icon_path = path.join(FONTS_PATH, 'meteocons.ttf')
font = ImageFont.truetype(font_path, 30)

weather_icon_font_map = {
    '01d':'B',
    '01n':'C',
    '02d':'H',
    '02n':'I',
    '03d':'N',
    '03n':'N',
    '04d':'Y',
    '04n':'Y',
    '09d':'R',
    '09n':'R',
    '10d':'R',
    '10n':'R',
    '11d':'P',
    '11n':'P',
    '13d':'W',
    '13n':'W',
    '50d':'M',
    '50n':'W'
}


"""Create a blank white page first"""
imageBlack = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawBlack = ImageDraw.Draw(imageBlack)
imageRed = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawRed = ImageDraw.Draw(imageRed)

"""Define helper functions"""

def draw_center_text(position, text, font=font, color='black'):
    text_width, text_height = font.getsize(text)
    if color == 'black':
        drawBlack.text((position[0] - text_width / 2,
                        position[1] - text_height / 2),
                       text, font=font)
    else:
        drawBlack.text((position[0] - text_width / 2,
                        position[1] - text_height / 2),
                       text, font=font)
        drawRed.text((position[0] - text_width / 2,
                      position[1] - text_height / 2),
                     text, font=font)


def draw_date(center_pos, font_size_day = 20, font_size_date = 20, font_size_year = 20, time = datetime.now(), sep_year = 0):
    font_day = ImageFont.truetype(font_path, font_size_day)
    font_date = ImageFont.truetype(font_path, font_size_date)
    font_year = ImageFont.truetype(font_path, font_size_year)
    pos_year = (center_pos[0], center_pos[1] - font_size_year / 2 - font_size_date / 2 - sep_year)
    pos_date = center_pos
    pos_day = (center_pos[0], center_pos[1] + font_size_day / 2 + font_size_date / 2)
    draw_center_text(pos_year, time.strftime("%Y"), font=font_year, color='red')
    draw_center_text(pos_date, time.strftime("%-d %B"), font=font_date)
    draw_center_text(pos_day, time.strftime("%A"), font=font_day)

"""Draw the caleandar"""
def draw_calendar(offset, width, font_size_day_of_week = 20, font_size_month_day = 20, seperation = 20, time = datetime.now()):
    font_day_of_week = ImageFont.truetype(font_path, font_size_day_of_week)
    font_month_day = ImageFont.truetype(font_path, font_size_month_day)

    days_in_week = list(map(lambda i: date(2019, 4, i + 1).strftime("%a"), range(7)))
    # days_in_week = [
    #     locale.ABDAY_1,
    #     locale.ABDAY_2,
    #     locale.ABDAY_3,
    #     locale.ABDAY_4,
    #     locale.ABDAY_5,
    #     locale.ABDAY_6,
    #     locale.ABDAY_7
    # ]
    
    day_of_week = time.weekday()
    day_of_month = time.day

    row_day_of_week = font_size_day_of_week / 2 + offset[1]
    def calendar_row(index):
        return font_size_day_of_week + font_size_month_day / 2 + font_size_month_day * index + offset[1] + seperation
    def calendar_col(index):
        return width * (index + 1) / 8 + offset[0]

    for index, day in enumerate(days_in_week):
        pos = (calendar_col(index), row_day_of_week)
        color = 'red' if index == day_of_week else 'black'
        draw_center_text(pos, day, font=font_day_of_week, color=color)

    monthCalendar = calendar.monthcalendar(time.year, time.month)
    calendar.setfirstweekday(calendar.MONDAY)

    for rowIndex in range(len(monthCalendar)):
        for monthDay in monthCalendar[rowIndex]:
            pos = (calendar_col(monthCalendar[rowIndex].index(monthDay)),
                   calendar_row(rowIndex))
            color = 'red' if monthDay == day_of_month else 'black'
            text = str(monthDay) if not monthDay == 0 else ''
            draw_center_text(pos, text, font=font_month_day, color=color)


"""Draw the weather section of the image."""
def draw_weather(offset, width, font_size_windspeed = 20, font_size_weather_icon = 90, font_size_temperature = 20, font_size_humidity = 20, font_size_description = 20, sep_weather_icon = 0):
    owm = pyowm.OWM(api_key)
    """Connect to Openweathermap API to fetch weather data"""
    print("Connecting to Openweathermap API servers...")
    # if owm.is_API_online() is True:
    if True:
        # observation = owm.weather_at_place(location)
        # print("weather data:")
        # weather = observation.get_weather()
        # weathericon = weather.get_weather_icon_name()
        # humidity = str(weather.get_humidity())
        # cloudstatus = str(weather.get_clouds())
        # weather_description = (str(weather.get_status()))
        # temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
        # windspeed = str(int(weather.get_wind()['speed']))
        # sunrisetime = str(datetime.fromtimestamp(
        #     int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
        # sunsettime = str(datetime.fromtimestamp(
        #     int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))

        weathericon = '04d'
        humidity = '20000'
        cloudstatus = '100'
        weather_description = 'cloudy'
        temperature = '20'
        windspeed = '1213'
        sunrisetime = '06:06'
        sunsettime = '20:20'

        """Debug print"""
        print('Temperature: ' + temperature + ' °C')
        print('Humidity: ' + humidity + '%')
        print('Icon code: ' + weathericon)
        print('Wind speed: ' + windspeed + 'm/s')
        print('Sunrise-time: ' + sunrisetime)
        print('Sunset time: ' + sunsettime)
        print('Cloudiness: ' + cloudstatus + '%')
        print('Weather description: ' + weather_description + '\n')

        font_windspeed = ImageFont.truetype(font_path, font_size_windspeed)
        font_weather_icon = ImageFont.truetype(font_weather_icon_path, font_size_weather_icon)
        font_temperature = ImageFont.truetype(font_path, font_size_temperature)
        font_humidity = ImageFont.truetype(font_path, font_size_humidity)
        font_description = ImageFont.truetype(font_path, font_size_description)
        
        pos_windspeed = (width / 2 + offset[0], font_size_windspeed / 2 + offset[1])
        pos_weather_icon = (width / 2 + offset[0], pos_windspeed[1] + font_size_windspeed / 2 + font_size_weather_icon / 2 + sep_weather_icon)
        pos_temperature = (width / 2 + offset[0],  pos_weather_icon[1] + font_size_weather_icon / 2 + font_size_temperature / 2)
        pos_humidity = (width / 2 + offset[0], 150 + offset[1])
        pos_description = (width / 2 + offset[0], 150 + offset[1])

        draw_center_text(pos_windspeed, windspeed + " m/s", font=font_windspeed)
        draw_center_text(pos_weather_icon, weather_icon_font_map[weathericon], font=font_weather_icon)
        draw_center_text(pos_temperature, temperature + "°C", font=font_temperature)
        #draw_center_text(pos_humidity, humidity + " %", font=font_humidity)
        #draw_center_text(pos_description, weather_description, font=font_description)
        
    else:
        """If no response was received from the openweathermap
        api server, add the cloud with question mark"""
        imageBlack.paste(no_response, (114, 0))
        



"""Add the line seperating the weather and Calendar section"""
draw_date((EPD_WIDTH / 4, 65), font_size_day = 20, font_size_date = 30, font_size_year = 13, sep_year=5)
draw_calendar((0, 130), EPD_WIDTH / 2, font_size_day_of_week = 10, font_size_month_day = 14, seperation = 5)
draw_weather((EPD_WIDTH / 2, 45), EPD_WIDTH / 2, font_size_windspeed = 18, font_size_weather_icon = 120, font_size_temperature = 50, sep_weather_icon = -15)

seperator_pos = 270
seperator_height = 4
drawBlack.rectangle(((EPD_WIDTH / 2, 0), (EPD_WIDTH / 2 + 1, seperator_pos)), fill='black')
drawRed.rectangle(((EPD_WIDTH / 2, 0), (EPD_WIDTH / 2 + 1, seperator_pos)), fill='black')
drawBlack.rectangle(((0, seperator_pos), (EPD_WIDTH, seperator_pos + seperator_height)), fill='black')
drawRed.rectangle(((0, seperator_pos), (EPD_WIDTH, seperator_pos + seperator_height)), fill='black')

#image.rotate(90, expand=True)
imageBlack.save('output_black.bmp')
imageRed.save('output_red.bmp')
