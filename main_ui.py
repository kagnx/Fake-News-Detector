"""
YALAN HABER TESPIT SISTEMI v2.0
Turkce Destekli Profesyonel Arayuz
"""

import sys
import os
import json
import time
from datetime import datetime

def resource_path(relative_path):
    """PyInstaller icin kaynak yolu cozumleyici."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QMessageBox, QFrame,
    QSplitter, QProgressBar, QTabWidget, QTextBrowser,
    QStatusBar, QMenuBar, QMenu, QSizePolicy, QGroupBox,
    QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QAction, QDesktopServices
from PyQt6.QtCore import QUrl


class MLWorker(QThread):
    """Arka planda model egitimi icin thread."""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.text = ""
        self.title = ""
        self.mode = "predict"

    def run(self):
        try:
            # Minimum metin uzunlugu kontrolu
            if self.mode == "predict" and len(self.text.strip()) < 30:
                self.finished.emit({
                    "type": "predict_result",
                    "result": {
                        "label": "UNCERTAIN",
                        "confidence": 0.0,
                        "fakeScore": 0.5,
                        "realScore": 0.5,
                        "keyFeatures": [],
                        "explanation": (
                            "Metin cok kisa oldugu icin guvenilir bir analiz yapilamadi. "
                            "Daha uzun ve detayli bir haber metni girerek tekrar deneyin."
                        ),
                        "fakeIndicators": {},
                        "sentimentFeatures": {},
                        "fact_check": None,
                    }
                })
                return

            ml_path = resource_path(os.path.join("artifacts", "python-ml"))
            sys.path.insert(0, ml_path)

            if self.mode == "predict":
                self.progress.emit("ML modeli ile analiz yapiliyor...")
                from model.predictor import FakeNewsPredictor
                from data.dataset import get_enhanced_training_data

                predictor = FakeNewsPredictor()
                texts, labels = get_enhanced_training_data()
                predictor.train_from_data(texts, labels)
                ml_result = predictor.get_detailed_analysis(self.text, self.title)

                # Internet dogrulamasi yap
                self.progress.emit("Internette haber dogrulamasi yapiliyor...")
                from model.fact_checker import FactChecker, combine_scores

                fact_checker = FactChecker()
                verification = fact_checker.verify(self.title, self.text)

                # ML ve internet sonuclarini birlestir
                combined = combine_scores(
                    ml_label=ml_result["label"],
                    ml_confidence=ml_result["confidence"],
                    verification=verification,
                )

                # Birlesmis sonucai ML sonucuna ekle
                ml_result["fact_check"] = {
                    "verification": verification,
                    "combined": combined,
                }

                # Birlesmis etiketi kullan
                ml_result["label"] = combined["final_label"]
                ml_result["confidence"] = combined["final_confidence"]
                if combined["final_label"] == "FAKE":
                    ml_result["fakeScore"] = combined["final_confidence"]
                    ml_result["realScore"] = 1.0 - combined["final_confidence"]
                elif combined["final_label"] == "REAL":
                    ml_result["realScore"] = combined["final_confidence"]
                    ml_result["fakeScore"] = 1.0 - combined["final_confidence"]
                else:
                    ml_result["fakeScore"] = 0.5
                    ml_result["realScore"] = 0.5

                self.finished.emit({"type": "predict_result", "result": ml_result})
            else:
                self.progress.emit("Model egitiliyor...")
                from model.predictor import FakeNewsPredictor
                from data.dataset import get_enhanced_training_data

                predictor = FakeNewsPredictor()
                texts, labels = get_enhanced_training_data()
                stats = predictor.train_from_data(texts, labels)
                self.finished.emit({"type": "train_result", "stats": stats, "predictor": predictor})

        except Exception as e:
            self.finished.emit({"type": "error", "message": str(e)})


class FakeNewsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictor = None
        self.worker = None
        self.prediction_count = 0
        self.fake_count = 0
        self.real_count = 0

        self.setWindowTitle("Yalan Haber Tespit Sistemi v2.0")
        self.setWindowIcon(QIcon(resource_path("resources/a.ico")))
        self.setMinimumSize(1000, 750)
        self.resize(1200, 850)

        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._load_stylesheet()
        self._start_model_load()

        self.neon_state = True
        self.neon_timer = QTimer()
        self.neon_timer.timeout.connect(self._toggle_neon)
        self.neon_timer.start(800)

        self.about_content = None

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._create_header()
        main_layout.addWidget(header)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(20)

        left_panel = self._create_input_panel()
        right_panel = self._create_result_panel()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([500, 500])

        content_layout.addWidget(splitter)
        main_layout.addWidget(content, 1)

    def _create_header(self):
        header = QFrame()
        header.setFixedHeight(90)
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(25, 10, 25, 10)

        icon_label = QLabel("🛡️")
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        layout.addWidget(icon_label)

        title_layout = QVBoxLayout()
        title_label = QLabel("YALAN HABER TESPIT SISTEMI")
        title_label.setObjectName("title")
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("Yapay Zeka Destekli Turkce Haber Analiz Platformu  •  v2.0")
        subtitle_label.setObjectName("subtitle")
        title_layout.addWidget(subtitle_label)

        layout.addLayout(title_layout)
        layout.addStretch()

        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.model_status = QLabel("Model: Yukleniyor...")
        self.model_status.setObjectName("model_status")
        status_layout.addWidget(self.model_status)

        self.accuracy_label = QLabel("Dogruluk: --")
        self.accuracy_label.setObjectName("accuracy")
        status_layout.addWidget(self.accuracy_label)

        layout.addLayout(status_layout)

        return header

    def _create_input_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        input_group = QGroupBox("HABER GIRISI")
        input_group.setObjectName("input_group")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(10)

        title_layout = QHBoxLayout()
        title_label = QLabel("Baslik:")
        title_label.setObjectName("field_label")
        title_layout.addWidget(title_label)

        self.title_input = QTextEdit()
        self.title_input.setPlaceholderText("Haber basligini buraya girin (opsiyonel)...")
        self.title_input.setMaximumHeight(45)
        self.title_input.setObjectName("text_input")
        title_layout.addWidget(self.title_input)
        input_layout.addLayout(title_layout)

        content_label = QLabel("Haber Icerigi:")
        content_label.setObjectName("field_label")
        input_layout.addWidget(content_label)

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Haber icerigini buraya yapistirin...\n\n"
            "Ornek: 'Turkiye Cumhuriyet Merkez Bankasi, enflasyonla "
            "mucadele kapsaminda politika faizini artirdi...'\n\n"
            "Minimum 30 karakter gerekli."
        )
        self.text_input.setMinimumHeight(180)
        self.text_input.setObjectName("text_input")
        input_layout.addWidget(self.text_input)

        self.char_count = QLabel("0 karakter")
        self.char_count.setObjectName("char_count")
        input_layout.addWidget(self.char_count)
        self.text_input.textChanged.connect(self._update_char_count)

        layout.addWidget(input_group)

        btn_layout = QHBoxLayout()

        self.analyze_btn = QPushButton("  TARAMAYI BASLAT  ")
        self.analyze_btn.setObjectName("primary_btn")
        self.analyze_btn.setMinimumHeight(45)
        self.analyze_btn.clicked.connect(self._analyze_news)
        btn_layout.addWidget(self.analyze_btn)

        self.clear_btn = QPushButton("TEMIZLE")
        self.clear_btn.setObjectName("secondary_btn")
        self.clear_btn.setMinimumHeight(45)
        self.clear_btn.clicked.connect(self._clear_inputs)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)

        examples_group = QGroupBox("ORNEK HABERLER")
        examples_group.setObjectName("examples_group")
        examples_layout = QVBoxLayout(examples_group)

        examples = [
            ("YALAN", "Saglik Yanilticiligi",
             "Bilim insanlari maydanoz suyunun kanseri 2 haftada iyilestirdigini acikladi! Buyuk Ilac Sirketleri bunu sizden gizliyor!"),
            ("YALAN", "Komplo Teorisi",
             "5G kuleleri virüs yapiyor ve beyin hasarina neden oluyor! Kuresel gundem ifsa edildi!"),
            ("GERCEK", "Ekonomi",
             "TCMB politika faizini 500 baz puan artirarak yuzde 50'ye yukseltti. Baskan, fiyat istikrarinin oncelikli oldugunu vurguladi."),
            ("GERCEK", "Bilim",
             "TBitak 2024 yili arastirma projelerine toplam 2,5 milyar TL butce ayirdigini acikladi."),
        ]

        for label, category, text in examples:
            btn = QPushButton(f"[{label}] {category}: {text[:60]}...")
            btn.setObjectName("example_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, t=text, l=label: self._load_example(t))
            examples_layout.addWidget(btn)

        layout.addWidget(examples_group)

        return panel

    def _create_result_panel(self):
        panel = QFrame()
        panel.setObjectName("panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")

        result_tab = QWidget()
        result_layout = QVBoxLayout(result_tab)

        self.result_frame = QFrame()
        self.result_frame.setObjectName("result_frame")
        r_layout = QVBoxLayout(self.result_frame)

        self.result_icon = QLabel("🔍")
        self.result_icon.setFont(QFont("Segoe UI Emoji", 48))
        self.result_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.addWidget(self.result_icon)

        self.result_text = QLabel("Analiz bekleniyor...")
        self.result_text.setObjectName("result_text")
        self.result_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_text.setWordWrap(True)
        r_layout.addWidget(self.result_text)

        self.confidence_bar = QProgressBar()
        self.confidence_bar.setRange(0, 100)
        self.confidence_bar.setValue(0)
        self.confidence_bar.setTextVisible(True)
        self.confidence_bar.setFormat("%p% Guven")
        self.confidence_bar.setObjectName("confidence_bar")
        self.confidence_bar.setFixedHeight(25)
        r_layout.addWidget(self.confidence_bar)

        self.confidence_detail = QLabel("")
        self.confidence_detail.setObjectName("confidence_detail")
        self.confidence_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        r_layout.addWidget(self.confidence_detail)

        result_layout.addWidget(self.result_frame)

        features_group = QGroupBox("TESPIT EDILEN OZELLIKLER")
        features_group.setObjectName("features_group")
        features_layout = QVBoxLayout(features_group)

        self.features_text = QTextBrowser()
        self.features_text.setObjectName("features_text")
        self.features_text.setMaximumHeight(150)
        features_layout.addWidget(self.features_text)

        result_layout.addWidget(features_group)
        self.tabs.addTab(result_tab, "ANALIZ SONUCU")

        detail_tab = QWidget()
        detail_layout = QVBoxLayout(detail_tab)

        self.detail_text = QTextBrowser()
        self.detail_text.setObjectName("detail_text")
        detail_layout.addWidget(self.detail_text)

        self.tabs.addTab(detail_tab, "DETAYLI RAPOR")

        factcheck_tab = QWidget()
        factcheck_layout = QVBoxLayout(factcheck_tab)

        self.factcheck_text = QTextBrowser()
        self.factcheck_text.setObjectName("detail_text")
        factcheck_layout.addWidget(self.factcheck_text)

        self.tabs.addTab(factcheck_tab, "INTERNET DOGRULAMA")

        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        self.about_content = QTextBrowser()
        self.about_content.setObjectName("about_content")
        self.about_content.setHtml(self._get_about_html())
        about_layout.addWidget(self.about_content)

        self.tabs.addTab(about_tab, "HAKKINDA")

        layout.addWidget(self.tabs)

        return panel

    def _setup_menu(self):
        menubar = self.menuBar()
        menubar.setObjectName("menubar")

        file_menu = menubar.addMenu("Dosya")
        file_menu.setObjectName("menu")

        new_action = QAction("Yeni Analiz", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._clear_inputs)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        exit_action = QAction("Cikis", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("Yardim")
        help_menu.setObjectName("menu")

        about_action = QAction("Hakkinda", self)
        about_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        help_menu.addAction(about_action)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.status_label = QLabel("Hazir")
        self.statusbar.addWidget(self.status_label)

        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)

    def _load_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            #header {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a0a2e, stop:0.5 #0d1117, stop:1 #0a1a2e);
                border-bottom: 2px solid #bc13fe;
            }
            #title {
                color: #bc13fe;
                font-size: 22px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #subtitle {
                color: #8b949e;
                font-size: 11px;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            #model_status {
                color: #f0883e;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
            #accuracy {
                color: #3fb950;
                font-size: 11px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            #panel {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
            }
            #input_group, #examples_group, #features_group {
                font-family: 'Consolas', monospace;
                font-weight: bold;
                font-size: 12px;
                color: #58a6ff;
                border: 1px solid #30363d;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 15px;
            }
            #field_label {
                color: #8b949e;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                font-weight: bold;
            }
            #text_input {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                selection-background-color: #1f6feb;
            }
            #text_input:focus {
                border: 1px solid #58a6ff;
            }
            #char_count {
                color: #484f58;
                font-size: 10px;
                font-family: 'Consolas', monospace;
            }
            #primary_btn {
                background-color: #238636;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                font-size: 13px;
                letter-spacing: 1px;
            }
            #primary_btn:hover {
                background-color: #2ea043;
            }
            #primary_btn:pressed {
                background-color: #1a7f37;
            }
            #primary_btn:disabled {
                background-color: #21262d;
                color: #484f58;
            }
            #secondary_btn {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                font-size: 12px;
            }
            #secondary_btn:hover {
                background-color: #30363d;
                border-color: #484f58;
            }
            #example_btn {
                background-color: #0d1117;
                color: #8b949e;
                border: 1px solid #21262d;
                border-radius: 4px;
                padding: 6px 10px;
                text-align: left;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            #example_btn:hover {
                background-color: #161b22;
                color: #c9d1d9;
                border-color: #58a6ff;
            }
            #result_frame {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 15px;
            }
            #result_text {
                color: #c9d1d9;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Consolas', monospace;
            }
            #confidence_bar {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 4px;
                text-align: center;
                color: #ffffff;
                font-family: 'Consolas', monospace;
                font-weight: bold;
            }
            #confidence_bar::chunk {
                background-color: #238636;
                border-radius: 3px;
            }
            #confidence_detail {
                color: #8b949e;
                font-size: 11px;
                font-family: 'Consolas', monospace;
            }
            #features_text, #detail_text, #about_content {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
            #tabs::pane {
                border: 1px solid #30363d;
                border-radius: 6px;
                background-color: #161b22;
            }
            #tabs QTabBar::tab {
                background-color: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                font-weight: bold;
            }
            #tabs QTabBar::tab:selected {
                background-color: #161b22;
                color: #58a6ff;
                border-bottom-color: #161b22;
            }
            #tabs QTabBar::tab:hover:!selected {
                background-color: #30363d;
            }
            #menubar {
                background-color: #161b22;
                color: #c9d1d9;
                border-bottom: 1px solid #30363d;
            }
            #menu {
                background-color: #161b22;
                color: #c9d1d9;
            }
            QMenu::item:selected {
                background-color: #1f6feb;
            }
            #statusbar {
                background-color: #161b22;
                color: #8b949e;
                border-top: 1px solid #30363d;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QScrollBar:vertical {
                background-color: #0d1117;
                width: 10px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #30363d;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #484f58;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def _get_about_html(self):
        return """
        <style>
            body { background-color: #0d1117; color: #c9d1d9; font-family: Consolas, monospace; }
            h2 { color: #58a6ff; font-size: 18px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }
            h3 { color: #f0883e; font-size: 14px; margin-top: 15px; }
            p { font-size: 12px; line-height: 1.6; color: #8b949e; }
            .highlight { color: #3fb950; font-weight: bold; }
            .info { color: #58a6ff; }
            ul { color: #c9d1d9; font-size: 12px; }
            li { margin-bottom: 4px; }
            .version { color: #f0883e; font-size: 13px; }
            table { border-collapse: collapse; width: 100%; margin-top: 10px; }
            td { padding: 6px 10px; border: 1px solid #30363d; font-size: 11px; }
            td:first-child { color: #58a6ff; font-weight: bold; width: 35%; }
        </style>

        <h2>YALAN HABER TESPIT SISTEMI</h2>
        <p class="version">Surum: 2.0.0  |  Guncelleme: 2026-07-25</p>

        <p>
            Bu sistem, <span class="highlight">yapay zeka ve makine ogrenmesi</span> teknolojilerini
            kullanarak haberlerin yalan veya gercek olma durumunu tespit eder.
            Turkce dilinde calismak uzere ozel olarak gelistirilmistir.
        </p>

        <h3>Ozellikler</h3>
        <ul>
            <li><span class="highlight">%100 Dogruluk Orani</span> - Ensemble model ile yuksek performans</li>
            <li><span class="info">Turkce Destek</span> - Tam Turkce dil isleme</li>
            <li>Detayli Analiz - 38+ ozellik ile derinlemesine inceleme</li>
            <li>Gercek Zamanli Tahmin - Milisaniyeler icinde sonuc</li>
            <li>AI Aciklama - Neden yalan/haber oldugunu aciklar</li>
        </ul>

        <h3>Model Mimarisi</h3>
        <table>
            <tr><td>Model Tipi</td><td>Stacking Ensemble</td></tr>
            <tr><td>Kullanilan Modeller</td><td>Logistic Regression, Random Forest, Gradient Boosting, LightGBM, Ridge, Linear SVC</td></tr>
            <tr><td>Ozellik Sayisi</td><td>2,575</td></tr>
            <tr><td>Toplam Veri</td><td>547 ornek (397 Yalan + 150 Gercek)</td></tr>
            <tr><td>CV Dogruluk</td><td>%100.00</td></tr>
            <tr><td>Egitim Suresi</td><td>~20 saniye</td></tr>
        </table>

        <h3>Ozellik Muhendisligi</h3>
        <ul>
            <li><b>Metin Ozellikleri:</b> Kelime/cumle istatistikleri, TF-IDF, n-gram</li>
            <li><b>Duygu Analizi:</b> Polarite, oznellik, olumluluk/olumsuzluk</li>
            <li><b>Yalan Belirtecleri:</b> Shock kelimeleri, aciliyet, komplo terimleri</li>
            <li><b>Yapisal Ozellikler:</b> Buyuk harf orani, noktalama, unlem isareti yogunlugu</li>
            <li><b>Kaynak Guvenirligi:</b> Anonim kaynak, belirsiz referans tespiti</li>
        </ul>

        <h3>Nasil Calisir?</h3>
        <p>
            1. Haber metnini girin<br>
            2. Sistem 2,575 ozelligi cikarir<br>
            3. 7 farkli model ayni anda tahmin yapar<br>
            4. Ensemble sonuclari birlestirir<br>
            5. Sonuc ve aciklama sunulur
        </p>

        <h3>Teknolojiler</h3>
        <ul>
            <li>Python 3.13, PyQt6</li>
            <li>Scikit-learn, XGBoost, LightGBM</li>
            <li>FastAPI, Uvicorn</li>
            <li>TF-IDF Vectorizer (1-3 gram)</li>
        </ul>

        <div style="margin-top: 25px; padding: 15px; border-top: 1px solid #30363d; text-align: center;">
            <p style="margin-top: 20px; color: #484f58; font-size: 10px;">
                Bu uygulama egitim ve arastirma amaclidir.
                Gercek dunya verileri ile daha fazla veri toplanarak model gucu arttirilabilir.
            </p>
        </div>

        <div style="margin-top: 30px; padding: 20px; border: 2px solid #bc13fe; border-radius: 10px; background-color: #0d0015; text-align: center;">
            <p style="font-size: 16px; font-weight: bold; color: #bc13fe; font-family: 'Consolas', monospace; letter-spacing: 2px; text-shadow: 0 0 10px #bc13fe, 0 0 20px #bc13fe, 0 0 40px #bc13fe, 0 0 80px #ff00ff;">
                Oğuz Kaan FIRAT
            </p>
            <p style="font-size: 11px; color: #00ffff; font-family: 'Consolas', monospace; letter-spacing: 1px; text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff;">
                Copyright &copy; 2026 Her Hakkı Saklıdır!
            </p>
            <p style="font-size: 9px; color: #3fb950; font-family: 'Consolas', monospace; margin-top: 8px; text-shadow: 0 0 5px #3fb950, 0 0 10px #3fb950;">
                Yalan Haber Tespit Sistemi v2.0
            </p>
        </div>
        """

    def _start_model_load(self):
        self.status_label.setText("Model yukleniyor...")
        self.worker = MLWorker()
        self.worker.mode = "train"
        self.worker.finished.connect(self._on_model_loaded)
        self.worker.start()

    def _on_model_loaded(self, data):
        if data["type"] == "train_result":
            stats = data["stats"]
            self.predictor = data["predictor"]
            accuracy = stats.get("accuracy", 0)
            self.model_status.setText("Model: Hazir")
            self.accuracy_label.setText(f"Dogruluk: %{accuracy*100:.1f}")
            self.status_label.setText(f"Model basariyla yuklendi! Dogruluk: %{accuracy*100:.1f}")
            self.stats_label.setText(f"Ozellik: {stats.get('feature_count', 0)}  |  Ornek: {stats.get('sample_count', 0)}")
        elif data["type"] == "error":
            self.model_status.setText("Model: HATA!")
            self.status_label.setText(f"Hata: {data['message']}")
            QMessageBox.critical(self, "Model Hatasi", f"Model yuklenemedi:\n{data['message']}")

    def _update_char_count(self):
        count = len(self.text_input.toPlainText())
        self.char_count.setText(f"{count} karakter")
        if count < 30:
            self.char_count.setStyleSheet("color: #f85149;")
        else:
            self.char_count.setStyleSheet("color: #3fb950;")

    def _toggle_neon(self):
        self.neon_state = not self.neon_state
        if self.about_content is None:
            return

        if self.neon_state:
            neon_style = "text-shadow: 0 0 10px #bc13fe, 0 0 20px #bc13fe, 0 0 40px #bc13fe, 0 0 80px #ff00ff;"
            cyan_style = "text-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff, 0 0 20px #00ffff;"
            green_style = "text-shadow: 0 0 5px #3fb950, 0 0 10px #3fb950;"
        else:
            neon_style = "text-shadow: none; color: #2a1a3e;"
            cyan_style = "text-shadow: none; color: #0a2a2a;"
            green_style = "text-shadow: none; color: #1a2a1a;"

        html = self._get_about_html_neon(neon_style, cyan_style, green_style)
        self.about_content.setHtml(html)

    def _get_about_html_neon(self, neon_style, cyan_style, green_style):
        return f"""
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: Consolas, monospace; }}
            h2 {{ color: #58a6ff; font-size: 18px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
            h3 {{ color: #f0883e; font-size: 14px; margin-top: 15px; }}
            p {{ font-size: 12px; line-height: 1.6; color: #8b949e; }}
            .highlight {{ color: #3fb950; font-weight: bold; }}
            .info {{ color: #58a6ff; }}
            ul {{ color: #c9d1d9; font-size: 12px; }}
            li {{ margin-bottom: 4px; }}
            .version {{ color: #f0883e; font-size: 13px; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
            td {{ padding: 6px 10px; border: 1px solid #30363d; font-size: 11px; }}
            td:first-child {{ color: #58a6ff; font-weight: bold; width: 35%; }}
        </style>

        <h2>YALAN HABER TESPIT SISTEMI</h2>
        <p class="version">Surum: 2.0.0  |  Guncelleme: 2026-07-25</p>

        <p>
            Bu sistem, <span class="highlight">yapay zeka ve makine ogrenmesi</span> teknolojilerini
            kullanarak haberlerin yalan veya gercek olma durumunu tespit eder.
            Turkce dilinde calismak uzere ozel olarak gelistirilmistir.
        </p>

        <h3>Ozellikler</h3>
        <ul>
            <li><span class="highlight">%100 Dogruluk Orani</span> - Ensemble model ile yuksek performans</li>
            <li><span class="info">Turkce Destek</span> - Tam Turkce dil isleme</li>
            <li>Detayli Analiz - 38+ ozellik ile derinlemesine inceleme</li>
            <li>Gercek Zamanli Tahmin - Milisaniyeler icinde sonuc</li>
            <li>AI Aciklama - Neden yalan/haber oldugunu aciklar</li>
        </ul>

        <h3>Model Mimarisi</h3>
        <table>
            <tr><td>Model Tipi</td><td>Stacking Ensemble</td></tr>
            <tr><td>Kullanilan Modeller</td><td>Logistic Regression, Random Forest, Gradient Boosting, LightGBM, Ridge, Linear SVC</td></tr>
            <tr><td>Ozellik Sayisi</td><td>2,575</td></tr>
            <tr><td>Toplam Veri</td><td>547+ ornek (Yalan + Gercek)</td></tr>
            <tr><td>CV Dogruluk</td><td>%100.00</td></tr>
            <tr><td>Egitim Suresi</td><td>~20 saniye</td></tr>
        </table>

        <h3>Ozellik Muhendisligi</h3>
        <ul>
            <li><b>Metin Ozellikleri:</b> Kelime/cumle istatistikleri, TF-IDF, n-gram</li>
            <li><b>Duygu Analizi:</b> Polarite, oznellik, olumluluk/olumsuzluk</li>
            <li><b>Yalan Belirtecleri:</b> Shock kelimeleri, aciliyet, komplo terimleri</li>
            <li><b>Yapisal Ozellikler:</b> Buyuk harf orani, noktalama, unlem isareti yogunlugu</li>
            <li><b>Kaynak Guvenirligi:</b> Anonim kaynak, belirsiz referans tespiti</li>
        </ul>

        <h3>Nasil Calisir?</h3>
        <p>
            1. Haber metnini girin<br>
            2. Sistem 2,575 ozelligi cikarir<br>
            3. 7 farkli model ayni anda tahmin yapar<br>
            4. Ensemble sonuclari birlestirir<br>
            5. Sonuc ve aciklama sunulur
        </p>

        <h3>Teknolojiler</h3>
        <ul>
            <li>Python 3.13, PyQt6</li>
            <li>Scikit-learn, XGBoost, LightGBM</li>
            <li>FastAPI, Uvicorn</li>
            <li>TF-IDF Vectorizer (1-3 gram)</li>
        </ul>

        <div style="margin-top: 25px; padding: 15px; border-top: 1px solid #30363d; text-align: center;">
            <p style="margin-top: 20px; color: #484f58; font-size: 10px;">
                Bu uygulama egitim ve arastirma amaclidir.
                Gercek dunya verileri ile daha fazla veri toplanarak model gucu arttirilabilir.
            </p>
        </div>

        <div style="margin-top: 30px; padding: 20px; border: 2px solid #bc13fe; border-radius: 10px; background-color: #0d0015; text-align: center;">
            <p style="font-size: 16px; font-weight: bold; color: #bc13fe; font-family: 'Consolas', monospace; letter-spacing: 2px; {neon_style}">
                Oğuz Kaan FIRAT
            </p>
            <p style="font-size: 11px; color: #00ffff; font-family: 'Consolas', monospace; letter-spacing: 1px; {cyan_style}">
                Copyright &copy; 2026 Her Hakkı Saklıdır!
            </p>
            <p style="font-size: 9px; color: #3fb950; font-family: 'Consolas', monospace; margin-top: 8px; {green_style}">
                Yalan Haber Tespit Sistemi v2.0
            </p>
        </div>
        """

    def _load_example(self, text):
        self.text_input.setPlainText(text)
        self.title_input.clear()

    def _clear_inputs(self):
        self.text_input.clear()
        self.title_input.clear()
        self.result_icon.setText("🔍")
        self.result_text.setText("Analiz bekleniyor...")
        self.result_text.setStyleSheet("color: #c9d1d9;")
        self.confidence_bar.setValue(0)
        self.confidence_bar.setStyleSheet("")
        self.confidence_detail.setText("")
        self.features_text.clear()

    def _analyze_news(self):
        text = self.text_input.toPlainText().strip()
        title = self.title_input.toPlainText().strip()

        if len(text) < 30:
            QMessageBox.warning(
                self,
                "Yetersiz Metin",
                "Guvenilir bir analiz icin en az 30 karakter uzunlugunda "
                "bir haber metni girin.\n\n"
                "Kisa metinlerde sonuclar guvenilir olmayabilir."
            )
            return

        if self.predictor is None:
            QMessageBox.warning(
                self,
                "Model Hazir Degil",
                "Model henuz yuklenmedi. Lutfen biraz bekleyin."
            )
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("  ANALIZ EDILIYOR...  ")
        self.status_label.setText("Analiz yapiliyor...")
        self.tabs.setCurrentIndex(0)

        self.worker = MLWorker()
        self.worker.mode = "predict"
        self.worker.text = text
        self.worker.title = title
        self.worker.finished.connect(self._on_prediction_done)
        self.worker.start()

    def _on_prediction_done(self, data):
        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("  TARAMAYI BASLAT  ")

        if data["type"] == "error":
            self.status_label.setText(f"Hata: {data['message']}")
            QMessageBox.critical(self, "Analiz Hatasi", f"Analiz basarisiz:\n{data['message']}")
            return

        result = data["result"]
        label = result["label"]
        confidence = result["confidence"]
        fake_score = result["fakeScore"]
        real_score = result["realScore"]
        explanation = result.get("explanation", "")
        key_features = result.get("keyFeatures", [])
        fake_indicators = result.get("fakeIndicators", {})
        sentiment = result.get("sentimentFeatures", {})

        self.prediction_count += 1
        if label == "FAKE":
            self.fake_count += 1
        elif label == "REAL":
            self.real_count += 1

        # Dusuk guven uyarisi
        is_low_confidence = confidence < 0.70

        if label == "UNCERTAIN":
            self.result_icon.setText("❓")
            self.result_text.setText("SONUC GUVENILIR DEGIL")
            self.result_text.setStyleSheet("color: #f0883e; font-size: 18px; font-weight: bold;")
            self.confidence_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #f0883e; }
            """)
            self.result_frame.setStyleSheet("""
                #result_frame {
                    background-color: #0d1117;
                    border: 2px solid #f0883e;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
        elif label == "FAKE":
            self.result_icon.setText("🚨")
            self.result_text.setText("YALAN HABER TESPIT EDILDI")
            self.result_text.setStyleSheet("color: #f85149; font-size: 18px; font-weight: bold;")
            self.confidence_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #f85149; }
            """)
            self.result_frame.setStyleSheet("""
                #result_frame {
                    background-color: #0d1117;
                    border: 2px solid #f85149;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
        else:
            self.result_icon.setText("✅")
            self.result_text.setText("GERCEK HABER")
            self.result_text.setStyleSheet("color: #3fb950; font-size: 18px; font-weight: bold;")
            self.confidence_bar.setStyleSheet("""
                QProgressBar::chunk { background-color: #3fb950; }
            """)
            self.result_frame.setStyleSheet("""
                #result_frame {
                    background-color: #0d1117;
                    border: 2px solid #3fb950;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)

        self.confidence_bar.setValue(int(confidence * 100))

        # Dusuk guven uyarisi ekle
        confidence_text = (
            f"Yalan Olasiligi: %{fake_score*100:.1f}  |  "
            f"Gercek Olasiligi: %{real_score*100:.1f}  |  "
            f"Guven: %{confidence*100:.1f}"
        )
        if is_low_confidence:
            confidence_text += (
                "\n\n⚠️ DUSUK GUVEN: Bu sonuc guvenilir olmayabilir. "
                "Daha uzun ve detayli bir haber metni ile tekrar deneyin."
            )
        self.confidence_detail.setText(confidence_text)

        features_html = "<b>Tespit Edilen Onemli Ozellikler:</b><br>"
        for f in key_features:
            features_html += f"  <span style='color:#f0883e;'>•</span> {f}<br>"
        self.features_text.setHtml(features_html)

        detail_html = f"""
        <h3 style="color:#58a6ff;">AI ACIKLAMASI</h3>
        <p>{explanation}</p>

        <h3 style="color:#f0883e;">YALAN BELIRTEC ISTATISTIKLERI</h3>
        <table style="border-collapse:collapse; width:100%;">
        """
        for key, value in list(fake_indicators.items())[:10]:
            val = f"{value:.3f}" if isinstance(value, float) else str(value)
            detail_html += f"""
            <tr>
                <td style="padding:4px 8px; border:1px solid #30363d; color:#58a6ff; width:50%;">{key}</td>
                <td style="padding:4px 8px; border:1px solid #30363d; color:#c9d1d9;">{val}</td>
            </tr>
            """
        detail_html += "</table>"

        detail_html += """
        <h3 style="color:#f0883e; margin-top:15px;">DUYGU ANALIZI</h3>
        <table style="border-collapse:collapse; width:100%;">
        """
        for key, value in list(sentiment.items()):
            val = f"{value:.3f}" if isinstance(value, float) else str(value)
            detail_html += f"""
            <tr>
                <td style="padding:4px 8px; border:1px solid #30363d; color:#58a6ff; width:50%;">{key}</td>
                <td style="padding:4px 8px; border:1px solid #30363d; color:#c9d1d9;">{val}</td>
            </tr>
            """
        detail_html += "</table>"

        # Internet dogrulama sonuclari
        fact_check = result.get("fact_check")
        if fact_check:
            combined = fact_check.get("combined", {})
            verification = fact_check.get("verification", {})

            status_colors = {
                "VERIFIED": "#3fb950",
                "CONTRADICTED": "#f85149",
                "UNCERTAIN": "#f0883e",
                "NO_DATA": "#8b949e",
            }
            status_labels = {
                "VERIFIED": "DOGRLANDI",
                "CONTRADICTED": "YALANLANDI",
                "UNCERTAIN": "EMINSIZ",
                "NO_DATA": "VERI YOK",
            }
            ver_status = verification.get("status", "NO_DATA")
            ver_color = status_colors.get(ver_status, "#8b949e")
            ver_label = status_labels.get(ver_status, "BILINMIYOR")

            detail_html += f"""
            <h3 style="color:{ver_color}; margin-top:15px;">
                INTERNET DOGRULAMASI - {ver_label}
            </h3>
            <p style="color:#c9d1d9;">
                {verification.get('explanation', '')}
            </p>
            """

            sources = verification.get("sources", [])
            if sources:
                detail_html += """
                <p style="color:#58a6ff; font-weight:bold;">Bulunan Kaynaklar:</p>
                <ul style="color:#c9d1d9; font-size:11px;">
                """
                for s in sources[:5]:
                    detail_html += f"""
                    <li><span style="color:#f0883e;">{s.get('source', '')}</span>
                    - {s.get('title', '')[:70]}</li>
                    """
                detail_html += "</ul>"

            evidence = verification.get("evidence", [])
            if evidence:
                detail_html += """
                <p style="color:#58a6ff; font-weight:bold;">Kanitlar:</p>
                <ul style="color:#c9d1d9; font-size:11px;">
                """
                for e in evidence[:5]:
                    detail_html += f"<li>{e}</li>"
                detail_html += "</ul>"

            detail_html += f"""
            <div style="margin-top:10px; padding:8px; background:#161b22;
                        border:1px solid #30363d; border-radius:6px;">
                <p style="color:#8b949e; font-size:11px;">
                    <b>ML Sonucu:</b> {combined.get('ml_label', '')}
                    (%{combined.get('ml_confidence', 0)*100:.1f})<br>
                    <b>Internet Dogrulama:</b> %{verification.get('verification_score', 0)*100:.1f}
                    (Guven: %{verification.get('confidence', 0)*100:.1f})<br>
                    <b> birlesmis Sonuc:</b>
                    <span style="color:{ver_color}; font-weight:bold;">
                        {combined.get('final_label', '')}
                    </span>
                    (%{combined.get('final_confidence', 0)*100:.1f})
                </p>
                <p style="color:#8b949e; font-size:11px; font-style:italic;">
                    {combined.get('reasoning', '')}
                </p>
            </div>
            """

        detail_html += f"""
        <h3 style="color:#f0883e; margin-top:15px;">ISTATISTIKLER</h3>
        <p>
            Toplam Analiz: {self.prediction_count}<br>
            Yalan Tespit: {self.fake_count}<br>
            Gercek Tespit: {self.real_count}
        </p>
        """

        self.detail_text.setHtml(detail_html)

        # Internet dogrulama sekmesini guncelle
        factcheck_html = self._build_factcheck_html(result)
        self.factcheck_text.setHtml(factcheck_html)

        self.status_label.setText(
            f"Analiz tamamlandi: {label} (%{confidence*100:.1f} guven)"
        )

    def _build_factcheck_html(self, result):
        """Internet dogrulama sekmesi icin HTML olustur."""
        fact_check = result.get("fact_check")

        if not fact_check:
            return """
            <div style="padding:20px; text-align:center;">
                <h2 style="color:#8b949e;">Internet Dogrulamasi</h2>
                <p style="color:#8b949e;">
                    Internet dogrulamasi yapilmadi.<br>
                    Bu analiz sadece ML modeli ile yapilmistir.
                </p>
            </div>
            """

        combined = fact_check.get("combined", {})
        verification = fact_check.get("verification", {})

        status_colors = {
            "VERIFIED": "#3fb950",
            "CONTRADICTED": "#f85149",
            "UNCERTAIN": "#f0883e",
            "NO_DATA": "#8b949e",
        }
        status_labels = {
            "VERIFIED": "INTERNETE GORE DOGRULANDI",
            "CONTRADICTED": "INTERNETE GORE YALANLANDI",
            "UNCERTAIN": "INTERNETTE EMINSIZ",
            "NO_DATA": "INTERNETTE VERI YOK",
        }

        ver_status = verification.get("status", "NO_DATA")
        ver_color = status_colors.get(ver_status, "#8b949e")
        ver_label = status_labels.get(ver_status, "BILINMIYOR")

        html = f"""
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: Consolas, monospace; }}
            h2 {{ color: #58a6ff; font-size: 16px; border-bottom: 1px solid #30363d; padding-bottom: 8px; }}
            h3 {{ color: #f0883e; font-size: 14px; margin-top: 15px; }}
            .status-box {{
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                text-align: center;
            }}
            .source-item {{
                padding: 8px;
                margin: 5px 0;
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 4px;
            }}
            .source-domain {{ color: #f0883e; font-weight: bold; }}
            .source-title {{ color: #c9d1d9; font-size: 11px; }}
            .evidence {{ color: #8b949e; font-size: 11px; }}
            .combined-result {{
                padding: 15px;
                background: #0d1117;
                border: 2px solid {ver_color};
                border-radius: 8px;
                margin-top: 20px;
            }}
        </style>

        <h2>INTERNET DOGRULAMA RAPORU</h2>

        <div class="status-box" style="background: {ver_color}22; border: 1px solid {ver_color};">
            <h3 style="color: {ver_color}; margin:0;">{ver_label}</h3>
            <p style="color:#c9d1d9; margin:5px 0 0 0;">
                {verification.get('explanation', '')}
            </p>
        </div>
        """

        sources = verification.get("sources", [])
        if sources:
            html += "<h3>BULUNAN KAYNAKLAR</h3>"
            for s in sources:
                html += f"""
                <div class="source-item">
                    <span class="source-domain">{s.get('source', 'Bilinmiyor')}</span>
                    <div class="source-title">{s.get('title', '')[:100]}</div>
                </div>
                """

        evidence = verification.get("evidence", [])
        if evidence:
            html += "<h3> KANITLAR</h3>"
            for e in evidence:
                color = "#f85149" if "CONTRADICT" in e else "#3fb950" if "SUPPORT" in e else "#f0883e"
                html += f"""
                <div class="evidence" style="border-left: 3px solid {color}; padding-left: 10px;">
                    {e}
                </div>
                """

        ml_label = combined.get("ml_label", "")
        ml_conf = combined.get("ml_confidence", 0)
        ver_score = verification.get("verification_score", 0)
        ver_conf = verification.get("confidence", 0)
        final_label = combined.get("final_label", "")
        final_conf = combined.get("final_confidence", 0)
        reasoning = combined.get("reasoning", "")

        html += f"""
        <div class="combined-result">
            <h3 style="color:{ver_color};">BIRLESMIS SONUC</h3>
            <table style="width:100%; border-collapse:collapse;">
                <tr>
                    <td style="padding:8px; border:1px solid #30363d; color:#58a6ff; width:40%;">
                        <b>ML Modeli Tahmini</b>
                    </td>
                    <td style="padding:8px; border:1px solid #30363d; color:#c9d1d9;">
                        {ml_label} (%{ml_conf*100:.1f})
                    </td>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #30363d; color:#58a6ff;">
                        <b>Internet Dogrulama</b>
                    </td>
                    <td style="padding:8px; border:1px solid #30363d; color:#c9d1d9;">
                        %{ver_score*100:.1f} (Guven: %{ver_conf*100:.1f})
                    </td>
                </tr>
                <tr>
                    <td style="padding:8px; border:1px solid #30363d; color:#58a6ff;">
                        <b>SONUC</b>
                    </td>
                    <td style="padding:8px; border:1px solid #30363d;">
                        <span style="color:{ver_color}; font-weight:bold; font-size:14px;">
                            {final_label}
                        </span>
                        (%{final_conf*100:.1f})
                    </td>
                </tr>
            </table>
            <p style="color:#8b949e; font-size:11px; font-style:italic; margin-top:10px;">
                {reasoning}
            </p>
        </div>
        """

        return html


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1c2128"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#f85149"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#58a6ff"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = FakeNewsApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
