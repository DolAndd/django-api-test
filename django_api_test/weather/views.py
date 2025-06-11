import os
import requests
from django.shortcuts import render
from dotenv import load_dotenv
from .models import City
from .forms import CityForm
from django.contrib import messages
import datetime
load_dotenv()


def weather_view(request):
    # Получаем все города из базы данных
    cities = City.objects.all()
    weather_data = []

    # Обработка POST-запроса (добавление нового города)
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']

            # Проверяем погоду для нового города
            url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&APPID=12af49092071ab4a79f4f25888f8c68a'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()


                # Добавляем данные о погоде
                weather = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon'],
                    'local_time': datetime.datetime.utcfromtimestamp(data['dt'] + data['timezone']).strftime("%H:%M, %d %B %Y")
                }
                weather_data.append(weather)

                context = {
                    'weather_data': weather_data,
                    'form': form,
                }
                return render(request, 'weather/weather.html', context)
            else:
                messages.error(request, 'Город не найден')

    # Получаем погоду для всех городов из базы
    for city in cities:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city.name}&units=metric&APPID=12af49092071ab4a79f4f25888f8c68a'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            weather = {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'local_time': datetime.datetime.utcfromtimestamp(data['dt'] + data['timezone']).strftime(
                    "%H:%M, %d %B %Y")
            }
            weather_data.append(weather)

    # Создаем форму для GET-запроса
    form = CityForm()

    context = {
        'weather_data': weather_data,
        'form': form,
    }
    return render(request, 'weather/weather.html', context)
