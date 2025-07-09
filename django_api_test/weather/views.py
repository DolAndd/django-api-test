import os
from django.views import View
import requests
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from .models import City
from .forms import CityForm
from django.contrib import messages
import datetime
load_dotenv()


class WeatherView(View):
    template_name = 'weather/weather.html'
    api_url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=12af49092071ab4a79f4f25888f8c68a'

    def get_weather_data(self, city_name, city_id=None):
        """Получение данных о погоде для города"""
        response = requests.get(self.api_url.format(city_name))
        if response.status_code == 200:
            data = response.json()

            # Создаем timezone-aware datetime объект
            timestamp = data['dt'] + data['timezone']
            utc_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)

            return {
                'city_id': city_id,
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'local_time': utc_time.strftime("%H:%M, %d %B %Y")
            }
        return None

    def get(self, request):
        """Обработка GET-запросов"""
        cities = City.objects.all()
        weather_data = []

        for city in cities:
            weather = self.get_weather_data(city.name, city.id)
            if weather:
                weather_data.append(weather)

        context = {
            'weather_data': weather_data,
            'form': CityForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Обработка POST-запросов"""
        if 'delete_city' in request.POST:
            return self.handle_delete_city(request)
        elif 'add_city' in request.POST:
            return self.handle_add_city(request)
        else:
            # Обработка проверки города без добавления
            return self.handle_city_check(request)

    def handle_delete_city(self, request):
        """Обработка удаления города"""
        city_id = request.POST.get('city_id')
        try:
            city = City.objects.get(id=city_id)
            city.delete()
            messages.success(request, f'Город {city.name} удалён')
        except City.DoesNotExist:
            messages.error(request, 'Город не найден в базе')
        return redirect('weather')

    def handle_add_city(self, request):
        """Обработка добавления города"""
        form = CityForm(request.POST)
        if not form.is_valid():
            return redirect('weather')

        city_name = form.cleaned_data['name']

        # Проверка существования города в базе
        if City.objects.filter(name__iexact=city_name).exists():
            messages.warning(request, f'Город {city_name} уже есть в списке')
            return redirect('weather')

        # Проверка через API
        weather_data = self.get_weather_data(city_name)
        if not weather_data:
            messages.error(request, 'Город не найден')
            return redirect('weather')

        # Сохранение города
        form.save()
        messages.success(request, f'Город {city_name} успешно добавлен')
        return redirect('weather')

    def handle_city_check(self, request):
        """Обработка проверки города (без добавления в базу)"""
        form = CityForm(request.POST)
        if not form.is_valid():
            return redirect('weather')

        city_name = form.cleaned_data['name']
        weather_data = []

        # Получаем данные о погоде только для проверяемого города
        weather = self.get_weather_data(city_name)
        if weather:
            weather_data.append(weather)

            context = {
                'weather_data': weather_data,
                'form': form,
                'show_only_checked_city': True  # Флаг для шаблона
            }
            return render(request, self.template_name, context)
        else:
            messages.error(request, 'Город не найден')
            return redirect('weather')


'''
Вью в виде функции
def weather_view(request):

    if request.method == 'POST' and 'delete_city' in request.POST:
        # Обработка удаления города
        city_id = request.POST.get('city_id')
        try:
            city = City.objects.get(id=city_id)
            city.delete()
            messages.success(request, f'Город {city.name} удалён')
        except City.DoesNotExist:
            messages.error(request, 'Город не найден в базе')
        return redirect('weather')

    if request.method == 'POST' and 'add_city' in request.POST:
        form = CityForm(request.POST)
        if form.is_valid():
            city_name = form.cleaned_data['name']

            # Проверяем, существует ли город в базе
            if City.objects.filter(name__iexact=city_name).exists():
                messages.warning(request, f'Город {city_name} уже есть в списке')
                return redirect('weather')
            else:
                # Проверяем через API, что город существует
                url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&APPID=12af49092071ab4a79f4f25888f8c68a'
                response = requests.get(url)

                if response.status_code == 200:
                    # Сохраняем город в базу
                    form.save()
                    messages.success(request, f'Город {city_name} успешно добавлен')
                    return redirect('weather')
                else:
                    messages.error(request, 'Город не найден')
                    return redirect('weather')

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
                'city_id': city.id,
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
'''
