# Sea Battle

Учебная игра «Морской бой» на Python и Pygame Zero.

## Запуск в Windows

1. Установите Python 3.10 или новее с сайта [python.org](https://www.python.org/downloads/).
2. При установке Python включите пункт **Add Python to PATH**.
3. Запустите файл `START_GAME.bat`.

При первом запуске сценарий автоматически:

- создаст изолированное окружение `.venv`;
- установит зависимости из `requirements.txt`;
- запустит игру как приложение.

При последующих запусках будет использоваться то же окружение. Для установки библиотек требуется подключение к интернету только при первом запуске или обновлении зависимостей.

## Ручной запуск

В PowerShell из папки проекта:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\pgzrun.exe game.py
```
