from django.shortcuts import render
import requests
from django.contrib import messages
from .forms import RoverForm


def nasa_view(request):
    form = RoverForm(request.GET or None)
    photos = []

    if form.is_valid():
        rover = form.cleaned_data['rover']
        url = f'https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/latest_photos?api_key=DEMO_KEY'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json().get("latest_photos", [])
            photos = [{
                'url': photo["img_src"],
                'camera': photo["camera"]["full_name"],
                'earth_date': photo["earth_date"],
                'rover_name': photo["rover"]["name"],
                'sol': photo["sol"]
            } for photo in data if "img_src" in photo]

            if not photos:
                messages.info(request, 'Нет доступных фотографий для этого марсохода.')
        else:
            messages.error(request, 'Ошибка при запросе к NASA API. Попробуйте позже.')

    context = {
        'form': form,
        'photos': photos,
    }
    return render(request, 'nasa/nasa.html', context)
