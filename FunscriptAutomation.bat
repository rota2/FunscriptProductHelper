@echo off
REM Activate the conda environment
call conda activate _python

REM Run the Streamlit app
streamlit run streamlit_ui.py

REM Pause the command window (optional, useful if running by double-clicking)
pause