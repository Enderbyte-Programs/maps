pyinstaller --icon=icon.ico -n map -w --no-confirm main.py
copy icon.png dist\map\icon.png
copy icon.ico dist\map\icon.ico
copy config.json dist\map\config.json
xcopy assets\ dist\map\assets\ /E /-Y