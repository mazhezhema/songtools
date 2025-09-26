#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌词文件URL下载器
从URL下载歌词文件并保存到本地

作者: SongTools Team
创建时间: 2025-09-04
版本: 1.0.0
"""

import os
import requests
import logging
from typing import Optional
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)


class LyricDownloader:
    """歌词文件下载器"""
    
    def __init__(self, download_dir: str = "temp_lyrics", timeout: int = 30):
        """
        初始化下载器
        
        Args:
            download_dir: 下载文件保存目录
            timeout: 下载超时时间（秒）
        """
        self.download_dir = download_dir
        self.timeout = timeout
        
        # 创建下载目录
        os.makedirs(download_dir, exist_ok=True)
        
        # 设置请求头，模拟浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logger.info(f"歌词下载器初始化完成，下载目录: {download_dir}")
    
    def download_lyric_file(self, url: str, song_id: str) -> Optional[str]:
        """
        从URL下载歌词文件或复制本地文件
        
        Args:
            url: 歌词文件URL或本地文件路径
            song_id: 歌曲ID，用于生成文件名
            
        Returns:
            下载成功的文件路径，失败返回None
        """
        try:
            logger.info(f"开始处理: {url}")
            
            # 检查是否为本地文件路径
            if os.path.exists(url) and os.path.isfile(url):
                return self._copy_local_file(url, song_id)
            else:
                return self._download_from_url(url, song_id)
            
        except Exception as e:
            logger.error(f"处理失败: {url}, 错误: {e}")
            return None
    
    def _copy_local_file(self, file_path: str, song_id: str) -> Optional[str]:
        """复制本地文件到下载目录"""
        try:
            # 确定文件扩展名
            file_extension = os.path.splitext(file_path)[1]
            if not file_extension:
                file_extension = '.txt'
            
            # 生成目标文件名
            filename = f"{song_id}{file_extension}"
            target_path = os.path.join(self.download_dir, filename)
            
            # 复制文件
            import shutil
            shutil.copy2(file_path, target_path)
            
            logger.info(f"复制成功: {file_path} -> {target_path}")
            return target_path
            
        except Exception as e:
            logger.error(f"复制文件失败: {file_path}, 错误: {e}")
            return None
    
    def _download_from_url(self, url: str, song_id: str) -> Optional[str]:
        """从URL下载文件"""
        try:
            # 发送请求
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # 确定文件扩展名
            parsed_url = urlparse(url)
            file_extension = os.path.splitext(parsed_url.path)[1]
            
            # 如果没有扩展名，尝试从Content-Type推断
            if not file_extension:
                content_type = response.headers.get('content-type', '').lower()
                if 'lrc' in content_type:
                    file_extension = '.lrc'
                elif 'krc' in content_type:
                    file_extension = '.krc'
                elif 'text' in content_type:
                    file_extension = '.txt'
                else:
                    file_extension = '.txt'  # 默认使用txt
            
            # 生成文件名
            filename = f"{song_id}{file_extension}"
            file_path = os.path.join(self.download_dir, filename)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"下载成功: {file_path}")
            return file_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"下载失败: {url}, 错误: {e}")
            return None
        except Exception as e:
            logger.error(f"保存文件失败: {url}, 错误: {e}")
            return None
    
    def download_multiple_files(self, url_list: list, delay: float = 1.0) -> dict:
        """
        批量下载多个文件
        
        Args:
            url_list: URL列表，每个元素为(song_id, url)元组
            delay: 下载间隔时间（秒），避免请求过于频繁
            
        Returns:
            下载结果字典，key为song_id，value为文件路径或None
        """
        results = {}
        
        for i, (song_id, url) in enumerate(url_list):
            logger.info(f"下载进度: {i+1}/{len(url_list)} - {song_id}")
            
            file_path = self.download_lyric_file(url, song_id)
            results[song_id] = file_path
            
            # 添加延迟，避免请求过于频繁
            if i < len(url_list) - 1:  # 最后一个不需要延迟
                time.sleep(delay)
        
        success_count = sum(1 for path in results.values() if path is not None)
        logger.info(f"批量下载完成: 成功 {success_count}/{len(url_list)} 个文件")
        
        return results
    
    def cleanup(self):
        """清理下载的临时文件"""
        try:
            if os.path.exists(self.download_dir):
                for filename in os.listdir(self.download_dir):
                    file_path = os.path.join(self.download_dir, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                logger.info(f"清理临时文件完成: {self.download_dir}")
        except Exception as e:
            logger.error(f"清理临时文件失败: {e}")


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 创建下载器
    downloader = LyricDownloader()
    
    # 测试下载
    test_url = "https://example.com/song.lrc"
    test_id = "test_001"
    
    file_path = downloader.download_lyric_file(test_url, test_id)
    if file_path:
        print(f"下载成功: {file_path}")
    else:
        print("下载失败")
