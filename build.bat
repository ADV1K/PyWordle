@REM @ECHO OFF
pyinstaller --clean -y --onefile --windowed --log-level INFO ^
            --add-data "assets/*.png;assets" ^
            --add-data "wordlists/*.txt;wordlists" ^
            --icon "assets/wordle_logo_32x32.ico" ^
            wordle.py
            @REM --splash "assets/wordle_logo_32x32.png" ^

copy dist\wordle.exe %cd%
del /s /q build dist __pycache__ wordle.spec
rmdir /s /q build dist __pycache__