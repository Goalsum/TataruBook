@echo off
reg query HKLM\Software\Classes\Directory\background\shell\TataruBook >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\Directory\background\shell\TataruBook /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable /f
)
reg query HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView >nul 2>&1
if %errorlevel% equ 0 (
    reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView /f
)
pause