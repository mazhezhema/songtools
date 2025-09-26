#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量URL歌词处理工具
从歌词路径.txt文件读取URL，下载歌词文件并生成摘要

作者: SongTools Team
创建时间: 2025-09-04
版本: 1.0.0
"""

import os
import csv
import logging
import argparse
from typing import List, Tuple, Optional
from .url_downloader import LyricDownloader
from .summary_generator import SummaryGenerator, LyricFormat

logger = logging.getLogger(__name__)


class BatchUrlProcessor:
    """批量URL歌词处理器"""
    
    def __init__(self, download_dir: str = "temp_lyrics", cleanup: bool = True):
        """
        初始化处理器
        
        Args:
            download_dir: 下载文件保存目录
            cleanup: 处理完成后是否清理临时文件
        """
        self.downloader = LyricDownloader(download_dir)
        self.summary_generator = SummaryGenerator()
        self.cleanup = cleanup
        
        logger.info("批量URL歌词处理器初始化完成")
    
    def parse_input_file(self, input_file: str) -> List[Tuple[str, str]]:
        """
        解析输入文件
        
        Args:
            input_file: 输入文件路径，每行格式为: 歌曲ID URL
            
        Returns:
            歌曲ID和URL的元组列表
        """
        url_list = []
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # 分割歌曲ID和URL（支持Tab和空格分隔）
                    if '\t' in line:
                        # 使用Tab分隔
                        parts = line.split('\t', 1)
                    else:
                        # 使用空格分隔
                        parts = line.split(' ', 1)
                    
                    if len(parts) >= 2:
                        song_id = parts[0].strip()
                        url = parts[1].strip()
                        url_list.append((song_id, url))
                    else:
                        logger.warning(f"第{line_num}行格式错误: {line}")
        
        except Exception as e:
            logger.error(f"解析输入文件失败: {e}")
        
        logger.info(f"解析到 {len(url_list)} 个URL")
        return url_list
    
    def detect_lyric_format(self, file_path: str) -> LyricFormat:
        """
        检测歌词文件格式
        
        Args:
            file_path: 文件路径
            
        Returns:
            歌词格式枚举
        """
        filename = os.path.basename(file_path).lower()
        
        if filename.endswith('.lrc'):
            return LyricFormat.LRC
        elif filename.endswith('.krc'):
            return LyricFormat.KRC
        else:
            return LyricFormat.CUSTOM
    
    def process_single_url(self, song_id: str, url: str) -> Optional[str]:
        """
        处理单个URL
        
        Args:
            song_id: 歌曲ID
            url: 歌词文件URL
            
        Returns:
            生成的摘要，失败返回None
        """
        try:
            # 下载文件
            file_path = self.downloader.download_lyric_file(url, song_id)
            if not file_path:
                logger.error(f"下载失败: {song_id} - {url}")
                return None
            
            # 检测格式
            format_type = self.detect_lyric_format(file_path)
            
            # 生成摘要
            summary = self.summary_generator.process_lyric_file(
                file_path=file_path,
                song_id=song_id,
                song_name=song_id,  # 使用ID作为歌曲名
                format_type=format_type
            )
            
            if summary:
                logger.info(f"处理成功: {song_id} -> {summary}")
                return summary
            else:
                logger.error(f"生成摘要失败: {song_id}")
                return None
                
        except Exception as e:
            logger.error(f"处理失败: {song_id} - {url}, 错误: {e}")
            return None
    
    def process_batch(self, input_file: str, output_file: str, delay: float = 1.0):
        """
        批量处理URL列表，每条结果立即追加到输出文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出CSV文件路径
            delay: 下载间隔时间（秒）
        """
        try:
            # 解析输入文件
            url_list = self.parse_input_file(input_file)
            if not url_list:
                logger.error("没有找到有效的URL")
                return
            
            # 初始化CSV文件（写入表头）
            self.initialize_csv_file(output_file)
            
            # 处理每个URL，立即追加结果
            success_count = 0
            for i, (song_id, url) in enumerate(url_list):
                logger.info(f"处理进度: {i+1}/{len(url_list)} - {song_id}")
                
                summary = self.process_single_url(song_id, url)
                if summary:
                    # 立即追加到CSV文件
                    self.append_result_to_csv(output_file, song_id, summary)
                    success_count += 1
                    logger.info(f"结果已追加到文件: {song_id} -> {summary}")
                else:
                    logger.warning(f"处理失败，跳过: {song_id}")
                
                # 添加延迟
                if i < len(url_list) - 1:
                    import time
                    time.sleep(delay)
            
            logger.info(f"批量处理完成: 成功处理 {success_count}/{len(url_list)} 个文件")
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
        finally:
            # 清理临时文件
            if self.cleanup:
                self.downloader.cleanup()
    
    def initialize_csv_file(self, output_file: str):
        """
        初始化CSV文件，写入表头
        
        Args:
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'summary'])
                writer.writeheader()
            
            logger.info(f"CSV文件已初始化: {output_file}")
            
        except Exception as e:
            logger.error(f"初始化CSV文件失败: {e}")
    
    def append_result_to_csv(self, output_file: str, song_id: str, summary: str):
        """
        将单个结果追加到CSV文件
        
        Args:
            output_file: 输出文件路径
            song_id: 歌曲ID
            summary: 摘要内容
        """
        try:
            with open(output_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'summary'])
                writer.writerow({
                    'id': song_id,
                    'summary': summary
                })
            
        except Exception as e:
            logger.error(f"追加结果到CSV文件失败: {e}")
    
    def write_results_to_csv(self, results: List[dict], output_file: str):
        """
        将结果列表写入CSV文件（保留此方法以兼容其他用途）
        
        Args:
            results: 结果列表
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'summary'])
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"结果已保存到: {output_file}")
            
        except Exception as e:
            logger.error(f"保存CSV文件失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='批量URL歌词处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 处理歌词路径.txt文件
  python batch_url_processor.py --input E:\\lrc\\歌词路径.txt --output results.csv
  
  # 设置下载间隔和临时目录
  python batch_url_processor.py --input lyrics.txt --output results.csv --delay 2 --temp-dir temp
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='输入文件路径，每行格式: 歌曲ID URL')
    parser.add_argument('--output', '-o', required=True,
                       help='输出CSV文件路径')
    parser.add_argument('--delay', '-d', type=float, default=1.0,
                       help='下载间隔时间（秒），默认1秒')
    parser.add_argument('--temp-dir', '-t', default='temp_lyrics',
                       help='临时文件目录，默认temp_lyrics')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='不清理临时文件')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    
    # 创建处理器
    processor = BatchUrlProcessor(
        download_dir=args.temp_dir,
        cleanup=not args.no_cleanup
    )
    
    # 开始处理
    processor.process_batch(args.input, args.output, args.delay)


if __name__ == "__main__":
    main()
