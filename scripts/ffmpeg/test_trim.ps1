# Trim Video Experiment
& "C:\Users\athar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe" -i assets/input/video/gameplay_test.mp4 -ss 2 -t 5 -c:v libx264 -c:a aac assets/temp/trimmed_test.mp4 -y
