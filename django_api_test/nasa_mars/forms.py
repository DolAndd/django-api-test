from django import forms


class RoverForm(forms.Form):
    ROVER_CHOICES = [
        ('curiosity', 'Curiosity'),
        ('opportunity', 'Opportunity'),
        ('spirit', 'Spirit'),
        ('perseverance', 'Perseverance'),
    ]

    rover = forms.ChoiceField(
        choices=ROVER_CHOICES,
        initial='curiosity',
        label='Выберите марсоход',
        widget=forms.Select(attrs={'class': 'form-control'}))
