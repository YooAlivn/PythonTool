import os
import subprocess

import torch
import whisper
from deep_translator import MyMemoryTranslator, ChatGptTranslator,BaiduTranslator,DeeplTranslator
from datetime import timedelta

VIDEO_MAIN = r"E:\yutobe\2026-03"


def extract_audio_from_video(video_path, audio_output_path=os.path.join(VIDEO_MAIN, "temp_audio.mp3")):
    """用ffmpeg提取音频（替代moviepy）"""
    try:
        # ffmpeg命令：-i 输入视频 -vn 只提取音频 -y 覆盖已有文件
        cmd = f'ffmpeg -i "{video_path}" -vn -acodec mp3 -y "{audio_output_path}"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"音频提取完成，保存至：{audio_output_path}")
        return audio_output_path
    except subprocess.CalledProcessError as e:
        print(f"音频提取失败（ffmpeg错误）：{e}")
        return None
    except Exception as e:
        print(f"音频提取失败：{e}")
        return None


def format_timestamp(seconds):
    """将秒数转换为SRT字幕的时间格式（00:00:00,000）"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    ms = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def speech_to_text(audio_path, model_size="large"):
    """用whisper将音频转文字，返回带时间戳的文本列表"""
    # 加载whisper模型（base模型轻量，适合新手；large模型更精准但慢）
    # Automatically select device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model = whisper.load_model(name="large-v3", download_root=r"C:\Z_SOFTWARE\Whisper", device=device)
    # 识别音频，输出带时间戳的segments
    result = model.transcribe(audio_path, verbose=False)
    segments = result["segments"]  # 每个segment包含start/end/text

    # 清理识别的文本（去除多余空格）
    clean_segments = []
    for seg in segments:
        clean_segments.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"].strip()
        })
    print(f"语音识别完成，共识别{len(clean_segments)}段文字")
    return clean_segments


def translate_text(text, target_lang="zh-CN"):
    api_id = 'X'
    api_key = 'X'
    """翻译文字（默认翻译成中文）"""
    if not text:
        return ""
    try:
        translator = BaiduTranslator(source="auto", target=target_lang, appid=api_id, secret_key=api_key)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"翻译失败（{text}）：{e}")
        return text  # 翻译失败则返回原文


def generate_srt(segments, srt_path=os.path.join(VIDEO_MAIN, "output_subtitle.srt")):
    """生成SRT字幕文件（包含原文+翻译）"""
    with open(srt_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, 1):
            # 转换时间戳格式
            start_time = format_timestamp(seg["start"])
            end_time = format_timestamp(seg["end"])

            # 翻译文本
            original_text = seg["text"]
            translated_text = translate_text(original_text)

            # 写入SRT格式（序号 → 时间范围 → 字幕内容）
            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{original_text}\n")
            f.write(f"{translated_text}\n\n")
    print(f"字幕文件生成完成：{srt_path}")
    return srt_path


def video_to_translated_subtitle(video_path, srt_output=os.path.join(VIDEO_MAIN, "translated_subtitle.srt")):
    """主函数：视频→音频→识别→翻译→字幕"""
    # 1. 提取音频
    audio_path = extract_audio_from_video(video_path)
    if not audio_path:
        return

    # 2. 语音转文字（带时间戳）
    segments = speech_to_text(audio_path)
    if not segments:
        return

    # 3. 生成翻译后的字幕文件
    generate_srt(segments, srt_output)

    # 清理临时音频文件
    if os.path.exists(audio_path):
        os.remove(audio_path)
    print("全部流程完成！")


# ------------------- 执行示例 -------------------
if __name__ == "__main__":
    # 替换成你的视频文件路径（支持MP4、AVI、MKV等常见格式）
    VIDEO_FILE = os.path.join(VIDEO_MAIN, "input.mp4")
    # 生成的字幕文件路径
    SRT_FILE = os.path.join(VIDEO_MAIN, "translated_subtitle.srt")

    # 运行主函数
    video_to_translated_subtitle(VIDEO_FILE, SRT_FILE)
