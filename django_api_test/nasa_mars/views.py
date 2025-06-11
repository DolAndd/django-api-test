from django.shortcuts import render
import requests
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
            photos = [photo["img_src"] for photo in data]

    context = {
        'form': form,
        'photos': photos,
    }
    return render(request, 'nasa/nasa.html', context)

