@echo off
rem Set the Conda environment name
set CONDA_ENV=cn

rem Set the Python executable path if necessary
set PYTHON_PATH=python

rem List of ports to start the peer servers
set PORTS=3000 3001 3002 3003 3004 3005 3006 3007 3008

rem Loop through each port and start a peer server in a new Command Prompt
for %%P in (%PORTS%) do (
    echo Starting Peer server on port %%P...
    start cmd /k %PYTHON_PATH% peer.py --port %%P --max-peers 20"
)

echo All Peer servers started.
