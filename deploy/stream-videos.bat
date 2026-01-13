@echo off
REM ============================================================
REM Smart Factory CV - RTSP Stream Simulator
REM ============================================================
REM This script streams video files to MediaMTX RTSP server
REM using FFmpeg. Each video becomes a "virtual CCTV camera".
REM ============================================================

echo.
echo ============================================================
echo   Smart Factory CV - RTSP Stream Simulator
echo ============================================================
echo.

REM Check if FFmpeg is installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] FFmpeg not found! Please install FFmpeg first.
    echo Download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

REM RTSP Server URL (MediaMTX default)
set RTSP_SERVER=rtsp://localhost:8554

REM Video folder
set VIDEO_DIR=%~dp0..\services\dashboard\public\videos

echo RTSP Server: %RTSP_SERVER%
echo Video Folder: %VIDEO_DIR%
echo.

REM Check if video folder exists
if not exist "%VIDEO_DIR%" (
    echo [ERROR] Video folder not found: %VIDEO_DIR%
    echo Please create the folder and add MP4 videos.
    pause
    exit /b 1
)

REM Stream each video file
echo Starting video streams...
echo.

REM Camera 1 - Main Entrance
if exist "%VIDEO_DIR%\cam1.mp4" (
    echo [CAM-1] Starting Main Entrance stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam1.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam1"
) else (
    echo [CAM-1] No video found (cam1.mp4)
)

REM Camera 2 - Assembly Line
if exist "%VIDEO_DIR%\cam2.mp4" (
    echo [CAM-2] Starting Assembly Line stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam2.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam2"
) else (
    echo [CAM-2] No video found (cam2.mp4)
)

REM Camera 3 - Loading Dock
if exist "%VIDEO_DIR%\cam3.mp4" (
    echo [CAM-3] Starting Loading Dock stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam3.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam3"
) else (
    echo [CAM-3] No video found (cam3.mp4)
)

REM Camera 4 - Machine Shop
if exist "%VIDEO_DIR%\cam4.mp4" (
    echo [CAM-4] Starting Machine Shop stream...
    start /min cmd /c "ffmpeg -re -stream_loop -1 -i "%VIDEO_DIR%\cam4.mp4" -c copy -f rtsp %RTSP_SERVER%/live/cam4"
) else (
    echo [CAM-4] No video found (cam4.mp4)
)

echo.
echo ============================================================
echo   Streams are running in background windows.
echo   RTSP URLs:
echo     - rtsp://localhost:8554/live/cam1
echo     - rtsp://localhost:8554/live/cam2
echo     - rtsp://localhost:8554/live/cam3
echo     - rtsp://localhost:8554/live/cam4
echo.
echo   Test with: ffplay rtsp://localhost:8554/live/cam1
echo   Press any key to stop all streams...
echo ============================================================
pause

REM Kill all FFmpeg processes
taskkill /f /im ffmpeg.exe >nul 2>&1
echo Streams stopped.
