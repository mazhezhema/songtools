#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebP图片重命名工具
支持批量重命名WebP图片文件，提供多种命名规则
"""

import os
import sys
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WebPRenamer:
    """WebP图片重命名器"""
    
    def __init__(self):
        self.supported_formats = ['.webp', '.WEBP']
        self.rename_rules = {
            'sequential': self._sequential_rename,
            'timestamp': self._timestamp_rename,
            'clean': self._clean_rename,
            'custom': self._custom_rename
        }
    
    def get_webp_files(self, directory: str) -> List[Path]:
        """
        获取目录中的所有WebP文件
        
        Args:
            directory: 目录路径
            
        Returns:
            WebP文件路径列表
        """
        webp_files = []
        for ext in self.supported_formats:
            webp_files.extend(Path(directory).glob(f"*{ext}"))
        
        return sorted(webp_files)
    
    def _sequential_rename(self, files: List[Path], prefix: str = "image", 
                          start_num: int = 1, padding: int = 3) -> List[Tuple[Path, Path]]:
        """
        顺序重命名规则
        
        Args:
            files: 文件列表
            prefix: 文件名前缀
            start_num: 起始编号
            padding: 数字填充位数
            
        Returns:
            (原路径, 新路径) 元组列表
        """
        rename_list = []
        for i, file_path in enumerate(files):
            new_name = f"{prefix}_{str(start_num + i).zfill(padding)}.webp"
            new_path = file_path.parent / new_name
            rename_list.append((file_path, new_path))
        
        return rename_list
    
    def _timestamp_rename(self, files: List[Path], prefix: str = "image") -> List[Tuple[Path, Path]]:
        """
        时间戳重命名规则
        
        Args:
            files: 文件列表
            prefix: 文件名前缀
            
        Returns:
            (原路径, 新路径) 元组列表
        """
        rename_list = []
        for file_path in files:
            # 获取文件修改时间
            mtime = file_path.stat().st_mtime
            timestamp = datetime.fromtimestamp(mtime).strftime("%Y%m%d_%H%M%S")
            new_name = f"{prefix}_{timestamp}.webp"
            new_path = file_path.parent / new_name
            rename_list.append((file_path, new_path))
        
        return rename_list
    
    def _clean_rename(self, files: List[Path], prefix: str = "image") -> List[Tuple[Path, Path]]:
        """
        清理重命名规则（去除特殊字符）
        
        Args:
            files: 文件列表
            prefix: 文件名前缀
            
        Returns:
            (原路径, 新路径) 元组列表
        """
        rename_list = []
        for i, file_path in enumerate(files):
            # 清理文件名，只保留字母、数字、下划线和连字符
            clean_name = re.sub(r'[^\w\-]', '_', file_path.stem)
            clean_name = re.sub(r'_+', '_', clean_name)  # 合并多个下划线
            clean_name = clean_name.strip('_')  # 去除首尾下划线
            
            if not clean_name:
                clean_name = f"{prefix}_{i+1}"
            
            new_name = f"{clean_name}.webp"
            new_path = file_path.parent / new_name
            rename_list.append((file_path, new_path))
        
        return rename_list
    
    def _custom_rename(self, files: List[Path], pattern: str) -> List[Tuple[Path, Path]]:
        """
        自定义重命名规则
        
        Args:
            files: 文件列表
            pattern: 自定义模式，支持 {index}, {name}, {timestamp} 变量
            
        Returns:
            (原路径, 新路径) 元组列表
        """
        rename_list = []
        for i, file_path in enumerate(files):
            # 替换模式中的变量
            new_name = pattern.replace('{index}', str(i + 1))
            new_name = new_name.replace('{name}', file_path.stem)
            new_name = new_name.replace('{timestamp}', 
                                      datetime.now().strftime("%Y%m%d_%H%M%S"))
            
            # 确保以.webp结尾
            if not new_name.endswith('.webp'):
                new_name += '.webp'
            
            new_path = file_path.parent / new_name
            rename_list.append((file_path, new_path))
        
        return rename_list
    
    def generate_rename_plan(self, files: List[Path], rule: str, **kwargs) -> List[Tuple[Path, Path]]:
        """
        生成重命名计划
        
        Args:
            files: 文件列表
            rule: 重命名规则
            **kwargs: 规则参数
            
        Returns:
            (原路径, 新路径) 元组列表
        """
        if rule not in self.rename_rules:
            raise ValueError(f"不支持的重命名规则: {rule}")
        
        return self.rename_rules[rule](files, **kwargs)
    
    def execute_rename(self, rename_plan: List[Tuple[Path, Path]], 
                      dry_run: bool = False) -> Dict[str, int]:
        """
        执行重命名操作
        
        Args:
            rename_plan: 重命名计划
            dry_run: 是否只是预览，不实际执行
            
        Returns:
            执行结果统计
        """
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for old_path, new_path in rename_plan:
            try:
                # 检查新路径是否已存在
                if new_path.exists() and new_path != old_path:
                    logger.warning(f"目标文件已存在，跳过: {new_path}")
                    results["skipped"] += 1
                    continue
                
                # 检查是否重命名为自己
                if old_path == new_path:
                    logger.info(f"文件名无需更改，跳过: {old_path}")
                    results["skipped"] += 1
                    continue
                
                if not dry_run:
                    # 执行重命名
                    old_path.rename(new_path)
                    logger.info(f"重命名成功: {old_path.name} -> {new_path.name}")
                else:
                    logger.info(f"预览: {old_path.name} -> {new_path.name}")
                
                results["success"] += 1
                
            except Exception as e:
                logger.error(f"重命名失败: {old_path} -> {new_path}, 错误: {str(e)}")
                results["failed"] += 1
        
        return results
    
    def batch_rename(self, directory: str, rule: str, **kwargs) -> Dict[str, int]:
        """
        批量重命名目录中的WebP文件
        
        Args:
            directory: 目录路径
            rule: 重命名规则
            **kwargs: 规则参数
            
        Returns:
            执行结果统计
        """
        # 获取WebP文件
        webp_files = self.get_webp_files(directory)
        
        if not webp_files:
            logger.warning(f"在目录 {directory} 中未找到WebP文件")
            return {"success": 0, "failed": 0, "skipped": 0, "total": 0}
        
        logger.info(f"找到 {len(webp_files)} 个WebP文件")
        
        # 生成重命名计划
        rename_plan = self.generate_rename_plan(webp_files, rule, **kwargs)
        
        # 执行重命名
        results = self.execute_rename(rename_plan)
        results["total"] = len(webp_files)
        
        return results


class WebPRenamerGUI:
    """WebP重命名器GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WebP图片重命名工具")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        self.renamer = WebPRenamer()
        self.input_dir = ""
        self.rename_plan = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="🖼️ WebP图片重命名工具", 
                               font=('微软雅黑', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 目录选择区域
        dir_frame = ttk.LabelFrame(main_frame, text="目录选择", padding="10")
        dir_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(dir_frame, text="选择包含WebP文件的目录:").pack(anchor='w')
        dir_select_frame = ttk.Frame(dir_frame)
        dir_select_frame.pack(fill='x', pady=(5, 0))
        
        self.dir_var = tk.StringVar()
        ttk.Entry(dir_select_frame, textvariable=self.dir_var, 
                 state='readonly').pack(side='left', fill='x', expand=True)
        ttk.Button(dir_select_frame, text="选择目录", 
                  command=self.select_directory).pack(side='right', padx=(10, 0))
        
        # 重命名规则区域
        rule_frame = ttk.LabelFrame(main_frame, text="重命名规则", padding="10")
        rule_frame.pack(fill='x', pady=(0, 10))
        
        # 规则选择
        ttk.Label(rule_frame, text="选择重命名规则:").pack(anchor='w')
        self.rule_var = tk.StringVar(value="sequential")
        
        rules_frame = ttk.Frame(rule_frame)
        rules_frame.pack(fill='x', pady=(5, 10))
        
        rules = [
            ("sequential", "顺序编号", "image_001.webp, image_002.webp..."),
            ("timestamp", "时间戳", "image_20250101_143022.webp"),
            ("clean", "清理文件名", "去除特殊字符，保留字母数字"),
            ("custom", "自定义模式", "支持 {index}, {name}, {timestamp} 变量")
        ]
        
        for i, (value, text, desc) in enumerate(rules):
            row = i // 2
            col = i % 2
            
            rule_btn = ttk.Radiobutton(rules_frame, text=text, variable=self.rule_var, 
                                      value=value, command=self.on_rule_change)
            rule_btn.grid(row=row, column=col*2, sticky='w', padx=(0, 20), pady=2)
            
            desc_label = ttk.Label(rules_frame, text=desc, font=('微软雅黑', 8), 
                                  foreground='#666')
            desc_label.grid(row=row, column=col*2+1, sticky='w', padx=(0, 20))
        
        # 参数设置区域
        self.params_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        self.params_frame.pack(fill='x', pady=(0, 10))
        
        self.setup_rule_params()
        
        # 文件预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="重命名预览", padding="10")
        preview_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 预览列表
        columns = ('原文件名', '新文件名', '状态')
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient='vertical', command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preview_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(control_frame, text="预览重命名", 
                  command=self.preview_rename).pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="执行重命名", 
                  command=self.execute_rename, style='Accent.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(control_frame, text="清空预览", 
                  command=self.clear_preview).pack(side='left')
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(anchor='w')
        
    def setup_rule_params(self):
        """设置规则参数界面"""
        # 清空现有控件
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        rule = self.rule_var.get()
        
        if rule == "sequential":
            # 顺序编号参数
            ttk.Label(self.params_frame, text="文件名前缀:").grid(row=0, column=0, sticky='w', padx=(0, 10))
            self.prefix_var = tk.StringVar(value="image")
            ttk.Entry(self.params_frame, textvariable=self.prefix_var, width=15).grid(row=0, column=1, padx=(0, 20))
            
            ttk.Label(self.params_frame, text="起始编号:").grid(row=0, column=2, sticky='w', padx=(0, 10))
            self.start_num_var = tk.IntVar(value=1)
            ttk.Spinbox(self.params_frame, from_=1, to=9999, textvariable=self.start_num_var, width=10).grid(row=0, column=3, padx=(0, 20))
            
            ttk.Label(self.params_frame, text="数字位数:").grid(row=0, column=4, sticky='w', padx=(0, 10))
            self.padding_var = tk.IntVar(value=3)
            ttk.Spinbox(self.params_frame, from_=1, to=6, textvariable=self.padding_var, width=10).grid(row=0, column=5)
            
        elif rule == "timestamp":
            # 时间戳参数
            ttk.Label(self.params_frame, text="文件名前缀:").grid(row=0, column=0, sticky='w', padx=(0, 10))
            self.prefix_var = tk.StringVar(value="image")
            ttk.Entry(self.params_frame, textvariable=self.prefix_var, width=15).grid(row=0, column=1)
            
        elif rule == "clean":
            # 清理文件名参数
            ttk.Label(self.params_frame, text="文件名前缀:").grid(row=0, column=0, sticky='w', padx=(0, 10))
            self.prefix_var = tk.StringVar(value="image")
            ttk.Entry(self.params_frame, textvariable=self.prefix_var, width=15).grid(row=0, column=1)
            
        elif rule == "custom":
            # 自定义模式参数
            ttk.Label(self.params_frame, text="自定义模式:").grid(row=0, column=0, sticky='w', padx=(0, 10))
            self.pattern_var = tk.StringVar(value="{name}_{index}")
            ttk.Entry(self.params_frame, textvariable=self.pattern_var, width=30).grid(row=0, column=1, padx=(0, 20))
            
            ttk.Label(self.params_frame, text="支持变量: {index}, {name}, {timestamp}", 
                     font=('微软雅黑', 8), foreground='#666').grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))
    
    def on_rule_change(self):
        """规则改变时的回调"""
        self.setup_rule_params()
        self.clear_preview()
    
    def select_directory(self):
        """选择目录"""
        directory = filedialog.askdirectory(title="选择包含WebP文件的目录")
        if directory:
            self.input_dir = directory
            self.dir_var.set(directory)
            self.status_var.set(f"已选择目录: {directory}")
            self.clear_preview()
    
    def preview_rename(self):
        """预览重命名"""
        if not self.input_dir:
            messagebox.showwarning("警告", "请先选择目录")
            return
        
        try:
            # 获取WebP文件
            webp_files = self.renamer.get_webp_files(self.input_dir)
            
            if not webp_files:
                messagebox.showinfo("提示", "所选目录中没有找到WebP文件")
                return
            
            # 获取参数
            rule = self.rule_var.get()
            kwargs = self.get_rule_params()
            
            # 生成重命名计划
            self.rename_plan = self.renamer.generate_rename_plan(webp_files, rule, **kwargs)
            
            # 更新预览列表
            self.update_preview()
            
            self.status_var.set(f"预览完成，共 {len(self.rename_plan)} 个文件")
            
        except Exception as e:
            messagebox.showerror("错误", f"预览失败: {str(e)}")
    
    def get_rule_params(self):
        """获取规则参数"""
        rule = self.rule_var.get()
        kwargs = {}
        
        if rule in ["sequential", "timestamp", "clean"]:
            kwargs["prefix"] = self.prefix_var.get()
            if rule == "sequential":
                kwargs["start_num"] = self.start_num_var.get()
                kwargs["padding"] = self.padding_var.get()
        elif rule == "custom":
            kwargs["pattern"] = self.pattern_var.get()
        
        return kwargs
    
    def update_preview(self):
        """更新预览列表"""
        # 清空现有项目
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 添加预览项目
        for old_path, new_path in self.rename_plan:
            status = "无需更改" if old_path == new_path else "将重命名"
            self.preview_tree.insert('', 'end', values=(
                old_path.name,
                new_path.name,
                status
            ))
    
    def clear_preview(self):
        """清空预览"""
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        self.rename_plan = []
        self.status_var.set("预览已清空")
    
    def execute_rename(self):
        """执行重命名"""
        if not self.rename_plan:
            messagebox.showwarning("警告", "请先预览重命名")
            return
        
        # 确认对话框
        result = messagebox.askyesno("确认", f"确定要重命名 {len(self.rename_plan)} 个文件吗？\n此操作不可撤销！")
        if not result:
            return
        
        try:
            # 执行重命名
            results = self.renamer.execute_rename(self.rename_plan)
            
            # 显示结果
            message = f"重命名完成！\n成功: {results['success']} 个\n失败: {results['failed']} 个\n跳过: {results['skipped']} 个"
            messagebox.showinfo("完成", message)
            
            self.status_var.set(f"重命名完成 - 成功: {results['success']}, 失败: {results['failed']}")
            
            # 清空预览
            self.clear_preview()
            
        except Exception as e:
            messagebox.showerror("错误", f"重命名失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = WebPRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
