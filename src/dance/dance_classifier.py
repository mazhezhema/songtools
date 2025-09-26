#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
广场舞分类工具
根据舞蹈名称智能分类到不同类别
"""

import os
import sys
import re
import csv
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DanceClassifier:
    """广场舞分类器"""
    
    def __init__(self):
        # 定义分类规则，包含rank value（热度值）用于前端排序
        self.categories = {
            "热门流行": {
                "keywords": ["热门", "流行", "时尚", "潮流", "新歌", "流行歌曲", "热门歌曲", "时尚舞曲", "潮流音乐", "流行音乐", "广场舞"],
                "patterns": [r"热门", r"流行", r"时尚", r"潮流", r"新歌", r"流行歌曲", r"热门歌曲", r"时尚舞曲", r"潮流音乐", r"流行音乐", r"广场舞"],
                "rank_value": 100,  # 最高热度
                "display_order": 1
            },
            "入门教学": {
                "keywords": ["教学", "入门", "基础", "教程", "分解", "学习", "新手", "简单", "易学", "初级", "示范", "指导", "背面", "演示", "口令"],
                "patterns": [r"教学", r"入门", r"基础", r"教程", r"分解", r"学习", r"新手", r"简单", r"易学", r"初级", r"示范", r"指导", r"背面", r"演示", r"口令"],
                "rank_value": 90,
                "display_order": 2
            },
            "动感健身": {
                "keywords": ["健身", "运动", "减肥", "塑形", "燃脂", "有氧", "活力", "动感", "激情", "力量", "健美", "锻炼", "操"],
                "patterns": [r"健身", r"运动", r"减肥", r"塑形", r"燃脂", r"有氧", r"活力", r"动感", r"激情", r"力量", r"健美", r"锻炼", r"操"],
                "rank_value": 85,
                "display_order": 3
            },
            "柔情慢歌": {
                "keywords": ["柔情", "慢歌", "温柔", "浪漫", "抒情", "深情", "缠绵", "温馨", "甜蜜", "柔情似水", "慢节奏", "舒缓", "月亮", "水乡", "梦里", "回忆", "爱情", "恋人", "姑娘", "玫瑰", "情歌"],
                "patterns": [r"柔情", r"慢歌", r"温柔", r"浪漫", r"抒情", r"深情", r"缠绵", r"温馨", r"甜蜜", r"柔情似水", r"慢节奏", r"舒缓", r"月亮", r"水乡", r"梦里", r"回忆", r"爱情", r"恋人", r"姑娘", r"玫瑰", r"情歌"],
                "rank_value": 80,
                "display_order": 4
            },
            "民族风情": {
                "keywords": ["民族", "风情", "传统", "古典", "古风", "汉服", "旗袍", "扇子", "水袖", "古典舞", "民族舞", "传统舞", "草原", "蒙古", "西藏", "新疆", "康定", "纳木措", "游牧", "梁祝", "茉莉花"],
                "patterns": [r"民族", r"风情", r"传统", r"古典", r"古风", r"汉服", r"旗袍", r"扇子", r"水袖", r"古典舞", r"民族舞", r"传统舞", r"草原", r"蒙古", r"西藏", r"新疆", r"康定", r"纳木措", r"游牧", r"梁祝", r"茉莉花"],
                "rank_value": 75,
                "display_order": 5
            },
            "喜庆欢快": {
                "keywords": ["喜庆", "欢快", "快乐", "开心", "欢乐", "热闹", "庆祝", "节日", "祝福", "吉祥", "红火", "热闹", "九九", "十八", "三朵", "一朵", "二朵", "百鸟", "千千", "鸟"],
                "patterns": [r"喜庆", r"欢快", r"快乐", r"开心", r"欢乐", r"热闹", r"庆祝", r"节日", r"祝福", r"吉祥", r"红火", r"热闹", r"九九", r"十八", r"三朵", r"一朵", r"二朵", r"百鸟", r"千千", r"鸟"],
                "rank_value": 70,
                "display_order": 6
            },
            "经典老歌": {
                "keywords": ["经典", "老歌", "怀旧", "回忆", "年代", "复古", "经典歌曲", "老歌新唱", "怀旧金曲", "经典重现", "时间", "岁月", "青春", "往事", "过去", "曾经", "甜蜜蜜", "月亮代表我的心", "朋友", "水手", "童年", "同桌的你", "南屏晚钟"],
                "patterns": [r"经典", r"老歌", r"怀旧", r"回忆", r"年代", r"复古", r"经典歌曲", r"老歌新唱", r"怀旧金曲", r"经典重现", r"时间", r"岁月", r"青春", r"往事", r"过去", r"曾经", r"甜蜜蜜", r"月亮代表我的心", r"朋友", r"水手", r"童年", r"同桌的你", r"南屏晚钟"],
                "rank_value": 65,
                "display_order": 7
            },
            "网红神曲": {
                "keywords": ["网红", "神曲", "爆红", "抖音", "快手", "短视频", "网络神曲", "网红歌曲", "爆款", "刷屏", "病毒式传播", "dou起", "热门音乐", "小苹果", "最炫民族风", "江南style", "小跳蛙", "学猫叫", "海草舞", "卡路里", "野狼disco", "芒种", "少年", "伤不起", "爱情买卖", "忐忑", "我的滑板鞋", "PPAP", "despacito", "凤凰传奇", "筷子兄弟", "大张伟", "薛之谦", "邓紫棋", "周杰伦", "林俊杰", "王力宏", "蔡依林", "张杰", "李荣浩", "毛不易", "华晨宇", "TFBOYS", "鹿晗", "吴亦凡", "张艺兴", "黄子韬", "易烊千玺", "王俊凯", "王源", "杨幂", "赵丽颖", "迪丽热巴", "关晓彤", "欧阳娜娜", "陈立农", "范丞丞", "黄明昊", "朱正廷", "王子异", "小鬼", "尤长靖", "蔡徐坤", "陈伟霆", "李易峰", "杨洋", "井柏然", "白敬亭", "刘昊然", "王嘉尔", "张艺兴", "黄子韬", "吴亦凡", "鹿晗", "张杰", "华晨宇", "毛不易", "李荣浩", "薛之谦", "邓紫棋", "周杰伦", "林俊杰", "王力宏", "蔡依林", "SHE", "五月天", "苏打绿", "田馥甄", "陈奕迅", "张学友", "刘德华", "郭富城", "黎明", "张国荣", "梅艳芳", "邓丽君", "王菲", "那英", "韩红", "孙楠", "刘欢", "毛阿敏", "韦唯", "宋祖英", "彭丽媛", "李谷一", "蒋大为", "阎维文", "郁钧剑", "杨洪基", "戴玉强", "廖昌永", "莫华伦", "魏松", "张建一", "范竞马", "丁毅", "王宏伟", "刘和刚", "王丽达", "雷佳", "王庆爽", "常思思", "吴碧霞", "龚琳娜", "谭晶", "祖海", "张也", "李丹阳", "陈思思", "吕薇", "刘媛媛", "王莉", "王莹", "王丽达", "雷佳", "王庆爽", "常思思", "吴碧霞", "龚琳娜", "谭晶", "祖海", "张也", "李丹阳", "陈思思", "吕薇", "刘媛媛", "王莉", "王莹"],
                "patterns": [r"网红", r"神曲", r"爆红", r"抖音", r"快手", r"短视频", r"网络神曲", r"网红歌曲", r"爆款", r"刷屏", r"病毒式传播", r"dou起", r"热门音乐", r"小苹果", r"最炫民族风", r"江南style", r"小跳蛙", r"学猫叫", r"海草舞", r"卡路里", r"野狼disco", r"芒种", r"少年", r"伤不起", r"爱情买卖", r"忐忑", r"我的滑板鞋", r"PPAP", r"despacito", r"凤凰传奇", r"筷子兄弟", r"大张伟", r"薛之谦", r"邓紫棋", r"周杰伦", r"林俊杰", r"王力宏", r"蔡依林", r"张杰", r"李荣浩", r"毛不易", r"华晨宇", r"TFBOYS", r"鹿晗", r"吴亦凡", r"张艺兴", r"黄子韬", r"易烊千玺", r"王俊凯", r"王源", r"杨幂", r"赵丽颖", r"迪丽热巴", r"关晓彤", r"欧阳娜娜", r"陈立农", r"范丞丞", r"黄明昊", r"朱正廷", r"王子异", r"小鬼", r"尤长靖", r"蔡徐坤", r"陈伟霆", r"李易峰", r"杨洋", r"井柏然", r"白敬亭", r"刘昊然", r"王嘉尔"],
                "rank_value": 60,
                "display_order": 8
            }
        }
    
    def clean_dance_name(self, name: str) -> str:
        """
        清理舞蹈名称，去除文件扩展名和编号
        
        Args:
            name: 原始名称
            
        Returns:
            清理后的名称
        """
        # 去除文件扩展名
        name = re.sub(r'\.(mp4|avi|mov|mkv|flv|wmv)$', '', name, flags=re.IGNORECASE)
        
        # 去除编号前缀
        name = re.sub(r'^\d+\.?\s*', '', name)
        name = re.sub(r'^\d+[-_]\s*', '', name)
        
        # 去除特殊字符
        name = re.sub(r'[#@$%^&*()_+=\[\]{}|\\:";\'<>?,./]', '', name)
        
        # 去除多余空格
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def classify_dance(self, dance_name: str) -> List[Tuple[str, float]]:
        """
        分类单个舞蹈 - 支持多标签分类
        
        Args:
            dance_name: 舞蹈名称
            
        Returns:
            [(分类名称, 置信度), ...] 按置信度降序排列
        """
        clean_name = self.clean_dance_name(dance_name)
        
        # 计算每个分类的匹配分数
        scores = {}
        
        for category, rules in self.categories.items():
            score = 0
            matched_keywords = 0
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                if keyword in clean_name:
                    score += 1
                    matched_keywords += 1
            
            # 正则表达式匹配（避免重复计算）
            for pattern in rules["patterns"]:
                if re.search(pattern, clean_name, re.IGNORECASE):
                    # 如果关键词已经匹配过，不重复加分
                    if not any(keyword in clean_name for keyword in rules["keywords"] if re.search(pattern, keyword, re.IGNORECASE)):
                        score += 0.5
            
            # 计算置信度 - 基于匹配的关键词数量
            if matched_keywords > 0:
                confidence = min(score / len(rules["keywords"]), 1.0)
            else:
                confidence = 0.0
            
            scores[category] = confidence
        
        # 智能分类补充
        intelligent_scores = self._intelligent_classify_multi(clean_name)
        for category, confidence in intelligent_scores.items():
            if category in scores:
                scores[category] = max(scores[category], confidence)
            else:
                scores[category] = confidence
        
        # 降低阈值，让更多分类被选中
        threshold = 0.1  # 降低置信度阈值
        filtered_scores = [(cat, conf) for cat, conf in scores.items() if conf >= threshold]
        
        # 按置信度降序排列
        filtered_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 如果没有符合条件的分类，返回默认分类
        if not filtered_scores:
            return [("热门流行", 0.3)]
        
        # 限制最多返回3个分类
        return filtered_scores[:3]
    
    def _intelligent_classify_multi(self, dance_name: str) -> Dict[str, float]:
        """
        多标签智能分类 - 基于歌曲名称特征进行分类
        
        Args:
            dance_name: 清理后的舞蹈名称
            
        Returns:
            {分类名称: 置信度} 字典
        """
        scores = {}
        
        # 基于歌曲名称的智能分类规则
        intelligent_rules = {
            "热门流行": {
                "keywords": ["小苹果", "最炫民族风", "江南style", "小跳蛙", "学猫叫", "海草舞", "卡路里", "野狼disco", "芒种", "少年", "抖音", "快手", "网红"],
                "confidence": 0.8
            },
            "经典老歌": {
                "keywords": ["月亮代表我的心", "甜蜜蜜", "小城故事", "我只在乎你", "千千阙歌", "朋友", "水手", "星星点灯", "童年", "同桌的你", "南屏晚钟"],
                "confidence": 0.8
            },
            "民族风情": {
                "keywords": ["茉莉花", "梁祝", "高山流水", "梅花三弄", "春江花月夜", "渔舟唱晚", "二泉映月", "十面埋伏", "广陵散", "平沙落雁", "古典", "扇子", "古风"],
                "confidence": 0.8
            },
            "喜庆欢快": {
                "keywords": ["恭喜发财", "新年好", "拜年", "红红火火", "喜洋洋", "好运来", "步步高", "金蛇狂舞", "春节序曲", "闹新春", "吉祥", "欢歌"],
                "confidence": 0.8
            },
            "柔情慢歌": {
                "keywords": ["月亮", "温柔", "浪漫", "深情", "缠绵", "温馨", "甜蜜", "柔情", "慢歌", "抒情", "水乡", "温柔"],
                "confidence": 0.6
            },
            "动感健身": {
                "keywords": ["健身", "运动", "减肥", "塑形", "燃脂", "有氧", "活力", "动感", "激情", "力量", "健美操", "健身操"],
                "confidence": 0.6
            },
            "入门教学": {
                "keywords": ["教学", "入门", "基础", "教程", "分解", "学习", "新手", "简单", "易学", "初级", "示范", "指导", "背面", "演示"],
                "confidence": 0.7
            },
            "网红神曲": {
                "keywords": ["网红", "神曲", "爆红", "抖音", "快手", "短视频", "网络神曲", "网红歌曲", "爆款", "刷屏", "病毒式传播", "dou起"],
                "confidence": 0.8
            }
        }
        
        # 检查智能分类规则
        for category, rules in intelligent_rules.items():
            for keyword in rules["keywords"]:
                if keyword in dance_name:
                    scores[category] = rules["confidence"]
                    break
        
        # 基于名称特征的额外分类 - 大幅扩展规则
        if "广场舞" in dance_name:
            scores["热门流行"] = max(scores.get("热门流行", 0), 0.3)
        
        # 入门教学分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["分解", "教学", "教程", "学习", "新手", "简单", "易学", "初级", "示范", "指导", "背面", "演示", "口令"]):
            scores["入门教学"] = max(scores.get("入门教学", 0), 0.5)
        
        # 动感健身分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["健身", "健美", "运动", "减肥", "塑形", "燃脂", "有氧", "活力", "动感", "激情", "力量", "操", "锻炼"]):
            scores["动感健身"] = max(scores.get("动感健身", 0), 0.5)
        
        # 民族风情分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["古典", "扇子", "古风", "民族", "传统", "汉服", "旗袍", "水袖", "梁祝", "茉莉花", "高山流水", "梅花三弄"]):
            scores["民族风情"] = max(scores.get("民族风情", 0), 0.5)
        
        # 柔情慢歌分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["温柔", "柔情", "月亮", "浪漫", "深情", "缠绵", "温馨", "甜蜜", "抒情", "慢歌", "水乡", "梦里", "回忆"]):
            scores["柔情慢歌"] = max(scores.get("柔情慢歌", 0), 0.4)
        
        # 喜庆欢快分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["吉祥", "欢歌", "喜庆", "快乐", "开心", "欢乐", "热闹", "庆祝", "节日", "祝福", "红火", "喜洋洋", "好运"]):
            scores["喜庆欢快"] = max(scores.get("喜庆欢快", 0), 0.4)
        
        # 经典老歌分类 - 扩展关键词
        if any(keyword in dance_name for keyword in ["经典", "老歌", "怀旧", "回忆", "年代", "复古", "甜蜜蜜", "月亮代表我的心", "朋友", "水手", "童年", "同桌的你", "南屏晚钟"]):
            scores["经典老歌"] = max(scores.get("经典老歌", 0), 0.4)
        
        # 网红神曲分类 - 网络爆红歌曲识别
        # 经典网络神曲
        classic_wanghong = ["小苹果", "最炫民族风", "江南style", "小跳蛙", "学猫叫", "海草舞", "卡路里", "野狼disco", "芒种", "少年", "伤不起", "爱情买卖", "忐忑", "我的滑板鞋", "PPAP", "despacito", "野狼disco", "芒种", "少年", "伤不起", "爱情买卖", "忐忑", "我的滑板鞋", "PPAP", "despacito"]
        
        # 知名歌手/组合
        famous_artists = ["凤凰传奇", "筷子兄弟", "大张伟", "薛之谦", "邓紫棋", "周杰伦", "林俊杰", "王力宏", "蔡依林", "张杰", "李荣浩", "毛不易", "华晨宇", "TFBOYS", "鹿晗", "吴亦凡", "张艺兴", "黄子韬", "易烊千玺", "王俊凯", "王源", "杨幂", "赵丽颖", "迪丽热巴", "关晓彤", "欧阳娜娜", "陈立农", "范丞丞", "黄明昊", "朱正廷", "王子异", "小鬼", "尤长靖", "蔡徐坤", "陈伟霆", "李易峰", "杨洋", "井柏然", "白敬亭", "刘昊然", "王嘉尔"]
        
        # 网络平台关键词
        platform_keywords = ["抖音", "快手", "短视频", "dou起", "热门音乐", "爆款", "刷屏", "病毒式传播"]
        
        # 检查经典网络神曲
        if any(song in dance_name for song in classic_wanghong):
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.8)
        
        # 检查知名歌手
        if any(artist in dance_name for artist in famous_artists):
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.7)
        
        # 检查网络平台关键词
        if any(keyword in dance_name for keyword in platform_keywords):
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.6)
        
        # 智能识别现代流行神曲特征
        # 短名称 + 现代感 -> 网红神曲
        if len(dance_name) <= 8 and any(keyword in dance_name for keyword in ["style", "舞", "歌", "曲", "爱", "你", "我", "的", "小", "大", "美", "好", "甜", "香"]):
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.4)
        
        # 包含英文或数字的现代歌曲 -> 网红神曲
        if any(char.isdigit() or char.isalpha() for char in dance_name) and len(dance_name) <= 12:
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.3)
        
        # 包含"广场舞"但名称很短的 -> 可能是网红神曲
        if "广场舞" in dance_name and len(dance_name) <= 15:
            scores["网红神曲"] = max(scores.get("网红神曲", 0), 0.3)
        
        # 基于歌曲名称的智能分类
        # 草原相关 -> 民族风情
        if any(keyword in dance_name for keyword in ["草原", "蒙古", "西藏", "新疆", "康定", "纳木措", "游牧"]):
            scores["民族风情"] = max(scores.get("民族风情", 0), 0.6)
        
        # 爱情相关 -> 柔情慢歌
        if any(keyword in dance_name for keyword in ["爱情", "恋人", "姑娘", "玫瑰", "情歌", "爱你", "想你", "思念"]):
            scores["柔情慢歌"] = max(scores.get("柔情慢歌", 0), 0.5)
        
        # 时间相关 -> 经典老歌
        if any(keyword in dance_name for keyword in ["时间", "岁月", "青春", "往事", "回忆", "过去", "曾经"]):
            scores["经典老歌"] = max(scores.get("经典老歌", 0), 0.5)
        
        # 数字相关 -> 喜庆欢快
        if any(keyword in dance_name for keyword in ["九九", "十八", "三朵", "一朵", "二朵", "百鸟", "千千"]):
            scores["喜庆欢快"] = max(scores.get("喜庆欢快", 0), 0.4)
        
        # 动物相关 -> 根据具体动物分类
        if "鸟" in dance_name:
            scores["喜庆欢快"] = max(scores.get("喜庆欢快", 0), 0.5)
        if "蝴蝶" in dance_name:
            scores["柔情慢歌"] = max(scores.get("柔情慢歌", 0), 0.4)
        
        # 颜色相关
        if any(keyword in dance_name for keyword in ["红", "绿", "蓝", "白", "黑", "金", "银"]):
            scores["热门流行"] = max(scores.get("热门流行", 0), 0.3)
        
        return scores
    
    def classify_dances_from_file(self, file_path: str) -> List[Dict[str, str]]:
        """
        从文件读取舞蹈名称并分类
        
        Args:
            file_path: 文件路径
            
        Returns:
            分类结果列表
        """
        results = []
        
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                logger.error(f"无法读取文件: {file_path}")
                return results
            
            # 按行分割
            lines = content.strip().split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 分类 - 支持多标签
                classifications = self.classify_dance(line)
                
                # 将多个分类合并为字符串，包含rank value
                categories_str = "; ".join([f"{cat}({conf:.2f})" for cat, conf in classifications])
                primary_category = classifications[0][0] if classifications else "未分类"
                primary_confidence = classifications[0][1] if classifications else 0.0
                
                # 获取主要分类的rank value
                primary_rank = self.categories.get(primary_category, {}).get('rank_value', 50)
                primary_display_order = self.categories.get(primary_category, {}).get('display_order', 9)
                
                # 计算综合热度值（基于rank value和置信度）
                composite_rank = primary_rank * primary_confidence
                
                results.append({
                    'line_number': line_num,
                    'original_name': line,
                    'clean_name': self.clean_dance_name(line),
                    'primary_category': primary_category,
                    'primary_confidence': f"{primary_confidence:.2f}",
                    'primary_rank_value': primary_rank,
                    'primary_display_order': primary_display_order,
                    'composite_rank': f"{composite_rank:.2f}",
                    'all_categories': categories_str,
                    'category_count': len(classifications)
                })
                
        except Exception as e:
            logger.error(f"处理文件失败: {file_path}, 错误: {str(e)}")
        
        return results
    
    def classify_dances_from_directory(self, directory: str) -> List[Dict[str, str]]:
        """
        从目录中的所有文件读取舞蹈名称并分类
        
        Args:
            directory: 目录路径
            
        Returns:
            分类结果列表
        """
        all_results = []
        
        try:
            directory_path = Path(directory)
            
            # 查找所有文本文件
            text_files = []
            for ext in ['.txt', '.csv', '.dat']:
                text_files.extend(directory_path.glob(f"*{ext}"))
            
            if not text_files:
                logger.warning(f"在目录 {directory} 中未找到文本文件")
                return all_results
            
            logger.info(f"找到 {len(text_files)} 个文本文件")
            
            for file_path in text_files:
                logger.info(f"处理文件: {file_path.name}")
                file_results = self.classify_dances_from_file(str(file_path))
                
                # 添加文件信息
                for result in file_results:
                    result['source_file'] = file_path.name
                
                all_results.extend(file_results)
                
        except Exception as e:
            logger.error(f"处理目录失败: {directory}, 错误: {str(e)}")
        
        return all_results
    
    def save_results_to_csv(self, results: List[Dict[str, str]], output_path: str = None):
        """
        保存分类结果到CSV文件
        
        Args:
            results: 分类结果
            output_path: 输出文件路径，如果为None则使用默认路径
        """
        if output_path is None:
            output_path = "square_dance_classification_results.csv"
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['source_file', 'line_number', 'original_name', 'clean_name', 
                             'primary_category', 'primary_confidence', 'primary_rank_value', 
                             'primary_display_order', 'composite_rank', 'all_categories', 'category_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(results)
            
            logger.info(f"分类结果已保存到: {output_path}")
            
        except Exception as e:
            logger.error(f"保存CSV文件失败: {str(e)}")
    
    def get_category_statistics(self, results: List[Dict[str, str]]) -> Dict[str, int]:
        """
        获取分类统计信息 - 支持多标签统计
        
        Args:
            results: 分类结果
            
        Returns:
            分类统计字典
        """
        stats = {}
        primary_stats = {}
        
        for result in results:
            # 主要分类统计
            primary_category = result.get('primary_category', '未分类')
            primary_stats[primary_category] = primary_stats.get(primary_category, 0) + 1
            
            # 所有分类统计
            all_categories = result.get('all_categories', '')
            if all_categories:
                # 解析所有分类
                categories = [cat.split('(')[0].strip() for cat in all_categories.split(';')]
                for category in categories:
                    if category:
                        stats[category] = stats.get(category, 0) + 1
        
        return {
            'primary_categories': primary_stats,
            'all_categories': stats
        }
    
    def get_category_rank_data(self, results: List[Dict[str, str]]) -> Dict:
        """
        获取分类排序数据，用于前端UI展示
        
        Args:
            results: 分类结果
            
        Returns:
            包含分类排序信息的字典
        """
        category_data = {}
        
        # 按分类组织数据
        for result in results:
            category = result.get('primary_category', '未分类')
            if category not in category_data:
                category_data[category] = {
                    'items': [],
                    'count': 0,
                    'rank_value': self.categories.get(category, {}).get('rank_value', 50),
                    'display_order': self.categories.get(category, {}).get('display_order', 9)
                }
            
            category_data[category]['items'].append({
                'original_name': result.get('original_name', ''),
                'clean_name': result.get('clean_name', ''),
                'confidence': float(result.get('primary_confidence', 0)),
                'composite_rank': float(result.get('composite_rank', 0)),
                'all_categories': result.get('all_categories', ''),
                'category_count': int(result.get('category_count', 1))
            })
            category_data[category]['count'] += 1
        
        # 为每个分类内的项目按综合热度排序
        for category in category_data:
            category_data[category]['items'].sort(
                key=lambda x: x['composite_rank'], 
                reverse=True
            )
        
        # 按display_order排序分类
        sorted_categories = sorted(
            category_data.items(), 
            key=lambda x: x[1]['display_order']
        )
        
        return {
            'categories': dict(sorted_categories),
            'category_order': [cat for cat, _ in sorted_categories],
            'total_items': len(results)
        }


class DanceClassifierGUI:
    """广场舞分类器GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("广场舞分类工具")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        self.classifier = DanceClassifier()
        self.input_dir = ""
        self.output_file = ""
        self.classification_results = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="💃 广场舞分类工具", 
                               font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 输入输出区域
        io_frame = ttk.LabelFrame(main_frame, text="输入输出设置", padding="10")
        io_frame.pack(fill='x', pady=(0, 10))
        
        # 输入目录
        ttk.Label(io_frame, text="输入目录:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.input_var = tk.StringVar()
        ttk.Entry(io_frame, textvariable=self.input_var, 
                 state='readonly', width=50).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(io_frame, text="选择目录", 
                  command=self.select_input_dir).grid(row=0, column=2)
        
        # 输出文件
        ttk.Label(io_frame, text="输出文件:").grid(row=1, column=0, sticky='w', padx=(0, 10), pady=(10, 0))
        self.output_var = tk.StringVar()
        ttk.Entry(io_frame, textvariable=self.output_var, 
                 state='readonly', width=50).grid(row=1, column=1, padx=(0, 10), pady=(10, 0))
        ttk.Button(io_frame, text="选择文件", 
                  command=self.select_output_file).grid(row=1, column=2, pady=(10, 0))
        
        # 分类规则显示
        rules_frame = ttk.LabelFrame(main_frame, text="分类规则", padding="10")
        rules_frame.pack(fill='x', pady=(0, 10))
        
        # 创建分类规则表格
        columns = ('分类', '关键词数量', '示例关键词')
        self.rules_tree = ttk.Treeview(rules_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.rules_tree.heading(col, text=col)
            self.rules_tree.column(col, width=200)
        
        # 添加分类规则数据
        for category, rules in self.classifier.categories.items():
            keywords = rules["keywords"][:5]  # 只显示前5个关键词
            self.rules_tree.insert('', 'end', values=(
                category,
                len(rules["keywords"]),
                ', '.join(keywords)
            ))
        
        self.rules_tree.pack(fill='x')
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="开始分类", 
                  command=self.start_classification, style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="预览结果", 
                  command=self.preview_results).pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="清空结果", 
                  command=self.clear_results).pack(side='left')
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.pack(anchor='w')
        
        # 结果显示区域
        results_frame = ttk.LabelFrame(main_frame, text="分类结果", padding="5")
        results_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # 结果表格
        result_columns = ('源文件', '行号', '原始名称', '主要分类', '置信度', '所有分类', '标签数')
        self.results_tree = ttk.Treeview(results_frame, columns=result_columns, show='headings', height=10)
        
        for col in result_columns:
            self.results_tree.heading(col, text=col)
            if col == '所有分类':
                self.results_tree.column(col, width=200)
            else:
                self.results_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        
        self.results_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def select_input_dir(self):
        """选择输入目录"""
        directory = filedialog.askdirectory(title="选择包含舞蹈名称文件的目录")
        if directory:
            self.input_dir = directory
            self.input_var.set(directory)
            self.status_var.set(f"已选择输入目录: {directory}")
    
    def select_output_file(self):
        """选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="选择输出CSV文件",
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.output_file = file_path
            self.output_var.set(file_path)
            self.status_var.set(f"已选择输出文件: {file_path}")
    
    def start_classification(self):
        """开始分类"""
        if not self.input_dir:
            messagebox.showwarning("警告", "请先选择输入目录")
            return
        
        if not self.output_file:
            messagebox.showwarning("警告", "请先选择输出文件")
            return
        
        # 在新线程中执行分类
        self.classification_thread = threading.Thread(target=self._classification_worker)
        self.classification_thread.daemon = True
        self.classification_thread.start()
    
    def _classification_worker(self):
        """分类工作线程"""
        try:
            self.root.after(0, lambda: self.status_var.set("正在分类..."))
            self.root.after(0, lambda: self.progress_var.set(0))
            
            # 执行分类
            self.classification_results = self.classifier.classify_dances_from_directory(self.input_dir)
            
            # 更新进度
            self.root.after(0, lambda: self.progress_var.set(50))
            
            # 保存结果
            self.classifier.save_results_to_csv(self.classification_results, self.output_file)
            
            # 更新进度
            self.root.after(0, lambda: self.progress_var.set(100))
            
            # 更新UI
            self.root.after(0, self._update_results_display)
            
            # 显示统计信息
            stats = self.classifier.get_category_statistics(self.classification_results)
            
            stats_text = "📊 分类统计结果\n\n"
            stats_text += "主要分类统计:\n"
            for k, v in stats['primary_categories'].items():
                stats_text += f"  {k}: {v}个\n"
            
            stats_text += "\n所有标签统计:\n"
            for k, v in stats['all_categories'].items():
                stats_text += f"  {k}: {v}个\n"
            
            self.root.after(0, lambda: self.status_var.set(f"分类完成! 共处理 {len(self.classification_results)} 个舞蹈"))
            self.root.after(0, lambda: messagebox.showinfo("完成", f"分类完成!\n\n{stats_text}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"分类失败: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"分类失败: {str(e)}"))
    
    def _update_results_display(self):
        """更新结果显示"""
        # 清空现有结果
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # 添加新结果
        for result in self.classification_results:
            self.results_tree.insert('', 'end', values=(
                result.get('source_file', ''),
                result.get('line_number', ''),
                result.get('original_name', '')[:30] + '...' if len(result.get('original_name', '')) > 30 else result.get('original_name', ''),
                result.get('primary_category', ''),
                result.get('primary_confidence', ''),
                result.get('all_categories', ''),
                result.get('category_count', '')
            ))
    
    def preview_results(self):
        """预览结果"""
        if not self.classification_results:
            messagebox.showinfo("提示", "请先执行分类")
            return
        
        # 显示统计信息
        stats = self.classifier.get_category_statistics(self.classification_results)
        
        stats_text = "📊 分类统计结果\n\n"
        stats_text += "主要分类统计:\n"
        for k, v in stats['primary_categories'].items():
            stats_text += f"  {k}: {v}个\n"
        
        stats_text += "\n所有标签统计:\n"
        for k, v in stats['all_categories'].items():
            stats_text += f"  {k}: {v}个\n"
        
        messagebox.showinfo("分类统计", stats_text)
    
    def clear_results(self):
        """清空结果"""
        self.classification_results = []
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.status_var.set("结果已清空")


def main():
    """主函数"""
    root = tk.Tk()
    app = DanceClassifierGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
