# 数据库表结构设计

## 📊 歌词摘要表 (lyric_summaries)

### 表结构
```sql
CREATE TABLE lyric_summaries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    song_id VARCHAR(50) NOT NULL COMMENT '歌曲ID',
    song_name VARCHAR(200) NOT NULL COMMENT '歌曲名称',
    artist VARCHAR(100) NOT NULL COMMENT '艺术家',
    
    -- 摘要信息
    summary_text VARCHAR(200) NOT NULL COMMENT '摘要文本',
    summary_type ENUM('emotional', 'structural', 'performance', 'hybrid') NOT NULL COMMENT '摘要类型',
    summary_score FLOAT DEFAULT 0.0 COMMENT '摘要质量分数',
    
    -- 歌词上下文
    start_time FLOAT COMMENT '开始时间（秒）',
    end_time FLOAT COMMENT '结束时间（秒）',
    lyric_context TEXT COMMENT '歌词上下文',
    
    -- 标签和分类
    emotion_tags JSON COMMENT '情感标签',
    difficulty_level ENUM('easy', 'medium', 'hard') DEFAULT 'medium' COMMENT '难度等级',
    popularity_score FLOAT DEFAULT 0.0 COMMENT '受欢迎度分数',
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    
    -- 索引
    INDEX idx_song_id (song_id),
    INDEX idx_summary_type (summary_type),
    INDEX idx_difficulty (difficulty_level),
    INDEX idx_popularity (popularity_score DESC),
    INDEX idx_emotion_tags ((CAST(emotion_tags AS CHAR(100))))
);
```

### 示例数据
```sql
INSERT INTO lyric_summaries VALUES
(1, 'song_001', '朋友', '周华健', '朋友一生一起走，那些日子不再有', 'emotional', 9.5, 45.2, 52.8, '朋友一生一起走，那些日子不再有，一句话，一辈子，一生情，一杯酒', '["友情", "回忆", "温暖"]', 'medium', 8.9, NOW(), NOW(), TRUE),
(2, 'song_001', '朋友', '周华健', '一句话，一辈子，一生情，一杯酒', 'structural', 8.8, 52.8, 60.5, '朋友一生一起走，那些日子不再有，一句话，一辈子，一生情，一杯酒', '["友情", "承诺", "深情"]', 'medium', 8.7, NOW(), NOW(), TRUE),
(3, 'song_002', '月亮代表我的心', '邓丽君', '你问我爱你有多深，我爱你有几分', 'emotional', 9.2, 30.5, 38.2, '你问我爱你有多深，我爱你有几分，我的情也真，我的爱也真', '["爱情", "深情", "浪漫"]', 'easy', 9.1, NOW(), NOW(), TRUE);
```

## 🎵 歌曲信息表 (songs)

### 表结构
```sql
CREATE TABLE songs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    album VARCHAR(200),
    duration FLOAT COMMENT '时长（秒）',
    genre VARCHAR(50),
    language VARCHAR(20) DEFAULT 'zh-CN',
    release_year INT,
    popularity_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🎤 用户演唱记录表 (user_performances)

### 表结构
```sql
CREATE TABLE user_performances (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(50) NOT NULL,
    song_id VARCHAR(50) NOT NULL,
    performance_score FLOAT NOT NULL COMMENT '演唱得分',
    summary_id BIGINT COMMENT '使用的摘要ID',
    
    -- 演唱数据
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    duration FLOAT COMMENT '演唱时长（秒）',
    
    -- 分享相关
    shared_to_social BOOLEAN DEFAULT FALSE,
    share_timestamp TIMESTAMP NULL,
    social_platform VARCHAR(50) NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (summary_id) REFERENCES lyric_summaries(id),
    INDEX idx_user_song (user_id, song_id),
    INDEX idx_performance_score (performance_score DESC)
);
```

## 📈 摘要使用统计表 (summary_usage_stats)

### 表结构
```sql
CREATE TABLE summary_usage_stats (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    summary_id BIGINT NOT NULL,
    usage_count INT DEFAULT 0 COMMENT '使用次数',
    share_count INT DEFAULT 0 COMMENT '分享次数',
    avg_performance_score FLOAT DEFAULT 0.0 COMMENT '平均演唱得分',
    last_used_at TIMESTAMP NULL,
    
    FOREIGN KEY (summary_id) REFERENCES lyric_summaries(id),
    INDEX idx_usage_count (usage_count DESC),
    INDEX idx_share_count (share_count DESC)
);
```
