import json
import random
import os
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QListWidget, QListWidgetItem, QScrollArea,
                             QFrame, QLineEdit, QMessageBox, QInputDialog, QTabWidget,
                             QGroupBox, QTextEdit, QSplitter, QStyleFactory, QComboBox,
                             QDialog, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
                             QCheckBox, QGridLayout, QSizePolicy, QFileDialog)
from PyQt5.QtCore import Qt, QSize, QTimer, QRectF, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QPainter, QBrush, QPen, QPainterPath, QIcon

# 数据文件
WORD_FILE = "vocabulary2.json"
MISTAKE_FILE = "mistake_counts.json"
ACCEPTED_FILE = "accepted_counts.json"
BOOK_FILE = "books.json"


class ModernButton(QPushButton):
    """自定义按钮，支持圆角和悬停效果，自适应尺寸"""

    def __init__(self, text, parent=None, accent=False, icon=None):
        super().__init__(text, parent)
        self.accent = accent
        self.setMinimumHeight(36)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if icon:
            self.setIcon(icon)
        self.setStyleSheet("""
            ModernButton {
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: 500;
            }
            ModernButton[accent="true"] {
                background-color: #0078D4;
                color: white;
            }
            ModernButton[accent="false"] {
                background-color: #F3F2F1;
                color: #111111;
                border: 1px solid #E0E0E0;
            }
            ModernButton:hover[accent="true"] {
                background-color: #005A9E;
            }
            ModernButton:hover[accent="false"] {
                background-color: #E5E5E5;
            }
            ModernButton:pressed {
                transform: translateY(1px);
            }
        """)
        self.setProperty("accent", str(accent).lower())


