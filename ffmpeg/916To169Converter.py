import sys
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QFileDialog, QLineEdit, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class VideoConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('视频比例转换器 2.0')
        self.setFixedSize(600, 250)
        self.setObjectName("MainWindow")

        # QSS Styles (Dark theme with Black text in Message Boxes)
        self.setStyleSheet("""
            #MainWindow { background-color: #1e1e2e; }
            QLabel { color: #cdd6f4; font-family: "Microsoft YaHei"; font-size: 14px; }
            QLineEdit { background-color: #ffffff; border: 1px solid #45475a; border-radius: 5px; color: #000000; padding: 5px; font-size: 13px; }
            QMessageBox QLabel { color: #000000; font-weight: bold; }
            QMessageBox QPushButton { color: #000000; background-color: #e0e0e0; padding: 5px 15px; }
            #btn_select { background-color: #45475a; color: white; font-family: "Microsoft YaHei"; border-radius: 5px; padding: 8px 15px; }
            #btn_convert { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89b4fa, stop:1 #b4befe); color: #11111b; font-size: 18px; font-weight: bold; border-radius: 5px; margin-top: 20px; }
            #btn_convert:hover { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b4befe, stop:1 #89b4fa); }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)

        title_label = QLabel("视频流转换 (9:16 → 16:9)")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        path_layout = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("空格将自动替换为下划线...")

        self.btn_select = QPushButton("浏览文件")
        self.btn_select.setObjectName("btn_select")
        self.btn_select.clicked.connect(self.select_file)

        path_layout.addWidget(self.file_input)
        path_layout.addWidget(self.btn_select)
        main_layout.addLayout(path_layout)

        self.btn_convert = QPushButton("转 换")
        self.btn_convert.setObjectName("btn_convert")
        self.btn_convert.setFixedHeight(50)
        self.btn_convert.clicked.connect(self.convert_video)
        main_layout.addWidget(self.btn_convert)

        self.setLayout(main_layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            self.file_input.setText(file_path)

    def show_message(self, title, text, icon):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.setStyleSheet("QLabel{ color: black; }")
        msg.exec_()

    def sanitize_filename(self, name):
        """仅将文件名中的空格替换为下划线"""
        return name.replace(" ", "_")

    def convert_video(self):
        original_path = self.file_input.text()
        if not original_path or not os.path.exists(original_path):
            self.show_message("错误", "请先选择有效的视频文件！", QMessageBox.Critical)
            return

        self.btn_convert.setText("正在处理...")
        self.btn_convert.setEnabled(False)
        QApplication.processEvents()

        file_dir = os.path.dirname(original_path)
        old_full_name = os.path.basename(original_path)
        old_name, ext = os.path.splitext(old_full_name)

        # 1. 自动替换空格逻辑
        new_name_only = self.sanitize_filename(old_name)
        new_full_name = f"{new_name_only}{ext}"
        input_file = os.path.join(file_dir, new_full_name)

        # 如果原文件名包含空格，执行物理重命名
        if old_full_name != new_full_name:
            try:
                # 如果处理后的名字已存在（例如目录下本来就有个下划线版本的），先移除旧的
                if os.path.exists(input_file):
                    os.remove(input_file)
                os.rename(original_path, input_file)
            except Exception as e:
                self.show_message("重命名失败", f"无法处理文件名: {str(e)}", QMessageBox.Critical)
                self.btn_convert.setText("转 换")
                self.btn_convert.setEnabled(True)
                return

        # 2. 转换逻辑
        output_file = os.path.join(file_dir, f"{new_name_only}_16_9{ext}")
        output_file_text = os.path.join(file_dir, f"{new_name_only}_16_9_logo{ext}")

        logo = r"E:/yutobe/logo/logo31.png"
        # 使用双引号包裹路径以处理路径中可能存在的其他特殊字符
        command = f'ffmpeg -y -i "{input_file}" -filter_complex "[0:v]scale=ih*16/9:-1,boxblur=luma_radius=min(h\,w)/20:luma_power=1:chroma_radius=min(h\,w)/20:chroma_power=1,setsar=1[bg];[0:v]scale=-1:ih[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,crop=w=iw:h=iw*9/16" -c:a copy "{output_file}"'
        add_logo = f'ffmpeg -y -i {output_file} -i "{logo}" -filter_complex "[1:v]scale=100:-1,format=rgba,colorchannelmixer=aa=0.8[logo];[0:v][logo]overlay=W-w-10:10" -c:v libx264 -crf 23 -c:a copy {output_file_text}'
        try:
            # 模糊背景16：9
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            # 添加文字水印 logo
            result1 = subprocess.run(add_logo, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result1.returncode == 0:
                self.show_message("成功", "视频转换完成！", QMessageBox.Information)
                os.remove(output_file)
                os.startfile(file_dir)
            else:
                self.show_message("失败", f"FFmpeg 报错：\n{result.stderr}", QMessageBox.Critical)
        except Exception as e:
            self.show_message("异常", str(e), QMessageBox.Critical)
        finally:
            self.btn_convert.setText("转 换")
            self.btn_convert.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VideoConverter()
    ex.show()
    sys.exit(app.exec_())
