## input : adjusted_subtitles.json
## output : trans.json

from openai import OpenAI
import json
import time

# 在开始翻译之前清空 trans.json 文件
with open('trans.json', 'w', encoding='utf-8') as file:
    file.write('')

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

with open('adjusted_subtitles.json', 'r', encoding='utf-8') as file:
    subtitles = json.load(file)

# 初始化变量
sentences_per_batch = 20
total_sentences = len(subtitles)  # 获取实际的字幕数量
batches = (total_sentences + sentences_per_batch - 1) // sentences_per_batch  # 计算需要的批次数量
translated_subtitles = []  # 存储翻译后的字幕

# 循环处理每个批次
for batch in range(batches):
    start_index = batch * sentences_per_batch
    end_index = min(start_index + sentences_per_batch, total_sentences)  # 确保不超过字幕总数
    batch_subtitles = subtitles[start_index:end_index]

    # 构建消息内容，包括字幕文本
    subtitles_text = "\n".join([f"{subtitle['start']}##{subtitle['text']}" for subtitle in batch_subtitles])
    message_content = "本句之後的內容是一段英文內容 ##前面的數值不須更動 只將後面英文內容翻譯成繁體中文 並保持一句英文對應一句翻譯的中文關係. \n" + subtitles_text
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
                    # 顯示翻譯進度
                    text = content.text.value
                    text = text.replace('\\(', '(').replace('\\)', ')')
                    print(f"{text}")

                    translated_text = content.text.value
                    #translated_sentences = translated_text.split('\n')
                    translated_sentences = [line for line in translated_text.split('\n') if line.strip()]

                    # 确保翻译后的句子数量与原始字幕中的句子数量相同
                    # if len(translated_sentences) == len(batch_subtitles):
                    #     for i, subtitle in enumerate(batch_subtitles):
                    #         # 从翻译文本中移除时间戳
                    #         trans_text = translated_sentences[i].split('##')[1] if '##' in translated_sentences[i] else translated_sentences[i]
                    #         subtitle['trans'] = trans_text
                    #         translated_subtitles.append(subtitle)
                    # else:
                    #     print(f'ERROR : {len(batch_subtitles)} -> {len(translated_sentences)}')
                    #     print(f'Content : {translated_sentences}')
                    # break


                    for i, subtitle in enumerate(batch_subtitles):
                        # 从翻译文本中移除时间戳
                        if 0 <= i < len(translated_sentences):
                            trans_text = translated_sentences[i].split('##')[1] if '##' in translated_sentences[i] else translated_sentences[i]
                            subtitle['trans'] = trans_text
                            translated_subtitles.append(subtitle)
                    
                    break
            break

    # 将翻译后的字幕追加写入 JSON 文件
    with open('trans.json', 'a', encoding='utf-8') as file:
        if batch == 0:
            file.write('[')  # 文件开始
        else:
            file.write(',\n')  # 分隔不同批次的内容

        json.dump([subtitle for subtitle in translated_subtitles if 'trans' in subtitle], file, ensure_ascii=False, indent=4)

        if batch == batches - 1:
            file.write(']')  # 文件结束