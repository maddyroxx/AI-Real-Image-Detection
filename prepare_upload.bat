@echo off
echo Preparing files for upload...
mkdir "c:\vortex\upload_to_huggingface"

REM Copy all files using robocopy, excluding large folders and cache
robocopy "c:\vortex\AI_Real_Detection" "c:\vortex\upload_to_huggingface" /E /XD model dataset venv env .git .vscode __pycache__ /XF *.pyc *.pyo

echo.
echo ------------------------------------------------------------
echo DONE! A new folder has opened with your files.
echo 1. Press CTRL+A to select all files in this new folder.
echo 2. Drag them into the Hugging Face "Upload files" box.
echo ------------------------------------------------------------
echo.
pause
explorer "c:\vortex\upload_to_huggingface"
