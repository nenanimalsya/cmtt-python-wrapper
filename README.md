# Установка
```
pip install cmtt-python-wrapper
```
# Использование
```
from cmtt_python_wrapper import CMTT, Platform
import asyncio

async def main():
    client = CMTT(Platform.TJ,'YOUR_TOKEN')

    uploaded = await client.uploaderExtract('https://i.imgur.com/K7Ovp03.jpg')
    await client.commentSend(92781,'',attachments=uploaded['result'])
    
asyncio.get_event_loop().run_until_complete(main()) # asyncio.run(main()) для python 3.7+

```
# Документация

https://cmtt-ru.github.io/osnova-api/redoc.html<br/>
https://cmtt-ru.github.io/osnova-api/swagger.html
