#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pyowm
import calendar
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
WEATHER_ICONS_PATH = path.join(FILE_PATH, 'weather-icons')
FONTS_PATH = path.join(FILE_PATH, 'fonts')


font_path = path.join(FONTS_PATH, 'DejaVuSans-Bold.ttf')
font = ImageFont.truetype(font_path, 30)

weathericons = {
    '01d': 'wi-day-sunny.jpeg',
    '02d': 'wi-day-cloudy.jpeg',
    '03d': 'wi-cloudy.jpeg',
    '04d': 'wi-cloudy-windy.jpeg',
    '09d': 'wi-showers.jpeg',
    '10d': 'wi-rain.jpeg',
    '11d': 'wi-thunderstorm.jpeg',
    '13d': 'wi-snow.jpeg',
    '50d': 'wi-fog.jpeg',
    '01n': 'wi-night-clear.jpeg',
    '02n': 'wi-night-cloudy.jpeg',
    '03n': 'wi-night-cloudy.jpeg',
    '04n': 'wi-night-cloudy.jpeg',
    '09n': 'wi-night-showers.jpeg',
    '10n': 'wi-night-rain.jpeg',
    '11n': 'wi-night-thunderstorm.jpeg',
    '13n': 'wi-night-snow.jpeg',
    '50n': 'wi-night-alt-cloudy-windy.jpeg'
}


"""Create a blank white page first"""
imageBlack = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawBlack = ImageDraw.Draw(imageBlack)
imageRed = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawRed = ImageDraw.Draw(imageRed)


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


"""Draw the weather section of the image."""
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
    temperature = '9999'
    windspeed = '1213'
    sunrisetime = '06:06'
    sunsettime = '20:20'

    """Debug print"""
    print('Temperature: ' + temperature + ' °C')
    print('Humidity: ' + humidity + '%')
    print('Icon code: ' + weathericon)
    print('weather-icon name: ' + weathericons[weathericon])
    print('Wind speed: ' + windspeed + 'm/s')
    print('Sunrise-time: ' + sunrisetime)
    print('Sunset time: ' + sunsettime)
    print('Cloudiness: ' + cloudstatus + '%')
    print('Weather description: ' + weather_description + '\n')

    drawBlack.text((334, 0), temperature + " °C", font=font)
    drawBlack.text((114, 0), windspeed + " m/s", font=font)

    """Add the weather icon at the top left corner"""
    imageBlack.paste(Image.open(path.join(WEATHER_ICONS_PATH, weathericons[weathericon])),
                     (0, 0))

    """Add the temperature icon at its position"""
    #imageBlack.paste(tempicon, tempplace)

    """Add the humidity icon and display the humidity"""
    #imageBlack.paste(humicon, humplace)
    drawBlack.text((334, 35), humidity + " %", font=font)

    """Add the wind icon at it's position"""
    # imageBlack.paste(windicon, windiconspace)

    """Add a short weather description"""
    drawBlack.text((70, 35), weather_description, font=font)

else:
    """If no response was received from the openweathermap
    api server, add the cloud with question mark"""
    imageBlack.paste(no_response, (114, 0))


"""Add the line seperating the weather and Calendar section"""
# imageBlack.paste(seperator, seperatorplace)
drawBlack.rectangle(((0, 72), (EPD_WIDTH, 76)), fill='black')
drawRed.rectangle(((0, 72), (EPD_WIDTH, 76)), fill='black')


time = datetime.now()
drawBlack.text((100, 75), time.strftime("%B"), font=font)

"""Draw the caleandar"""
def draw_calendar(offset, size, font_size):
    font_day_of_week = ImageFont.truetype(font_path, font_size)
    font_month_day = ImageFont.truetype(font_path, font_size)
    calendar_col = [
        size[0] * 1 / 8 + offset[0],
        size[0] * 2 / 8 + offset[0],
        size[0] * 3 / 8 + offset[0],
        size[0] * 4 / 8 + offset[0],
        size[0] * 5 / 8 + offset[0],
        size[0] * 6 / 8 + offset[0],
        size[0] * 7 / 8 + offset[0]
    ]

    row_day_of_week = font_size / 2 + offset[1]
    calendar_row = [
        font_size / 2 + font_size * 1 + offset[1],
        font_size / 2 + font_size * 2 + offset[1],
        font_size / 2 + font_size * 3 + offset[1],
        font_size / 2 + font_size * 4 + offset[1],
        font_size / 2 + font_size * 5 + offset[1],
        font_size / 2 + font_size * 6 + offset[1]
    ]

    calendar.setfirstweekday(calendar.MONDAY)
    time = datetime.now()
    dayOfWeek = time.weekday()
    dayOfMonth = time.day

    for index, day in enumerate(['Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør', 'Søn']):
        pos = (calendar_col[index], row_day_of_week)
        color = 'red' if index == dayOfWeek else 'black'
        draw_center_text(pos, day, font=font_day_of_week, color=color)

    monthCalendar = calendar.monthcalendar(time.year, time.month)
    for rowIndex in range(len(monthCalendar)):
        for monthDay in monthCalendar[rowIndex]:
            pos = (calendar_col[monthCalendar[rowIndex].index(monthDay)],
                   calendar_row[rowIndex])
            color = 'red' if monthDay == dayOfMonth else 'black'
            text = str(monthDay) if not monthDay == 0 else ''
            draw_center_text(pos, text, font=font_month_day, color=color)

draw_calendar((0, 130), (EPD_WIDTH / 2, EPD_HEIGHT), 10)

#image.rotate(90, expand=True)
imageBlack.save('output_black.bmp')
imageRed.save('output_red.bmp')
