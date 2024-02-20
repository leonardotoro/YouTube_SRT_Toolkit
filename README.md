# YouTube .SRT Toolkit with OpenAI API

## Overview
The YouTube .SRT Toolkit is a comprehensive script designed to automate the extraction, processing, and transcription of audio from YouTube videos. This script is particularly useful for content creators, educators, and anyone looking to create transcripts or subtitles for YouTube videos. It simplifies the workflow by downloading audio, segmenting it based on silence, transcribing the segmented audio, and merging the transcriptions into a single SRT file.

PS Comments and some functions on .py script are in italian, I will translate it soon but if you have urgency is fully usable.

## Features
- **Video Audio Extraction**: Downloads the audio track of a given YouTube video URL.
- **Audio Segmentation**: Splits the audio into smaller segments based on periods of silence, facilitating easier transcription.
- **Audio Transcription**: Utilizes OpenAI's API to transcribe the audio segments into text.
- **Subtitles Merging**: Combines all individual SRT files into a single, comprehensive subtitle file.

## Structure
The script is organized into several key functions, each responsible for a part of the process:
- `get_video_title(url)`: Retrieves the title of a YouTube video.
- `check_and_delete_mp3(title)`: Checks for and deletes any pre-existing MP3 files with the same title.
- `download_audio(url)`: Downloads and converts the YouTube video's audio to MP3 format.
- `split_and_rename(audio_segment, base_name)`: Segments the audio file based on silence.
- `transcribe_audio_files()`: Transcribes the segmented audio files into text.
- `merge_srt_files(srt_files_info, final_file_path)`: Merges all SRT files into a single file.

## How to Use
1. **Setup**: Ensure Python is installed on your system and install the required packages (`pydub`, `pytube`, `openai`, etc.).
2. **API Key**: Set your OpenAI API key in the environment variables or directly in the script. --> https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
3. **Execution**: Run the script from the command line, providing the YouTube video URL when prompted.
4. **Follow Prompts**: The script will guide you through the process, asking for any necessary input along the way.
5. **Output**: The final output will be an MP3 file of the video's audio and an SRT file containing the transcriptions.

## Dependencies
- Python 3.x
- `pydub`
- `pytube`
- `openai`
- `ffmpeg` (for audio conversion)

## Installation
To install the necessary dependencies, run the following command:
```
pip install pydub pytube openai ffmpeg pytube
```
## Contributing
Contributions are welcome! If you have suggestions for improving the script, feel free to open an issue or submit a pull request.

## License
This project is open source and available under the [MIT License](LICENSE).
