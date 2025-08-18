import time
import cv2
import win32con
import numpy as np
import win32gui
import win32ui
import threading
import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, QFrame, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QComboBox, QLineEdit, QGridLayout, QMessageBox, QDialog
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
import win32api
import win32con
import win32process
from pymem import Pymem
import pymem.process
import interception


VERSAO_ATUAL = "1.2.8-MG"


base_templates = {}
itens_ativos = {}

CONFIG_FILE = "config.json"

# Constantes de Mensagens do Windows (API)
WM_SETCURSOR = 0x0020
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_MENU = 0x12

HTCLIENT = 1
MK_LBUTTON = 0x0001
MK_RBUTTON = 0x0002

THRESHOLD = 0.85
MARGIN_PERCENT = 0.15
bot_ativo = False
tempo_ativo = 0
label_tempo = None
label_tempo_valor = None
label_kalima = None

# ADICIONE no início do script:
buff_config = {}  # Configuração de buff automático por janela
buff_timers = {}  # Controlador de tempo para cada janela
zona_perigo = {}  # { "titulo_parcial": True/False }
status_vars = {}  # Armazena status de cada janela (player detectado ou não)
status_player_label = {}
########################
monitor_threads = {}
status_vars = {}
status_labels = {}
zona_perigo = {}
janela_ativa = {}
selected_window_var = None

# Adicionado para detectar movimento humano
ultima_pos_mouse_real = (0, 0)
ultima_pos_bot = None
parar_por_movimento = False
tempo_parado = time.time()
tempo_espera = 1.5  # segundos parado para reativar
# Dicionário com os templates dos itens
templates = {
    'zen_res800fhd': 'Templates/zen_res800fhd.png',
    'zen_1024': 'Templates/zen_1024.png',
    'Jewels_res800fhd': 'Templates/jewel_res800fhd.png',
    'Jewels_1024': 'Templates/jewel_1024.png',
    'gemstone_res800fhd': 'Templates/gemstone_res800fhd.png',
    'gemstone_1024': 'Templates/gemstone_1024.png',
    'devils_key_res800fhd': 'Templates/devils_key_res800fhd.png',
    'devils_key_res1024': 'Templates/devils_key_res1024.png',
    'devils_eye_6_res800fhd': 'Templates/devils_eye_6_res800fhd.png',
    'devils_eye_6_1024': 'Templates/devils_eye_6_1024.png',
    'complex_potion_res800fhd': 'Templates/complex_media_res800fhd.png',
    'complex_potion_1024': 'Templates/complex_media_1024.png',
    'symbol_of_kundun_6_res800fhd': 'Templates/symbol_of_kundun_6_res800fhd.png',
    'symbol_of_kundun_6_1024': 'Templates/symbol_of_kundun_6_1024.png',
    'symbol_of_kundun_7_800fhd': 'Templates/symbol_of_kundun_7_res800fhd.png',
    'symbol_of_kundun_7_1024': 'Templates/symbol_of_kundun_7_1024.png',
    'sign_of_lord_res800fhd': 'Templates/sign_of_lord_res800fhd.png',
    'sign_of_lord_1024': 'Templates/sign_of_lord_1024.png',
    'horn_of_uniria_1024': 'Templates/uniria_1024.png',
    'red_chocolate_box_res1024': 'Templates/red_chocolate_box_res1024.png',
    'pink_chocolate_box_res1024': 'Templates/pink_chocolate_box_res1024.png',
    'red_chocolate_box_res800fhd': 'Templates/red_chocolate_box_res800fhd.jpg',
    'pink_chocolate_box_res800fhd': 'Templates/pink_chocolate_box_res800fhd.jpg'
}

nomes_amigaveis = {
    "zen": "Zen",
    "jewels": "Jóias",
    "gemstone": "Gemstone",
    "devils": "DS [+5 e +6]",
    "complex": "Complex Potions",
    "symbol": "Symbol of Kundun [+5 à +7]",
    "sign": "Sign of Lord",
    'pets': "H. of Uniria",
    'box': "[Evento] Chocolate Box"
}

