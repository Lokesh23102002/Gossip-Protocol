@echo off
rem Set the Conda environment name
set CONDA_ENV=cn

rem Set the Python executable path if necessary
set PYTHON_PATH=python

rem List of ports to start the peer servers
set PORTS=1234 1235 1236

rem Initialize Conda (Adjust path if necessary)
call "%UserProfile%\anaconda3\Scripts\activate.bat" >nul

rem Loop through each port and start a peer server in a new Command Prompt
for %%P in (%PORTS%) do (
    echo Starting Seed server on port %%P...
    start cmd /k "conda activate %CONDA_ENV% && %PYTHON_PATH% Seed\seed.py --port %%P --max-peers 10"
)

echo All Seed servers started.
