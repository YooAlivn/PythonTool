import sys
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QFileDialog,
    QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QPalette, QColor
import yt_dlp


class YtDlpCustomLogger:
    def __init__(self, log_signal):
        self.log_signal = log_signal
    def debug(self, msg):
        """处理debug信息"""
        self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def info(self, msg):
        """处理普通信息"""
        self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def warning(self, msg):
        """处理警告信息"""
        self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

    def error(self, msg):
        """处理错误信息"""
        self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# 下载线程类（模拟下载过程，实际使用时替换为真实下载逻辑）
class DownloadThread(QThread):
    """下载线程，避免UI阻塞"""
    log_signal = pyqtSignal(str)  # 日志信号
    finish_signal = pyqtSignal(bool)  # 完成信号

    def __init__(self, window_param):
        super().__init__()
        self.save_path = window_param.get("save_path")
        self.media_type = window_param.get("media_type")
        self.media_url = window_param.get("media_url")
        self.cookie_file = window_param.get("cookie_file")

    def run(self):
        try:
            # 模拟下载过程（实际使用时替换为真实下载逻辑）
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始下载 {self.media_type} 媒体文件")
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 保存路径: {self.save_path}")
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 媒体地址: {self.media_url}")
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cookie地址: {self.cookie_file}")

            ydl_opts = {
                'format': self.media_type,
                'logger' : YtDlpCustomLogger(self.log_signal),
                'paths' : {
                    'home' : self.save_path,
                    'thumbnail' : self.save_path
                },
                'writethumbnail' : True,
                'noplaylist': True,
                # FFmpeg路径
                'ffmpeg': 'F:/downloader/ffmpeg-2025-08-18-git-0226b6fb2c-full_build/bin/ffmpeg.exe',
                'outtmpl': '%(title)s.%(ext)s'

            }
            # 设置Cookie
            if self.cookie_file:
                ydl_opts['cookiefile'] = self.cookie_file

                # 开始下载
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.media_url])

            # 模拟下载完成
            filename = os.path.basename(self.media_url) or f"download_{int(time.time())}.{self.media_type}"
            full_path = os.path.join(self.save_path, filename)
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 下载完成！文件保存至: {full_path}")
            self.finish_signal.emit(True)

        except Exception as e:
            self.log_signal.emit(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 下载失败: {str(e)}")
            self.finish_signal.emit(False)


# 主窗口类
class MediaDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.download_thread = None
        self.center_window_manual()  # 手动计算居中

    def center_window_manual(self):
        """手动计算并设置窗口居中"""
        # 获取屏幕宽度和高度
        screen_width = QApplication.primaryScreen().geometry().width()
        screen_height = QApplication.primaryScreen().geometry().height()
        # 获取窗口宽度和高度
        window_width = self.width()
        window_height = self.height()
        # 计算窗口左上角坐标
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        # 移动窗口
        self.move(x, y)

    def init_ui(self):
        # 窗口基本设置
        self.setWindowTitle("媒体下载器")
        self.setGeometry(100, 100, 800, 600)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 1. 媒体存放位置区域
        save_layout = QHBoxLayout()
        save_label = QLabel("保存位置:")
        save_label.setFixedWidth(80)
        self.save_edit = QLineEdit()
        self.save_edit.setPlaceholderText("选择媒体文件保存的路径...")
        self.save_edit.setReadOnly(True)
        default_save_path = f'D:/yutobe/{time.strftime('%Y-%m-%d')}'
        self.save_edit.setText(default_save_path)
        if not os.path.exists(default_save_path):
            os.makedirs(default_save_path, exist_ok=True)
        save_btn = QPushButton("浏览")
        save_btn.clicked.connect(self.select_save_path)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_edit)
        save_layout.addWidget(save_btn)

        # 1. 媒体存放位置区域
        cookie_layout = QHBoxLayout()
        cookie_label = QLabel("Cookie位置:")
        cookie_label.setFixedWidth(80)
        self.cookie_edit = QLineEdit()
        self.cookie_edit.setPlaceholderText("选择Cookie文件保存的路径...")
        self.cookie_edit.setReadOnly(True)
        cookie_btn = QPushButton("浏览")
        cookie_btn.clicked.connect(self.select_cookie_path)
        cookie_clear_btn = QPushButton("清空")
        cookie_clear_btn.clicked.connect(self.clear_cookie_path)
        cookie_layout.addWidget(cookie_label)
        cookie_layout.addWidget(self.cookie_edit)
        cookie_layout.addWidget(cookie_btn)
        cookie_layout.addWidget(cookie_clear_btn)

        # 2. 媒体类型选择区域
        type_layout = QHBoxLayout()
        type_label = QLabel("媒体类型:")
        type_label.setFixedWidth(80)
        self.type_combo = QComboBox()
        # 添加常见媒体类型
        self.type_combo.addItems(["bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b", "bestvideo*+bestaudio/best",
                                  "bv*+ba/b", "bv+ba/b"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)

        # 3. 媒体地址输入区域
        url_layout = QHBoxLayout()
        url_label = QLabel("媒体地址:")
        url_label.setFixedWidth(80)
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("输入媒体文件的URL地址...")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_edit)

        # 4. 开始下载按钮
        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("开始下载")
        self.download_btn.setFixedHeight(30)
        self.download_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addStretch()

        # 5. 日志输出框
        log_layout = QVBoxLayout()
        log_label = QLabel("操作日志:")
        self.log_edit = QTextEdit()
        # 设置黑色背景日志框
        self.log_edit.setReadOnly(True)  # 只读
        self.log_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: Consolas, monospace;
                font-size: 12px;
                border: 1px solid #444444;
                padding: 8px;
            }
        """)
        # 初始日志
        self.append_log("欢迎使用媒体下载器！")
        self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 程序已启动")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_edit)

        # 将所有布局添加到主布局
        main_layout.addLayout(save_layout)
        main_layout.addLayout(cookie_layout)
        main_layout.addLayout(type_layout)
        main_layout.addLayout(url_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(log_layout)

    def select_save_path(self):
        """选择保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择保存位置", self.save_edit.text())
        if path:
            self.save_edit.setText(path)
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已选择保存路径: {path}")

    def select_cookie_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择Cookie位置", r'D:\yutobe\cookiefile', '文本文件 (*.txt)')
        if path:
            self.cookie_edit.setText(path)
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 已选择Cookie路径: {path}")
        else:
            self.cookie_edit.setText(r'D:\yutobe\cookiefile\www.youtube.com_cookies.txt')
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cookie默认路径: {self.cookie_edit.text()}")

    def clear_cookie_path(self):
        self.cookie_edit.setText('')
        self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Cookie默认路径已清空")

    def append_log(self, text):
        """追加日志内容"""
        self.log_edit.append(text)
        # 自动滚动到最后一行
        cursor = self.log_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_edit.setTextCursor(cursor)

    def start_download(self):
        """开始下载"""
        # 获取输入内容
        save_path = self.save_edit.text().strip()
        media_type = self.type_combo.currentText()
        media_url = self.url_edit.text().strip()

        # 验证输入
        if not save_path:
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：请选择保存路径！")
            return

        if not media_url:
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：请输入媒体地址！")
            return

        # 检查保存路径是否存在
        if not os.path.exists(save_path):
            try:
                os.makedirs(save_path)
                self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 保存路径不存在，已创建: {save_path}")
            except Exception as e:
                self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 错误：创建保存路径失败 - {str(e)}")
                return

        # 禁用下载按钮，避免重复点击
        self.download_btn.setEnabled(False)
        self.download_btn.setText("下载中...")

        # 创建并启动下载线程
        self.download_thread = DownloadThread({
            'save_path' : save_path,
            'media_type' : media_type,
            'media_url': media_url,
            'cookie_file': self.cookie_edit.text().strip(),
        })
        self.download_thread.log_signal.connect(self.append_log)
        self.download_thread.finish_signal.connect(self.download_finished)
        self.download_thread.start()

    def download_finished(self, success):
        """下载完成回调"""
        self.download_btn.setEnabled(True)
        self.download_btn.setText("开始下载")
        if not success:
            self.append_log(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 下载任务已终止")
            return
        os.startfile(self.save_edit.text())


# 主函数
if __name__ == "__main__":
    # pyinstaller -F -w main.py
    # 设置高DPI支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = MediaDownloader()
    window.show()
    sys.exit(app.exec_())