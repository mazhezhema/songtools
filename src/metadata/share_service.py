#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享服务
提供卡拉OK演唱结果分享功能

作者: SongTools Team
创建时间: 2025-08-23
版本: 1.0.0
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime
from .summary_manager import SummaryManager, LyricSummary

logger = logging.getLogger(__name__)


class ShareService:
    """分享服务"""
    
    def __init__(self, summary_manager: SummaryManager):
        """
        初始化分享服务
        
        Args:
            summary_manager: 摘要管理器
        """
        self.summary_manager = summary_manager
        logger.info("分享服务初始化完成")
    
    def get_share_content(self, 
                         song_id: str, 
                         performance_score: float,
                         user_id: str,
                         performance_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        获取分享内容
        
        Args:
            song_id: 歌曲ID
            performance_score: 演唱得分
            user_id: 用户ID
            performance_data: 演唱表现数据
            
        Returns:
            分享内容字典
        """
        try:
            # 获取推荐摘要
            summary = self.summary_manager.get_recommended_summary(
                song_id, performance_score
            )
            
            if not summary:
                # 如果没有找到摘要，使用默认内容
                return self._get_default_share_content(performance_score)
            
            # 构建分享内容
            share_content = {
                'summary_text': summary.summary_text,
                'song_name': summary.song_name,
                'artist': summary.artist,
                'performance_score': performance_score,
                'score_level': self._get_score_level(performance_score),
                'share_text': self._generate_share_text(summary, performance_score),
                'emotion_tags': summary.emotion_tags,
                'summary_type': summary.summary_type.value,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            logger.info(f"生成分享内容成功: {share_content['summary_text']}")
            return share_content
            
        except Exception as e:
            logger.error(f"获取分享内容失败: {e}")
            return self._get_default_share_content(performance_score)
    
    def _get_score_level(self, score: float) -> str:
        """获取得分等级"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "fair"
        else:
            return "needs_improvement"
    
    def _generate_share_text(self, summary: LyricSummary, score: float) -> str:
        """生成分享文本"""
        score_level = self._get_score_level(score)
        
        templates = {
            'excellent': [
                f"🎵 完美演绎《{summary.song_name}》！得分：{score}分\n{summary.summary_text}",
                f"🌟 超棒表现！《{summary.song_name}》得分：{score}分\n{summary.summary_text}",
                f"💫 惊艳演唱！《{summary.song_name}》获得{score}分\n{summary.summary_text}"
            ],
            'good': [
                f"🎤 不错的表现！《{summary.song_name}》得分：{score}分\n{summary.summary_text}",
                f"👍 唱得不错！《{summary.song_name}》获得{score}分\n{summary.summary_text}",
                f"🎵 继续加油！《{summary.song_name}》得分：{score}分\n{summary.summary_text}"
            ],
            'fair': [
                f"🎵 演唱《{summary.song_name}》，得分：{score}分\n{summary.summary_text}",
                f"🎤 练习中！《{summary.song_name}》获得{score}分\n{summary.summary_text}",
                f"💪 努力进步！《{summary.song_name}》得分：{score}分\n{summary.summary_text}"
            ],
            'needs_improvement': [
                f"🎵 演唱《{summary.song_name}》，还有进步空间\n{summary.summary_text}",
                f"🎤 继续练习！《{summary.song_name}》得分：{score}分\n{summary.summary_text}",
                f"💪 加油！《{summary.song_name}》还有提升空间\n{summary.summary_text}"
            ]
        }
        
        import random
        return random.choice(templates[score_level])
    
    def _get_default_share_content(self, score: float) -> Dict[str, Any]:
        """获取默认分享内容"""
        return {
            'summary_text': "继续努力，下次会更好！",
            'song_name': "未知歌曲",
            'artist': "未知歌手",
            'performance_score': score,
            'score_level': self._get_score_level(score),
            'share_text': f"🎵 卡拉OK演唱，得分：{score}分\n继续努力，下次会更好！",
            'emotion_tags': ["鼓励"],
            'summary_type': "default",
            'timestamp': datetime.now().isoformat()
        }
    
    def share_to_social_platform(self, 
                               share_content: Dict[str, Any],
                               platform: str) -> bool:
        """
        分享到社交平台
        
        Args:
            share_content: 分享内容
            platform: 社交平台 ('wechat', 'weibo', 'qq', 'douyin')
            
        Returns:
            是否分享成功
        """
        try:
            # 根据不同平台调整分享内容
            platform_content = self._adapt_for_platform(share_content, platform)
            
            # TODO: 实现实际的社交平台分享API调用
            # 这里应该调用各平台的分享API
            
            logger.info(f"分享到{platform}成功")
            return True
            
        except Exception as e:
            logger.error(f"分享到{platform}失败: {e}")
            return False
    
    def _adapt_for_platform(self, 
                           content: Dict[str, Any], 
                           platform: str) -> Dict[str, Any]:
        """根据平台调整内容格式"""
        base_content = content.copy()
        
        platform_configs = {
            'wechat': {
                'max_length': 200,
                'hashtags': False,
                'emoji': True
            },
            'weibo': {
                'max_length': 140,
                'hashtags': True,
                'emoji': True
            },
            'qq': {
                'max_length': 300,
                'hashtags': False,
                'emoji': True
            },
            'douyin': {
                'max_length': 100,
                'hashtags': True,
                'emoji': True
            }
        }
        
        config = platform_configs.get(platform, platform_configs['wechat'])
        
        # 调整文本长度
        if len(base_content['share_text']) > config['max_length']:
            base_content['share_text'] = base_content['share_text'][:config['max_length']-3] + "..."
        
        # 添加话题标签
        if config['hashtags']:
            base_content['share_text'] += f"\n#卡拉OK#{base_content['song_name']}#{base_content['artist']}"
        
        return base_content
    
    def get_share_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户分享统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            分享统计数据
        """
        try:
            # TODO: 从数据库获取用户分享统计
            # 这里应该查询用户分享记录
            
            return {
                'total_shares': 0,
                'platform_shares': {
                    'wechat': 0,
                    'weibo': 0,
                    'qq': 0,
                    'douyin': 0
                },
                'total_score': 0.0,
                'average_score': 0.0,
                'favorite_songs': [],
                'share_trend': []
            }
            
        except Exception as e:
            logger.error(f"获取分享统计失败: {e}")
            return {}
    
    def record_share(self, 
                    user_id: str, 
                    song_id: str, 
                    summary_id: int,
                    platform: str,
                    performance_score: float) -> bool:
        """
        记录分享行为
        
        Args:
            user_id: 用户ID
            song_id: 歌曲ID
            summary_id: 摘要ID
            platform: 分享平台
            performance_score: 演唱得分
            
        Returns:
            是否记录成功
        """
        try:
            # TODO: 记录分享到数据库
            # 更新用户演唱记录表和摘要使用统计表
            
            logger.info(f"记录分享成功: 用户{user_id}分享到{platform}")
            return True
            
        except Exception as e:
            logger.error(f"记录分享失败: {e}")
            return False


# 使用示例
if __name__ == "__main__":
    # 创建摘要管理器
    summary_manager = SummaryManager()
    
    # 创建分享服务
    share_service = ShareService(summary_manager)
    
    # 获取分享内容
    share_content = share_service.get_share_content(
        song_id="song_001",
        performance_score=85.5,
        user_id="user_123"
    )
    
    print("分享内容:")
    print(f"摘要: {share_content['summary_text']}")
    print(f"歌曲: {share_content['song_name']} - {share_content['artist']}")
    print(f"得分: {share_content['performance_score']}")
    print(f"等级: {share_content['score_level']}")
    print(f"分享文本: {share_content['share_text']}")
    
    # 分享到微信
    success = share_service.share_to_social_platform(share_content, 'wechat')
    print(f"分享到微信: {'成功' if success else '失败'}")
