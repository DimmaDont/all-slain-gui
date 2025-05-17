@echo off

echo setting up...
python -m venv %~dp0\venv --upgrade-deps >NUL 2>NUL

echo downloading and installing dependencies...
%~dp0\venv\Scripts\python.exe -m pip install -U -e %~dp0 >NUL 2>NUL

%~dp0\venv\Scripts\python.exe -OO %~dp0\main.pyw

exit /b
