#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量分享词生成工具
批量处理多个歌词文件，为每首歌生成一句最经典的分享词

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import argparse
import os
import sys
import csv
import logging
from typing import List, Dict, Tuple
from .chorus_extractor import ChorusExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_songs_list(input_file: str) -> List[Tuple[str, str, str]]:
    """解析歌曲列表文件"""
    songs = []
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 格式: 文件路径,歌曲ID,歌曲名称
                parts = line.split(',')
                if len(parts) >= 3:
                    file_path = parts[0].strip()
                    song_id = parts[1].strip()
                    song_name = parts[2].strip()
                    songs.append((file_path, song_id, song_name))
                else:
                    logger.warning(f"第{line_num}行格式错误: {line}")
    
    except Exception as e:
        logger.error(f"解析歌曲列表文件失败: {e}")
    
    return songs


def scan_directory(directory: str) -> List[Tuple[str, str, str]]:
    """扫描目录，自动识别歌词文件"""
    songs = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                
                # 根据文件扩展名确定是否为歌词文件
                if file.endswith(('.txt', '.lrc', '.krc')):
                    # 生成歌曲ID和名称
                    song_id = f"song_{len(songs) + 1:03d}"
                    song_name = os.path.splitext(file)[0]
                    songs.append((file_path, song_id, song_name))
    
    except Exception as e:
        logger.error(f"扫描目录失败: {e}")
    
    return songs


def generate_share_quotes(songs: List[Tuple[str, str, str]], output_file: str):
    """批量生成分享词并保存到CSV"""
    results = []
    extractor = ChorusExtractor()
    
    for file_path, song_id, song_name in songs:
        logger.info(f"处理文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不存在: {file_path}")
            results.append({
                'id': song_id,
                'song_name': song_name,
                'share_quote': '文件不存在',
                'status': 'error'
            })
            continue
        
        try:
            # 生成分享词
            share_quote = extractor.process_share_quote(file_path)
            
            if share_quote:
                results.append({
                    'id': song_id,
                    'song_name': song_name,
                    'share_quote': share_quote,
                    'status': 'success'
                })
                logger.info(f"成功生成分享词: {song_name} -> {share_quote}")
            else:
                results.append({
                    'id': song_id,
                    'song_name': song_name,
                    'share_quote': '未能生成合适的分享词',
                    'status': 'failed'
                })
                logger.warning(f"未能生成分享词: {song_name}")
        
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {e}")
            results.append({
                'id': song_id,
                'song_name': song_name,
                'share_quote': f'处理失败: {str(e)}',
                'status': 'error'
            })
    
    # 写入CSV文件
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'song_name', 'share_quote', 'status'])
            writer.writeheader()
            writer.writerows(results)
        
        # 统计结果
        success_count = sum(1 for r in results if r['status'] == 'success')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        error_count = sum(1 for r in results if r['status'] == 'error')
        
        logger.info(f"CSV文件生成成功: {output_file}")
        logger.info(f"处理结果: 成功 {success_count} 首, 失败 {failed_count} 首, 错误 {error_count} 首")
        
        return results
        
    except Exception as e:
        logger.error(f"生成CSV文件失败: {e}")
        return []


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量生成歌曲分享词',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用歌曲列表文件批量处理
  python -m src.lyrics.batch_share_quotes --input songs.txt --output share_quotes.csv
  
  # 扫描目录自动处理
  python -m src.lyrics.batch_share_quotes --dir songs/ --output share_quotes.csv
  
  # 显示详细输出
  python -m src.lyrics.batch_share_quotes --input songs.txt --output share_quotes.csv --verbose
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--input', '-i',
        help='歌曲列表文件路径'
    )
    
    group.add_argument(
        '--dir', '-d',
        help='扫描目录路径'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='输出CSV文件路径'
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
    
    try:
        # 获取歌曲列表
        if args.input:
            if not os.path.exists(args.input):
                logger.error(f"输入文件不存在: {args.input}")
                sys.exit(1)
            songs = parse_songs_list(args.input)
            logger.info(f"从文件读取到 {len(songs)} 首歌曲")
        else:
            if not os.path.exists(args.dir):
                logger.error(f"目录不存在: {args.dir}")
                sys.exit(1)
            songs = scan_directory(args.dir)
            logger.info(f"从目录扫描到 {len(songs)} 首歌曲")
        
        if not songs:
            logger.error("未找到任何歌曲文件")
            sys.exit(1)
        
        # 批量生成分享词
        results = generate_share_quotes(songs, args.output)
        
        if results:
            # 显示成功的结果
            success_results = [r for r in results if r['status'] == 'success']
            if success_results:
                print(f"\n🎵 成功生成的分享词:")
                for result in success_results:
                    print(f"📝 {result['song_name']}: {result['share_quote']}")
            
            print(f"\n✨ 批量处理完成！共处理 {len(songs)} 首歌曲")
            print(f"📁 结果已保存到: {args.output}")
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
