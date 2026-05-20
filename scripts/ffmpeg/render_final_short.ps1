# Final Short Render Script
$FFMPEG = "C:\Users\athar\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin\ffmpeg.exe"

& $FFMPEG -i assets/input/video/gameplay_test.mp4 `
    -i assets/input/audio/narration_test.mp3 `
    -i assets/input/video/watermark.png `
    -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,ass='assets/input/subtitles/test.ass'[v1]; [2:v]scale=200:-1[logo]; [v1][logo]overlay=main_w-overlay_w-50:50[outv]" `
    -map "[outv]" -map 1:a `
    -c:v libx264 -preset fast -crf 23 `
    -c:a aac -shortest `
    assets/output/final_short.mp4 -y

Write-Host "Render Complete: assets/output/final_short.mp4"
