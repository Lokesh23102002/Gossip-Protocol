@echo off
rem Set the Conda environment name
set CONDA_ENV=cn

rem Set the Python executable path if necessary
set PYTHON_PATH=python

rem List of ports to start the peer servers
set PORTS=1234 1235 1236

rem Loop through each port and start a peer server in a new Command Prompt
for %%P in (%PORTS%) do (
    echo Starting Seed server on port %%P...
    start cmd /k %PYTHON_PATH% seed.py --port %%P --max-peers 10"
)

echo All Seed servers started.
