#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高潮歌词提取命令行工具
专门处理变形LRC格式，提取高潮部分歌词或生成分享词

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import argparse
import os
import sys
import logging
from .chorus_extractor import ChorusExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='提取歌曲高潮部分歌词或生成分享词',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 提取高潮歌词
  python -m src.lyrics.extract_chorus --file song.txt --output chorus.txt
  
  # 生成分享词（一句最经典的歌词）
  python -m src.lyrics.extract_chorus --file song.txt --share-quote
  
  # 显示详细输出
  python -m src.lyrics.extract_chorus --file song.txt --verbose
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        required=True,
        help='变形LRC格式的歌词文件路径'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='输出文件路径（不指定则输出到控制台）'
    )
    
    parser.add_argument(
        '--share-quote', '-s',
        action='store_true',
        help='生成分享词（一句最经典的歌词）而不是提取所有高潮歌词'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示详细日志信息'
    )
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 检查输入文件
    if not os.path.exists(args.file):
        logger.error(f"输入文件不存在: {args.file}")
        sys.exit(1)
    
    try:
        # 创建高潮提取器
        extractor = ChorusExtractor()
        
        if args.share_quote:
            # 生成分享词
            logger.info(f"开始生成分享词: {args.file}")
            share_quote = extractor.process_share_quote(args.file)
            
            if not share_quote:
                logger.warning("未能生成合适的分享词")
                sys.exit(1)
            
            # 输出分享词
            if args.output:
                # 写入文件
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"# 歌曲分享词\n")
                    f.write(f"# 源文件: {args.file}\n")
                    f.write(f"# 生成时间: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n\n")
                    f.write(f"{share_quote}\n")
                
                logger.info(f"分享词已保存到: {args.output}")
                logger.info(f"分享词: {share_quote}")
                
            else:
                # 输出到控制台
                print(f"\n🎵 歌曲分享词")
                print(f"📁 源文件: {args.file}")
                print(f"💬 分享词: {share_quote}")
                print(f"\n✨ 生成完成！")
        
        else:
            # 提取高潮歌词
            logger.info(f"开始提取高潮歌词: {args.file}")
            chorus_lyrics = extractor.process_chorus_file(args.file)
            
            if not chorus_lyrics:
                logger.warning("未提取到高潮歌词")
                sys.exit(1)
            
            # 输出结果
            if args.output:
                # 写入文件
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"# 歌曲高潮歌词提取结果\n")
                    f.write(f"# 源文件: {args.file}\n")
                    f.write(f"# 提取时间: {logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))}\n\n")
                    
                    for i, lyric in enumerate(chorus_lyrics, 1):
                        f.write(f"{i}. {lyric}\n")
                
                logger.info(f"高潮歌词已保存到: {args.output}")
                logger.info(f"共提取 {len(chorus_lyrics)} 句高潮歌词")
                
            else:
                # 输出到控制台
                print(f"\n🎵 歌曲高潮歌词提取结果")
                print(f"📁 源文件: {args.file}")
                print(f"📊 共提取 {len(chorus_lyrics)} 句高潮歌词\n")
                
                for i, lyric in enumerate(chorus_lyrics, 1):
                    print(f"{i:2d}. {lyric}")
                
                print(f"\n✨ 提取完成！")
    
    except Exception as e:
        logger.error(f"处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
