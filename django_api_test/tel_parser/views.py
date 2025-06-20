from django.views import View
from django.shortcuts import render
from .forms import TelegramAuthForm
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio


class TelegramParserView(View):
    template_name = 'tel_parser/tel_parser.html'
    results_template = 'tel_parser/results.html'
    form_class = TelegramAuthForm

    def get_telegram_data(self, api_id, api_hash, channel_name):
        """Асинхронный метод для получения данных из Telegram"""

        async def fetch_data():
            async with TelegramClient('session_name', api_id, api_hash) as client:
                # Очистка имени канала
                if channel_name.startswith('https://t.me/'):
                    channel_name_clean = channel_name.split('/')[-1]
                elif channel_name.startswith('@'):
                    channel_name_clean = channel_name[1:]
                else:
                    channel_name_clean = channel_name

                try:
                    channel = await client.get_entity(channel_name_clean)
                except ValueError:
                    # Попробуем с @, если не получилось без него
                    channel = await client.get_entity(f'@{channel_name_clean}')

                posts = await client(GetHistoryRequest(
                    peer=channel,
                    limit=100,
                    offset_date=None,
                    offset_id=0,
                    max_id=0,
                    min_id=0,
                    add_offset=0,
                    hash=0
                ))

                return [
                    {
                        'id': message.id,
                        'date': message.date.strftime('%Y-%m-%d %H:%M:%S'),
                        'views': getattr(message, 'views', 'N/A'),
                        'text': message.message or '',
                        'media': 'Да' if message.media else 'Нет',
                    }
                    for message in posts.messages
                ]

        return asyncio.run(fetch_data())

    def get(self, request, *args, **kwargs):
        """Обработка GET-запросов"""
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        """Обработка POST-запросов"""
        form = self.form_class(request.POST)
        context = {'form': form}

        if form.is_valid():
            try:
                posts = self.get_telegram_data(
                    form.cleaned_data['api_id'],
                    form.cleaned_data['api_hash'],
                    form.cleaned_data['channel_name']
                )
                context.update({
                    'posts': posts,
                    'channel_name': form.cleaned_data['channel_name']
                })
                return render(request, self.results_template, context)
            except Exception as e:
                form.add_error(None, f'Ошибка: {str(e)}. Проверьте данные и попробуйте снова.')

        return render(request, self.template_name, context)
