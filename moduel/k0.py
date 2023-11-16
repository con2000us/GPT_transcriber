import os
import subprocess
import sys

def scan_files(directory):
    # 支持的檔案格式
    video_extensions = ['.mp4', '.avi', '.mov', 'mkv']
    audio_extensions = ['.mp3', '.wav', '.aac', 'm4a']

    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    media_files = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions + audio_extensions]

    return media_files

def main():
    directory = '.'  # 當前目錄
    media_files = scan_files(directory)
    selected_file = '';

    # 检查是否存在 default.mp4
    if 'default.mp4' in media_files:
        selected_file = 'default.mp4'

        with open('process.txt', 'w') as file:
            file.write(selected_file)
    if not media_files:
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

                with open('process.txt', 'w') as file:
                    file.write(selected_file)
            except (IndexError, ValueError):
                print("無效的選擇。")
                return

    # 執行shell命令
    try:
        subprocess.run(["python", "-m", "whisper", selected_file, "--model", "large"], check=True)
        # 构建.vtt文件的路径
        base_name = os.path.splitext(selected_file)[0]
        vtt_file = base_name + '.vtt'
        # 重命名.vtt文件
        os.rename(vtt_file, 'v.vtt')
    except subprocess.CalledProcessError as e:
        print(f"执行错误: {e}")
    except OSError as e:
        print(f"文件重命名失败: {e}")

if __name__ == "__main__":
    main()