# Dicionário de deslocamentos específicos para cada item
deslocamentos = {
    'zen_res800fhd': (17, 5), # OK
    'zen_1024': (17, 5), # OK
    'Jewels_res800fhd': (30, -3), # OK
    'Jewels_1024': (30, -3), # OK
    'gemstone_res800fhd': (5, 2),
    'gemstone_1024': (5, 2),
    'devils_key_res800fhd': (30, -5), # OK
    'devils_key_res1024': (30, -5), # OK
    'devils_eye_6_res800fhd': (30, -3), # OK
    'devils_eye_6_1024': (30, -3), # OK
    'complex_potion_res800fhd': (18, -5), # OK
    'complex_potion_1024': (18, -5), # OK
    'symbol_of_kundun_6_1024': (45, -5), #OK
    'symbol_of_kundun_6_res800fhd': (45, -5), #OK
    'symbol_of_kundun_7_800fhd': (45, -5), # OK
    'symbol_of_kundun_7_1024': (45, -5), # OK
    'sign_of_lord_res800fhd': (15, 0), # OK
    'sign_of_lord_1024': (15, 0), # OK
    'horn_of_uniria_1024': (5, 2),
    'red_chocolate_box_res1024': (23, 4),
    'pink_chocolate_box_res1024': (25, 4),
    'red_chocolate_box_res800fhd': (18, 29),
    'pink_chocolate_box_res800fhd': (18, 29)
}

deslocamentos_kalima = {
    'zen_res800fhd': (17, -23), # OK
    'zen_1024': (17, -23), # OK
    'Jewels_res800fhd': (45, -10),
    'Jewels_1024': (45, -10),
    'gemstone_res800fhd': (5, 10),
    'gemstone_1024': (5, 10),
    'devils_key_res800fhd': (33, -8), # OK
    'devils_key_res1024': (33, -8), # OK
    'devils_eye_6_res800fhd': (30, -8), # OK
    'devils_eye_6_1024': (30, -8), # OK
    'complex_potion_res800fhd': (25, -18), # OK
    'complex_potion_1024': (25, -18), # OK
    'symbol_of_kundun_6_1024': (45, -10), # OK
    'symbol_of_kundun_6_res800fhd': (45, -10), # OK
    'symbol_of_kundun_7_800fhd': (45, -10), # OK
    'symbol_of_kundun_7_1024': (45, -10), # OK
    'sign_of_lord_res800fhd': (15, -10),  #OK
    'sign_of_lord_1024': (15, -10), # OK
    'horn_of_uniria_1024': (45, -10),
    'red_chocolate_box_res800fhd': (5, 10),
    'pink_chocolate_box_res800fhd': (5, 10),
    'red_chocolate_box_res1024': (5, 10),
    'pink_chocolate_box_res1024': (5, 10)
}

def agrupar_itens_unicos():
    base_por_template = {
        'zen_res800fhd': 'zen',
        'zen_1024': 'zen',
        'Jewels_res800fhd': 'jewels',
        'Jewels_1024': 'jewels',
        'gemstone_res800fhd': 'gemstone',
        'gemstone_1024': 'gemstone',
        'devils_key_res800fhd': 'devils',
        'devils_key_res1024': 'devils',
        'devils_eye_6_res800fhd': 'devils',
        'devils_eye_6_1024': 'devils',
        'complex_potion_res800fhd': 'complex',
        'complex_potion_1024': 'complex',
        'symbol_of_kundun_6_res800fhd': 'symbol',
        'symbol_of_kundun_6_1024': 'symbol',
        'symbol_of_kundun_7_800fhd': 'symbol',
        'symbol_of_kundun_7_1024': 'symbol',
        'sign_of_lord_res800fhd': 'sign',
        'sign_of_lord_1024': 'sign',
        'horn_of_uniria_1024': 'pets',
        'red_chocolate_box_res1024': 'box',
        'pink_chocolate_box_res1024': 'box',
        'red_chocolate_box_res800fhd': 'box',
        'pink_chocolate_box_res800fhd': 'box',
      }

    agrupados = {}
    for nome_template, base in base_por_template.items():
        if base not in agrupados:
            agrupados[base] = []
        agrupados[base].append(nome_template)
    return agrupados

def pressionar_tecla(hwnd, tecla_char):
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.05)
    except Exception as e:
        print(f"Failed to set foreground window: {e}")

    if tecla_char:
        try:
            interception.press(tecla_char)
        except Exception as e:
            print(f"Failed to press key '{tecla_char}' using interception: {e}")


