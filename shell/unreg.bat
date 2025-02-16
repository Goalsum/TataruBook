@echo off
reg delete HKLM\Software\Classes\Directory\background\shell\TataruBook /f
reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck /f
reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade /f
reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /f
reg delete HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /f
pause