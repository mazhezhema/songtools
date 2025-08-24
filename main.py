#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐工具集合主程序
提供GUI界面来访问各种音乐处理工具
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class SongToolsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("音乐工具集合 - SongTools")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 设置图标和样式
        self.setup_styles()
        
        # 创建主界面
        self.create_main_interface()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Tool.TButton',
                        font=('微软雅黑', 12, 'bold'),
                        padding=10,
                        background='#4CAF50',
                        foreground='white')
        
        # 配置标签样式
        style.configure('Title.TLabel',
                        font=('微软雅黑', 16, 'bold'),
                        foreground='#2196F3')
        
    def create_main_interface(self):
        """创建主界面"""
        # 标题
        title_label = ttk.Label(self.root, 
                               text="🎵 音乐工具集合", 
                               style='Title.TLabel')
        title_label.pack(pady=20)
        
        # 副标题
        subtitle_label = ttk.Label(self.root, 
                                  text="SongTools - 专业的音乐处理工具集",
                                  font=('微软雅黑', 10),
                                  foreground='#666')
        subtitle_label.pack(pady=5)
        
        # 创建工具按钮框架
        tools_frame = ttk.Frame(self.root)
        tools_frame.pack(pady=30, padx=50, fill='both', expand=True)
        
        # 工具按钮
        tools = [
            ("🎵 音频处理", self.open_audio_tools, "MP3转换、音频剪辑、音轨分离"),
            ("📝 歌词工具", self.open_lyrics_tools, "歌词同步、编辑、搜索"),
            ("🎤 卡拉OK", self.open_karaoke_tools, "伴奏提取、KTV效果"),
            ("🎬 MV工具", self.open_video_tools, "视频处理、音视频同步"),
            ("ℹ️ 音乐信息", self.open_metadata_tools, "元数据编辑、音乐识别"),
            ("⚙️ 设置", self.open_settings, "程序设置和配置")
        ]
        
        # 创建按钮网格
        for i, (text, command, tooltip) in enumerate(tools):
            row = i // 2
            col = i % 2
            
            # 创建按钮框架
            button_frame = ttk.Frame(tools_frame)
            button_frame.grid(row=row, column=col, padx=20, pady=15, sticky='ew')
            
            # 创建按钮
            btn = ttk.Button(button_frame, 
                           text=text, 
                           command=command,
                           style='Tool.TButton')
            btn.pack(fill='x', pady=5)
            
            # 创建提示标签
            tip_label = ttk.Label(button_frame, 
                                text=tooltip,
                                font=('微软雅黑', 9),
                                foreground='#888',
                                wraplength=200)
            tip_label.pack()
        
        # 配置网格权重
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        # 底部信息
        info_frame = ttk.Frame(self.root)
        info_frame.pack(side='bottom', fill='x', padx=20, pady=10)
        
        version_label = ttk.Label(info_frame, 
                                text="版本 1.0.0 | 作者: SongTools Team",
                                font=('微软雅黑', 8),
                                foreground='#999')
        version_label.pack(side='left')
        
        help_label = ttk.Label(info_frame, 
                             text="帮助文档",
                             font=('微软雅黑', 8),
                             foreground='#2196F3',
                             cursor='hand2')
        help_label.pack(side='right')
        help_label.bind('<Button-1>', self.show_help)
        
    def open_audio_tools(self):
        """打开音频处理工具"""
        try:
            from audio.audio_processor import AudioProcessorGUI
            audio_window = tk.Toplevel(self.root)
            AudioProcessorGUI(audio_window)
        except ImportError:
            messagebox.showwarning("功能开发中", "音频处理工具正在开发中，敬请期待！")
    
    def open_lyrics_tools(self):
        """打开歌词工具"""
        try:
            from lyrics.lyrics_manager import LyricsManagerGUI
            lyrics_window = tk.Toplevel(self.root)
            LyricsManagerGUI(lyrics_window)
        except ImportError:
            messagebox.showwarning("功能开发中", "歌词工具正在开发中，敬请期待！")
    
    def open_karaoke_tools(self):
        """打开卡拉OK工具"""
        try:
            from karaoke.karaoke_maker import KaraokeMakerGUI
            karaoke_window = tk.Toplevel(self.root)
            KaraokeMakerGUI(karaoke_window)
        except ImportError:
            messagebox.showwarning("功能开发中", "卡拉OK工具正在开发中，敬请期待！")
    
    def open_video_tools(self):
        """打开视频工具"""
        try:
            from video.video_processor import VideoProcessorGUI
            video_window = tk.Toplevel(self.root)
            VideoProcessorGUI(video_window)
        except ImportError:
            messagebox.showwarning("功能开发中", "视频工具正在开发中，敬请期待！")
    
    def open_metadata_tools(self):
        """打开元数据工具"""
        try:
            from metadata.metadata_editor import MetadataEditorGUI
            metadata_window = tk.Toplevel(self.root)
            MetadataEditorGUI(metadata_window)
        except ImportError:
            messagebox.showwarning("功能开发中", "元数据工具正在开发中，敬请期待！")
    
    def open_settings(self):
        """打开设置"""
        messagebox.showinfo("设置", "设置功能正在开发中！")
    
    def show_help(self, event=None):
        """显示帮助文档"""
        help_text = """
音乐工具集合使用说明：

1. 音频处理：支持MP3转换、音频剪辑、音轨分离等功能
2. 歌词工具：提供歌词同步、编辑、搜索等工具
3. 卡拉OK：支持伴奏提取、KTV效果添加
4. MV工具：视频处理、音视频同步
5. 音乐信息：元数据编辑、音乐识别

更多详细说明请查看docs目录下的文档。
        """
        messagebox.showinfo("帮助", help_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = SongToolsGUI(root)
    
    # 设置窗口居中
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()