def mouse_dentro_jogo(hwnd):
    try:
        cursor_pos = win32gui.GetCursorPos()
        janela_rect = win32gui.GetWindowRect(hwnd)
        return janela_rect[0] <= cursor_pos[0] <= janela_rect[2] and janela_rect[1] <= cursor_pos[1] <= janela_rect[3]
    except:
        return False

def monitorar_mouse(hwnd):
    global ultima_pos_mouse_real, ultima_pos_bot, tempo_parado, parar_por_movimento

    if mouse_dentro_jogo(hwnd):
        atual = win32gui.GetCursorPos()

        if atual != ultima_pos_mouse_real and atual != ultima_pos_bot:
            ultima_pos_mouse_real = atual
            tempo_parado = time.time()
            if not parar_por_movimento:
                parar_por_movimento = True
        else:
            if parar_por_movimento and time.time() - tempo_parado >= tempo_espera:
                parar_por_movimento = False
    else:
        if parar_por_movimento:
            parar_por_movimento = False

def pressionar_direito(hwnd):
    win32gui.SendMessage(hwnd, WM_RBUTTONDOWN, MK_RBUTTON, 0)

def soltar_direito(hwnd):
    win32gui.SendMessage(hwnd, WM_RBUTTONUP, 0, 0)
    time.sleep(0.02)

def carregar_config():
    global MARGIN_PERCENT, itens_ativos, selected_window_var, buff_config

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            MARGIN_PERCENT = config.get("margin_percent", 0.15)
            itens_salvos = config.get("itens_ativos", [])
            buffs_lidos = config.get("buffs", {})
            selected_window_var = config.get("selected_window", "")
    else:
        MARGIN_PERCENT = 0.15
        itens_salvos = []
        buffs_lidos = {}
        selected_window_var = ""

    if not base_templates:
        base_templates = agrupar_itens_unicos()

    for nome_base in base_templates:
        itens_ativos[nome_base] = nome_base in itens_salvos

    for nome, dados in buffs_lidos.items():
        buff_config[nome] = {
            "habilitado": dados.get("habilitado", False),
            "intervalo": str(dados.get("intervalo", 240)),
            "tecla_buff": dados.get("tecla_buff", "2"),
            "tecla_ataque": dados.get("tecla_ataque", "1"),
            "desativar_centralizacao": dados.get("desativar_centralizacao", False),
            "desativar_coleta": dados.get("desativar_coleta", False),
            "tempo_coleta": str(dados.get("tempo_coleta", 60)),
            "tempo_pausa": str(dados.get("tempo_pausa", 1)),
            "kalima": dados.get("kalima", False)
        }

def salvar_config():
    global MARGIN_PERCENT, selected_window_var, itens_ativos, buff_config

    selected_window = selected_window_var
    if not selected_window:
        aviso_customizado("Nenhuma janela foi selecionada.")
        return

    itens_marcados = [nome for nome, var in itens_ativos.items() if var]

    buffs = {}
    for nome, config_vars in buff_config.items():
        buffs[nome] = {
            "habilitado": config_vars["habilitado"],
            "intervalo": int(config_vars["intervalo"] or 240),
            "tecla_buff": config_vars["tecla_buff"],
            "tecla_ataque": config_vars["tecla_ataque"],
            "desativar_centralizacao": config_vars["desativar_centralizacao"],
            "desativar_coleta": config_vars["desativar_coleta"],
            "tempo_coleta": int(config_vars["tempo_coleta"] or 60),
            "tempo_pausa": int(config_vars["tempo_pausa"] or 1),
            "kalima": config_vars["kalima"]
        }

    config = {
        "margin_percent": MARGIN_PERCENT,
        "selected_window": selected_window,
        "itens_ativos": itens_marcados,
        "buffs": buffs
    }

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)


