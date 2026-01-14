@echo off
REM Smart Factory CV - RTSP Stream Simulator

echo.
echo ============================================================
echo   Smart Factory CV - RTSP Stream Simulator
echo ============================================================
echo.

where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] FFmpeg not found! Please install FFmpeg first.
    pause
    exit /b 1
)

set RTSP_SERVER=rtsp://localhost:8554
set VIDEO_DIR=%~dp0..\services\dashboard\public\videos

echo RTSP Server: %RTSP_SERVER%
echo Video Folder: %VIDEO_DIR%
echo.

if not exist "%VIDEO_DIR%" (
    echo [ERROR] Video folder not found: %VIDEO_DIR%
    pause
    exit /b 1
)

echo Starting video streams...
echo.

if exist "%VIDEO_DIR%\cam1.mp4" (
    echo [CAM-1] Starting Main Entrance stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam1.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam1"
)

if exist "%VIDEO_DIR%\cam2.mp4" (
    echo [CAM-2] Starting Assembly Line stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam2.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam2"
)

if exist "%VIDEO_DIR%\cam3.mp4" (
    echo [CAM-3] Starting Loading Dock stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam3.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam3"
)

if exist "%VIDEO_DIR%\cam4.mp4" (
    echo [CAM-4] Starting Machine Shop stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam4.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam4"
)

echo.
echo ============================================================
echo   Streams running! Press any key to stop all streams...
echo ============================================================
pause

taskkill /f /im ffmpeg.exe >nul 2>&1
echo Streams stopped.
