from django import forms


class TelegramAuthForm(forms.Form):
    api_id = forms.IntegerField(
        label='API ID',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    api_hash = forms.CharField(
        label='API HASH',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    channel_name = forms.CharField(
        label='Название канала (например: @channelname или https://t.me/channelname)',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