def aviso_customizado(mensagem):
    # This is a global function now, might need to pass parent window later
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(mensagem)
    msg_box.setWindowTitle("Aviso")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.setStyleSheet("""
        QMessageBox { background-color: #1A1A1A; border: 1px solid #D4AF37; }
        QMessageBox QLabel { color: white; font-family: Arial; font-size: 12px; }
        QMessageBox QPushButton {
            background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #4f9ddc;
            padding: 5px; min-width: 70px;
        }
        QMessageBox QPushButton:hover { background-color: #3a3a3a; }
        QMessageBox QPushButton:pressed { background-color: #4a4a4a; }
    """)
    msg_box.exec_()


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setModal(False)
        self.setFixedSize(360, 420)
        self.init_ui()
        self.apply_stylesheet()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # Window Selection
        layout.addWidget(QLabel("Selecione a janela:"))
        self.window_dropdown = QComboBox()
        self.populate_windows()
        self.window_dropdown.currentTextChanged.connect(self.load_window_settings)
        layout.addWidget(self.window_dropdown)

        # Checkboxes
        checkbox_frame = QFrame()
        checkbox_layout = QGridLayout(checkbox_frame)
        self.chk_disable_collect = QCheckBox("Desativar Coleta")
        self.chk_disable_center = QCheckBox("Des. Mouse Centro")
        self.chk_buff = QCheckBox("Buff")
        self.chk_kalima = QCheckBox("Kalima")
        checkbox_layout.addWidget(self.chk_disable_collect, 0, 0)
        checkbox_layout.addWidget(self.chk_disable_center, 0, 1)
        checkbox_layout.addWidget(self.chk_buff, 1, 0)
        checkbox_layout.addWidget(self.chk_kalima, 1, 1)
        layout.addWidget(checkbox_frame)

        # Buff settings
        buff_frame = QFrame()
        buff_layout = QHBoxLayout(buff_frame)
        buff_layout.addWidget(QLabel("Tempo (s):"))
        self.entry_interval = QLineEdit()
        self.entry_interval.setFixedWidth(40)
        buff_layout.addWidget(self.entry_interval)
        buff_layout.addWidget(QLabel("Buff:"))
        self.entry_buff_key = QLineEdit()
        self.entry_buff_key.setFixedWidth(30)
        buff_layout.addWidget(self.entry_buff_key)
        buff_layout.addWidget(QLabel("Atk:"))
        self.entry_attack_key = QLineEdit()
        self.entry_attack_key.setFixedWidth(30)
        buff_layout.addWidget(self.entry_attack_key)
        buff_layout.addStretch()
        layout.addWidget(buff_frame)

        # Collect/Pause time
        time_frame = QFrame()
        time_layout = QHBoxLayout(time_frame)
        time_layout.addWidget(QLabel("Coletar (m):"))
        self.entry_collect_time = QLineEdit()
        self.entry_collect_time.setFixedWidth(40)
        time_layout.addWidget(self.entry_collect_time)
        time_layout.addWidget(QLabel("Pausa (m):"))
        self.entry_pause_time = QLineEdit()
        self.entry_pause_time.setFixedWidth(40)
        time_layout.addWidget(self.entry_pause_time)
        time_layout.addStretch()
        layout.addWidget(time_frame)

        # Item Selection
        layout.addWidget(QLabel("Itens para coletar:"))
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        item_widget = QWidget()
        self.item_layout = QGridLayout(item_widget)
        scroll_area.setWidget(item_widget)
        layout.addWidget(scroll_area)

        self.item_checkboxes = {}
        self.populate_items()

        # Save Button
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.save_and_close)
        layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        self.load_window_settings()

    def populate_windows(self):
        janelas = find_window_titles_by_partial_title("MUCABRASIL")
        self.shortened_titles = [t.split(' - ')[0] for t in janelas]
        if not self.shortened_titles: return

        for title in self.shortened_titles:
            if title not in buff_config:
                buff_config[title] = {"habilitado": False, "intervalo": "240", "tecla_buff": "2", "tecla_ataque": "1", "desativar_centralizacao": False, "desativar_coleta": False, "tempo_coleta": "60", "tempo_pausa": "1", "kalima": False}

        self.window_dropdown.addItems(self.shortened_titles)
        if selected_window_var and selected_window_var in self.shortened_titles:
            self.window_dropdown.setCurrentText(selected_window_var)

    def populate_items(self):
        row, col = 0, 0
        for base_name in sorted(base_templates.keys()):
            display_name = nomes_amigaveis.get(base_name, base_name.capitalize())
            checkbox = QCheckBox(display_name)
            checkbox.setChecked(itens_ativos.get(base_name, True))
            self.item_layout.addWidget(checkbox, row, col)
            self.item_checkboxes[base_name] = checkbox
            col = 1 - col
            if col == 0: row += 1

    def load_window_settings(self):
        window_title = self.window_dropdown.currentText()
        if not window_title: return
        config = buff_config.get(window_title, {})
        self.chk_buff.setChecked(config.get("habilitado", False))
        self.entry_interval.setText(str(config.get("intervalo", "240")))
        self.entry_buff_key.setText(config.get("tecla_buff", "2"))
        self.entry_attack_key.setText(config.get("tecla_ataque", "1"))
        self.chk_disable_center.setChecked(config.get("desativar_centralizacao", False))
        self.chk_disable_collect.setChecked(config.get("desativar_coleta", False))
        self.entry_collect_time.setText(str(config.get("tempo_coleta", "60")))
        self.entry_pause_time.setText(str(config.get("tempo_pausa", "1")))
        self.chk_kalima.setChecked(config.get("kalima", False))

    def save_and_close(self):
        global selected_window_var
        window_title = self.window_dropdown.currentText()
        if window_title:
            selected_window_var = window_title
            buff_config[window_title] = {"habilitado": self.chk_buff.isChecked(), "intervalo": self.entry_interval.text(), "tecla_buff": self.entry_buff_key.text(), "tecla_ataque": self.entry_attack_key.text(), "desativar_centralizacao": self.chk_disable_center.isChecked(), "desativar_coleta": self.chk_disable_collect.isChecked(), "tempo_coleta": self.entry_collect_time.text(), "tempo_pausa": self.entry_pause_time.text(), "kalima": self.chk_kalima.isChecked()}
        for base_name, checkbox in self.item_checkboxes.items():
            itens_ativos[base_name] = checkbox.isChecked()
        salvar_config()
        self.accept()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QDialog { background-color: #1A1A1A; }
            QLabel, QCheckBox { color: white; font-family: Arial; font-size: 11px; }
            QLineEdit { background-color: #333333; color: white; border: 1px solid #555; border-radius: 3px; padding: 3px; }
            QComboBox { background-color: #2a2a2a; color: #e0e0e0; border: 1px solid #4f9ddc; padding: 4px; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView { background-color: #2a2a2a; color: #e0e0e0; selection-background-color: #4f9ddc; }
            QPushButton { background-color: #2a2a2a; color: #e0e0e0; border: 2px solid #4f9ddc; border-radius: 5px; padding: 5px; min-width: 80px; }
            QPushButton:hover { background-color: #3a3a3a; }
            QPushButton:pressed { background-color: #4a4a4a; }
            QScrollArea { border: 1px solid #333; }
        """)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_window = None
        self.init_ui()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.atualizar_tempo)

    def init_ui(self):
        self.setWindowTitle("VKG - Autopick")
        self.setFixedSize(335, 160)
        icon_path = os.path.join(os.path.dirname(__file__), "vkgico.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setStyleSheet("background-color: #1A1A1A; color: white;")
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        button_layout = QHBoxLayout()
        self.btn_iniciar = self.create_button("Iniciar", self.alternar_bot)
        self.btn_config = self.create_button("Configurações", self.abrir_seletor_janelas)
        button_layout.addWidget(self.btn_iniciar)
        button_layout.addWidget(self.btn_config)
        main_layout.addLayout(button_layout)
        self.status_player_label = QLabel("Boas-vindas!")
        self.status_player_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.status_player_label.setAlignment(Qt.AlignCenter)
        self.status_player_label.setStyleSheet("color: #D4AF37;")
        main_layout.addWidget(self.status_player_label, alignment=Qt.AlignCenter)
        status_frame_layout = QHBoxLayout()
        status_frame_layout.setAlignment(Qt.AlignCenter)
        self.label_tempo_valor_text, self.label_tempo_valor = self.create_status_label("Sessão:", "00:00")
        self.label_expira_valor_text, self.label_expira_valor = self.create_status_label("Expira:", "--/--/----")
        self.label_versao_text, self.label_versao = self.create_status_label("Versão:", f"{VERSAO_ATUAL}")
        status_frame_layout.addWidget(self.label_tempo_valor_text)
        status_frame_layout.addWidget(self.label_tempo_valor)
        status_frame_layout.addSpacing(10)
        status_frame_layout.addWidget(self.label_expira_valor_text)
        status_frame_layout.addWidget(self.label_expira_valor)
        status_frame_layout.addSpacing(10)
        status_frame_layout.addWidget(self.label_versao_text)
        status_frame_layout.addWidget(self.label_versao)
        main_layout.addLayout(status_frame_layout)
        self.set_data_expiracao_from_env()

    def create_button(self, text, on_click):
        button = QPushButton(text)
        button.setFixedSize(120, 30)
        button.setFont(QFont("Arial", 10))
        button.setStyleSheet("""
            QPushButton { background-color: #2a2a2a; color: #e0e0e0; border: 2px solid #4f9ddc; border-radius: 5px; }
            QPushButton:hover { background-color: #3a3a3a; }
            QPushButton:pressed { background-color: #4a4a4a; }
        """)
        button.clicked.connect(on_click)
        return button

    def create_status_label(self, text, value):
        label_text = QLabel(text)
        label_text.setFont(QFont("Arial", 12, QFont.Bold))
        label_text.setStyleSheet("color: #CCCCCC;")
        label_value = QLabel(value)
        label_value.setFont(QFont("Arial", 12, QFont.Bold))
        label_value.setStyleSheet("color: #D4AF37;")
        return label_text, label_value

    def set_data_expiracao(self, data_str: str):
        txt = (data_str or "").strip()
        try:
            if "-" in txt:
                parts = txt.split("-")
                if len(parts[0]) == 4: y, m, d = parts
                else: d, m, y = parts
            elif "/" in txt:
                d, m, y = txt.split("/")
            else:
                txt = "--/--/----"
            if 'y' in locals() and 'm' in locals() and 'd' in locals():
              txt = f"{str(d).zfill(2)}/{str(m).zfill(2)}/{y}"
        except Exception:
            txt = "--/--/----"
        self.label_expira_valor.setText(txt)

    def set_data_expiracao_from_env(self):
        data_exp_env = os.getenv("KB_EXPIRACAO", "").strip()
        if not data_exp_env and len(sys.argv) > 1:
            data_exp_env = sys.argv[1].strip()
        if data_exp_env:
            self.set_data_expiracao(data_exp_env)

    def alternar_bot(self):
        global bot_ativo, tempo_ativo
        if not bot_ativo:
            bot_ativo = True
            tempo_ativo = 0
            self.status_player_label.setText("Monitorando...")
            self.status_player_label.setStyleSheet("color: #D4AF37;")
            self.btn_iniciar.setText("Desativar")
            self.update_timer.start(1000)
            self.atualizar_tempo()
            threading.Thread(target=iniciar_bot, args=(self,), daemon=True).start()
        else:
            bot_ativo = False
            self.btn_iniciar.setText("Iniciar")
            if hasattr(self, 'label_tempo_valor'): self.label_tempo_valor.setText("00:00")
            self.update_timer.stop()

    def atualizar_tempo(self):
        global tempo_ativo
        if bot_ativo:
            tempo_ativo += 1
            minutos, segundos = divmod(tempo_ativo, 60)
            horas, minutos = divmod(minutos, 60)
            if horas > 0:
                tempo_str = f"{horas}H{minutos:02d}M"
            else:
                tempo_str = f"{minutos:02d}:{segundos:02d}"
            if hasattr(self, 'label_tempo_valor'): self.label_tempo_valor.setText(tempo_str)

    def update_status_player(self, text, color):
        self.status_player_label.setText(text)
        self.status_player_label.setStyleSheet(f"color: {color};")

    def abrir_seletor_janelas(self):
        janelas = find_window_titles_by_partial_title("MUCABRASIL")
        if not janelas:
            aviso_customizado("Nenhuma janela do MUCABRASIL encontrada.")
            return
        if self.config_window is None or not self.config_window.isVisible():
            self.config_window = SettingsWindow(self)
            main_pos = self.pos()
            main_width = self.width()
            dialog_pos_x = main_pos.x() + main_width + 10
            dialog_pos_y = main_pos.y()
            self.config_window.move(dialog_pos_x, dialog_pos_y)
            self.config_window.show()
        else:
            self.config_window.activateWindow()
            self.config_window.raise_()

if __name__ == '__main__':
    base_templates = agrupar_itens_unicos()
    carregar_config()
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
