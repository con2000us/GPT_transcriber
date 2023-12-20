# config_reader.py
import configparser

import configparser

whisperModelOpt = ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large']
AImodelOpt = ['gpt-3.5-turbo','gpt-3.5-turbo-1106','gpt-4','gpt-4-1106-preview']

def str_to_bool(s):
    return s.lower() in ['true', '1', 't', 'y', 'yes', 'True', 'TRUE'] 

class Config:
    def __init__(self):
        self.whisper_model = None
        self.lng_detct_model = None
        self.split_line_model = None
        self.ai_model = None
        self.forced_time_stamp = None
        self.max_req_time = None
        self.lineArrange = None

def load_config(file_path):
    config_parser = configparser.ConfigParser()
    with open(file_path, 'r', encoding='utf-8') as file:
        config_parser.read_string('[SETTING]\n' + file.read())

    config = Config()
    config.whisperModel = whisperModelOpt[config_parser.getint('SETTING', 'WhisperModel')]
    config.lngDetctModel = whisperModelOpt[config_parser.getint('SETTING', 'LngDetctModel')]
    config.lineArrange = config_parser.getboolean('SETTING', 'LineArrangeEnable')
    config.splitLineModel = AImodelOpt[config_parser.getint('SETTING', 'SplitLineModel')]
    config.AIModel = AImodelOpt[config_parser.getint('SETTING', 'AImodel')]
    config.forceMatch = config_parser.getboolean('SETTING', 'ForcedTimeStamp')
    config.maxReqTime = config_parser.getint('SETTING', 'MaxReqTime')

    return config

# 這會讀取配置並保存在一個全域變數中
config = load_config('moduel/config.txt')

# 加載配置檔案
config = load_config('moduel/config.txt')

