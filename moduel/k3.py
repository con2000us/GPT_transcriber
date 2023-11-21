## input : trans.json
## output : trans.srt

import json
import os
import shutil

def convert_to_srt(json_data):
    srt_format = ""
    for i, entry in enumerate(json_data, start=1):
        print(i)
        print(entry)
        start_time = format_time(entry['start'])
        end_time = format_time(entry['end'])
        text = entry['trans'].replace('\n', '\n')
        srt_format += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_format

def format_time(seconds):
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{milliseconds:03}"

# 读取 JSON 数据
with open('trans.json', 'r', encoding='utf-8') as file:
    subtitles = json.load(file)

# 处理嵌套的 JSON 结构
#flattened_subtitles = [item for sublist in subtitles for item in sublist]
#print(json.dumps(subtitles, ensure_ascii=False, indent=4))

with open('process.txt', 'r') as file:
    selected_file = file.read()

# 转换为 SRT 格式
srt_content = convert_to_srt(subtitles)

# 保存为 SRT 文件
with open(os.path.splitext(selected_file)[0]+'.cht.srt', 'w', encoding='utf-8') as file:
    file.write(srt_content)