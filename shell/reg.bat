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
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable /v MUIVerb /t REG_SZ /d "TataruBook export table" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable /v subcommands /t REG_SZ /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\a_asset_types /d asset_types /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\a_asset_types\command /d "\"%~dp0export.bat\" \"%%1\" asset_types" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\b_standard_asset /d standard_asset /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\b_standard_asset\command /d "\"%~dp0export.bat\" \"%%1\" standard_asset" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\c_accounts /d accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\c_accounts\command /d "\"%~dp0export.bat\" \"%%1\" accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\d_interest_accounts /d interest_accounts /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\d_interest_accounts\command /d "\"%~dp0export.bat\" \"%%1\" interest_accounts" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\e_postings /d postings /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\e_postings\command /d "\"%~dp0export.bat\" \"%%1\" postings" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\f_prices /d prices /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\f_prices\command /d "\"%~dp0export.bat\" \"%%1\" prices" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\g_start_date /d start_date /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\g_start_date\command /d "\"%~dp0export.bat\" \"%%1\" start_date" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\h_end_date /d end_date /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportTable\shell\h_end_date\command /d "\"%~dp0export.bat\" \"%%1\" end_date" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView /v icon /t REG_SZ /d "%~dp0..\tatarubook.exe" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView /v MUIVerb /t REG_SZ /d "TataruBook export view" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView /v subcommands /t REG_SZ /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\a_statements /d statements /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\a_statements\command /d "\"%~dp0export.bat\" \"%%1\" statements" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\b_start_stats /d start_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\b_start_stats\command /d "\"%~dp0export.bat\" \"%%1\" start_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\c_start_assets /d start_assets /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\c_start_assets\command /d "\"%~dp0export.bat\" \"%%1\" start_assets" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\d_end_stats /d end_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\d_end_stats\command /d "\"%~dp0export.bat\" \"%%1\" end_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\e_end_assets /d end_assets /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\e_end_assets\command /d "\"%~dp0export.bat\" \"%%1\" end_assets" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\f_income_and_expenses /d income_and_expenses /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\f_income_and_expenses\command /d "\"%~dp0export.bat\" \"%%1\" income_and_expenses" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\g_portfolio_stats /d portfolio_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\g_portfolio_stats\command /d "\"%~dp0export.bat\" \"%%1\" portfolio_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\h_flow_stats /d flow_stats /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\h_flow_stats\command /d "\"%~dp0export.bat\" \"%%1\" flow_stats" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\i_return_on_shares /d return_on_shares /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\i_return_on_shares\command /d "\"%~dp0export.bat\" \"%%1\" return_on_shares" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\j_interest_rates /d interest_rates /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\j_interest_rates\command /d "\"%~dp0export.bat\" \"%%1\" interest_rates" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\k_periods_cash_flows /d periods_cash_flows /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\k_periods_cash_flows\command /d "\"%~dp0export.bat\" \"%%1\" periods_cash_flows" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\l_price_unavailable /d price_unavailable /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\l_price_unavailable\command /d "\"%~dp0export.bat\" \"%%1\" price_unavailable" /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\m_net_worth_changes /d net_worth_changes /f
reg add HKLM\Software\Classes\SystemFileAssociations\.db\shell\TataruBookExportView\shell\m_net_worth_changes\command /d "\"%~dp0export.bat\" \"%%1\" net_worth_changes" /f

echo Note: If you move the program's folder, you MUST rerun install.bat!
pause