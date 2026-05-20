# FFmpeg Basics & Manual Render Pipeline

This document serves as the foundational knowledge base for the Zem media engine rendering pipeline.

## 1. Installation & Verification
- **Command**: `ffmpeg -version`, `ffprobe -version`
- **Purpose**: Ensure FFmpeg is accessible globally with H264 support.

## 2. Basic Video Inspection
- **Command**: `ffprobe <input>`
- **Usage**: Check resolution, FPS, bitrate, and codecs.
- **Example**: `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,avg_frame_rate,codec_name -of default=noprint_wrappers=1 input.mp4`

## 3. Video Trimming
- **Command**: `ffmpeg -i <input> -ss <start> -t <duration> <output>`
- **Example**: `ffmpeg -i input.mp4 -ss 00:00:10 -t 30 -c copy output.mp4` (Uses `-c copy` for fast trimming without re-encoding).

## 4. Scaling & Aspect Ratio
- **Goal**: 1080x1920 (Vertical)
- **Command**: `ffmpeg -i <input> -vf scale=1080:1920 <output>`
- **Pro Tip**: Use `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920` to fill the screen without stretching.

## 5. Cropping
- **Command**: `-vf "crop=w:h:x:y"`
- **Example**: `-vf "crop=1080:1920:(in_w-1080)/2:(in_h-1920)/2"` (Center crop).

## 6. Audio Management
- **Replace Audio**: `ffmpeg -i video.mp4 -i audio.mp3 -map 0:v -map 1:a -shortest output.mp4`
- **Mix Audio**: `[0:a][1:a]amix=inputs=2:duration=first[aout]`

## 7. Subtitles
- **SRT/ASS**: `ffmpeg -i video.mp4 -vf subtitles=subs.srt output.mp4`
- **ASS Styling**: Advanced styles like `Alignment=2,Outline=1,Shadow=1`.

## 8. Overlays & Transitions
- **Overlay**: `[0:v][1:v]overlay=x:y[outv]`
- **Transitions**: `xfade=transition=fade:duration=1:offset=5`

## 9. Performance & Export
- **Codec**: `libx264`
- **Preset**: `fast` (Good balance), `veryslow` (Best quality/size).
- **CRF**: `23` (Standard), `18` (High quality).
- **Format**: MP4 (H264/AAC).

## 10. Manual Render Pipeline
1. **Trim**: Extract gameplay clip.
2. **Format**: Scale and crop to 1080x1920.
3. **Audio**: Add narration and background music.
4. **Captions**: Burn styled ASS subtitles.
5. **Branding**: Add watermark/overlays.
6. **Final**: Export mobile-optimized MP4.

## 11. Lessons Learned & Failure Learning
- **Path Escaping**: On Windows, FFmpeg filter paths (like `subtitles` or `ass`) must use single quotes and sometimes double-escaped backslashes.
- **Codec Mismatch**: Using `.mp3` extension with `aac` codec leads to errors. Match extension with proper encoder (`libmp3lame` for mp3, `aac` for m4a/mp4).
- **Keyframes and Trimming**: Using `-c copy` with `-ss` and `-t` can lead to audio-only files if no keyframe is found at the start point. Re-encoding (removing `-c copy`) is safer for precise trimming.
- **Filter Order**: Scaling should usually happen before overlaying to ensure correct coordinate mapping.
- **ASS Fonts**: Ensure fonts used in ASS styles are installed on the system, otherwise FFmpeg will fallback to Arial.

## 12. Future Preparation
- **Automation**: The `filter_complex` used in `render_final_short.ps1` is the template for the future automated engine.
- **Performance**: GPU acceleration (`-c:v h264_nvenc`) can be explored for faster renders.
- **Dynamic Content**: Subtitles and overlays will be generated dynamically based on AI-derived scripts.
