@echo off
setlocal enabledelayedexpansion

REM Create output directory
if not exist "output" mkdir output

REM Processed files tracking
set processed_list=processed_files.txt
set processed=0
set skipped=0

REM Create processed files list if it doesn't exist
if not exist "%processed_list%" (
    echo Creating new processed files list...
    type nul > "%processed_list%"
)

echo ================================================
echo LOLA Data Processing
echo ================================================
echo Checking processed files list: %processed_list%
echo.

REM Process all .dat files in lola_data directory
for %%f in (lola_data\*.dat) do (
    REM Extract filename without extension
    set "filename=%%~nf"
    set "datfile=%%~nxf"
    
    REM Check if file is in processed list
    findstr /C:"!datfile!" "%processed_list%" >nul 2>&1
    
    if !errorlevel! equ 0 (
        REM File found in list - already processed
        echo [SKIP] !datfile! - already processed
        set /a skipped+=1
    ) else (
        REM File not in list - process it
        echo [PROCESS] !datfile!...
        
        REM Run rdr2tab on the file
        .\rdr2tab "%%f" a h > "output\!filename!.csv"
        
        REM Add filename to processed list
        echo !datfile! >> "%processed_list%"
        
        echo   ^-^> Completed !filename!.csv
        set /a processed+=1
    )
)

echo.
echo ================================================
echo Processing Summary:
echo   New files processed: !processed!
echo   Files skipped: !skipped!
echo   Processed list: %processed_list%
echo ================================================
echo.
echo You can edit %processed_list% to reprocess specific files
echo (just delete the filename from the list)
pause