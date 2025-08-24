#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌词摘要生成使用示例

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from lyrics.summary_generator import SummaryGenerator, LyricFormat


def create_sample_lrc():
    """创建示例LRC文件"""
    lrc_content = """[ti:朋友]
[ar:周华健]
[al:朋友]
[by:歌词生成器]

[00:00.00]朋友 - 周华健
[00:03.00]作词：刘思铭
[00:06.00]作曲：刘志宏
[00:09.00]

[00:12.00]这些年 一个人
[00:15.00]风也过 雨也走
[00:18.00]有过泪 有过错
[00:21.00]还记得坚持什么

[00:24.00]真爱过 才会懂
[00:27.00]会寂寞 会回首
[00:30.00]终有梦 终有你 在心中

[00:33.00]朋友 一生一起走
[00:36.00]那些日子 不再有
[00:39.00]一句话 一辈子
[00:42.00]一生情 一杯酒

[00:45.00]朋友 不曾孤单过
[00:48.00]一声朋友 你会懂
[00:51.00]还有伤 还有痛
[00:54.00]还要走 还有我

[00:57.00]这些年 一个人
[01:00.00]风也过 雨也走
[01:03.00]有过泪 有过错
[01:06.00]还记得坚持什么

[01:09.00]真爱过 才会懂
[01:12.00]会寂寞 会回首
[01:15.00]终有梦 终有你 在心中

[01:18.00]朋友 一生一起走
[01:21.00]那些日子 不再有
[01:24.00]一句话 一辈子
[01:27.00]一生情 一杯酒

[01:30.00]朋友 不曾孤单过
[01:33.00]一声朋友 你会懂
[01:36.00]还有伤 还有痛
[01:39.00]还要走 还有我

[01:42.00]朋友 一生一起走
[01:45.00]那些日子 不再有
[01:48.00]一句话 一辈子
[01:51.00]一生情 一杯酒

[01:54.00]朋友 不曾孤单过
[01:57.00]一声朋友 你会懂
[02:00.00]还有伤 还有痛
[02:03.00]还要走 还有我
"""
    
    with open('sample_friend.lrc', 'w', encoding='utf-8') as f:
        f.write(lrc_content)
    
    print("创建示例LRC文件: sample_friend.lrc")


def create_sample_input_file():
    """创建示例输入文件"""
    input_content = """# 歌词文件列表
# 格式: id,歌名,文件路径,格式
song_001,朋友,sample_friend.lrc,lrc
song_002,月亮代表我的心,sample_moon.lrc,lrc
song_003,青花瓷,sample_blue.lrc,lrc
"""
    
    with open('songs_list.txt', 'w', encoding='utf-8') as f:
        f.write(input_content)
    
    print("创建示例输入文件: songs_list.txt")


def demo_single_file():
    """演示处理单个文件"""
    print("\n=== 演示：处理单个文件 ===")
    
    generator = SummaryGenerator()
    
    # 处理LRC文件
    summary = generator.process_lyric_file(
        file_path="sample_friend.lrc",
        song_id="song_001",
        song_name="朋友",
        format_type=LyricFormat.LRC
    )
    
    if summary:
        print(f"歌曲: 朋友")
        print(f"摘要: {summary}")
    else:
        print("处理失败")


def demo_batch_processing():
    """演示批量处理"""
    print("\n=== 演示：批量处理 ===")
    
    generator = SummaryGenerator()
    
    # 定义要处理的文件列表
    lyric_files = [
        ("sample_friend.lrc", "song_001", "朋友", LyricFormat.LRC),
        # 可以添加更多文件
    ]
    
    # 生成CSV
    generator.generate_csv(lyric_files, "summaries_demo.csv")
    
    print("批量处理完成，结果保存到: summaries_demo.csv")


def demo_different_formats():
    """演示不同格式的处理"""
    print("\n=== 演示：不同格式处理 ===")
    
    generator = SummaryGenerator()
    
    # 创建示例KRC文件（简化版）
    krc_content = """[0,3000]朋友 一生一起走
[3000,6000]那些日子 不再有
[6000,9000]一句话 一辈子
[9000,12000]一生情 一杯酒
"""
    
    with open('sample_friend.krc', 'w', encoding='utf-8') as f:
        f.write(krc_content)
    
    # 处理KRC文件
    summary = generator.process_lyric_file(
        file_path="sample_friend.krc",
        song_id="song_001",
        song_name="朋友",
        format_type=LyricFormat.KRC
    )
    
    if summary:
        print(f"KRC格式处理结果: {summary}")
    
    # 创建示例自定义格式文件
    custom_content = """# 自定义格式歌词文件
00:12 这些年 一个人
00:15 风也过 雨也走
00:18 有过泪 有过错
00:21 还记得坚持什么
00:33 朋友 一生一起走
00:36 那些日子 不再有
"""
    
    with open('sample_friend.txt', 'w', encoding='utf-8') as f:
        f.write(custom_content)
    
    # 处理自定义格式文件
    summary = generator.process_lyric_file(
        file_path="sample_friend.txt",
        song_id="song_001",
        song_name="朋友",
        format_type=LyricFormat.CUSTOM
    )
    
    if summary:
        print(f"自定义格式处理结果: {summary}")


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
    
    print("\n" + "=" * 50)
    print("示例运行完成！")
    print("\n生成的文件:")
    print("- sample_friend.lrc (示例LRC文件)")
    print("- songs_list.txt (示例输入文件)")
    print("- summaries_demo.csv (批量处理结果)")
    print("- sample_friend.krc (示例KRC文件)")
    print("- sample_friend.txt (示例自定义格式文件)")


if __name__ == "__main__":
    main()
