@echo off
title Command Processor

:loop
    set /p Command=<commands.txt
    if not "%Command%"=="" (
        %Command%
        echo. > commands.txt
    )
    timeout /t 1 >nul
goto loop