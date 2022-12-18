#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import pyowm
import calendar
import pickle
import locale
from os import path
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageOps
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from backports.datetime_fromisoformat import MonkeyPatch
MonkeyPatch.patch_fromisoformat()


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

locale.setlocale(locale.LC_ALL, 'da_DK.utf8')

"""Create a blank white page first"""
imageBlack = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawBlack = ImageDraw.Draw(imageBlack)
imageRed = Image.new('1', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawRed = ImageDraw.Draw(imageRed)
imageColor = Image.new('P', (EPD_WIDTH, EPD_HEIGHT), 'white')
drawColor = ImageDraw.Draw(imageColor)

"""Define helper functions"""

def draw_center_text(position, text, font = font, color = 'black'):
    x, y = position
    text_width, text_height = drawBlack.textsize(text, font = font)
    fill_black = 'black' if color == 'black' else 'white'
    fill_red = 'black' if color == 'red' else 'white'
    center_pos = (x - text_width / 2, y - text_height / 2)
    drawBlack.text(center_pos, text, font = font, fill = fill_black, align = "center")
    drawRed.text(center_pos, text, font = font, fill = fill_red, align = "center")
    drawColor.text(center_pos, text, font = font, fill = color, align = "center")

def draw_left_text(position, text, font = font, color = 'black'):
    x, y = position
    text_width, text_height = drawBlack.textsize(text, font = font)
    fill_black = 'black' if color == 'black' else 'white'
    fill_red = 'black' if color == 'red' else 'white'
    drawBlack.text((x, y - text_height / 2),
                   text, font = font, fill = fill_black)
    drawRed.text((x, y - text_height / 2),
                 text, font = font, fill = fill_red)
    drawColor.text((x, y - text_height / 2),
                   text, font = font, fill = color)

def draw_rect_outline(rect, color):
    if color == 'black':
        drawBlack.rectangle(rect, outline = 'black')
    elif color == 'red':
        drawRed.rectangle(rect, outline = 'black')
    else:
        drawBlack.rectangle(rect, outline = 'white')
        drawRed.rectangle(rect, outline = 'white')
    drawColor.rectangle(rect, outline = color)

def draw_rect_fill(rect, color):
    if color == 'black':
        drawBlack.rectangle(rect, fill = 'black')
    elif color == 'red':
        drawRed.rectangle(rect, fill = 'black')
    else:
        drawBlack.rectangle(rect, fill = 'white')
        drawRed.rectangle(rect, fill = 'white')
    drawColor.rectangle(rect, fill = color)

def paste_image(image_path, pos, color):
    image = Image.open(image_path)
    inverted_image = ImageOps.invert(image.convert('L')).convert('1')
    if color == 'black':
        drawBlack.bitmap(pos, inverted_image)
    elif color == 'red':
        drawRed.bitmap(pos, inverted_image)
    else:
        # Not sure what this is surpose to do.
        drawBlack.bitmap(pos, image)
        drawRed.bitmap(pos, image)
    drawColor.bitmap(pos, inverted_image, fill = color)


def draw_date(center_pos, font_size_day = 20, font_size_date = 20, font_size_month = 20, font_size_year = 20, time = datetime.now(), sep_year = 0, color = 'black', color_year = 'red'):
    x, y = center_pos
    font_day = ImageFont.truetype(font_path, font_size_day)
    font_date = ImageFont.truetype(font_path, font_size_date)
    font_month = ImageFont.truetype(font_path, font_size_month)
    font_year = ImageFont.truetype(font_path, font_size_year)
    pos_year = (x, y - font_size_year / 2 - font_size_date - sep_year)
    pos_date = (x, y - font_size_date / 2)
    pos_month = (x, y + font_size_month / 2)
    pos_day = (x, y + font_size_day / 2 + font_size_month + sep_year)

    draw_center_text(pos_year, time.strftime("%Y"), font = font_year, color = color_year)
    draw_center_text(pos_date, time.strftime("%-d"), font = font_date, color = color)
    draw_center_text(pos_month, time.strftime("%B"), font = font_month, color = color)
    draw_center_text(pos_day, time.strftime("%A"), font = font_day, color = color)

"""Draw the caleandar"""
def draw_calendar(offset, width, font_size_day_of_week = 20, font_size_month_day = 20, seperation = 20, color = 'black', color_weekend = 'red', time = datetime.now()):
    x, y = offset
    font_day_of_week = ImageFont.truetype(font_path, font_size_day_of_week)
    font_month_day = ImageFont.truetype(font_path, font_size_month_day)

    days_in_week = list(map(lambda i: date(2019, 4, i + 1).strftime("%a"), range(7)))
    
    day_of_week = time.weekday()
    day_of_month = time.day

    row_day_of_week = font_size_day_of_week / 2 + y
    def calendar_row(index):
        return font_size_day_of_week + font_size_month_day / 2 + font_size_month_day * index + y + seperation
    def calendar_col(index):
        return width * (index + 1) / 8 + x

    for index, day in enumerate(days_in_week):
        pos = (calendar_col(index), row_day_of_week)
        day_color = color_weekend if index == 5 or index == 6 else color
        if index == day_of_week:
            half_height = font_size_day_of_week / 2 + 2
            half_width = 12
            draw_rect_fill(((pos[0] - half_width, pos[1] - half_height), (pos[0] + half_width, pos[1] + half_height)), color = day_color)
            draw_center_text(pos, day, font = font_day_of_week, color = 'white')
        else:
            draw_center_text(pos, day, font = font_day_of_week, color = day_color)

    monthCalendar = calendar.monthcalendar(time.year, time.month)
    calendar.setfirstweekday(calendar.MONDAY)

    for rowIndex in range(len(monthCalendar)):
        for monthDay in monthCalendar[rowIndex]:
            colIndex = monthCalendar[rowIndex].index(monthDay)
            pos = (calendar_col(colIndex),
                   calendar_row(rowIndex))
            day_color = color_weekend if colIndex == 5 or colIndex == 6 else color
            text = str(monthDay) if not monthDay == 0 else ''
            if monthDay == day_of_month:
                half_height = font_size_month_day / 2
                half_width = 10
                draw_rect_fill(((pos[0] - half_width - 1, pos[1] - half_height + 1), (pos[0] + half_width, pos[1] + half_height)), color = day_color)
                draw_center_text(pos, text, font = font_month_day, color = 'white')
            else:
                draw_center_text(pos, text, font = font_month_day, color = day_color)


"""Draw the weather section of the image."""
def draw_weather(offset, width, font_size_windspeed = 20, font_size_weather_icon = 90, font_size_temperature = 20, font_size_humidity = 20, font_size_description = 20, sep_weather_icon = 0):
    x, y = offset
    owm = pyowm.OWM(api_key)
    """Connect to Openweathermap API to fetch weather data"""
    if testing or owm.is_API_online():
        if not testing:
            print("Connecting to Openweathermap API servers...")
            observation = owm.weather_at_place(location)
            print("weather data:")
            weather = observation.get_weather()
            weathericon = weather.get_weather_icon_name()
            humidity = weather.get_humidity()
            cloudstatus = weather.get_clouds()
            weather_description = weather.get_status()
            temperature = int(weather.get_temperature(unit='celsius')['temp'])
            windspeed = int(weather.get_wind()['speed'])
            sunrisetime = str(datetime.fromtimestamp(
                int(weather.get_sunrise_time(timeformat='unix'))).strftime('%-H:%M'))
            sunsettime = str(datetime.fromtimestamp(
                int(weather.get_sunset_time(timeformat='unix'))).strftime('%-H:%M'))
            rose_weather = windspeed < 5.5 and temperature >= 19.5
        else:
            weathericon = '01d'
            humidity = 54
            cloudstatus = 8
            weather_description = 'Clear'
            temperature = 22
            windspeed = 3
            sunrisetime = '6:15'
            sunsettime = '20:25'
            rose_weather = True

        """Debug print"""
        print('weathericon = \'' + weathericon + '\'')
        print('humidity = ' + str(humidity))
        print('cloudstatus = ' + str(cloudstatus))
        print('weather_description = \'' + weather_description + '\'')
        print('temperature = ' + str(temperature))
        print('windspeed = ' + str(windspeed))
        print('sunrisetime = \'' + sunrisetime + '\'')
        print('sunsettime = \'' + sunsettime + '\'')
        print('rose_weather = ' + str(rose_weather))

        font_windspeed = ImageFont.truetype(font_path, font_size_windspeed)
        font_weather_icon = ImageFont.truetype(font_weather_icon_path, font_size_weather_icon)
        font_temperature = ImageFont.truetype(font_path, font_size_temperature)
        font_humidity = ImageFont.truetype(font_path, font_size_humidity)
        font_description = ImageFont.truetype(font_path, font_size_description)
        
        pos_windspeed = (width / 2 + x, font_size_windspeed / 2 + y)
        pos_weather_icon = (width / 2 + x, pos_windspeed[1] + font_size_windspeed / 2 + font_size_weather_icon / 2 + sep_weather_icon)
        pos_rose = (int(width / 2 + x - 66), int(pos_weather_icon[1] + 20))
        pos_temperature = (width / 2 + x,  pos_weather_icon[1] + font_size_weather_icon / 2 + font_size_temperature / 2)
        pos_humidity = (width / 2 + x, 150 + y)
        pos_description = (width / 2 + x, pos_temperature[1] + font_size_temperature / 2 + font_size_description)

        draw_center_text(pos_windspeed, "{} m/s".format(windspeed), font=font_windspeed)
        if rose_weather:
            paste_image(path.join('gfx', 'glass_black.bmp'), pos_rose, color = 'black')
        draw_center_text(pos_weather_icon, weather_icon_font_map[weathericon], font=font_weather_icon)
        if rose_weather:
            paste_image(path.join('gfx', 'glass_red.bmp'), pos_rose, color = 'red')
        draw_center_text(pos_temperature, "{}°C".format(temperature), font=font_temperature)
        #draw_center_text(pos_humidity,  "{} %".format(humidity), font=font_humidity)
        draw_center_text(pos_description, weather_description, font=font_description, color='red')

    else:
        """If no response was received from the openweathermap
        api server, add the cloud with question mark"""
        font_error = ImageFont.truetype(font_path, 18)
        draw_center_text((x + width / 2, y + 200 / 2), "Openweathermap\nnot\nresponding", font = font_error, color = 'red')


def get_calendar_events():
    google_credentials = None
    if path.exists('/tmp/token.pickle'):
        with open('/tmp/token.pickle', 'rb') as token:
            google_credentials = pickle.load(token)
    elif path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            google_credentials = pickle.load(token)
            
    if not google_credentials or not google_credentials.valid:
        if google_credentials and google_credentials.expired and google_credentials.refresh_token:
            google_credentials.refresh(Request())
            # Save the credentials for the next run
            with open('/tmp/token.pickle', 'wb') as token:
                pickle.dump(google_credentials, token)
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', CREDENTIALS_SCOPES)
            google_credentials = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(google_credentials, token)

    service = build('calendar', 'v3', credentials = google_credentials)

    # Call the Calendar API
    now = datetime.utcnow().replace(hour = 0, minute = 0, second = 0, microsecond = 0).isoformat() + 'Z'
    sevenDaysFromNow = (datetime.utcnow() + timedelta(days = 14)).isoformat() + 'Z'
    events_result = service.events().list(calendarId = 'primary',
                                          timeMin = now,
                                          timeMax = sevenDaysFromNow,
                                          maxResults = 15,
                                          singleEvents = True,
                                          orderBy = 'startTime').execute()
    return events_result.get('items', [])


def draw_calendar_events(offset, events = [], font_size = 20, font_size_time = 13, font_size_day = 25, font_size_multi_day = 14, font_size_month = 10, seperator = 0):
    month_x, month_y = offset
    month_seperator = 2
    month_width = 42
    day_seperator = 0
    y_event = month_y
    y_day_start = month_y
    y_day_size = font_size_day + 2 + month_seperator + font_size_month + month_seperator + 3
    font_day = ImageFont.truetype(font_path, font_size_day)
    font_multi_day = ImageFont.truetype(font_path, font_size_multi_day)
    font_month = ImageFont.truetype(font_path, font_size_month)
    font_time = ImageFont.truetype(font_path, font_size_time)
    font = ImageFont.truetype(font_path, font_size)
    currentDate = None

    for event in events:
        eventStartDateTime = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        eventEndDateTime = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        if 'date' in event['end']:
            eventEndDateTime = eventEndDateTime - timedelta(days = 1)
        eventStartDate = eventStartDateTime.date()
        singleDay = eventEndDateTime.date() - eventStartDate <= timedelta(days = 1)
        color = 'red' if eventStartDate <= datetime.now().date() else 'black'
        if not currentDate == eventStartDate:
            # Draw event date.
            currentDate = eventStartDate
            # if eventStartDate == datetime.now().date():
            #     drawRed.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            #     drawBlack.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            #     drawRed.rectangle(((0, y), (70, y + font_size_day + 3)))
            #     drawBlack.rectangle(((0, y), (70, y + font_size_day + 3)))
            # else:
            #     drawBlack.polygon(((0, y), (EPD_WIDTH, y), (EPD_WIDTH, y + 3), (70, y + font_size_day + 3), (0, y + font_size_day + 3)), fill='black')
            # y += 1
            # draw_center_text((70 / 2, y + font_size_day / 2), currentDate.strftime('%d/%m'), font=font_day, color='white')
            # y += font_size_day + seperator

            y_event = max(y_day_start, y_event) + day_seperator
            y_day_start = y_event
            day_seperator = 5

            draw_rect_outline(((month_x, y_event), (month_x + month_width, y_event + font_size_day + 2 + month_seperator + font_size_month + month_seperator)), color='black')
            if singleDay:
                draw_center_text((month_x + month_width / 2, y_event + font_size_day / 2), currentDate.strftime('%d'), font=font_day, color='black')
            else:
                draw_center_text((month_x + month_width / 2, y_event + font_size_multi_day / 2), currentDate.strftime('%d'), font=font_multi_day, color='black')
                draw_center_text((month_x + month_width / 2, y_event + font_size_multi_day / 2 + font_size_multi_day - 2), eventEndDateTime.strftime('%d'), font=font_multi_day, color='black')

            draw_rect_fill(((month_x + 1, y_event + font_size_day + 2), (month_x + month_width - 1, y_event + font_size_day + month_seperator + font_size_month + month_seperator + 2 - 1)), color = 'red')
            draw_center_text((month_x + month_width / 2, y_event + font_size_day + 2 + month_seperator + font_size_month / 2), currentDate.strftime('%b'), font=font_month, color='white')

            y_day_start += y_day_size

        # Draw the event it self.
        if singleDay:
            draw_left_text((month_x + month_width + 4, y_event + font_size_time / 2), "{} - {}".format(eventStartDateTime.strftime('%H:%M'), eventEndDateTime.strftime('%H:%M')), font=font_time, color=color)
        else:
            draw_left_text((month_x + month_width + 4, y_event + font_size_time / 2), "{} - {}".format(eventStartDateTime.strftime('%-d/%-m'), eventEndDateTime.strftime('%-d/%-m')), font=font_time, color=color)
        y_event += font_size_time
        draw_left_text((month_x + month_width + 4, y_event + font_size / 2), event['summary'], font=font, color=color)
        y_event += font_size + seperator

def generate(black_image_path, red_image_path, color_image_path = None):
    # Draw date in a red square in left side.
    draw_rect_fill(((0, 0), (EPD_WIDTH / 2, 130)), color = 'red')
    draw_date((EPD_WIDTH / 4, 65), font_size_day = 20, font_size_date = 30, font_size_month = 25, font_size_year = 13, sep_year=5, color = 'white', color_year = 'white')

    # Draw calendar below the date.
    draw_calendar((0, 145), EPD_WIDTH / 2, font_size_day_of_week = 9, font_size_month_day = 14, seperation = 5)

    # Draw weather status in right side.
    draw_weather((EPD_WIDTH / 2, 20), EPD_WIDTH / 2, font_size_windspeed = 18, font_size_weather_icon = 120, font_size_temperature = 50, font_size_description = 10, sep_weather_icon = 0)

    # Draw borders between sections.
    seperator_pos = 250
    draw_rect_fill(((EPD_WIDTH / 2, 130), (EPD_WIDTH / 2, seperator_pos)), color = 'black')
    draw_rect_fill(((0, seperator_pos), (EPD_WIDTH, seperator_pos)), color = 'black')

    # Draw the list of all calendar events
    draw_calendar_events((2, seperator_pos + 3), events = get_calendar_events(), font_size = 19, font_size_time = 12, seperator = 5)

    # Output the images.
    imageBlack.save(black_image_path)
    imageRed.save(red_image_path)
    if (color_image_path):
        imageColor.save(color_image_path)

def main():
    generate('output_black.bmp', 'output_red.bmp', 'output.bmp')
    
if __name__ == '__main__':
    main()
