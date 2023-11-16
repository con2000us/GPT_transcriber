## input : v.vtt
## output : adjusted_subtitles.json

from openai import OpenAI
import re
import json
import time

inputfile = "v.vtt"

def time_to_seconds(time_str):
    """将时间字符串转换为秒"""
    minutes, seconds = map(float, time_str.split(':'))
    return minutes * 60 + seconds

def parse_srt(file_content):
    """解析 SRT 文件内容"""
    pattern = re.compile(r'(\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}\.\d{3})\n(.*?)\n\n', re.DOTALL)
    subtitles = []

    for match in pattern.finditer(file_content):
        start_str, end_str, text = match.groups()
        start = time_to_seconds(start_str)
        end = time_to_seconds(end_str)
        subtitles.append({
            "id": len(subtitles) + 1,
            "start": start,
            "end": end,
            "text": text.replace('\n', ' ')
        })

    return subtitles

def read_srt_file(filename):
    """从文件中读取 SRT 内容"""
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# 读取字幕文件
srt_content = read_srt_file(inputfile)

# 解析字幕文件
subtitles = parse_srt(srt_content)

# 将结果以 JSON 格式输出到屏幕
#print(json.dumps(subtitles, ensure_ascii=False, indent=4))


def check_subtitles(subtitles):
    # 新数组，用于存储连续的不符合条件的字幕对象
    continuous_subtitles = []
    # 用于计数连续不符合条件的字幕对象数量
    count = 0

    for subtitle in subtitles:
        text = subtitle['text']
        # 检查字幕文本是否不符合条件
        if not (text.endswith('.') or text.endswith('!') or '. ' in text):
            count += 1
            # 当连续不符合条件的字幕达到4个时，开始复制
            if count >= 4:
                continuous_subtitles.append(subtitle)
        else:
            # 如果当前字幕符合条件，则重置计数器
            count = 0

    return continuous_subtitles

# 示例：应用函数并显示结果
problematic_subtitles = check_subtitles(subtitles)

##########################################要處理文句過長沒分段問題############################################### 
def group_array(arr):

    # 分组
    groups = []
    current_group = []

    for item in arr:
        if current_group and (item['id'] - current_group[-1]['id'] > 1 or len(current_group) >= 13):
            groups.append(current_group)
            current_group = [item]
        else:
            current_group.append(item)

    # 添加最后一组
    groups.append(current_group)

    # 确保最后一组至少有4个元素
    # if len(groups) > 1 and len(groups[-1]) < 4:
    #     while len(groups[-1]) < 4:
    #         groups[-1].insert(0, groups[-2].pop())

    return groups

grouped_objects = group_array(problematic_subtitles)
for group in grouped_objects:
    print([obj['id'] for obj in group])

###########################################讓AI處理文句分段問題####################################################
with open('moduel/key.txt', 'r') as file:
    key = file.read()
client = OpenAI(
    #api_key="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",
    api_key=key,
)

# 步骤 1: 创建一个助手
assistant = client.beta.assistants.create(
    name="John Doe",
    instructions="你是個英語翻譯，負責翻譯英文轉成文句通暢的中文",
    model="gpt-4-1106-preview"
)


def update_subtitles(subtitles, adj_sentences):
    for sentence in adj_sentences:
        # 分割每行以获取开始时间和文本
        if "##" in sentence:
            sid, new_text = sentence.split("##")
            iid = int(sid.strip())

            # 在subtitles中查找匹配的开始时间
            for subtitle in subtitles:
                if int(subtitle["id"]) == iid:
                    # 找到匹配项，更新text并保存旧的text
                    subtitle["text_old"] = subtitle["text"]
                    subtitle["text"] = new_text.strip()
                    break

adj_subtitles = []  # 存储斷句后的字幕

