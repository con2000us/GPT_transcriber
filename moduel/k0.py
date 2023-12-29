import os
import subprocess
import sys
import whisper
from datetime import timedelta
import json
import config_reader

config = config_reader.config
process_path = os.path.join("process")

def str_to_bool(s):
    return s.lower() in ['true', '1', 't', 'y', 'yes'] 

def scan_files(directory):
    # 支持的檔案格式
    video_extensions = ['.mp4', '.avi', '.mov', 'mkv']
    audio_extensions = ['.mp3', '.wav', '.aac', 'm4a']

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    media_files = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions + audio_extensions]

    return media_files

def identify_language(audio_path):
    # 載入模型
    model = whisper.load_model(config.lngDetctModel)

    # 處理音頻檔案
    result = model.transcribe(audio_path)

    # 獲取語言代碼
    language_code = result["language"]

    return language_code

def format_time(seconds):
    """将秒数格式化为 VTT 时间戳"""
    return str(timedelta(seconds=seconds)).replace(".", ",")

def generate_vtt(audio_path, model_size="large"):
    model = whisper.load_model(config.whisperModel )
    result = model.transcribe(audio_path, verbose=False)

    # 偵測影片語言
    language_code = result["language"]
    print(f"影片語言 : {language_code}")
    # 打開並讀取 JSON 文件
    with open(os.path.join(process_path,config.workingFile), 'r') as file:
        data = json.load(file)

    data['lng'] = language_code  # 替換為你想要的值
    with open(os.path.join(process_path,config.workingFile), 'w') as file:
        json.dump(data, file, indent=4)

    vtt_content = ""

    for segment in result["segments"]:
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        text = segment["text"]
        vtt_content += f"{start_time} --> {end_time}\n{text}\n\n"

    return vtt_content

def main():
    directory = '.'  # 當前目錄
    media_files = scan_files(directory)
    process_files = scan_files(process_path)
    selected_file = '';

    # 检查是否存在 default.mp4
    if 'default.mp4' in process_files:
        selected_file = 'default.mp4'

        selected_file_data = {
            "file_name": selected_file,
            "lng": "en"
        }
        with open(os.path.join(process_path,config.workingFile), 'w') as file:
            json.dump(selected_file_data, file, indent=4)
    if not media_files and not process_files:
        print("沒有找到任何媒體檔案。")
        sys.exit(1)  # 非零退出状态码表示错误
        return
    else:

        # 如果已经选择了 default.mp4，则跳过用户选择
        if selected_file != 'default.mp4':
            # 顯示檔案列表
            for i, file in enumerate(media_files):
                print(f"{i + 1}: {file}")
            # 讓使用者選擇
            choice = input("請選擇一個檔案（輸入數字）: ")
            try:
                selected_file = media_files[int(choice) - 1]
                shutil.move(selected_file, process_path)
                selected_file_data = {
                    "file_name": selected_file,
                    "lng": "en"
                }
                with open(os.path.join(process_path,config.workingFile), 'w') as file:
                    json.dump(selected_file_data, file, indent=4)
            except (IndexError, ValueError):
                print("無效的選擇。")
                return

    # 執行shell命令
    print("*****開始解析影片轉錄字幕*****")
    try:
        # vtt_text = generate_vtt(selected_file, model_size=config.whisperModel)
        vtt_text = generate_vtt(os.path.join(process_path,selected_file), model_size=config.whisperModel)


        # 将生成的 VTT 内容写入文件
        # with open(config.whisperFile, "w", encoding="utf-8") as file:
        with open(os.path.join(process_path,config.whisperFile), "w", encoding="utf-8") as file:
            file.write(vtt_text)

    except subprocess.CalledProcessError as e:
        print(f"执行错误: {e}")
    except OSError as e:
        print(f"文件重命名失败: {e}")

if __name__ == "__main__":
    main()
