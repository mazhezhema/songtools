#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高潮部分歌词提取器
专门提取歌曲高潮部分的歌词，忽略时长信息

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import re
import logging
from typing import List, Optional
from .summary_generator import LyricLine

logger = logging.getLogger(__name__)


class ChorusExtractor:
    """高潮部分歌词提取器"""
    
    def __init__(self):
        """初始化提取器"""
        # 高潮部分通常的特征
        self.chorus_indicators = [
            '副歌', '高潮', 'chorus', '重复', '再次'
        ]
        
        # 常见的重复模式（高潮部分通常重复出现）
        self.repetition_patterns = [
            r'(.+?)(?:\1)',  # 直接重复
            r'(.+?)(?:\s*\1)',  # 带空格的重复
        ]
        
        # 经典词汇库（用于评分）
        self.classic_keywords = {
            'philosophical': [
                '一生', '永远', '瞬间', '时光', '岁月', '青春', '年华',
                '人生', '命运', '缘分', '爱情', '友情', '亲情'
            ],
            'emotional': [
                '爱', '情', '心', '泪', '笑', '痛', '伤', '思念', '回忆',
                '孤独', '寂寞', '温暖', '幸福', '快乐', '悲伤'
            ],
            'imagery': [
                '月亮', '星星', '太阳', '风', '雨', '雪', '云', '天空',
                '大海', '山', '花', '树', '草', '远方', '天涯'
            ],
            'time': [
                '昨天', '今天', '明天', '永远', '瞬间', '时光', '岁月',
                '青春', '年华', '从前', '以后', '现在'
            ]
        }
        
        # 避免的词汇（不适合分享）
        self.avoid_words = [
            '啊啊啊', '哦哦哦', '嗯嗯嗯', '啦啦啦', '嘿嘿嘿',
            '哈哈', '呵呵', '嘻嘻', '嘿嘿', '哈哈'
        ]
        
        logger.info("高潮提取器初始化完成")
    
    def parse_deformed_lrc(self, file_path: str) -> List[LyricLine]:
        """解析变形LRC文件，只提取歌词内容"""
        lyrics = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for i in range(0, len(lines), 2):  # 每两行一组
                    if i + 1 >= len(lines):
                        break
                    
                    # 第一行：歌词内容
                    lyric_line = lines[i].strip()
                    # 第二行：时长信息（忽略）
                    timing_line = lines[i + 1].strip()
                    
                    # 解析时间标签
                    time_match = re.search(r'\[(\d{2}):(\d{2})\.(\d{3})\]', lyric_line)
                    if time_match:
                        minutes = int(time_match.group(1))
                        seconds = int(time_match.group(2))
                        milliseconds = int(time_match.group(3))
                        time = minutes * 60 + seconds + milliseconds / 1000
                        
                        # 提取歌词文本（去掉时间标签）
                        text = re.sub(r'\[\d{2}:\d{2}\.\d{3}\]', '', lyric_line).strip()
                        if text:
                            lyrics.append(LyricLine(time, text))
        
        except Exception as e:
            logger.error(f"解析变形LRC文件失败: {e}")
        
        return sorted(lyrics, key=lambda x: x.time)
    
    def extract_chorus_lyrics(self, lyrics: List[LyricLine]) -> List[LyricLine]:
        """提取高潮部分歌词"""
        if not lyrics:
            return []
        
        # 策略1：寻找重复的歌词（高潮部分通常重复）
        chorus_candidates = self._find_repetitive_lyrics(lyrics)
        
        # 策略2：寻找情感强烈的歌词
        emotional_candidates = self._find_emotional_lyrics(lyrics)
        
        # 策略3：选择后半部分的歌词（通常高潮在后半部分）
        later_candidates = self._find_later_lyrics(lyrics)
        
        # 合并候选歌词，去重
        all_candidates = chorus_candidates + emotional_candidates + later_candidates
        unique_candidates = self._remove_duplicates(all_candidates)
        
        # 按时间排序
        unique_candidates.sort(key=lambda x: x.time)
        
        return unique_candidates
    
    def select_best_share_quote(self, lyrics: List[LyricLine]) -> Optional[str]:
        """选择最经典的一句歌词作为分享词"""
        if not lyrics:
            return None
        
        # 过滤出适合分享的歌词
        shareable_quotes = []
        for lyric in lyrics:
            if self._is_shareable_quote(lyric.text):
                score = self._calculate_classic_score(lyric.text)
                shareable_quotes.append((lyric.text, score))
        
        if not shareable_quotes:
            # 如果没有找到合适的，返回中间部分的歌词
            middle_index = len(lyrics) // 2
            return lyrics[middle_index].text
        
        # 按分数排序，返回最高分的
        shareable_quotes.sort(key=lambda x: x[1], reverse=True)
        return shareable_quotes[0][0]
    
    def _is_shareable_quote(self, text: str) -> bool:
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
    
    def _calculate_classic_score(self, text: str) -> float:
        """计算经典程度分数"""
        score = 0.0
        
        # 基础分数
        score += 1.0
        
        # 经典词汇加分
        for category, keywords in self.classic_keywords.items():
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
    
    def _find_repetitive_lyrics(self, lyrics: List[LyricLine]) -> List[LyricLine]:
        """寻找重复的歌词"""
        repetitive = []
        text_count = {}
        
        # 统计每句歌词出现的次数
        for lyric in lyrics:
            clean_text = re.sub(r'[^\u4e00-\u9fff]', '', lyric.text)
            if clean_text:
                text_count[clean_text] = text_count.get(clean_text, 0) + 1
        
        # 选择出现次数大于1的歌词
        for lyric in lyrics:
            clean_text = re.sub(r'[^\u4e00-\u9fff]', '', lyric.text)
            if clean_text and text_count.get(clean_text, 0) > 1:
                repetitive.append(lyric)
        
        return repetitive
    
    def _find_emotional_lyrics(self, lyrics: List[LyricLine]) -> List[LyricLine]:
        """寻找情感强烈的歌词"""
        emotional_keywords = [
            '爱', '情', '心', '泪', '痛', '伤', '思念', '回忆',
            '孤独', '寂寞', '温暖', '幸福', '快乐', '悲伤',
            '永远', '一生', '瞬间', '时光', '岁月', '青春'
        ]
        
        emotional = []
        for lyric in lyrics:
            for keyword in emotional_keywords:
                if keyword in lyric.text:
                    emotional.append(lyric)
                    break
        
        return emotional
    
    def _find_later_lyrics(self, lyrics: List[LyricLine]) -> List[LyricLine]:
        """选择后半部分的歌词"""
        if len(lyrics) < 4:
            return lyrics
        
        # 选择后半部分的歌词
        start_index = len(lyrics) // 2
        return lyrics[start_index:]
    
    def _remove_duplicates(self, lyrics: List[LyricLine]) -> List[LyricLine]:
        """去除重复的歌词"""
        seen = set()
        unique = []
        
        for lyric in lyrics:
            clean_text = re.sub(r'[^\u4e00-\u9fff]', '', lyric.text)
            if clean_text not in seen:
                seen.add(clean_text)
                unique.append(lyric)
        
        return unique
    
    def process_chorus_file(self, file_path: str) -> List[str]:
        """处理文件并提取高潮歌词"""
        try:
            # 解析文件
            lyrics = self.parse_deformed_lrc(file_path)
            if not lyrics:
                logger.warning(f"未解析到歌词内容: {file_path}")
                return []
            
            # 提取高潮部分
            chorus_lyrics = self.extract_chorus_lyrics(lyrics)
            
            # 转换为纯文本
            chorus_texts = [lyric.text for lyric in chorus_lyrics]
            
            logger.info(f"成功提取高潮歌词 {len(chorus_texts)} 句")
            return chorus_texts
            
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {e}")
            return []
    
    def process_share_quote(self, file_path: str) -> Optional[str]:
        """处理文件并生成分享词（一句最经典的歌词）"""
        try:
            # 解析文件
            lyrics = self.parse_deformed_lrc(file_path)
            if not lyrics:
                logger.warning(f"未解析到歌词内容: {file_path}")
                return None
            
            # 选择最经典的分享词
            share_quote = self.select_best_share_quote(lyrics)
            
            if share_quote:
                logger.info(f"成功生成分享词: {share_quote}")
            else:
                logger.warning("未能生成合适的分享词")
            
            return share_quote
            
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {e}")
            return None


# 使用示例
if __name__ == "__main__":
    # 创建高潮提取器
    extractor = ChorusExtractor()
    
    # 处理文件
    chorus_lyrics = extractor.process_chorus_file("your_lyric_file.txt")
    
    print("提取的高潮歌词：")
    for i, lyric in enumerate(chorus_lyrics, 1):
        print(f"{i}. {lyric}")
    
    # 生成分享词
    share_quote = extractor.process_share_quote("your_lyric_file.txt")
    if share_quote:
        print(f"\n最经典的分享词: {share_quote}")
