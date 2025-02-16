@echo off
set /p filename="Input DB filename to create with(for example: financial.db):"
"%~dp0..\tatarubook.exe" init %filename%
pause