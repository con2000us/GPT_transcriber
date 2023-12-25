import subprocess
import json
import os
import shutil
from pytube import YouTube
import string
import math
import config_reader
import unicodedata

config = config_reader.config

def run_script(script_name):
    try:
        subprocess.run(['python', script_name], check=True)
    except subprocess.CalledProcessError as e:
        #print(f"Error running {script_name}: {e}")
        return False
    return True

def get_resolution_streams(streams):
    """ 获取所有可用的解析度选项 """
    resolutions = set()
    for stream in streams:
        if stream.resolution:
            resolutions.add(stream.resolution)
    return sorted(resolutions, reverse=True)

# 清理文件名函数
def clean_filename(filename):
    # 定义不允许的特殊字符
    invalid_chars = '/\\:*?"<>|.'
    # 使用 unicodedata.category 获取字符的通用类别，然后过滤掉控制字符（如换行符）
    cleaned_filename = ''.join(c for c in filename if unicodedata.category(c)[0] != 'C' and c not in invalid_chars)
    return cleaned_filename

def get_resolution_streams(streams):
    """ 获取所有可用的解析度选项 """
    resolutions = set()
    for stream in streams:
        if stream.resolution:
            resolutions.add(stream.resolution)
    return sorted(resolutions, reverse=True)

def show_progress_bar(chunk, file_handle, bytes_remaining):
    """ 显示下载进度的回调函数 """
    current = ((stream.filesize - bytes_remaining) / stream.filesize)
    percent = '{0:.1f}'.format(current * 100)
    progress = int(50 * current)
    status = '█' * progress + '-' * (50 - progress)
    print(f'\r|{status}| {percent}%', end='')

# 请求用户输入YouTube视频的URL
url = input("请输入YouTube视频的URL（留空则跳过）: ")
video_title = ""

# 检查URL是否为空
if url:
    try:
        # 创建YouTube对象
        yt = YouTube(url, on_progress_callback=show_progress_bar)
        # 获取视频标题并清理
        video_title = clean_filename(yt.title)
        print(f"Video title : {video_title}")

        # 获取所有可用的解析度
        available_resolutions = get_resolution_streams(yt.streams.filter(progressive=True, file_extension='mp4'))
        
        # 显示解析度选项
        print("可用的解析度: ")
        for i, resolution in enumerate(available_resolutions, start=1):
            print(f"{i}. {resolution}")

        # 请求用户选择解析度
        choice = input("请选择解析度的编号（例如输入 '1' 选择第一个）: ")
        selected_resolution = available_resolutions[int(choice) - 1]

        # 选择指定解析度的视频流
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=selected_resolution).first()

        # 显示文件大小
        filesize = stream.filesize
        print(f"文件大小: {math.ceil(filesize / (1024 * 1024))} MB")


        # 下载视频
        print("正在下载视频，请稍候...")
        stream.download(filename="default.mp4")
        print("下载完成！")
    except Exception as e:
        print("下载失败：", e)
else:
    print("没有输入URL，跳过下载。")


# 執行 k0.py
if not run_script('moduel/k0.py'):
    exit(1)

print("*****開始解讀字幕*****")
# 執行 k1.py
if not run_script('moduel/k1.py'):
    exit(1)

with open(config.workingFile, 'r') as file:
    #selected_file = file.read()
    data = json.load(file)
    selected_file = data['file_name']

print("*****開始翻譯成中文*****")
# 執行 k2.py
if not run_script('moduel/k2.py'):
    exit(1)

print("*****轉換成字幕檔*****")
# 執行 k3.py
if not run_script('moduel/k3.py'):
    exit(1)

os.makedirs("output", exist_ok=True)
if video_title:
    output_path = os.path.join("output", video_title)
else:
    output_path = os.path.join("output", selected_file)

os.makedirs(output_path, exist_ok=True)
debug_path = os.path.join(output_path, "debug")
os.makedirs(debug_path, exist_ok=True)

#搬移其他中繼資料
if video_title:
    try:
        os.rename(selected_file, video_title+".mp4")
        os.rename(os.path.splitext(selected_file)[0]+'.cht.srt', video_title+".cht.srt")
    except FileNotFoundError:
        print(f"文件 {original_filename} 不存在。")
    except OSError as e:
        print(f"發生錯誤：{e}")

    shutil.move(video_title+".mp4", output_path)
    shutil.move(video_title+'.cht.srt', output_path)
else:
    shutil.move(selected_file, output_path)
    shutil.move(os.path.splitext(selected_file)[0]+'.cht.srt', output_path)

shutil.move(config.AIPunctuationLog, debug_path)
shutil.move(config.AIPunctuationFile, debug_path)
shutil.move(config.workingFile, debug_path)
shutil.move(config.AITranslationFile, debug_path)
shutil.move(config.AITranslationLog, debug_path)
shutil.move(config.whisperFile, debug_path)

print(f"字幕轉換處理完成")