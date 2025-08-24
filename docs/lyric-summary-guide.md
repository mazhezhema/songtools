# 歌词摘要生成工具使用指南

## 📋 概述

歌词摘要生成工具是一个专门为卡拉OK系统设计的工具，能够从LRC、KRC等歌词文件中智能提取一句话摘要，用于用户分享。

## 🎯 功能特性

- **多格式支持**: 支持LRC、KRC、自定义格式歌词文件
- **智能摘要**: 基于情感分析、重复度、长度等多维度选择最佳摘要
- **批量处理**: 支持批量处理多个歌词文件
- **CSV输出**: 生成标准CSV格式，便于后端导入
- **命令行工具**: 提供便捷的命令行接口

## 📁 输出格式

生成的CSV文件包含三个字段：
- `id`: 歌曲ID
- `song_name`: 歌曲名称  
- `summary`: 摘要文本

示例：
```csv
id,song_name,summary
song_001,朋友,朋友一生一起走，那些日子不再有
song_002,月亮代表我的心,你问我爱你有多深，我爱你有几分
song_003,青花瓷,天青色等烟雨，而我在等你
```

## 🚀 使用方法

### 1. 命令行工具

#### 处理单个文件
```bash
python generate_summaries.py --file song.lrc --id song_001 --name "歌曲名" --output summary.csv
```

#### 批量处理（使用输入文件）
```bash
# 创建输入文件 songs.txt
echo "song_001,朋友,songs/song1.lrc,lrc" > songs.txt
echo "song_002,月亮代表我的心,songs/song2.krc,krc" >> songs.txt

# 批量处理
python generate_summaries.py --input songs.txt --output summaries.csv
```

#### 扫描目录
```bash
python generate_summaries.py --dir songs/ --output summaries.csv
```

### 2. Python API

#### 处理单个文件
```python
from src.lyrics.summary_generator import SummaryGenerator, LyricFormat

generator = SummaryGenerator()

summary = generator.process_lyric_file(
    file_path="song.lrc",
    song_id="song_001", 
    song_name="朋友",
    format_type=LyricFormat.LRC
)

print(f"摘要: {summary}")
```

#### 批量处理
```python
from src.lyrics.summary_generator import SummaryGenerator, LyricFormat

generator = SummaryGenerator()

lyric_files = [
    ("song1.lrc", "song_001", "朋友", LyricFormat.LRC),
    ("song2.krc", "song_002", "月亮代表我的心", LyricFormat.KRC),
    ("song3.txt", "song_003", "青花瓷", LyricFormat.CUSTOM),
]

generator.generate_csv(lyric_files, "summaries.csv")
```

## 📝 输入文件格式

### 1. LRC格式
```lrc
[ti:朋友]
[ar:周华健]
[al:朋友]

[00:12.00]这些年 一个人
[00:15.00]风也过 雨也走
[00:18.00]有过泪 有过错
[00:21.00]还记得坚持什么

[00:33.00]朋友 一生一起走
[00:36.00]那些日子 不再有
[00:39.00]一句话 一辈子
[00:42.00]一生情 一杯酒
```

### 2. KRC格式
```krc
[0,3000]朋友 一生一起走
[3000,6000]那些日子 不再有
[6000,9000]一句话 一辈子
[9000,12000]一生情 一杯酒
```

### 3. 自定义格式
```txt
# 自定义格式歌词文件
00:12 这些年 一个人
00:15 风也过 雨也走
00:18 有过泪 有过错
00:21 还记得坚持什么
00:33 朋友 一生一起走
00:36 那些日子 不再有
```

### 4. 批量处理输入文件
```txt
# 歌词文件列表
# 格式: id,歌名,文件路径,格式
song_001,朋友,songs/song1.lrc,lrc
song_002,月亮代表我的心,songs/song2.krc,krc
song_003,青花瓷,songs/song3.txt,custom
```

## 🧠 摘要生成策略

工具采用多种策略来选择最佳摘要：

### 1. 长度策略
- 优先选择8-20字的歌词行
- 避免过短或过长的句子

### 2. 情感策略
- 识别包含情感关键词的歌词
- 正面情感：爱、快乐、幸福、美好、温暖、希望等
- 负面情感：伤、痛、泪、寂寞、孤独、失去等
- 力量情感：勇敢、坚强、奋斗、力量、胜利等

### 3. 重复度策略
- 识别重复出现的歌词行（通常是副歌）
- 优先选择重复度高的句子

### 4. 位置策略
- 选择歌曲中间部分的歌词
- 避免开头和结尾的过渡部分

### 5. 完整性策略
- 优先选择有标点符号的完整句子
- 避免断句或不完整的歌词

## ⚙️ 配置选项

### 命令行参数
- `--input, -i`: 输入文件路径
- `--dir, -d`: 扫描目录路径
- `--file, -f`: 单个歌词文件路径
- `--output, -o`: 输出CSV文件路径
- `--id`: 歌曲ID（单个文件）
- `--name`: 歌曲名称（单个文件）
- `--format`: 歌词格式（lrc/krc/custom）
- `--verbose, -v`: 详细输出

### 情感关键词配置
可以在代码中修改情感关键词：
```python
self.emotion_keywords = {
    'positive': ['爱', '快乐', '幸福', '美好', '温暖', '希望'],
    'negative': ['伤', '痛', '泪', '寂寞', '孤独', '失去'],
    'powerful': ['勇敢', '坚强', '奋斗', '力量', '胜利']
}
```

## 🔧 扩展开发

### 添加新的歌词格式
1. 在`LyricFormat`枚举中添加新格式
2. 实现对应的解析方法（如`parse_new_format_file`）
3. 在`process_lyric_file`方法中添加格式判断

### 自定义摘要策略
1. 修改`generate_summary`方法
2. 添加新的选择策略
3. 调整评分权重

### 集成到现有系统
```python
# 示例：集成到现有数据库系统
def import_summaries_to_db(csv_file, db_connection):
    import csv
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 插入到数据库
            query = "INSERT INTO lyric_summaries (song_id, song_name, summary_text) VALUES (%s, %s, %s)"
            db_connection.execute(query, (row['id'], row['song_name'], row['summary']))
```

## 🐛 常见问题

### Q: 解析LRC文件失败
A: 检查文件编码是否为UTF-8，确保时间标签格式正确

### Q: KRC文件无法解析
A: KRC文件通常需要解密，当前版本提供基础解析，复杂加密需要额外处理

### Q: 生成的摘要质量不高
A: 可以调整情感关键词或修改评分策略

### Q: 批量处理时部分文件失败
A: 检查文件路径是否正确，格式是否支持

## 📞 技术支持

如有问题，请查看：
1. 日志输出信息
2. 示例文件格式
3. 错误处理机制

---

*最后更新: 2025年8月23日*
