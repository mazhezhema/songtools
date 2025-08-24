#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌词摘要生成器
专门生成适合分享卡片的一句话经典歌词

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import csv
import re
import logging
from typing import List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class LyricFormat(Enum):
    """歌词格式枚举"""
    LRC = "lrc"
    KRC = "krc"
    CUSTOM = "custom"


class LyricLine:
    """歌词行数据"""
    
    def __init__(self, time: float, text: str):
        self.time = time
        self.text = text.strip()
    
    def __str__(self):
        return f"[{self.time:.2f}] {self.text}"


class SummaryGenerator:
    """歌词摘要生成器"""
    
    def __init__(self):
        """初始化生成器"""
        # 中国流行歌曲经典表达模式
        self.classic_patterns = {
            'philosophical': [
                '一生', '永远', '瞬间', '时光', '岁月', '青春', '年华',
                '人生', '命运', '缘分', '爱情', '友情', '亲情'
            ],
            'emotional_peak': [
                '爱', '情', '心', '泪', '笑', '痛', '伤', '思念', '回忆',
                '孤独', '寂寞', '温暖', '幸福', '快乐', '悲伤'
            ],
            'imagery_classic': [
                '月亮', '星星', '太阳', '风', '雨', '雪', '云', '天空',
                '大海', '山', '花', '树', '草', '远方', '天涯'
            ],
            'time_expression': [
                '昨天', '今天', '明天', '永远', '瞬间', '时光', '岁月',
                '青春', '年华', '从前', '以后', '现在'
            ]
        }
        
        # 避免的词汇（不适合分享）
        self.avoid_words = [
            '啊啊啊', '哦哦哦', '嗯嗯嗯', '啦啦啦', '嘿嘿嘿',
            '哈哈', '呵呵', '嘻嘻', '嘿嘿', '哈哈'
        ]
        
        logger.info("歌词摘要生成器初始化完成")
    
    def parse_lrc_file(self, file_path: str) -> List[LyricLine]:
        """解析LRC文件"""
        lyrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('[') and ']' not in line:
                        continue
                    
                    # 匹配时间标签 [mm:ss.xx]
                    time_match = re.search(r'\[(\d{2}):(\d{2})\.(\d{2})\]', line)
                    if time_match:
                        minutes = int(time_match.group(1))
                        seconds = int(time_match.group(2))
                        centiseconds = int(time_match.group(3))
                        time = minutes * 60 + seconds + centiseconds / 100
                        
                        # 提取歌词文本
                        text = line[time_match.end():].strip()
                        if text:
                            lyrics.append(LyricLine(time, text))
        
        except Exception as e:
            logger.error(f"解析LRC文件失败: {e}")
        
        return sorted(lyrics, key=lambda x: x.time)
    
    def parse_krc_file(self, file_path: str) -> List[LyricLine]:
        """解析KRC文件"""
        lyrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # KRC格式通常是加密的，这里提供基础解析
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('['):
                        continue
                    
                    # 简单的KRC解析
                    time_match = re.search(r'\[(\d+),(\d+)\]', line)
                    if time_match:
                        start_time = int(time_match.group(1)) / 1000
                        text = re.sub(r'\[\d+,\d+\]', '', line).strip()
                        if text:
                            lyrics.append(LyricLine(start_time, text))
        
        except Exception as e:
            logger.error(f"解析KRC文件失败: {e}")
        
        return sorted(lyrics, key=lambda x: x.time)
    
    def parse_custom_file(self, file_path: str) -> List[LyricLine]:
        """解析自定义格式文件"""
        lyrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # 尝试解析时间戳格式
                    # 格式1: [时间] 歌词
                    time_match = re.search(r'\[([\d:\.]+)\]', line)
                    if time_match:
                        time_str = time_match.group(1)
                        time = self._parse_time_string(time_str)
                        text = line[time_match.end():].strip()
                        if text:
                            lyrics.append(LyricLine(time, text))
                        continue
                    
                    # 格式2: 时间 歌词
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        time_str = parts[0]
                        text = parts[1]
                        time = self._parse_time_string(time_str)
                        if time >= 0:
                            lyrics.append(LyricLine(time, text))
        
        except Exception as e:
            logger.error(f"解析自定义文件失败: {e}")
        
        return sorted(lyrics, key=lambda x: x.time)
    
    def _parse_time_string(self, time_str: str) -> float:
        """解析时间字符串"""
        try:
            # 格式: mm:ss 或 mm:ss.xx
            if ':' in time_str:
                parts = time_str.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                # 纯秒数
                return float(time_str)
        except ValueError:
            return -1
    
    def is_shareable_quote(self, text: str) -> bool:
        """判断是否适合分享的经典歌词"""
        # 过滤掉包含避免词汇的歌词
        for avoid_word in self.avoid_words:
            if avoid_word in text:
                return False
        
        # 过滤掉太短或太长的歌词
        clean_text = re.sub(r'[^\u4e00-\u9fff]', '', text)
        if len(clean_text) < 4 or len(clean_text) > 20:
            return False
        
        # 过滤掉纯重复的歌词
        if self._is_pure_repetition(text):
            return False
        
        return True
    
    def _is_pure_repetition(self, text: str) -> bool:
        """判断是否为纯重复内容"""
        # 检查是否全是重复字符
        if len(set(text)) <= 2 and len(text) > 4:
            return True
        
        # 检查是否有明显的重复模式
        if re.search(r'(.)\1{2,}', text):  # 连续3个以上相同字符
            return True
        
        return False
    
    def calculate_classic_score(self, text: str) -> float:
        """计算经典程度分数"""
        score = 0.0
        
        # 基础分数
        score += 1.0
        
        # 经典词汇加分
        for category, keywords in self.classic_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    score += 0.5
        
        # 句式优美加分
        if self._has_beautiful_structure(text):
            score += 1.0
        
        # 情感深度加分
        if self._has_emotional_depth(text):
            score += 1.0
        
        # 意象丰富加分
        if self._has_rich_imagery(text):
            score += 0.8
        
        # 哲理深刻加分
        if self._has_philosophical_depth(text):
            score += 1.2
        
        # 长度适中加分
        clean_length = len(re.sub(r'[^\u4e00-\u9fff]', '', text))
        if 6 <= clean_length <= 12:
            score += 0.5
        elif 4 <= clean_length <= 16:
            score += 0.3
        
        return score
    
    def _has_beautiful_structure(self, text: str) -> bool:
        """判断是否有优美的结构"""
        # 对仗工整
        if len(text) == 4 or len(text) == 8:
            return True
        
        # 有标点符号（表示完整句子）
        if any(p in text for p in '，。！？'):
            return True
        
        # 首尾呼应
        words = re.findall(r'\w+', text)
        if len(words) >= 2 and words[0] == words[-1]:
            return True
        
        return False
    
    def _has_emotional_depth(self, text: str) -> bool:
        """判断是否有情感深度"""
        emotion_keywords = [
            '爱', '情', '心', '泪', '痛', '伤', '思念', '回忆',
            '孤独', '寂寞', '温暖', '幸福', '快乐', '悲伤'
        ]
        
        emotion_count = sum(1 for keyword in emotion_keywords if keyword in text)
        return emotion_count >= 1
    
    def _has_rich_imagery(self, text: str) -> bool:
        """判断是否有丰富的意象"""
        imagery_keywords = [
            '月亮', '星星', '太阳', '风', '雨', '雪', '云', '天空',
            '大海', '山', '花', '树', '草', '远方', '天涯'
        ]
        
        imagery_count = sum(1 for keyword in imagery_keywords if keyword in text)
        return imagery_count >= 1
    
    def _has_philosophical_depth(self, text: str) -> bool:
        """判断是否有哲理深度"""
        philosophical_keywords = [
            '一生', '永远', '瞬间', '时光', '岁月', '青春', '年华',
            '人生', '命运', '缘分', '爱情', '友情', '亲情'
        ]
        
        philosophical_count = sum(1 for keyword in philosophical_keywords if keyword in text)
        return philosophical_count >= 1
    
    def generate_summary(self, lyrics: List[LyricLine], song_name: str) -> str:
        """生成适合分享的经典歌词"""
        if not lyrics:
            return "继续努力，下次会更好！"
        
        # 提取所有歌词文本
        lyric_texts = [lyric.text for lyric in lyrics]
        
        # 过滤出适合分享的歌词
        shareable_quotes = []
        for text in lyric_texts:
            if self.is_shareable_quote(text):
                score = self.calculate_classic_score(text)
                shareable_quotes.append((text, score))
        
        if not shareable_quotes:
            # 如果没有找到合适的，返回中间部分的歌词
            middle_index = len(lyrics) // 2
            return lyrics[middle_index].text
        
        # 按分数排序，返回最高分的
        shareable_quotes.sort(key=lambda x: x[1], reverse=True)
        return shareable_quotes[0][0]
    
    def process_lyric_file(self, 
                          file_path: str, 
                          song_id: str, 
                          song_name: str,
                          format_type: LyricFormat = LyricFormat.LRC) -> Optional[str]:
        """处理歌词文件并生成分享歌词"""
        try:
            # 根据格式解析歌词
            if format_type == LyricFormat.LRC:
                lyrics = self.parse_lrc_file(file_path)
            elif format_type == LyricFormat.KRC:
                lyrics = self.parse_krc_file(file_path)
            elif format_type == LyricFormat.CUSTOM:
                lyrics = self.parse_custom_file(file_path)
            else:
                logger.error(f"不支持的歌词格式: {format_type}")
                return None
            
            if not lyrics:
                logger.warning(f"未解析到歌词内容: {file_path}")
                return "继续努力，下次会更好！"
            
            # 生成分享歌词
            share_quote = self.generate_summary(lyrics, song_name)
            logger.info(f"生成分享歌词成功: {song_name} -> {share_quote}")
            
            return share_quote
            
        except Exception as e:
            logger.error(f"处理歌词文件失败: {file_path}, 错误: {e}")
            return None
    
    def generate_csv(self, 
                    lyric_files: List[tuple], 
                    output_path: str):
        """批量处理歌词文件并生成CSV"""
        results = []
        
        for file_path, song_id, song_name, format_type in lyric_files:
            logger.info(f"处理文件: {file_path}")
            
            share_quote = self.process_lyric_file(file_path, song_id, song_name, format_type)
            if share_quote:
                results.append({
                    'id': song_id,
                    'song_name': song_name,
                    'summary': share_quote
                })
        
        # 写入CSV文件
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'song_name', 'summary'])
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"CSV文件生成成功: {output_path}, 共处理 {len(results)} 首歌曲")
            
        except Exception as e:
            logger.error(f"生成CSV文件失败: {e}")


# 使用示例
if __name__ == "__main__":
    # 创建分享歌词生成器
    generator = SummaryGenerator()
    
    # 示例：处理单个文件
    share_quote = generator.process_lyric_file(
        file_path="example.lrc",
        song_id="song_001",
        song_name="朋友",
        format_type=LyricFormat.LRC
    )
    
    if share_quote:
        print(f"生成的分享歌词: {share_quote}")
    
    # 示例：批量处理
    lyric_files = [
        ("songs/song1.lrc", "song_001", "朋友", LyricFormat.LRC),
        ("songs/song2.krc", "song_002", "月亮代表我的心", LyricFormat.KRC),
        ("songs/song3.txt", "song_003", "青花瓷", LyricFormat.CUSTOM),
    ]
    
    generator.generate_csv(lyric_files, "share_quotes.csv")
