# 音乐工具集合 (SongTools)

一个功能强大的音乐处理工具集合，包含音频处理、歌词管理、卡拉OK制作、MV编辑等多种功能。

## 🎵 功能特性

### 音频处理
- MP3格式转换和压缩
- 音频剪辑和拼接
- 音轨分离（人声/伴奏）
- 音频效果处理（均衡器、混响等）

### 歌词工具
- 歌词同步和编辑
- 歌词搜索和下载
- 歌词时间轴调整
- 多语言歌词支持

### 卡拉OK工具
- 伴奏提取
- 音轨分离
- KTV效果添加
- 卡拉OK文件生成

### MV工具
- 视频格式转换
- 音视频同步
- 视频剪辑
- 特效添加

### 音乐信息
- 元数据编辑
- 音乐识别
- 专辑信息管理
- 标签整理

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行主程序
```bash
python main.py
```

## 📁 项目结构

```
songtools/
├── src/                    # 源代码
│   ├── audio/             # 音频处理模块
│   ├── lyrics/            # 歌词处理模块
│   ├── karaoke/           # 卡拉OK模块
│   ├── video/             # 视频处理模块
│   ├── metadata/          # 元数据处理模块
│   └── utils/             # 通用工具
├── tests/                 # 测试文件
├── docs/                  # 文档
├── examples/              # 使用示例
├── requirements.txt       # 依赖包
└── main.py               # 主程序入口
```

## 🛠️ 技术栈

- **Python 3.8+**
- **FFmpeg** - 音视频处理
- **librosa** - 音频分析
- **pydub** - 音频操作
- **moviepy** - 视频处理
- **tkinter** - GUI界面

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
