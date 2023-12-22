import requests
import telebot
from telebot import types
import json


bot_token = '6976555048:AAG0Fd3AKOA6EGISwFU-sAAv-XiXZE-HL-Q'
api_key = '4f23403f8d8783172eedf5a04aa0e08c'

bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def start_message(message):
    greeting = "Hi! I'm a Weather Report bot, I can tell you about a forecast in a specific city. To check weather in a specific city use command /check"
    bot.send_message(message.chat.id, greeting)


@bot.message_handler(commands=['check'])
def start_message(message):
    check = "Type in the name of the city to find out about weather conditions there..."
    bot.send_message(message.chat.id, check)


def is_text_message(message):
    return True if message.content_type == 'text' else False


@bot.message_handler(func=is_text_message)
def get_answer(message):
    city = message.text

    # пока бот ждет ответа от сервера, мы высвечиваем сообщение об отправленном запросе
    bot.send_message(message.chat.id, f'Okay! Let me check the forecast in {city}...')
    weather = check_weather(c=city)

    # обрабатываем случай, когда город не нашелся
    if weather == [] or weather == -1:
        bot.send_message(
            message.chat.id,
            f'Sorry! Could not find the {city} city. Try writing another one with /check'
        )
    else:
        w = weather["w"]
        we = weather["we"]
        wi = weather["wi"]
        h = weather["h"]
        t = weather["t"]
        p = weather["p"]
        n = weather["n"]

        bot.send_message(
            message.chat.id,
            f'Weather conditions in {n} are: at the moment it is {w}, {we}, the speed of the wind is: {wi}m/h, humidity: {h}%, temperature is: {t} degree celsius, pressure is: {p} hPa'
        )

        inline = types.InlineKeyboardMarkup()
        button_1 = types.InlineKeyboardButton('Yes', callback_data='yes')
        button_2 = types.InlineKeyboardButton('No', callback_data='no')

        inline.add(button_1, button_2)

        bot.send_message(
            message.chat.id,
            f'Is {n} the city you were looking for?',
            reply_markup=inline
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'yes':
        bot.send_message(call.message.chat.id, 'Was glad to report to you!')
    elif call.data == 'no':
        bot.send_message(call.message.chat.id, 'Okay, let us try again! Enter /check command again')


def get_city_coordinates(c):
    api_url = f'http://api.openweathermap.org/geo/1.0/direct?q={c}&limit=5&appid={api_key}'
    response = requests.get(url=api_url)
    if response.status_code == 200:

        # сохраняем ответ от сервера и раскодируем json
        data = json.loads(response.text)
        print(data)

        # if data == []

        # из множества городов берем самый популярный первый вариант
        first_place = data[0]
        # записываем его координаты для функции check_weather
        lat = first_place["lat"]
        lon = first_place["lon"]
        name = first_place["name"]

        # возвращаем координаты
        return (lat, lon, name)
    else:
        print("There was a problem with getting data: ", response.status_code, response.text)
        return -1


def check_weather(c):
    # подаем запрос чтобы выяснить координаты
    coordinates = get_city_coordinates(c)
    lat = coordinates[0]
    lon = coordinates[1]
    name = coordinates[2]

    # используем координаты в api-запросе и посылаем запрос
    api_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url=api_url)
    if response.status_code == 200:

        # сохраняем ответ от сервера и раскодируем json
        data = json.loads(response.text)

        # Обрабатываем принятый json
        weather = data["weather"][0]["main"]
        weather_explanaition = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        temperature_kelvin = data["main"]["temp"]
        temperature_celsius = round(temperature_kelvin - 273.15, 2)
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]

        # для удобства заносим все данные в словарь
        weather_data = {"w": weather, "we": weather_explanaition, "wi": wind,
                        "h": humidity, "t": temperature_celsius, "p": pressure, "n": name}

        # возвращаем словарь состоящий из нужных нам данных
        return (weather_data)
    else:
        print("There was a problem with getting data: ", response.status_code, response.text)
        return -1


bot.infinity_polling()