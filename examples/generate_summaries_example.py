#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌词摘要生成器使用示例
演示如何使用摘要生成器处理不同格式的歌词文件

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from lyrics.summary_generator import SummaryGenerator, LyricFormat, LyricLine


def create_sample_lrc():
    """创建示例LRC文件"""
    lrc_content = """[ti:朋友]
[ar:周华健]
[al:朋友]
[by:歌词编辑]
[00:00.00]朋友 - 周华健
[00:02.00]词：刘思铭
[00:04.00]曲：刘志宏
[00:06.00]
[00:08.00]这些年 一个人
[00:12.00]风也过 雨也走
[00:16.00]有过泪 有过错
[00:20.00]还记得坚持什么
[00:24.00]
[00:28.00]真爱过 才会懂
[00:32.00]会寂寞 会回首
[00:36.00]终有梦 终有你 在心中
[00:40.00]
[00:44.00]朋友 一生一起走
[00:48.00]那些日子 不再有
[00:52.00]一句话 一辈子
[00:56.00]一生情 一杯酒
[01:00.00]
[01:04.00]朋友 不曾孤单过
[01:08.00]一声朋友 你会懂
[01:12.00]还有伤 还有痛
[01:16.00]还要走 还有我
[01:20.00]
[01:24.00]朋友 一生一起走
[01:28.00]那些日子 不再有
[01:32.00]一句话 一辈子
[01:36.00]一生情 一杯酒
[01:40.00]
[01:44.00]朋友 不曾孤单过
[01:48.00]一声朋友 你会懂
[01:52.00]还有伤 还有痛
[01:56.00]还要走 还有我
"""
    
    with open('sample_friend.lrc', 'w', encoding='utf-8') as f:
        f.write(lrc_content)
    print("创建示例LRC文件: sample_friend.lrc")


def create_sample_input_file():
    """创建示例输入文件"""
    input_content = """sample_friend.lrc,song_001,朋友,lrc
sample_moon.lrc,song_002,月亮代表我的心,lrc
sample_blue_porcelain.lrc,song_003,青花瓷,lrc"""
    
    with open('songs_list.txt', 'w', encoding='utf-8') as f:
        f.write(input_content)
    print("创建示例输入文件: songs_list.txt")


def demo_single_file():
    """演示单个文件处理"""
    print("\n=== 单个文件处理演示 ===")
    
    generator = SummaryGenerator()
    
    # 处理LRC文件
    share_quote = generator.process_lyric_file(
        file_path="sample_friend.lrc",
        song_id="song_001",
        song_name="朋友",
        format_type=LyricFormat.LRC
    )
    
    if share_quote:
        print(f"歌曲: 朋友")
        print(f"分享歌词: {share_quote}")
    else:
        print("处理失败")


def demo_batch_processing():
    """演示批量处理"""
    print("\n=== 批量处理演示 ===")
    
    generator = SummaryGenerator()
    
    # 定义要处理的文件列表
    lyric_files = [
        ("sample_friend.lrc", "song_001", "朋友", LyricFormat.LRC),
        ("sample_moon.lrc", "song_002", "月亮代表我的心", LyricFormat.LRC),
        ("sample_blue_porcelain.lrc", "song_003", "青花瓷", LyricFormat.LRC),
    ]
    
    # 生成CSV文件
    generator.generate_csv(lyric_files, "batch_summaries.csv")
    print("批量处理完成，结果保存到: batch_summaries.csv")


def demo_different_formats():
    """演示不同格式处理"""
    print("\n=== 不同格式处理演示 ===")
    
    generator = SummaryGenerator()
    
    # 创建示例KRC文件
    krc_content = """[0,4000]朋友 一生一起走
[4000,8000]那些日子 不再有
[8000,12000]一句话 一辈子
[12000,16000]一生情 一杯酒"""
    
    with open('sample_friend.krc', 'w', encoding='utf-8') as f:
        f.write(krc_content)
    
    # 创建示例自定义格式文件
    custom_content = """# 朋友 - 周华健
00:08 这些年 一个人
00:12 风也过 雨也走
00:16 有过泪 有过错
00:20 还记得坚持什么
00:28 真爱过 才会懂
00:32 会寂寞 会回首
00:36 终有梦 终有你 在心中"""
    
    with open('sample_friend.txt', 'w', encoding='utf-8') as f:
        f.write(custom_content)
    
    # 处理不同格式
    formats = [
        ("sample_friend.lrc", LyricFormat.LRC, "LRC格式"),
        ("sample_friend.krc", LyricFormat.KRC, "KRC格式"),
        ("sample_friend.txt", LyricFormat.CUSTOM, "自定义格式"),
    ]
    
    for file_path, format_type, format_name in formats:
        if os.path.exists(file_path):
            share_quote = generator.process_lyric_file(
                file_path=file_path,
                song_id="demo_song",
                song_name="朋友",
                format_type=format_type
            )
            
            if share_quote:
                print(f"{format_name}: {share_quote}")
            else:
                print(f"{format_name}: 处理失败")


def demo_analysis_features():
    """演示分析功能"""
    print("\n=== 分析功能演示 ===")
    
    generator = SummaryGenerator()
    
    # 测试不同类型的歌词
    test_lyrics = [
        "朋友一生一起走，那些日子不再有",  # 哲理深刻
        "月亮代表我的心",  # 意象丰富
        "啊啊啊，哦哦哦",  # 重复词汇
        "爱你在心口难开",  # 情感深度
        "青春岁月如歌",  # 时间表达
    ]
    
    for lyric in test_lyrics:
        is_shareable = generator.is_shareable_quote(lyric)
        score = generator.calculate_classic_score(lyric)
        print(f"歌词: {lyric}")
        print(f"  适合分享: {is_shareable}")
        print(f"  经典分数: {score:.2f}")
        print()


def main():
    """主函数"""
    print("歌词摘要生成器使用示例")
    print("=" * 50)
    
    # 创建示例文件
    create_sample_lrc()
    create_sample_input_file()
    
    # 演示各种功能
    demo_single_file()
    demo_batch_processing()
    demo_different_formats()
    demo_analysis_features()
    
    print("示例运行完成！")
    print("\n生成的文件:")
    print("- sample_friend.lrc: 示例LRC文件")
    print("- songs_list.txt: 示例输入文件")
    print("- batch_summaries.csv: 批量处理结果")


if __name__ == "__main__":
    main()
