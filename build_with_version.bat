@echo off
for /f "tokens=2 delims== " %%v in ('findstr /b "VERSION" src\main.py') do (
    set "ver=%%~v"
)
set "ver=%ver:"=%"
pyinstaller --onefile --name "unstructured-renamer-%ver%" src\main.py