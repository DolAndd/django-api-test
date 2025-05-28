import os
import requests
from django.shortcuts import render
from dotenv import load_dotenv
from .models import City

load_dotenv()


def weather_view(request):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    cities = City.objects.all()

    weather_data = []

    for city in cities:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city.name}&units=metric&APPID=12af49092071ab4a79f4f25888f8c68a'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            weather = {
                'city': city.name,
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
            }
            weather_data.append(weather)

    context = {'weather_data': weather_data}
    return render(request, 'nasa-mars/nasa-mars.html', context)