class WindowControlButton(QPushButton):
    """窗口控制按钮（最小化、关闭）"""

    def __init__(self, text, parent=None, button_type="minimize"):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setMinimumSize(30, 30)
        self.setMaximumSize(30, 30)
        self.setStyleSheet("""
            WindowControlButton {
                border-radius: 4px;
                background-color: transparent;
                color: #666666;
                font-weight: bold;
            }
            WindowControlButton:hover {
                background-color: #E5E5E5;
            }
            WindowControlButton[pressed="true"] {
                background-color: #D0D0D0;
            }
            WindowControlButton[button_type="close"]:hover {
                background-color: #F53F3F;
                color: white;
            }
            WindowControlButton[button_type="close"][pressed="true"] {
                background-color: #D83B01;
                color: white;
            }
        """)
        self.setProperty("button_type", button_type)
        self.setProperty("pressed", "false")

    def mousePressEvent(self, event):
        self.setProperty("pressed", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setProperty("pressed", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        super().mouseReleaseEvent(event)


class RoundedFrame(QFrame):
    """带圆角的框架，支持自适应尺寸"""

    def __init__(self, radius=10, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.setStyleSheet("background-color: transparent;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆角背景
        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)
        painter.fillPath(path, QBrush(self.palette().color(QPalette.Window)))

        # 绘制边框
        if self.frameShape() != QFrame.NoFrame:
            pen = QPen(self.palette().color(QPalette.Mid))
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawPath(path)


class ThemeManager:
    """主题管理类，负责切换和应用不同主题"""

    def __init__(self, app):
        self.app = app
        self.current_theme = "light"
        self.themes = {
            "light": {
                "background": "#FFFFFF",
                "surface": "#F9F9F9",
                "accent": "#0078D4",
                "accent_dark": "#005A9E",
                "text_primary": "#111111",
                "text_secondary": "#666666",
                "border": "#E0E0E0",
                "highlight": "#E8F4FD",
                "success": "#00B42A",
                "error": "#F53F3F",
                "warning": "#FA6400",
                "mistake_bg": "#FFF8E1",
                "mistake_text": "#D83B01"
            },
            "dark": {
                "background": "#1E1E1E",
                "surface": "#2D2D2D",
                "accent": "#3B82F6",
                "accent_dark": "#2563EB",
                "text_primary": "#F0F0F0",
                "text_secondary": "#AAAAAA",
                "border": "#3E3E3E",
                "highlight": "#1E3A8A",
                "success": "#10B981",
                "error": "#EF4444",
                "warning": "#F59E0B",
                "mistake_bg": "#372208",
                "mistake_text": "#FBBF24"
            },
            "blue": {
                "background": "#F0F7FF",
                "surface": "#E6F0FF",
                "accent": "#1E40AF",
                "accent_dark": "#1E3A8A",
                "text_primary": "#0F172A",
                "text_secondary": "#475569",
                "border": "#94A3B8",
                "highlight": "#DBEAFE",
                "success": "#059669",
                "error": "#DC2626",
                "warning": "#D97706",
                "mistake_bg": "#EFF6FF",
                "mistake_text": "#0C4A6E"
            }
        }

    def set_theme(self, theme_name):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.apply_theme()

    def get_theme(self):
        return self.themes[self.current_theme]

    def apply_theme(self):
        theme = self.get_theme()

        # 设置全局样式
        self.app.setStyle(QStyleFactory.create("Fusion"))
        palette = QPalette()

        # 设置颜色
        palette.setColor(QPalette.Window, QColor(theme["background"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Base, QColor(theme["surface"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["background"]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme["background"]))
        palette.setColor(QPalette.ToolTipText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Text, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Button, QColor(theme["surface"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(theme["accent"]))
        palette.setColor(QPalette.Highlight, QColor(theme["accent"]))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(theme["text_secondary"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(theme["text_secondary"]))

        self.app.setPalette(palette)

        # 设置全局字体
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

        return theme


class VocabularyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # 无标题栏设置
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 拖动窗口相关变量
        self.dragging = False
        self.drag_position = QPoint()

        # 初始化主题管理器
        self.theme_manager = ThemeManager(QApplication.instance())
        self.theme_manager.set_theme("light")
        self.theme = self.theme_manager.get_theme()

        # 窗口设置
        self.setWindowTitle("单词听写系统")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 600)

        # 当前选择的词书
        self.current_book = None

        # 创建数据文件（如果不存在）
        self.init_files()

        # 加载数据
        self.load_data()

        # 初始化统计相关变量
        self.accepted_count = 0  # 单次测试正确数
        self.sum_count = 0  # 单次测试总数

        # 创建UI
        self.init_ui()

        # 测试状态变量
        self.test_in_progress = False
        self.current_words = []
        self.current_index = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.current_sections = []
        self.wrong_words = []
        self.current_attempts = 0
        self.current_word_correct = False
        self.now_remind = 0

    def init_files(self):
        """初始化数据文件"""
        if not os.path.exists(BOOK_FILE):
            with open(BOOK_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        if not os.path.exists(MISTAKE_FILE):
            with open(MISTAKE_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

        if not os.path.exists(ACCEPTED_FILE):
            with open(ACCEPTED_FILE, "w") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)

    def import_vocabulary_book(self):
        """导入词书作为独立实体"""
        current_dir = os.path.dirname(os.path.abspath(__file__))

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择词书文件", current_dir, "JSON文件 (*.json);;所有文件 (*)"
        )

        if not file_path:
            return

        if not os.path.exists(file_path):
            QMessageBox.warning(self, "文件不存在", f"未找到文件: {file_path}")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # 修复常见的JSON格式问题
                content = re.sub(r"(?<!\\)'", '"', content)
                content = re.sub(r",\s*}", "}", content)
                content = re.sub(r",\s*]", "]", content)

                imported_vocab = json.loads(content)

            # 获取文件名作为词书名称
            file_name = os.path.basename(file_path)
            book_name = os.path.splitext(file_name)[0]

            # 生成唯一词书ID
            import uuid
            book_id = str(uuid.uuid4())[:8]

            # 检查是否已有同名词书
            existing_names = [info["name"] for info in self.books.values()]
            original_name = book_name
            count = 1
            while book_name in existing_names:
                book_name = f"{original_name}_{count}"
                count += 1

            # 添加新词书
            self.books[book_id] = {
                "name": book_name,
                "vocab": imported_vocab
            }

            # 初始化该词书的错误计数和正确率
            self.mistake_counts[book_id] = {}
            self.accepted_stats[book_id] = {"accepted": 0, "total": 0}

            # 保存所有数据
            self.save_books()
            self.save_mistake_counts()
            self.save_accepted_stats()

            # 刷新界面并切换到新词书
            self.refresh_book_combo()
            index = self.book_combo.findData(book_id)
            if index >= 0:
                self.book_combo.setCurrentIndex(index)

            QMessageBox.information(self, "导入成功", f"词书 '{book_name}' 已成功导入！")

        except json.JSONDecodeError as e:
            error_msg = f"JSON格式错误:\n在第{e.lineno}行，第{e.colno}列\n错误原因: {e.msg}"
            QMessageBox.critical(self, "导入失败", error_msg)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入词书时发生错误:\n{str(e)}")

    def save_accepted_stats(self):
        """保存所有词书的正确率统计"""
        with open(ACCEPTED_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.accepted_stats, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        # 加载词书数据
        try:
            with open(BOOK_FILE, 'r', encoding='utf-8') as f:
                self.books = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.books = {}

        # 加载每个词书独立的错误计数
        try:
            with open(MISTAKE_FILE, 'r', encoding='utf-8') as f:
                self.mistake_counts = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.mistake_counts = {}

        # 加载每个词书的正确率
        try:
            with open(ACCEPTED_FILE, "r") as f:
                self.accepted_stats = json.load(f)
        except:
            self.accepted_stats = {}

        # 当前词书的词汇数据
        self.current_vocab = {}
        self.current_mistakes = {}
        self.current_accepted = {"accepted": 0, "total": 0}

    def add_section_dialog(self):
        """在当前词书中添加新的单词集合"""
        if not self.current_book or self.current_book not in self.books:
            QMessageBox.warning(self, "未选择词书", "请先选择一个词书!")
            return

        section, ok = QInputDialog.getText(self, "添加集合", "请输入新的集合编号:")
        if ok and section.strip():
            section = section.strip()

            if not re.match(r'^[a-zA-Z0-9_\.]+$', section):
                QMessageBox.warning(self, "格式错误", "集合编号只能包含字母、数字、下划线和点!")
                return

            if section in self.current_vocab:
                QMessageBox.warning(self, "集合已存在", f"当前词书中已存在集合 '{section}'!")
            else:
                self.current_vocab[section] = {}
                self.books[self.current_book]["vocab"] = self.current_vocab

                self.save_books()
                self.update_sections_list()
                QMessageBox.information(self, "添加成功", f"已在当前词书中创建集合 '{section}'!")

    def init_ui(self):
        """初始化用户界面"""
        # 创建主部件和布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 自定义标题栏 - 添加最小化和关闭按钮
        title_bar = QWidget()
        title_bar.setStyleSheet(
            f"background-color: {self.theme['surface']}; border-bottom: 1px solid {self.theme['border']};")
        title_bar.setMinimumHeight(38)
        title_bar.setMaximumHeight(38)

        # 允许标题栏区域拖动窗口
        title_bar.mousePressEvent = self.title_bar_mouse_press_event
        title_bar.mouseMoveEvent = self.title_bar_mouse_move_event
        title_bar.mouseReleaseEvent = self.title_bar_mouse_release_event

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 0, 10, 0)
        title_layout.setSpacing(10)

        # 标题文本
        self.title_label = QLabel("单词听写系统")
        self.title_font = QFont("Segoe UI", 12, QFont.Bold)
        self.title_label.setFont(self.title_font)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # 窗口控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)

        # 最小化按钮
        self.minimize_btn = WindowControlButton("—", button_type="minimize")
        self.minimize_btn.clicked.connect(self.showMinimized)

        # 关闭按钮
        self.close_btn = WindowControlButton("✕", button_type="close")
        self.close_btn.clicked.connect(self.close)

        control_layout.addWidget(self.minimize_btn)
        control_layout.addWidget(self.close_btn)
        title_layout.addLayout(control_layout)

        main_layout.addWidget(title_bar)

        # 主内容区域容器
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        main_layout.addWidget(content_container)

        # 主题选择和词书选择
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)
        content_layout.addLayout(top_layout)

        # 词书选择
        book_layout = QHBoxLayout()
        book_layout.setSpacing(10)
        book_label = QLabel("词书:")
        self.book_combo = QComboBox()
        self.book_combo.setMinimumWidth(150)
        self.refresh_book_combo()
        self.book_combo.currentIndexChanged.connect(self.on_book_changed)

        self.manage_books_btn = ModernButton("管理词书", accent=False)
        self.manage_books_btn.setMinimumWidth(100)
        self.manage_books_btn.clicked.connect(self.manage_books_dialog)

        self.import_book_btn = ModernButton("导入词书", accent=False)
        self.import_book_btn.setMinimumWidth(100)
        self.import_book_btn.clicked.connect(self.import_vocabulary_book)

        book_layout.addWidget(book_label)
        book_layout.addWidget(self.book_combo)
        book_layout.addWidget(self.manage_books_btn)
        book_layout.addWidget(self.import_book_btn)

        # 主题选择
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(10)
        theme_label = QLabel("主题:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["浅色", "深色", "蓝色"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(120)

        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)

        top_layout.addLayout(book_layout)
        top_layout.addLayout(theme_layout)
        top_layout.addStretch()

        # 主内容区域 - 分割为左右两部分
        self.splitter = QSplitter(Qt.Horizontal)
        content_layout.addWidget(self.splitter)

        # 左侧面板 - 单词库管理
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        left_panel.setMinimumWidth(280)

        # 单词库列表（当前词书）
        self.sections_group = QGroupBox("单词库集合")
        self.sections_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        sections_layout = QVBoxLayout(self.sections_group)

        self.sections_listbox = QListWidget()
        self.sections_listbox.setSelectionMode(QListWidget.ExtendedSelection)
        self.sections_listbox.setMinimumHeight(200)
        self.sections_listbox.setStyleSheet("""
            QListWidget {
                border: 1px solid %s;
                border-radius: 8px;
                padding: 5px;
                background-color: %s;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: %s;
                color: %s;
            }
        """ % (self.theme["border"], self.theme["surface"],
               self.theme["highlight"], self.theme["text_primary"]))

        sections_layout.addWidget(self.sections_listbox)
        left_layout.addWidget(self.sections_group)

        # 单词操作按钮
        word_btn_layout = QHBoxLayout()
        word_btn_layout.setSpacing(10)
        self.add_word_btn = ModernButton("添加单词")
        self.delete_word_btn = ModernButton("删除单词")
        self.add_word_btn.clicked.connect(self.add_word_dialog)
        self.delete_word_btn.clicked.connect(self.delete_word_dialog)

        word_btn_layout.addWidget(self.add_word_btn)
        word_btn_layout.addWidget(self.delete_word_btn)
        left_layout.addLayout(word_btn_layout)

        # 集合操作按钮
        section_btn_layout = QHBoxLayout()
        section_btn_layout.setSpacing(10)
        self.add_section_btn = ModernButton("添加集合")
        self.delete_section_btn = ModernButton("删除集合")
        self.add_section_btn.clicked.connect(self.add_section_dialog)
        self.delete_section_btn.clicked.connect(self.delete_section_dialog)

        section_btn_layout.addWidget(self.add_section_btn)
        section_btn_layout.addWidget(self.delete_section_btn)
        left_layout.addLayout(section_btn_layout)

        # 开始听写按钮
        self.start_test_btn = ModernButton("开始听写", accent=True)
        self.start_test_btn.clicked.connect(self.start_test)
        left_layout.addWidget(self.start_test_btn)

        # 错误单词管理区域
        mistake_group = QGroupBox("错误单词管理")
        mistake_group.setStyleSheet("QGroupBox { font-weight: bold; font-size: 14px; }")
        mistake_layout = QVBoxLayout(mistake_group)
        mistake_layout.setSpacing(8)

        self.show_mistake_btn = ModernButton("查看错误次数")
        self.redo_wrong_btn = ModernButton("重听错词")
        self.modify_mistake_btn = ModernButton("修改错误次数")
        self.reset_mistake_btn = ModernButton("重置错误次数")
        self.export_mistake_btn = ModernButton("导出错词")
        self.export_mistake_btn.clicked.connect(self.export_wrong_words)

        self.show_mistake_btn.clicked.connect(self.show_mistake_counts)
        self.redo_wrong_btn.clicked.connect(self.redo_wrong_words)
        self.modify_mistake_btn.clicked.connect(self.modify_mistake_count)
        self.reset_mistake_btn.clicked.connect(self.reset_mistake_counts)

        mistake_layout.addWidget(self.show_mistake_btn)
        mistake_layout.addWidget(self.redo_wrong_btn)
        mistake_layout.addWidget(self.modify_mistake_btn)
        mistake_layout.addWidget(self.reset_mistake_btn)
        mistake_layout.addWidget(self.export_mistake_btn)

        left_layout.addWidget(mistake_group)
        left_layout.addStretch()

        # 右侧面板 - 测试区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        right_panel.setMinimumWidth(500)

        # 当前测试信息
        self.test_info = QLabel("选择词书和单词集合并点击'开始听写'按钮")
        self.test_info.setStyleSheet(f"color: {self.theme['text_secondary']}; font-size: 14px;")
        self.test_info.setWordWrap(True)
        right_layout.addWidget(self.test_info)

        # 测试问题区域
        self.question_frame = RoundedFrame()
        self.question_frame.setStyleSheet(
            f"background-color: {self.theme['surface']}; border: 1px solid {self.theme['border']};")
        question_layout = QVBoxLayout(self.question_frame)
        question_layout.setContentsMargins(20, 20, 20, 20)
        question_layout.setSpacing(15)

        # 问题标题
        self.question_label = QLabel("请准备...")
        self.question_font = QFont("Segoe UI", 18, QFont.Bold)
        self.question_label.setFont(self.question_font)
        question_layout.addWidget(self.question_label)

        # 尝试次数显示
        self.attempts_label = QLabel("")
        self.attempts_label.setStyleSheet(f"color: {self.theme['warning']}; font-size: 13px;")
        question_layout.addWidget(self.attempts_label)

        # 答案输入框
        self.answer_entry = QLineEdit()
        self.answer_entry.setFont(QFont("Segoe UI", 14))
        self.answer_entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                background-color: {self.theme['background']};
            }}
            QLineEdit:focus {{
                border-color: {self.theme['accent']};
                outline: none;
            }}
        """)
        self.answer_entry.returnPressed.connect(self.check_answer)
        question_layout.addWidget(self.answer_entry)

        # 反馈信息
        self.feedback_label = QLabel("")
        self.feedback_label.setFont(QFont("Segoe UI", 14))
        self.feedback_label.setWordWrap(True)
        question_layout.addWidget(self.feedback_label)

        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.check_btn = ModernButton("检查")
        self.skip_btn = ModernButton("跳过")
        self.remind_btn = ModernButton("提示")
        self.end_btn = ModernButton("结束测试")

        self.check_btn.clicked.connect(self.check_answer)
        self.skip_btn.clicked.connect(self.next_question)
        self.remind_btn.clicked.connect(self.remind)
        self.end_btn.clicked.connect(self.end_test)

        btn_layout.addWidget(self.check_btn)
        btn_layout.addWidget(self.skip_btn)
        btn_layout.addWidget(self.remind_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.end_btn)

        question_layout.addLayout(btn_layout)
        right_layout.addWidget(self.question_frame)

        # 重新测试按钮（初始隐藏）
        self.retry_btn = ModernButton("重新测试", accent=True)
        self.retry_btn.clicked.connect(self.retry_test)
        self.retry_btn.hide()
        right_layout.addWidget(self.retry_btn)

        # 正确率信息
        self.accepted_info = QLabel("正确率：暂无")
        self.accepted_info.setStyleSheet(f"color: {self.theme['accent']}; font-size: 14px; font-weight: 500;")
        right_layout.addWidget(self.accepted_info)
        self.check_accepted_ratio()

        # 测试结果区域
        self.result_frame = RoundedFrame()
        self.result_frame.setStyleSheet(
            f"background-color: {self.theme['surface']}; border: 1px solid {self.theme['border']};")
        result_layout = QVBoxLayout(self.result_frame)
        result_layout.setContentsMargins(20, 20, 20, 20)

        result_label = QLabel("测试结果")
        result_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        result_layout.addWidget(result_label)

        # 结果详情区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
        """)
        result_layout.addWidget(self.result_text)

        right_layout.addWidget(self.result_frame, 1)

        # 添加面板到分割器
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.splitter.setSizes([350, 850])
        self.splitter.setHandleWidth(8)

        # 更新单词库显示
        self.update_sections_list()

    # 窗口拖动相关方法
    def title_bar_mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def title_bar_mouse_move_event(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def title_bar_mouse_release_event(self, event):
        self.dragging = False

    def refresh_book_combo(self):
        """刷新词书下拉列表"""
        current_book = self.book_combo.currentData() if self.book_combo.count() > 0 else None
        self.book_combo.clear()

        # 添加"所有词书"选项
        self.book_combo.addItem("所有词书", None)

        # 添加所有词书
        for book_id, book_info in self.books.items():
            self.book_combo.addItem(book_info["name"], book_id)

        # 恢复之前的选择
        if current_book is not None:
            index = self.book_combo.findData(current_book)
            if index >= 0:
                self.book_combo.setCurrentIndex(index)
            else:
                self.book_combo.setCurrentIndex(0)
                self.current_book = None

    def on_book_changed(self, index):
        """切换词书时加载对应词书的完整数据"""
        self.current_book = self.book_combo.currentData()

        # 重置当前词书的数据
        self.current_vocab = {}
        self.current_mistakes = {}
        self.current_accepted = {"accepted": 0, "total": 0}

        # 加载选中词书的数据
        if self.current_book and self.current_book in self.books:
            self.current_vocab = self.books[self.current_book].get("vocab", {})
            self.current_mistakes = self.mistake_counts.get(self.current_book, {})
            self.current_accepted = self.accepted_stats.get(self.current_book, {"accepted": 0, "total": 0})

            # 更新标题
            book_name = self.books[self.current_book]["name"]
            self.sections_group.setTitle(f"单词库集合 - {book_name}")
        else:
            self.sections_group.setTitle("单词库集合")

        # 更新界面显示
        self.update_sections_list()
        self.check_accepted_ratio()

    def manage_books_dialog(self):
        """词书管理对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("词书管理")
        dialog.resize(600, 450)
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        # 标题
        title_label = QLabel("词书管理")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 词书列表
        self.books_listbox = QListWidget()
        self.books_listbox.setSelectionMode(QListWidget.SingleSelection)
        self.books_listbox.setStyleSheet("""
            QListWidget {
                border: 1px solid %s;
                border-radius: 8px;
                padding: 5px;
                background-color: %s;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item:selected {
                background-color: %s;
                color: %s;
            }
        """ % (self.theme["border"], self.theme["surface"],
               self.theme["highlight"], self.theme["text_primary"]))

        layout.addWidget(self.books_listbox)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.add_book_btn = ModernButton("添加词书", accent=True)
        self.edit_book_btn = ModernButton("编辑词书")
        self.delete_book_btn = ModernButton("删除词书")
        self.add_sections_to_book_btn = ModernButton("添加集合到词书")

        self.add_book_btn.clicked.connect(self.add_book)
        self.edit_book_btn.clicked.connect(self.edit_book)
        self.delete_book_btn.clicked.connect(self.delete_book)
        self.add_sections_to_book_btn.clicked.connect(self.add_sections_to_book)

        btn_layout.addWidget(self.add_book_btn)
        btn_layout.addWidget(self.edit_book_btn)
        btn_layout.addWidget(self.delete_book_btn)
        btn_layout.addWidget(self.add_sections_to_book_btn)

        layout.addLayout(btn_layout)

        # 刷新词书列表
        self.refresh_books_list()

        dialog.exec_()

    def refresh_books_list(self):
        """刷新词书列表"""
        self.books_listbox.clear()
        for book_id, book_info in self.books.items():
            sections_count = len(book_info.get("vocab", {}))
            item = QListWidgetItem(f"{book_info['name']} (包含 {sections_count} 个集合)")
            item.setData(Qt.UserRole, book_id)
            self.books_listbox.addItem(item)

    def add_book(self):
        """添加新词书"""
        name, ok = QInputDialog.getText(self, "添加词书", "请输入词书名称:")
        if ok and name.strip():
            name = name.strip()

            # 生成唯一ID
            import uuid
            book_id = str(uuid.uuid4())[:8]

            self.books[book_id] = {
                "name": name,
                "vocab": {}
            }

            # 保存词书数据
            self.save_books()

            # 刷新列表
            self.refresh_books_list()
            self.refresh_book_combo()

            QMessageBox.information(self, "添加成功", f"词书 '{name}' 已创建!")

    def edit_book(self):
        """编辑词书"""
        selected_item = self.books_listbox.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "未选择", "请先选择一个词书!")
            return

        book_id = selected_item.data(Qt.UserRole)
        if book_id not in self.books:
            QMessageBox.warning(self, "错误", "所选词书不存在!")
            return

        current_name = self.books[book_id]["name"]
        name, ok = QInputDialog.getText(self, "编辑词书", "请输入新词书名称:",
                                        text=current_name)

        if ok and name.strip() and name != current_name:
            self.books[book_id]["name"] = name.strip()
            self.save_books()
            self.refresh_books_list()
            self.refresh_book_combo()
            QMessageBox.information(self, "修改成功", f"词书已更新为 '{name}'!")

    def delete_book(self):
        """删除词书"""
        selected_item = self.books_listbox.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "未选择", "请先选择一个词书!")
            return

        book_id = selected_item.data(Qt.UserRole)
        if book_id not in self.books:
            QMessageBox.warning(self, "错误", "所选词书不存在!")
            return

        book_name = self.books[book_id]["name"]
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除词书 '{book_name}' 吗？\n此操作将删除词书中的所有单词和记录。",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            del self.books[book_id]
            # 删除相关的错误计数
            if book_id in self.mistake_counts:
                del self.mistake_counts[book_id]
            # 删除相关的正确率统计
            if book_id in self.accepted_stats:
                del self.accepted_stats[book_id]

            self.save_books()
            self.save_mistake_counts()
            self.save_accepted_stats()
            self.refresh_books_list()
            self.refresh_book_combo()
            QMessageBox.information(self, "删除成功", f"词书 '{book_name}' 已删除!")

    def add_sections_to_book(self):
        """向词书添加集合"""
        selected_item = self.books_listbox.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "未选择", "请先选择一个词书!")
            return

        book_id = selected_item.data(Qt.UserRole)
        if book_id not in self.books:
            QMessageBox.warning(self, "错误", "所选词书不存在!")
            return

        book_name = self.books[book_id]["name"]

        # 创建选择集合的对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"添加集合到词书: {book_name}")
        dialog.resize(400, 400)

        layout = QVBoxLayout(dialog)

        # 标题
        title_label = QLabel(f"请选择要添加到 '{book_name}' 的集合:")
        layout.addWidget(title_label)

        # 所有可用集合
        all_sections = list(self.books[book_id].get("vocab", {}).keys())
        # 已在词书中的集合
        book_sections = all_sections

        # 集合列表
        self.section_checkboxes = []
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for section in all_sections:
            word_count = len(self.books[book_id]["vocab"][section])
            checkbox = QCheckBox(f"集合 {section} ({word_count} 个单词)")
            checkbox.setChecked(section in book_sections)
            checkbox.setProperty("section_id", section)
            self.section_checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # 按钮
        btn_layout = QHBoxLayout()
        ok_btn = ModernButton("确定", accent=True)
        cancel_btn = ModernButton("取消")

        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

        if dialog.exec_():
            # 更新词书中的集合
            selected_sections = []
            for checkbox in self.section_checkboxes:
                if checkbox.isChecked():
                    selected_sections.append(checkbox.property("section_id"))

            # 只保留选中的集合
            new_vocab = {}
            for section in selected_sections:
                if section in self.books[book_id]["vocab"]:
                    new_vocab[section] = self.books[book_id]["vocab"][section]

            self.books[book_id]["vocab"] = new_vocab
            self.save_books()
            QMessageBox.information(self, "更新成功",
                                    f"词书 '{book_name}' 已更新，包含 {len(selected_sections)} 个集合!")

    def save_books(self):
        """保存所有词书数据"""
        with open(BOOK_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, ensure_ascii=False, indent=2)

    def get_sections_in_current_book(self):
        """获取当前词书中的所有集合"""
        if not self.current_book or self.current_book not in self.books:
            return []
        return list(self.books[self.current_book].get("vocab", {}).keys())

    def resizeEvent(self, event):
        """窗口大小变化时调整UI元素"""
        # 获取当前窗口宽度
        width = self.width()

        # 调整问题字体大小
        question_font_size = min(20, max(14, width // 60))
        self.question_font.setPointSize(question_font_size)
        self.question_label.setFont(self.question_font)

        super().resizeEvent(event)

    def change_theme(self, index):
        """切换主题"""
        themes = ["light", "dark", "blue"]
        self.theme_manager.set_theme(themes[index])
        self.theme = self.theme_manager.get_theme()
        self.update_theme_styles()

        # 更新标题栏样式
        self.findChild(QWidget).findChild(QWidget).setStyleSheet(
            f"background-color: {self.theme['surface']}; border-bottom: 1px solid {self.theme['border']};")

    def update_theme_styles(self):
        """更新界面样式以适应新主题"""
        # 更新列表框样式
        self.sections_listbox.setStyleSheet("""
            QListWidget {
                border: 1px solid %s;
                border-radius: 8px;
                padding: 5px;
                background-color: %s;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: %s;
                color: %s;
            }
        """ % (self.theme["border"], self.theme["surface"],
               self.theme["highlight"], self.theme["text_primary"]))

        # 更新测试信息颜色
        self.test_info.setStyleSheet(f"color: {self.theme['text_secondary']}; font-size: 14px;")

        # 更新问题区域样式
        self.question_frame.setStyleSheet(
            f"background-color: {self.theme['surface']}; border: 1px solid {self.theme['border']};")

        # 更新输入框样式
        self.answer_entry.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px;
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                background-color: {self.theme['background']};
            }}
            QLineEdit:focus {{
                border-color: {self.theme['accent']};
                outline: none;
            }}
        """)

        # 更新尝试次数颜色
        self.attempts_label.setStyleSheet(f"color: {self.theme['warning']}; font-size: 13px;")

        # 更新正确率颜色
        self.accepted_info.setStyleSheet(f"color: {self.theme['accent']}; font-size: 14px; font-weight: 500;")

        # 更新结果区域样式
        self.result_frame.setStyleSheet(
            f"background-color: {self.theme['surface']}; border: 1px solid {self.theme['border']};")
        self.result_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {self.theme['background']};
                border: 1px solid {self.theme['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }}
        """)

        # 刷新显示
        self.update_sections_list()
        self.update()

    def check_accepted_ratio(self):
        """检查并更新当前词书的正确率"""
        total = self.current_accepted.get("total", 0)
        if total > 0:
            accepted = self.current_accepted.get("accepted", 0)
            ratio = accepted / total
            self.accepted_info.setText(f"当前词书正确率：{ratio:.2%}")
        else:
            self.accepted_info.setText("当前词书正确率：暂无")

    def save_accepted_file(self):
        """保存正确率数据"""
        if self.current_book:
            if self.current_book not in self.accepted_stats:
                self.accepted_stats[self.current_book] = {"accepted": 0, "total": 0}

            self.accepted_stats[self.current_book]["accepted"] += self.accepted_count
            self.accepted_stats[self.current_book]["total"] += self.sum_count
            self.current_accepted = self.accepted_stats[self.current_book]

        self.save_accepted_stats()

    def remind(self):
        """提供单词提示"""
        if not self.test_in_progress or self.current_index >= len(self.current_words):
            return

        self.now_remind += 1
        chinese, correct_english, section = self.current_words[self.current_index]
        tmpstr = ""
        if self.now_remind == 1:
            tmpstr = f"单词长度：{len(correct_english)}"
        elif self.now_remind == 2:
            tmpstr = f"单词首字母：{correct_english[0].upper()}"
        elif self.now_remind == 3:
            tmpstr = f"单词第二个字母：{correct_english[1].upper()}"
            self.now_remind = 0

        self.feedback_label.setText(tmpstr)
        self.feedback_label.setStyleSheet(f"color: {self.theme['text_secondary']};")

    def update_sections_list(self):
        """只显示当前词书的集合"""
        self.sections_listbox.clear()

        # 只显示当前词书的集合
        for section in self.current_vocab:
            word_count = len(self.current_vocab[section])
            item = QListWidgetItem(f"集合 {section} ({word_count}个单词)")
            self.sections_listbox.addItem(item)

        # 如果有词书但没有集合
        if self.current_book and self.current_book in self.books and not self.current_vocab:
            item = QListWidgetItem("该词书暂无集合")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setForeground(QColor(self.theme["text_secondary"]))
            self.sections_listbox.addItem(item)

    def add_word_dialog(self):
        """添加单词到当前词书的集合"""
        selected_items = self.sections_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择", "请先选择一个集合!")
            return

        # 获取选中的集合
        section_text = selected_items[0].text()
        if "个单词" in section_text:
            section = section_text.split()[1]
        else:
            QMessageBox.warning(self, "选择错误", "请选择有效的集合!")
            return

        # 检查集合是否存在于当前词书
        if section not in self.current_vocab:
            QMessageBox.warning(self, "集合不存在", f"集合 '{section}' 不存在，请先创建该集合!")
            return

        # 创建添加单词窗口
        class AddWordDialog(QDialog):
            def __init__(self, parent, section):
                super().__init__(parent)
                self.setWindowTitle("添加单词")
                self.resize(400, 200)
                self.section = section
                self.setMinimumWidth(300)

                layout = QVBoxLayout(self)
                title_label = QLabel(f"添加到集合: {section}")
                title_font = QFont("Segoe UI", 12, QFont.Bold)
                title_label.setFont(title_font)
                layout.addWidget(title_label)

                form_layout = QFormLayout()
                self.chinese_entry = QLineEdit()
                self.english_entry = QLineEdit()
                self.chinese_entry.setFont(QFont("Segoe UI", 11))
                self.english_entry.setFont(QFont("Segoe UI", 11))
                form_layout.addRow("中文:", self.chinese_entry)
                form_layout.addRow("英文:", self.english_entry)
                layout.addLayout(form_layout)

                btn_layout = QHBoxLayout()
                self.add_btn = ModernButton("添加", accent=True)
                self.cancel_btn = ModernButton("取消")
                self.add_btn.clicked.connect(self.accept)
                self.cancel_btn.clicked.connect(self.reject)
                btn_layout.addStretch()
                btn_layout.addWidget(self.cancel_btn)
                btn_layout.addWidget(self.add_btn)
                layout.addLayout(btn_layout)

            def get_data(self):
                return (self.chinese_entry.text().strip(),
                        self.english_entry.text().strip())

        dialog = AddWordDialog(self, section)
        if dialog.exec_():
            chinese, english = dialog.get_data()

            if not chinese or not english:
                QMessageBox.warning(self, "输入错误", "中文和英文都不能为空!")
                return

            if chinese in self.current_vocab[section]:
                reply = QMessageBox.question(self, "单词已存在",
                                             f"单词 '{chinese}' 已存在，是否覆盖?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply != QMessageBox.Yes:
                    return

            # 添加到当前词书的词汇库
            self.current_vocab[section][chinese] = english
            self.books[self.current_book]["vocab"] = self.current_vocab

            # 初始化当前词书的错误计数
            if chinese not in self.current_mistakes:
                self.current_mistakes[chinese] = {}
            if section not in self.current_mistakes[chinese]:
                self.current_mistakes[chinese][section] = 0
            self.mistake_counts[self.current_book] = self.current_mistakes

            # 保存数据
            self.save_books()
            self.save_mistake_counts()
            self.update_sections_list()
            QMessageBox.information(self, "添加成功", f"已添加单词: {chinese} = {english}")

    def delete_section_dialog(self):
        """删除单词集合"""
        selected_items = self.sections_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择", "请选择一个或多个集合!")
            return

        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除选中的 {len(selected_items)} 个集合吗？\n该操作不可恢复!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            sections_to_delete = []
            for item in selected_items:
                section_text = item.text()
                if "个单词" in section_text:
                    section = section_text.split()[1]
                    sections_to_delete.append(section)

            for section in sections_to_delete:
                if section in self.current_vocab:
                    del self.current_vocab[section]
                    self.books[self.current_book]["vocab"] = self.current_vocab

                # 同时删除该集合的所有错误计数
                for chinese in list(self.current_mistakes.keys()):
                    if chinese in self.current_mistakes and section in self.current_mistakes[chinese]:
                        del self.current_mistakes[chinese][section]
                        if not self.current_mistakes[chinese]:
                            del self.current_mistakes[chinese]

            # 更新全局错误计数
            self.mistake_counts[self.current_book] = self.current_mistakes

            self.save_books()
            self.save_mistake_counts()
            self.update_sections_list()
            QMessageBox.information(self, "删除成功", f"已删除 {len(sections_to_delete)} 个集合!")

    def delete_word_dialog(self):
        """删除单词对话框"""
        # 获取选中的集合
        selected_items = self.sections_listbox.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择", "请先选择一个集合!")
            return

        section_text = selected_items[0].text()
        if "个单词" in section_text:
            section = section_text.split()[1]
        else:
            QMessageBox.warning(self, "选择错误", "请选择有效的集合!")
            return

        if section not in self.current_vocab or not self.current_vocab.get(section, {}):
            QMessageBox.information(self, "集合为空", f"集合 '{section}' 中没有单词!")
            return

        # 创建删除单词窗口
        class DeleteWordDialog(QDialog):
            def __init__(self, parent, section, words):
                super().__init__(parent)
                self.setWindowTitle(f"删除单词 - 集合 {section}")
                self.resize(550, 450)
                self.setMinimumSize(400, 300)

                layout = QVBoxLayout(self)

                # 单词列表
                self.word_listbox = QListWidget()
                self.word_listbox.setSelectionMode(QListWidget.ExtendedSelection)
                self.word_listbox.setStyleSheet("""
                    QListWidget {
                        border: 1px solid %s;
                        border-radius: 8px;
                        padding: 5px;
                    }
                    QListWidget::item {
                        padding: 5px;
                        border-radius: 4px;
                    }
                    QListWidget::item:selected {
                        background-color: %s;
                        color: %s;
                    }
                """ % (parent.theme["border"], parent.theme["highlight"], parent.theme["text_primary"]))

                layout.addWidget(self.word_listbox)

                # 按钮
                btn_layout = QHBoxLayout()

                self.delete_btn = ModernButton("删除选中", accent=True)
                self.cancel_btn = ModernButton("取消")

                self.delete_btn.clicked.connect(self.accept)
                self.cancel_btn.clicked.connect(self.reject)

                btn_layout.addStretch()
                btn_layout.addWidget(self.cancel_btn)
                btn_layout.addWidget(self.delete_btn)

                layout.addLayout(btn_layout)

                # 填充单词列表
                self.words = words
                for chinese, english in words.items():
                    item = QListWidgetItem(f"{chinese} = {english}")
                    self.word_listbox.addItem(item)

        dialog = DeleteWordDialog(self, section, self.current_vocab[section])
        if dialog.exec_():
            selected_items = dialog.word_listbox.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "未选择", "请选择要删除的单词!")
                return

            reply = QMessageBox.question(self, "确认删除",
                                         f"确定要删除选中的 {len(selected_items)} 个单词吗?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                # 删除选中的单词
                for item in selected_items:
                    chinese = item.text().split('=')[0].strip()
                    del self.current_vocab[section][chinese]

                    # 同时删除错误计数
                    if chinese in self.current_mistakes and section in self.current_mistakes[chinese]:
                        del self.current_mistakes[chinese][section]
                        if not self.current_mistakes[chinese]:
                            del self.current_mistakes[chinese]

                # 更新当前词书数据
                self.books[self.current_book]["vocab"] = self.current_vocab
                self.mistake_counts[self.current_book] = self.current_mistakes

                self.save_books()
                self.save_mistake_counts()
                self.update_sections_list()
                QMessageBox.information(self, "删除成功", f"已删除 {len(selected_items)} 个单词!")

    def get_mistake_count(self, chinese, section):
        """获取指定单词的错误次数"""
        if chinese in self.current_mistakes and section in self.current_mistakes[chinese]:
            return self.current_mistakes[chinese][section]
        return 0

    def increment_mistake_count(self, chinese, section):
        """增加指定单词的错误计数"""
        if chinese not in self.current_mistakes:
            self.current_mistakes[chinese] = {}
        if section not in self.current_mistakes[chinese]:
            self.current_mistakes[chinese][section] = 0

        self.current_mistakes[chinese][section] += 1
        self.mistake_counts[self.current_book] = self.current_mistakes
        self.save_mistake_counts()

    def reset_mistake_counts(self):
        """重置所有错误计数"""
        if not self.current_mistakes:
            QMessageBox.information(self, "提示", "当前没有错误计数记录")
            return

        reply = QMessageBox.question(self, "确认重置",
                                     "确定要重置当前词书中所有单词的错误计数吗？\n此操作不可撤销!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.current_mistakes = {}
            self.mistake_counts[self.current_book] = self.current_mistakes
            self.save_mistake_counts()
            QMessageBox.information(self, "成功", "所有错误计数已重置!")

    def show_mistake_counts(self):
        """显示错误次数统计"""
        if not self.current_mistakes:
            QMessageBox.information(self, "提示", "当前没有错误计数记录")
            return

        # 创建窗口
        mistake_window = QDialog(self)
        mistake_window.setWindowTitle("单词错误次数统计")
        mistake_window.resize(800, 600)
        mistake_window.setMinimumSize(600, 400)

        layout = QVBoxLayout(mistake_window)

        # 标题
        title_label = QLabel("单词错误次数统计")
        title_font = QFont("Segoe UI", 14, QFont.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # 创建表格
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["单词", "英文", "所属集合", "错误次数"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid %s;
                border-radius: 8px;
                background-color: %s;
            }
            QHeaderView::section {
                background-color: %s;
                padding: 5px;
                border: 1px solid %s;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid %s;
            }
        """ % (self.theme["border"], self.theme["surface"],
               self.theme["highlight"], self.theme["border"], self.theme["border"]))

        layout.addWidget(table)

        # 收集所有错误记录
        all_mistakes = []
        for chinese, sections in self.current_mistakes.items():
            for section, count in sections.items():
                # 查找英文翻译
                english = ""
                if section in self.current_vocab and chinese in self.current_vocab[section]:
                    english = self.current_vocab[section][chinese]
                all_mistakes.append((chinese, english, section, count))

        # 按错误次数排序
        all_mistakes.sort(key=lambda x: x[3], reverse=True)

        # 填充表格
        table.setRowCount(len(all_mistakes))
        for row, (chinese, english, section, count) in enumerate(all_mistakes):
            # 单词
            item = QTableWidgetItem(chinese)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 0, item)

            # 英文
            item = QTableWidgetItem(english)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            table.setItem(row, 1, item)

            # 所属集合
            item = QTableWidgetItem(section)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(row, 2, item)

            # 错误次数
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignCenter)

            # 根据错误次数设置颜色
            if count >= 3:
                item.setForeground(QColor(self.theme["error"]))
            elif count >= 2:
                item.setForeground(QColor(self.theme["warning"]))

            font = item.font()
            font.setBold(True)
            item.setFont(font)

            table.setItem(row, 3, item)

        mistake_window.exec_()

    def start_test(self):
        """只使用当前词书的内容进行测试"""
        if not self.current_book:
            QMessageBox.warning(self, "未选择词书", "请先选择一个词书!")
            return

        # 获取当前词书中的所有集合
        all_sections = list(self.current_vocab.keys())
        if not all_sections:
            QMessageBox.warning(self, "无集合", "当前词书中没有可用的集合!")
            return

        # 获取选中的集合
        selected_items = self.sections_listbox.selectedItems()
        self.current_sections = []

        if selected_items:
            # 使用选中的集合
            for item in selected_items:
                section_text = item.text()
                if "个单词" in section_text:
                    section = section_text.split()[1]
                    if section in all_sections:
                        self.current_sections.append(section)
        else:
            # 如果没有选中任何集合，使用当前词书中的所有集合
            reply = QMessageBox.question(self, "使用所有集合",
                                         f"是否使用当前词书中的所有 {len(all_sections)} 个集合进行测试？",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

            if reply == QMessageBox.Yes:
                self.current_sections = all_sections
            else:
                return

        if not self.current_sections:
            QMessageBox.warning(self, "无集合", "未选择有效的集合!")
            return

        # 只使用当前词书的单词
        self.current_words = []
        for section in self.current_sections:
            if section in self.current_vocab:
                for chinese, english in self.current_vocab[section].items():
                    self.current_words.append((chinese, english, section))

        if not self.current_words:
            QMessageBox.warning(self, "无单词", "选中的集合中没有单词!")
            return

        # 打乱单词顺序并开始测试
        random.shuffle(self.current_words)
        self.current_index = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.wrong_words = []
        self.current_attempts = 0
        self.current_word_correct = False
        self.accepted_count = 0  # 重置统计
        self.sum_count = 0

        # 更新测试信息
        section_names = ", ".join(self.current_sections)
        self.test_info.setText(f"测试集合: {section_names} | 单词总数: {len(self.current_words)}")
        self.result_text.clear()
        self.answer_entry.setEnabled(True)
        self.check_btn.show()
        self.skip_btn.show()
        self.remind_btn.show()
        self.end_btn.show()
        self.retry_btn.hide()

        self.test_in_progress = True
        self.show_question()

    def retry_test(self):
        """重新测试相同的单词集合"""
        if not self.current_sections:
            QMessageBox.information(self, "提示", "没有之前的测试记录")
            return

        # 重新开始测试
        self.start_test()

    def show_question(self):
        """显示当前问题"""
        if self.current_index < len(self.current_words):
            chinese, _, _ = self.current_words[self.current_index]
            self.question_label.setText(f"{chinese} 的英文是？")
            self.answer_entry.clear()
            self.feedback_label.setText("")
            self.current_attempts = 0
            self.current_word_correct = False
            self.update_attempts_label()
            self.answer_entry.setFocus()
        else:
            self.end_test()

    def update_attempts_label(self):
        """更新尝试次数显示"""
        if self.current_attempts > 0:
            attempts_left = 3 - self.current_attempts
            self.attempts_label.setText(f"剩余尝试次数: {attempts_left}")
        else:
            self.attempts_label.setText("")

    def check_answer(self):
        """检查答案"""
        if not self.test_in_progress or self.current_index >= len(self.current_words):
            return

        user_answer = self.answer_entry.text().strip()
        if not user_answer:
            QMessageBox.warning(self, "未输入", "请输入英文单词!")
            return

        chinese, correct_english, section = self.current_words[self.current_index]
        self.current_attempts += 1

        if user_answer.lower() == correct_english.lower():
            # 答对处理
            self.feedback_label.setText("✅ 正确！")
            self.feedback_label.setStyleSheet(f"color: {self.theme['success']};")
            self.accepted_count += 1
            self.sum_count += 1
            self.correct_count += 1
            self.current_word_correct = True
            QTimer.singleShot(500, self.next_question)
        else:
            # 答错处理
            if self.current_attempts < 3:
                # 还有尝试机会
                self.feedback_label.setText("❌ 错误，请再试一次")
                self.feedback_label.setStyleSheet(f"color: {self.theme['error']};")
                self.update_attempts_label()
                self.answer_entry.clear()
                self.answer_entry.setFocus()
            else:
                # 三次尝试都错误
                self.feedback_label.setText(f"❌ 错误，正确答案: {correct_english}")
                self.feedback_label.setStyleSheet(f"color: {self.theme['error']};")
                self.wrong_count += 1
                self.sum_count += 1
                self.wrong_words.append((chinese, correct_english, section))

                # 增加错误计数
                self.increment_mistake_count(chinese, section)
                QTimer.singleShot(500, self.next_question)

        self.save_accepted_file()
        self.check_accepted_ratio()

    def next_question(self):
        """显示下一个问题"""
        if self.current_word_correct or self.current_attempts >= 3:
            self.current_index += 1
            self.show_question()
        else:
            self.answer_entry.clear()
            self.answer_entry.setFocus()

    def end_test(self):
        """结束测试并显示结果"""
        self.test_in_progress = False

        # 更新问题区域
        self.question_label.setText("测试结束!")
        self.answer_entry.clear()
        self.feedback_label.setText("")
        self.attempts_label.setText("")

        # 隐藏测试按钮，显示重新测试按钮
        self.check_btn.hide()
        self.skip_btn.hide()
        self.remind_btn.hide()
        self.end_btn.hide()
        self.retry_btn.show()

        # 显示结果
        total = self.correct_count + self.wrong_count

        result_text = f"测试结果: 共 {total} 个单词\n\n"

        if total > 0:
            accuracy = self.correct_count / total * 100
            result_text += f"正确率: {accuracy:.1f}%\n\n"

        result_text += "正确单词:\n"
        correct_count = 0
        for i in range(min(self.correct_count, len(self.current_words))):
            chinese, english, _ = self.current_words[i]
            result_text += f"• {chinese} = {english}\n"
            correct_count += 1
            if correct_count >= 10:
                result_text += "...\n"
                break

        result_text += "\n错误单词:\n"
        # 为每个错误单词获取错误次数并排序
        wrong_with_counts = []
        for chinese, english, section in self.wrong_words:
            count = self.get_mistake_count(chinese, section)
            wrong_with_counts.append((chinese, english, section, count))

        # 按错误次数从大到小排序
        wrong_with_counts.sort(key=lambda x: x[3], reverse=True)

        for i, (chinese, english, _, count) in enumerate(wrong_with_counts):
            result_text += f"• {chinese} = {english} (错误次数: {count})\n"
            if i >= 9:
                result_text += "...\n"
                break

        self.result_text.setText(result_text)

    def redo_wrong_words(self):
        """重新听写错误单词"""
        # 收集所有错误单词
        self.current_words = []
        for chinese, sections in self.current_mistakes.items():
            for section, count in sections.items():
                if count > 0 and section in self.get_sections_in_current_book() and \
                        section in self.current_vocab and chinese in self.current_vocab[section]:
                    english = self.current_vocab[section][chinese]
                    self.current_words.append((chinese, english, section))

        if not self.current_words:
            QMessageBox.information(self, "无错词", "当前词书中没有记录任何错词!")
            return

        random.shuffle(self.current_words)
        self.current_index = 0
        self.correct_count = 0
        self.wrong_count = 0
        self.wrong_words = []
        self.current_sections = list(set([s for _, _, s in self.current_words]))
        self.test_info.setText(f"重听错词 | 单词总数: {len(self.current_words)}")

        self.result_text.clear()

        self.answer_entry.setEnabled(True)
        self.check_btn.show()
        self.skip_btn.show()
        self.remind_btn.show()
        self.end_btn.show()
        self.retry_btn.hide()

        self.test_in_progress = True
        self.show_question()

    def modify_mistake_count(self):
        """修改单词错误次数"""
        section, ok = QInputDialog.getText(self, "输入集合编号", "请输入单词所在集合编号:")
        if not ok or not section:
            return

        chinese, ok = QInputDialog.getText(self, "输入中文", "请输入要修改的中文词:")
        if not ok or not chinese:
            return

        count_str, ok = QInputDialog.getText(self, "设置错误次数", f"请输入新的错误次数 (整数):")
        if not ok or not count_str:
            return

        try:
            count = int(count_str)
        except ValueError:
            QMessageBox.showerror(self, "输入错误", "请输入有效的整数")
            return

        if chinese not in self.current_mistakes:
            self.current_mistakes[chinese] = {}
        self.current_mistakes[chinese][section] = count
        self.mistake_counts[self.current_book] = self.current_mistakes

        self.save_mistake_counts()
        QMessageBox.information(self, "修改成功", f"{chinese}（集合 {section}）的错误次数已设置为 {count} 次")

    def save_vocabulary(self):
        """保存单词库"""
        with open(WORD_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.current_vocab, f, ensure_ascii=False, indent=2)

    def save_mistake_counts(self):
        """保存所有词书的错误计数"""
        with open(MISTAKE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.mistake_counts, f, ensure_ascii=False, indent=2)

    def export_wrong_words(self):
        """导出当前词书的错误单词到文件"""
        if not self.current_mistakes:
            QMessageBox.warning(self, "无错词", "当前词书中没有错误单词可导出")
            return

        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出错误单词", "", "Text Files (*.txt);;Excel Files (*.xlsx)"
        )
        if not file_path:
            return

        # 收集错词数据
        wrong_data = []
        for chinese, sections in self.current_mistakes.items():
            for section, count in sections.items():
                if section in self.current_vocab and chinese in self.current_vocab[section]:
                    english = self.current_vocab[section][chinese]
                    wrong_data.append([chinese, english, section, count])

        # 按错误次数排序
        wrong_data.sort(key=lambda x: x[3], reverse=True)

        # 导出为TXT
        if file_path.endswith(".txt"):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("中文\t英文\t所属集合\t错误次数\n")
                for row in wrong_data:
                    f.write(f"{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\n")
            QMessageBox.information(self, "导出成功", f"错词已导出到：{file_path}")

        # 导出为Excel
        elif file_path.endswith(".xlsx"):
            try:
                from openpyxl import Workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "错误单词"
                # 写入表头
                ws.append(["中文", "英文", "所属集合", "错误次数"])
                # 写入数据
                for row in wrong_data:
                    ws.append(row)
                wb.save(file_path)
                QMessageBox.information(self, "导出成功", f"错词已导出到：{file_path}")
            except ImportError:
                QMessageBox.warning(self, "依赖缺失", "请先安装openpyxl库（pip install openpyxl）")


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = VocabularyApp()
    window.show()
    sys.exit(app.exec_())
