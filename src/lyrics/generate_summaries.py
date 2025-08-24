#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌词摘要生成命令行工具
批量处理歌词文件并生成CSV格式的摘要

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import argparse
import os
import sys
import logging
from typing import List, Tuple
from .summary_generator import SummaryGenerator, LyricFormat

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_input_file(input_file: str) -> List[Tuple[str, str, str, LyricFormat]]:
    """解析输入文件，返回歌词文件信息列表"""
    lyric_files = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 格式: 文件路径,歌曲ID,歌曲名称,格式类型
                parts = line.split(',')
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    song_id = parts[1].strip()
                    song_name = parts[2].strip()
                    format_str = parts[3].strip().lower()
                    
                    # 确定格式类型
                    if format_str == 'lrc':
                        format_type = LyricFormat.LRC
                    elif format_str == 'krc':
                        format_type = LyricFormat.KRC
                    elif format_str == 'custom':
                        format_type = LyricFormat.CUSTOM
                    else:
                        logger.warning(f"第{line_num}行格式类型未知: {format_str}")
                        continue
                    
                    lyric_files.append((file_path, song_id, song_name, format_type))
                else:
                    logger.warning(f"第{line_num}行格式错误: {line}")
    
    except Exception as e:
        logger.error(f"解析输入文件失败: {e}")
    
    return lyric_files


def scan_directory(directory: str) -> List[Tuple[str, str, str, LyricFormat]]:
    """扫描目录，自动识别歌词文件"""
    lyric_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 根据文件扩展名确定格式
                if file.endswith('.lrc'):
                    format_type = LyricFormat.LRC
                elif file.endswith('.krc'):
                    format_type = LyricFormat.KRC
                elif file.endswith('.txt'):
                    format_type = LyricFormat.CUSTOM
                else:
                    continue
                
                # 生成歌曲ID和名称
                song_id = f"song_{len(lyric_files) + 1:03d}"
                song_name = os.path.splitext(file)[0]
                
                lyric_files.append((file_path, song_id, song_name, format_type))
    
    except Exception as e:
        logger.error(f"扫描目录失败: {e}")
    
    return lyric_files


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='歌词摘要生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用输入文件
  python generate_summaries.py --input songs.txt --output summaries.csv
  
  # 扫描目录
  python generate_summaries.py --dir songs/ --output summaries.csv
  
  # 处理单个文件
  python generate_summaries.py --file song.lrc --id song_001 --name "歌曲名" --output summary.csv
        """
    )
    
    # 输入方式
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', '-i', 
                           help='输入文件路径，包含歌词文件信息')
    input_group.add_argument('--dir', '-d', 
                           help='扫描目录路径，自动识别歌词文件')
    input_group.add_argument('--file', '-f', 
                           help='单个歌词文件路径')
    
    # 输出参数
    parser.add_argument('--output', '-o', required=True,
                       help='输出CSV文件路径')
    
    # 单个文件参数
    parser.add_argument('--id', 
                       help='歌曲ID（仅用于单个文件）')
    parser.add_argument('--name', 
                       help='歌曲名称（仅用于单个文件）')
    parser.add_argument('--format', choices=['lrc', 'krc', 'custom'],
                       default='lrc', help='文件格式（仅用于单个文件）')
    
    # 日志参数
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # 创建摘要生成器
    generator = SummaryGenerator()
    
    # 处理输入
    if args.file:
        # 处理单个文件
        if not args.id or not args.name:
            logger.error("处理单个文件时必须指定 --id 和 --name 参数")
            sys.exit(1)
        
        # 确定格式类型
        format_map = {
            'lrc': LyricFormat.LRC,
            'krc': LyricFormat.KRC,
            'custom': LyricFormat.CUSTOM
        }
        format_type = format_map[args.format]
        
        lyric_files = [(args.file, args.id, args.name, format_type)]
        
    elif args.input:
        # 使用输入文件
        lyric_files = parse_input_file(args.input)
        
    elif args.dir:
        # 扫描目录
        lyric_files = scan_directory(args.dir)
    
    else:
        logger.error("必须指定输入方式")
        sys.exit(1)
    
    if not lyric_files:
        logger.error("没有找到有效的歌词文件")
        sys.exit(1)
    
    # 生成CSV文件
    generator.generate_csv(lyric_files, args.output)
    
    print(f"处理完成！共处理 {len(lyric_files)} 首歌曲")
    print(f"结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