for group in grouped_objects:
    # 构建消息内容，包括字幕文本
    subtitles_text = "\n".join([f"{subtitle['id']}##{subtitle['text']}" for subtitle in group])
    message_content = "本句之後是一段英文內容 ##前面的數值不須更動 只將後面英文內容補上標點符號 讓句子盡量不超過20個單字.另外不要使用省略號 \n" + subtitles_text
    print(f"############################################################################################")
    print(f"{message_content}")
    print(f"--------------------------------------------------------------------------------------------")

    # 步骤 2: 创建一个线程
    thread = client.beta.threads.create()

    # 步骤 3: 向线程添加一条消息
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )

    # 步骤 4: 运行助手
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please address the user as Jane Doe. The user has a premium account."
    )

    # 检查运行状态
    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run.status == 'completed':
            break
        time.sleep(1)  # 等待一秒再次检查

    # 步骤 5: 显示助手的回应并处理翻译结果
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for message in messages.data:
        if message.role == "assistant":
            for content in message.content:
                if content.type == 'text':
                    # 顯示斷句內容
                    text = content.text.value
                    text = text.replace('\\(', '(').replace('\\)', ')')
                    
                    adj_text = content.text.value
                    #translated_sentences = translated_text.split('\n')
                    adj_sentences = [line for line in adj_text.split('\n') if line.strip()]

                    update_subtitles(subtitles, adj_sentences)


#################################################################################################################

def split_subtitle(subtitle):
    """根据句号分割字幕，并调整时间戳"""
    text = subtitle['text']
    start = subtitle['start']
    end = subtitle['end']

    # 检查文本是否包含句号
    if '. ' or '! ' in text:
        # 根据句号分割文本
        sentences = re.split(r'[.!?]\s', text)
        split_subtitles = []

        # 计算每个句子的时间戳
        total_length = len(text)
        current_start = start

        for i, sentence in enumerate(sentences):
            if i < len(sentences) - 1:  # 为除最后一个句子外的句子添加句号
                sentence += '.'

            sentence_length = len(sentence)
            proportion = sentence_length / total_length
            current_end = current_start + proportion * (end - start)

            # 创建新的字幕对象
            split_subtitles.append({
                "start": current_start,
                "end": current_end,
                "text": sentence.strip()
            })

            current_start = current_end

        return split_subtitles
    else:
        return [subtitle]

# 应用分割函数
split_subtitles = []
for subtitle in subtitles:
    split_subtitles.extend(split_subtitle(subtitle))

# 输出结果
# print(json.dumps(split_subtitles, ensure_ascii=False, indent=4))

def merge_subtitles(subtitles):
    merged_subtitles = []
    i = 0

    while i < len(subtitles):
        current_subtitle = subtitles[i]
        text = current_subtitle['text']
        start = current_subtitle['start']
        end = current_subtitle['end']

        # 合并直到找到以句号结尾的文本
        while not text.endswith(('.', '!', '?')) and i < len(subtitles) - 1:
            i += 1
            next_subtitle = subtitles[i]
            text += ' ' + next_subtitle['text']
            end = next_subtitle['end']

        # 添加合并后的字幕
        merged_subtitles.append({
            "start": start,
            "end": end,
            "text": text
        })
        i += 1

    return merged_subtitles

# 应用合并函数
merged_subtitles = merge_subtitles(split_subtitles)

# 输出结果
# print(json.dumps(merged_subtitles, ensure_ascii=False, indent=4))

def round_timestamps(subtitles):
    rounded_subtitles = []

    for subtitle in subtitles:
        rounded_start = round(subtitle['start'], 2)
        rounded_end = round(subtitle['end'], 2)
        rounded_subtitles.append({
            "start": rounded_start,
            "end": rounded_end,
            "text": subtitle['text']
        })

    return rounded_subtitles

# 应用四舍五入函数
rounded_subtitles = round_timestamps(merged_subtitles)

# 输出结果
print(json.dumps(rounded_subtitles, ensure_ascii=False, indent=4))

# 将处理后的字幕数据写入 JSON 文件
with open('adjusted_subtitles.json', 'w', encoding='utf-8') as json_file:
    json.dump(rounded_subtitles, json_file, ensure_ascii=False, indent=4)

print("字幕数据已保存到 adjusted_subtitles.json 文件中。")
