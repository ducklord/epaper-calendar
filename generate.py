#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import pyowm
import calendar
import pickle
from os import path
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


"""
Copyright bullshit stuff.
"""

"""Settings:"""
api_key = ""
location = "Aalborg, DK"
testing = True

"""Defines:"""
EPD_WIDTH = 384
EPD_HEIGHT = 640
FILE_PATH = path.dirname(path.realpath(__file__))
FONTS_PATH = path.join(FILE_PATH, 'fonts')
CREDENTIALS_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
    fill_black = 'white' if color == 'white' else 'black'
    fill_red = 'black' if color == 'red' else 'white'
    drawBlack.text((position[0] - text_width / 2,
                    position[1] - text_height / 2),
                   text, font = font, fill = fill_black)
    drawRed.text((position[0] - text_width / 2,
                  position[1] - text_height / 2),
                 text, font = font, fill = fill_red)

def draw_left_text(position, text, font=font, color='black'):
    text_width, text_height = font.getsize(text)
    fill_black = 'white' if color == 'white' else 'black'
    fill_red = 'black' if color == 'red' else 'white'
    drawBlack.text((position[0],
                    position[1] - text_height / 2),
                   text, font = font, fill = fill_black)
    drawRed.text((position[0],
                  position[1] - text_height / 2),
                 text, font = font, fill = fill_red)


def draw_date(center_pos, font_size_day = 20, font_size_date = 20, font_size_year = 20, time = datetime.now(), sep_year = 0, color = 'black', color_year = 'red'):
    font_day = ImageFont.truetype(font_path, font_size_day)
    font_date = ImageFont.truetype(font_path, font_size_date)
    font_year = ImageFont.truetype(font_path, font_size_year)
    pos_year = (center_pos[0], center_pos[1] - font_size_year / 2 - font_size_date / 2 - sep_year)
    pos_date = center_pos
    pos_day = (center_pos[0], center_pos[1] + font_size_day / 2 + font_size_date / 2)
    draw_center_text(pos_year, time.strftime("%Y"), font = font_year, color = color_year)
    draw_center_text(pos_date, time.strftime("%-d %B"), font = font_date, color = color)
    draw_center_text(pos_day, time.strftime("%A"), font = font_day, color = color)

"""Draw the caleandar"""
def draw_calendar(offset, width, font_size_day_of_week = 20, font_size_month_day = 20, seperation = 20, color = 'black', color_current = 'red', time = datetime.now()):
    font_day_of_week = ImageFont.truetype(font_path, font_size_day_of_week)
    font_month_day = ImageFont.truetype(font_path, font_size_month_day)

    days_in_week = list(map(lambda i: date(2019, 4, i + 1).strftime("%a"), range(7)))
    
    day_of_week = time.weekday()
    day_of_month = time.day

    row_day_of_week = font_size_day_of_week / 2 + offset[1]
    def calendar_row(index):
        return font_size_day_of_week + font_size_month_day / 2 + font_size_month_day * index + offset[1] + seperation
    def calendar_col(index):
        return width * (index + 1) / 8 + offset[0]

    for index, day in enumerate(days_in_week):
        pos = (calendar_col(index), row_day_of_week)
        day_color = color_current if index == day_of_week else color
        draw_center_text(pos, day, font=font_day_of_week, color=day_color)

    monthCalendar = calendar.monthcalendar(time.year, time.month)
    calendar.setfirstweekday(calendar.MONDAY)

    for rowIndex in range(len(monthCalendar)):
        for monthDay in monthCalendar[rowIndex]:
            pos = (calendar_col(monthCalendar[rowIndex].index(monthDay)),
                   calendar_row(rowIndex))
            day_color = color_current if monthDay == day_of_month else color
            text = str(monthDay) if not monthDay == 0 else ''
            draw_center_text(pos, text, font=font_month_day, color=day_color)


