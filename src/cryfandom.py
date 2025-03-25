import sys
import os
import random
import logging
import requests
from bs4 import BeautifulSoup
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QSpinBox, QTextEdit, QPushButton, 
    QMessageBox, QTabWidget, QFileDialog, QComboBox
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QTextCursor, QColor

class ArticleCreatorThread(QThread):
    """Background thread for creating articles to prevent GUI freezing"""
    article_created = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, creator, articles_data):
        super().__init__()
        self.creator = creator
        self.articles_data = articles_data

    def run(self):
        try:
            for article_info in self.articles_data:
                title = article_info.get('title', '')
                content = article_info.get('content', '')
                
                success = self.creator.create_article(title, content)
                if success:
                    self.article_created.emit(f"Created: {title}")
                else:
                    self.error.emit(f"Failed to create: {title}")
                
                # Random delay between article creations
                time.sleep(random.uniform(1, 3))
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class FandomArticleCreatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # ASCII Art Logo
        self.logo = """  ████████ ██████████████ ███████████████████  █████ █████████████  ███████████████  █████
 █        ██        ██  ██   ██      ███    █  █    ██   █        ███       ███   ███    █
█   ████  ██  ████  ██      ███  ██████  █   ███    ██  ██  ████  ██  ████   █     ██    █
█   █  █████       █  █    █ █       █  ███  ██   █  █  ██  █  █   █  █  ██  █  █  █ █   █
█   ████  █   ███   █ ██  █  █  ██████       ██   ██    █   ███   ██  ████   █  ██   █  ██
 █       ██  ██ █   █ █   █  █  █   █   ███   █  ███    █        ███        ██  ██  ██  ██
  ████████████  █████ █████  ████  ███████████████  ██████████████  █████████████████████ """

        # Window Setup
        self.setWindowTitle("🌐 Fandom Article Creator")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: monospace;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Logo Label
        logo_label = QLabel(self.logo)
        logo_label.setFont(QFont("Courier", 8))
        logo_label.setStyleSheet("color: navy;")
        main_layout.addWidget(logo_label)

        # Anti-War Statement
        war_label = QLabel("#RussiaIsATerroristState")
        war_label.setStyleSheet("color: red; font-weight: bold; margin-bottom: 10px;")
        war_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(war_label)

        # Language Selection
        language_layout = QHBoxLayout()
        language_label = QLabel("🌐 Мова / Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Українська (Ukrainian)", "English", "Русский (Russian)"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        main_layout.addLayout(language_layout)

        # Tabs for different functionalities
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Create tabs
        self.create_login_tab()
        self.create_article_tab()
        self.create_advanced_tab()

        # Logs
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #f9f9f9; color: #333;")
        main_layout.addWidget(self.log_display)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("🚀 Create Articles")
        self.create_button.clicked.connect(self.start_article_creation)
        
        self.stop_button = QPushButton("🛑 Stop")
        self.stop_button.setEnabled(False)
        
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        # Default language setup
        self.change_language(0)  # Default to first language

    def create_login_tab(self):
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        
        # Wiki URL Input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("🌐 Wiki URL:"))
        self.wiki_url_input = QLineEdit()
        self.wiki_url_input.setPlaceholderText("https://example.fandom.com")
        url_layout.addWidget(self.wiki_url_input)
        login_layout.addLayout(url_layout)

        # Username Input
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("👤 Username:"))
        self.username_input = QLineEdit()
        username_layout.addWidget(self.username_input)
        login_layout.addLayout(username_layout)

        # Password Input
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("🔐 Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)

        self.tabs.addTab(login_tab, "🔑 Login")

    def create_article_tab(self):
        article_tab = QWidget()
        article_layout = QVBoxLayout(article_tab)

        # Article Creation Options
        article_options_layout = QHBoxLayout()
        
        # Number of Articles
        article_count_label = QLabel("📊 Number of Articles:")
        self.article_count_spin = QSpinBox()
        self.article_count_spin.setRange(1, 100)
        self.article_count_spin.setValue(5)
        article_options_layout.addWidget(article_count_label)
        article_options_layout.addWidget(self.article_count_spin)
        
        # Article Prefix
        prefix_label = QLabel("🏷️ Article Prefix:")
        self.title_prefix_input = QLineEdit()
        self.title_prefix_input.setPlaceholderText("Optional prefix")
        article_options_layout.addWidget(prefix_label)
        article_options_layout.addWidget(self.title_prefix_input)
        
        article_layout.addLayout(article_options_layout)

        # Content Template
        content_label = QLabel("📝 Content Template:")
        self.content_template_input = QTextEdit()
        self.content_template_input.setPlaceholderText(
            "Optional template. Use {number} for iteration.\n"
            "Leave blank for random text generation."
        )
        article_layout.addWidget(content_label)
        article_layout.addWidget(self.content_template_input)

        self.tabs.addTab(article_tab, "📝 Article Settings")

    def create_advanced_tab(self):
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)

        # Delay between article creation
        delay_layout = QHBoxLayout()
        delay_label = QLabel("⏱️ Delay between articles (seconds):")
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 60)
        self.delay_spin.setValue(3)
        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        advanced_layout.addLayout(delay_layout)

        # Save/Load Configuration
        config_layout = QHBoxLayout()
        save_config_btn = QPushButton("💾 Save Configuration")
        load_config_btn = QPushButton("📂 Load Configuration")
        config_layout.addWidget(save_config_btn)
        config_layout.addWidget(load_config_btn)
        advanced_layout.addLayout(config_layout)

        self.tabs.addTab(advanced_tab, "⚙️ Advanced")

    def change_language(self, index):
        # Placeholder for language changes
        languages = {
            0: {  # Ukrainian
                "wiki_url": "🌐 URL вікі:",
                "username": "👤 Ім'я користувача:",
                "password": "🔐 Пароль:",
                "articles": "📊 Кількість статей:",
                "prefix": "🏷️ Префікс статті:",
                "content": "📝 Шаблон вмісту:"
            },
            1: {  # English
                "wiki_url": "🌐 Wiki URL:",
                "username": "👤 Username:",
                "password": "🔐 Password:",
                "articles": "📊 Number of Articles:",
                "prefix": "🏷️ Article Prefix:",
                "content": "📝 Content Template:"
            },
            2: {  # Russian
                "wiki_url": "🌐 URL вики:",
                "username": "👤 Имя пользователя:",
                "password": "🔐 Пароль:",
                "articles": "📊 Количество статей:",
                "prefix": "🏷️ Префикс статьи:",
                "content": "📝 Шаблон содержимого:"
            }
        }
        
        # Update labels with selected language
        selected_lang = languages.get(index, languages[1])
        # (Add more comprehensive translation logic here)

    def start_article_creation(self):
        # Implement article creation logic
        # Similar to previous implementation
        pass

def main():
    app = QApplication(sys.argv)
    gui = FandomArticleCreatorGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
