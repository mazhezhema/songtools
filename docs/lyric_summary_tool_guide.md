# 歌词摘要生成工具使用指南

## 📋 概述

歌词摘要生成工具是一个专门为卡拉OK系统设计的工具，能够从LRC、KRC等歌词文件中智能提取一句话摘要，用于用户分享。

## 🎯 功能特性

- **多格式支持**: 支持LRC、KRC、自定义格式歌词文件
- **智能摘要**: 基于中国流行歌曲特点，选择最适合分享的经典歌词
- **批量处理**: 支持批量处理多个歌词文件
- **CSV输出**: 生成标准CSV格式，便于后端导入
- **命令行工具**: 提供便捷的命令行接口

## 🚀 使用方法

### 1. 命令行工具

#### 处理单个文件
```bash
python -m src.lyrics.generate_summaries --file song.lrc --id song_001 --name "歌曲名" --output summary.csv
```

#### 批量处理（使用输入文件）
```bash
python -m src.lyrics.generate_summaries --input songs.txt --output summaries.csv
```

#### 扫描目录自动处理
```bash
python -m src.lyrics.generate_summaries --dir songs/ --output summaries.csv
```

### 2. Python API

```python
from src.lyrics import SummaryGenerator, LyricFormat

# 创建生成器
generator = SummaryGenerator()

# 处理单个文件
share_quote = generator.process_lyric_file(
    file_path="song.lrc",
    song_id="song_001", 
    song_name="朋友",
    format_type=LyricFormat.LRC
)

# 批量处理
lyric_files = [
    ("song1.lrc", "song_001", "朋友", LyricFormat.LRC),
    ("song2.krc", "song_002", "月亮代表我的心", LyricFormat.KRC),
]
generator.generate_csv(lyric_files, "summaries.csv")
```

## 📁 输入文件格式

### 1. LRC格式
```
[ti:歌曲名]
[ar:艺术家]
[00:08.00]歌词内容
[00:12.00]更多歌词
```

### 2. KRC格式
```
[0,4000]歌词内容
[4000,8000]更多歌词
```

### 3. 自定义格式
```
# 注释行
00:08 歌词内容
00:12 更多歌词
```

### 4. 批量处理输入文件
```
文件路径,歌曲ID,歌曲名称,格式类型
song1.lrc,song_001,朋友,lrc
song2.krc,song_002,月亮代表我的心,krc
```

## 📊 输出格式

生成的CSV文件包含以下字段：
- `id`: 歌曲ID
- `song_name`: 歌曲名称  
- `summary`: 生成的分享歌词

示例：
```csv
id,song_name,summary
song_001,朋友,朋友一生一起走，那些日子不再有
song_002,月亮代表我的心,月亮代表我的心
```

## 🧠 摘要生成策略

工具采用多种策略来选择最佳摘要：

### 1. 过滤机制
- **避免词汇**: 过滤掉"啊啊啊"、"哦哦哦"等重复词汇
- **长度控制**: 4-20个中文字符
- **重复检测**: 避免纯重复内容

### 2. 评分机制
- **哲理深度**: 包含"一生"、"永远"、"时光"等词汇
- **情感深度**: 包含"爱"、"情"、"心"等情感词汇
- **意象丰富**: 包含"月亮"、"星星"、"风"等自然意象
- **结构优美**: 对仗工整、有标点符号、首尾呼应
- **长度适中**: 6-12个字符最佳

### 3. 经典词汇库
- **哲理类**: 一生、永远、瞬间、时光、岁月、青春、年华
- **情感类**: 爱、情、心、泪、痛、伤、思念、回忆
- **意象类**: 月亮、星星、太阳、风、雨、雪、云、天空
- **时间类**: 昨天、今天、明天、永远、瞬间、时光、岁月

## ⚙️ 配置选项

### 命令行参数
- `--file/-f`: 单个歌词文件路径
- `--input/-i`: 批量处理输入文件
- `--dir/-d`: 扫描目录路径
- `--output/-o`: 输出CSV文件路径
- `--id`: 歌曲ID（单个文件）
- `--name`: 歌曲名称（单个文件）
- `--format`: 文件格式（lrc/krc/custom）
- `--verbose/-v`: 显示详细日志

## 🔧 扩展开发

### 添加新的歌词格式
1. 在`LyricFormat`枚举中添加新格式
2. 实现对应的解析方法
3. 在`process_lyric_file`中添加处理逻辑

### 自定义评分规则
1. 修改`classic_patterns`词汇库
2. 调整`calculate_classic_score`评分逻辑
3. 更新`avoid_words`过滤词汇

## ❓ 常见问题

### Q: 为什么某些歌词没有被选中？
A: 可能因为包含避免词汇、长度不合适或重复度过高。

### Q: 如何处理加密的KRC文件？
A: 当前版本提供基础解析，复杂加密需要额外解密步骤。

### Q: 可以自定义评分规则吗？
A: 可以修改`SummaryGenerator`类中的相关方法。

### Q: 支持哪些字符编码？
A: 默认使用UTF-8编码，确保歌词文件编码正确。

## 📝 更新日志

### v1.0.0 (2025-08-23)
- 初始版本发布
- 支持LRC、KRC、自定义格式
- 实现智能摘要生成算法
- 提供命令行和Python API
- 支持批量处理功能
