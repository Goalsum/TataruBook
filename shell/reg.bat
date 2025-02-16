@echo off
reg add HKLM\Software\Classes\Directory\background\shell\TataruBook /d "TataruBook create DB file" /f
reg add HKLM\Software\Classes\Directory\background\shell\TataruBook /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\Directory\background\shell\TataruBook\command /d "\"%~dp0init.bat\"" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck /d "TataruBook check" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookCheck\command /d "\"%~dp0check.bat\" \"%%1\"" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade /d "TataruBook upgrade" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookUpgrade\command /d "\"%~dp0upgrade.bat\" \"%%1\"" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /v MUIVerb /t REG_SZ /d "TataruBook paste" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste /v subcommands /t REG_SZ /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\a_asset_types /d asset_types /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\a_asset_types\command /d "\"%~dp0paste.bat\" \"%%1\" asset_types" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\b_standard_asset /d standard_asset /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\b_standard_asset\command /d "\"%~dp0paste.bat\" \"%%1\" standard_asset" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\c_accounts /d accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\c_accounts\command /d "\"%~dp0paste.bat\" \"%%1\" accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\d_interest_accounts /d interest_accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\d_interest_accounts\command /d "\"%~dp0paste.bat\" \"%%1\" interest_accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\e_postings /d postings /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\e_postings\command /d "\"%~dp0paste.bat\" \"%%1\" postings" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\f_prices /d prices /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\f_prices\command /d "\"%~dp0paste.bat\" \"%%1\" prices" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\g_start_date /d start_date /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\g_start_date\command /d "\"%~dp0paste.bat\" \"%%1\" start_date" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\h_end_date /d end_date /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookPaste\shell\h_end_date\command /d "\"%~dp0paste.bat\" \"%%1\" end_date" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /v MUIVerb /t REG_SZ /d "TataruBook export" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport /v subcommands /t REG_SZ /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\a_asset_types /d asset_types /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\a_asset_types\command /d "\"%~dp0export.bat\" \"%%1\" asset_types" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\b_accounts /d accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\b_accounts\command /d "\"%~dp0export.bat\" \"%%1\" accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\c_interest_accounts /d interest_accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\c_interest_accounts\command /d "\"%~dp0export.bat\" \"%%1\" interest_accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\d_postings /d postings /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\d_postings\command /d "\"%~dp0export.bat\" \"%%1\" postings" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\e_prices /d prices /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\e_prices\command /d "\"%~dp0export.bat\" \"%%1\" prices" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\f_statements /d statements /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\f_statements\command /d "\"%~dp0export.bat\" \"%%1\" statements" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\g_start_stats /d start_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\g_start_stats\command /d "\"%~dp0export.bat\" \"%%1\" start_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\h_start_assets /d start_assets /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\h_start_assets\command /d "\"%~dp0export.bat\" \"%%1\" start_assets" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\i_end_stats /d end_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\i_end_stats\command /d "\"%~dp0export.bat\" \"%%1\" end_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\j_end_assets /d end_assets /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\j_end_assets\command /d "\"%~dp0export.bat\" \"%%1\" end_assets" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\k_income_and_expenses /d income_and_expenses /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\k_income_and_expenses\command /d "\"%~dp0export.bat\" \"%%1\" income_and_expenses" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\l_portfolio_stats /d portfolio_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\l_portfolio_stats\command /d "\"%~dp0export.bat\" \"%%1\" portfolio_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\m_flow_stats /d flow_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\m_flow_stats\command /d "\"%~dp0export.bat\" \"%%1\" flow_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\n_return_on_shares /d return_on_shares /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\n_return_on_shares\command /d "\"%~dp0export.bat\" \"%%1\" return_on_shares" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\o_interest_rates /d interest_rates /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\o_interest_rates\command /d "\"%~dp0export.bat\" \"%%1\" interest_rates" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\p_periods_cash_flows /d periods_cash_flows /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExport\shell\p_periods_cash_flows\command /d "\"%~dp0export.bat\" \"%%1\" periods_cash_flows" /f

echo Note: If you move the program's folder, you MUST rerun install.bat!
pause