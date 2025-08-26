#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量处理歌词文件夹，生成高潮分享词
从指定目录读取变形LRC格式文件，为每首歌生成一句最经典的分享词

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import os
import sys
import logging
from pathlib import Path
from .chorus_extractor import ChorusExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_chorus_folder(input_dir: str, output_dir: str):
    """批量处理歌词文件夹"""
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 创建高潮提取器
    extractor = ChorusExtractor()
    
    # 获取输入目录中的所有歌词文件
    input_path = Path(input_dir)
    lyric_files = []
    
    # 支持的歌词文件扩展名
    supported_extensions = {'.txt', '.lrc', '.krc'}
    
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            lyric_files.append(file_path)
    
    if not lyric_files:
        logger.warning(f"在目录 {input_dir} 中未找到歌词文件")
        return
    
    logger.info(f"找到 {len(lyric_files)} 个歌词文件")
    
    # 处理每个文件
    success_count = 0
    failed_count = 0
    
    for file_path in lyric_files:
        try:
            logger.info(f"处理文件: {file_path.name}")
            
            # 生成分享词
            share_quote = extractor.process_share_quote(str(file_path))
            
            if share_quote:
                # 创建输出文件路径（保持原文件名）
                output_file = output_path / file_path.name
                
                # 写入分享词到文件
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(share_quote)
                
                logger.info(f"成功生成分享词: {file_path.name} -> {share_quote}")
                success_count += 1
            else:
                logger.warning(f"未能生成分享词: {file_path.name}")
                failed_count += 1
                
        except Exception as e:
            logger.error(f"处理文件失败: {file_path.name}, 错误: {e}")
            failed_count += 1
    
    # 输出统计结果
    logger.info(f"处理完成！成功: {success_count} 个, 失败: {failed_count} 个")
    logger.info(f"分享词文件已保存到: {output_dir}")


def main():
    """主函数"""
    if len(sys.argv) != 3:
        print("使用方法: python process_chorus_folder.py <输入目录> <输出目录>")
        print("示例: python process_chorus_folder.py 'E:\\高潮\\txt20231031' 'E:\\高潮\\lines'")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        logger.error(f"输入目录不存在: {input_dir}")
        sys.exit(1)
    
    try:
        # 批量处理歌词文件夹
        process_chorus_folder(input_dir, output_dir)
        
        print(f"\n✨ 批量处理完成！")
        print(f"📁 输入目录: {input_dir}")
        print(f"📁 输出目录: {output_dir}")
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
