# Установка
```
pip install cmtt-python-wrapper
```
# Использование
```
from cmtt_python_wrapper import Committee, Platform

client=Committee(Platform.TJ,'YOUR_TOKEN')
uploaded=client.uploaderExtract('https://i.imgur.com/K7Ovp03.jpg')
client.commentSend(92781,'',attachments=uploaded['result'])
```
# Документация
https://cmtt-ru.github.io/osnova-api/redoc.html<br/>
https://cmtt-ru.github.io/osnova-api/swagger.html