"""Draw the weather section of the image."""
def draw_weather(offset, width, font_size_windspeed = 20, font_size_weather_icon = 90, font_size_temperature = 20, font_size_humidity = 20, font_size_description = 20, sep_weather_icon = 0):
    owm = pyowm.OWM(api_key)
    """Connect to Openweathermap API to fetch weather data"""
    print("Connecting to Openweathermap API servers...")
    if testing or owm.is_API_online() is True:
        if not testing:
            observation = owm.weather_at_place(location)
            print("weather data:")
            weather = observation.get_weather()
            weathericon = weather.get_weather_icon_name()
            humidity = str(weather.get_humidity())
            cloudstatus = str(weather.get_clouds())
            weather_description = (str(weather.get_status()))
            temperature = str(int(weather.get_temperature(unit='celsius')['temp']))
            windspeed = str(int(weather.get_wind()['speed']))
            sunrisetime = str(datetime.fromtimestamp(
                int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
            sunsettime = str(datetime.fromtimestamp(
                int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))
        else:
            weathericon = '01d'
            humidity = '67'
            cloudstatus = '0'
            weather_description = 'Clear'
            temperature = '13'
            windspeed = '1'
            sunrisetime = '6:34'
            sunsettime = '20:10'

        """Debug print"""
        print('weathericon = \'' + weathericon + '\'')
        print('humidity = \'' + humidity + '\'')
        print('cloudstatus = \'' + cloudstatus + '\'')
        print('weather_description = \'' + weather_description + '\'')
        print('temperature = \'' + temperature + '\'')
        print('windspeed = \'' + windspeed + '\'')
        print('sunrisetime = \'' + sunrisetime + '\'')
        print('sunsettime = \'' + sunsettime + '\'')

        font_windspeed = ImageFont.truetype(font_path, font_size_windspeed)
        font_weather_icon = ImageFont.truetype(font_weather_icon_path, font_size_weather_icon)
        font_temperature = ImageFont.truetype(font_path, font_size_temperature)
        font_humidity = ImageFont.truetype(font_path, font_size_humidity)
        font_description = ImageFont.truetype(font_path, font_size_description)
        
        pos_windspeed = (width / 2 + offset[0], font_size_windspeed / 2 + offset[1])
        pos_weather_icon = (width / 2 + offset[0], pos_windspeed[1] + font_size_windspeed / 2 + font_size_weather_icon / 2 + sep_weather_icon)
        pos_temperature = (width / 2 + offset[0],  pos_weather_icon[1] + font_size_weather_icon / 2 + font_size_temperature / 2)
        pos_humidity = (width / 2 + offset[0], 150 + offset[1])
        pos_description = (width / 2 + offset[0], pos_temperature[1] + font_size_temperature / 2 + font_size_description)

        draw_center_text(pos_windspeed, windspeed + " m/s", font=font_windspeed)
        draw_center_text(pos_weather_icon, weather_icon_font_map[weathericon], font=font_weather_icon)
        draw_center_text(pos_temperature, temperature + "°C", font=font_temperature)
        #draw_center_text(pos_humidity, humidity + " %", font=font_humidity)
        draw_center_text(pos_description, weather_description, font=font_description, color='red')
    else:
        """If no response was received from the openweathermap
        api server, add the cloud with question mark"""
        imageBlack.paste(no_response, (114, 0))


def get_calendar_events():
    google_credentials = None
    if path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            google_credentials = pickle.load(token)
            
    if not google_credentials or not google_credentials.valid:
        if google_credentials and google_credentials.expired and google_credentials.refresh_token:
            google_credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', CREDENTIALS_SCOPES)
            google_credentials = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(google_credentials, token)

    service = build('calendar', 'v3', credentials = google_credentials)

    # Call the Calendar API
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
    sevenDaysFromNow = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary',
                                          timeMin=now,
                                          timeMax=sevenDaysFromNow,
                                          maxResults=10,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    return events_result.get('items', [])


def draw_calendar_events(offset, events = [], font_size = 20, font_size_time = 13, font_size_day = 25, font_size_month = 10, seperator = 0):
    y = offset[1]
    month_x = offset[0]
    month_seperator = 2
    month_width = 42
    font_day = ImageFont.truetype(font_path, font_size_day)
    font_month = ImageFont.truetype(font_path, font_size_month)
    font_time = ImageFont.truetype(font_path, font_size_time)
    font = ImageFont.truetype(font_path, font_size)
    currentDate = None

    for event in events:
        eventDateTime = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        eventDate = eventDateTime.date()
        color = 'red' if eventDate == datetime.now().date() else 'black'
        if not currentDate == eventDate:
            # Draw event date.
            currentDate = eventDate
            # if eventDate == datetime.now().date():
            #     drawRed.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            #     drawBlack.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            #     drawRed.rectangle(((0, y), (70, y + font_size_day + 3)))
            #     drawBlack.rectangle(((0, y), (70, y + font_size_day + 3)))
            # else:
            #     drawBlack.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            # y += 1
            # draw_center_text((70 / 2, y + font_size_day / 2), currentDate.strftime('%d/%m'), font=font_day, color='white')
            # y += font_size_day + seperator

            drawBlack.rectangle(((month_x, y), (month_x + month_width, y + font_size_day + 2 + month_seperator + font_size_month + month_seperator)))
            draw_center_text((month_x + month_width / 2, y + font_size_day / 2), currentDate.strftime('%d'), font=font_day, color='black')
            drawBlack.rectangle(((month_x + 1, y + font_size_day + 2), (month_x + month_width - 1, y + font_size_day + month_seperator + font_size_month + month_seperator + 2 - 1)), fill = 'black')
            drawRed.rectangle(((month_x + 1, y + font_size_day + 2), (month_x + month_width - 1, y + font_size_day + month_seperator + font_size_month + month_seperator + 2 - 1)), fill = 'black')
            draw_center_text((month_x + month_width / 2, y + font_size_day + 2 + month_seperator + font_size_month / 2), currentDate.strftime('%b'), font=font_month, color='white')
            y += font_size_day + 2 + month_seperator + font_size_month + month_seperator + 3

        # Draw the event it self.
        draw_center_text((month_x + month_width / 2, y + font_size / 2), eventDateTime.strftime('%H:%M'), font=font_time, color=color)
        draw_left_text((month_x + month_width + 7, y + font_size / 2), event['summary'], font=font, color=color)
        y += font_size + seperator

def main():
    seperator_pos = 250

    # Draw date in a red square in left side.
    drawRed.rectangle(((0, 0), (EPD_WIDTH / 2, 130)), fill='black')
    draw_date((EPD_WIDTH / 4, 65), font_size_day = 20, font_size_date = 30, font_size_year = 13, sep_year=5, color = 'white', color_year = 'white')

    # Draw calendar below the date.
    draw_calendar((0, 145), EPD_WIDTH / 2, font_size_day_of_week = 9, font_size_month_day = 14, seperation = 5, color = 'black', color_current = 'red')

    # Draw weather status in right side.
    draw_weather((EPD_WIDTH / 2, 20), EPD_WIDTH / 2, font_size_windspeed = 18, font_size_weather_icon = 120, font_size_temperature = 50, font_size_description = 10, sep_weather_icon = 0)

    # Draw borders between sections.
    drawBlack.rectangle(((EPD_WIDTH / 2, 130), (EPD_WIDTH / 2, seperator_pos)), fill='black')
    drawBlack.rectangle(((0, seperator_pos), (EPD_WIDTH, seperator_pos)), fill='black')

    # Draw the list of all calendar events
    draw_calendar_events((2, seperator_pos + 4), events = get_calendar_events(), font_size = 16, seperator = 5)

    # Output the images.
    #image.rotate(90, expand=True)
    imageBlack.save('output_black.bmp')
    imageRed.save('output_red.bmp')

    
if __name__ == '__main__':
    main()
