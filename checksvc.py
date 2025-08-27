import time
import cv2
import win32con
import numpy as np
import win32gui
import win32ui
import tkinter as tk
import threading
import json
import os
import customtkinter as ctk
import win32api
import win32con
import win32process
from pymem import Pymem
import pymem.process
from tkinter import ttk


VERSAO_ATUAL = "1.2.8-MG"

# if __name__ == "__main__":
#     exit()

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

# Adicionado para detectar movimento humano
ultima_pos_mouse_real = (0, 0)
ultima_pos_bot = None
parar_por_movimento = False
tempo_parado = time.time()
tempo_espera = 1.5  # segundos parado para reativar
kalimas = False

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

# ---------- NOVO: EXPIRAÇÃO ----------
def set_data_expiracao(data_str: str):
    """
    Aceita 'YYYY-MM-DD', 'DD/MM/YYYY' ou 'DD-MM-YYYY' e atualiza a label.
    """
    txt = (data_str or "").strip()
    try:
        if "-" in txt:
            a, b, c = txt.split("-")
            if len(a) == 4:  # YYYY-MM-DD
                y, m, d = a, b, c
            else:            # DD-MM-YYYY
                d, m, y = a, b, c
            txt = f"{str(d).zfill(2)}/{str(m).zfill(2)}/{y}"
        elif "/" in txt:      # DD/MM/YYYY
            d, m, y = txt.split("/")
            txt = f"{str(d).zfill(2)}/{str(m).zfill(2)}/{y}"
        else:
            txt = "--/--/----"
    except Exception:
        txt = "--/--/----"
    try:
        expiracao_var.set(txt)
    except Exception:
        pass
# ------------------------------------


def pressionar_tecla(hwnd, tecla_char):
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        pass

    vk_code = {
        "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34, "5": 0x35,
        "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39, "0": 0x30
    }.get(tecla_char)

    if vk_code:
        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)


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
    global kalimas, MARGIN_PERCENT, itens_ativos

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            kalimas = config.get("kalimas", False)
            MARGIN_PERCENT = config.get("margin_percent", 0.15)
            itens_salvos = config.get("itens_ativos", [])
            buffs_lidos = config.get("buffs", {})
            janela_var.set(config.get("janela_selecionada", ""))
    else:
        kalimas = False
        MARGIN_PERCENT = 0.15
        itens_salvos = []
        buffs_lidos = {}
        janela_var.set("")

    for nome_base in base_templates:
        itens_ativos[nome_base] = tk.BooleanVar(value=(nome_base in itens_salvos))

    for nome, dados in buffs_lidos.items():
        buff_config[nome] = {
            "habilitado": tk.BooleanVar(value=dados.get("habilitado", False)),
            "intervalo": tk.StringVar(value=str(dados.get("intervalo", 240))),
            "tecla_buff": tk.StringVar(value=dados.get("tecla_buff", "2")),
            "tecla_ataque": tk.StringVar(value=dados.get("tecla_ataque", "1")),
            "desativar_centralizacao": tk.BooleanVar(value=dados.get("desativar_centralizacao", False)),
            "desativar_coleta": tk.BooleanVar(value=dados.get("desativar_coleta", False)),
            "tempo_coleta": tk.StringVar(value=str(dados.get("tempo_coleta", 60))),
            "tempo_pausa": tk.StringVar(value=str(dados.get("tempo_pausa", 1))),
            "kalima": tk.BooleanVar(value=dados.get("kalima", False))
        }

def atualizar_tempo():
    global tempo_ativo
    if bot_ativo:
        tempo_ativo += 1
        minutos = tempo_ativo // 60
        segundos = tempo_ativo % 60

        if minutos >= 60:
            horas = minutos // 60
            minutos = minutos % 60
            tempo_str = f"{horas}H{minutos:02d}M"
        else:
            tempo_str = f"{minutos:02d}:{segundos:02d}"
        try:
            label_tempo_valor.configure(text=tempo_str)
        except ValueError:
            print("Não foi possível atualizar tempo")

        root.after(1000, atualizar_tempo)

# Agrupar templates por nome base
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

def salvar_config():
    global kalimas, MARGIN_PERCENT

    partial_title = janela_var.get()
    if not partial_title:
        aviso_customizado("Nenhuma janela foi selecionada.")
        return

    itens_marcados = [nome for nome, var in itens_ativos.items() if var.get()]

    buffs = {}
    for nome in buff_config:
        buffs[nome] = {
            "habilitado": buff_config[nome]["habilitado"].get(),
            "intervalo": int(buff_config[nome]["intervalo"].get() or 240),
            "tecla_buff": buff_config[nome]["tecla_buff"].get(),
            "tecla_ataque": buff_config[nome]["tecla_ataque"].get(),
            "desativar_centralizacao": buff_config[nome]["desativar_centralizacao"].get(),
            "desativar_coleta": buff_config[nome]["desativar_coleta"].get(),
            "tempo_coleta": int(buff_config[nome]["tempo_coleta"].get() or 60),
            "tempo_pausa": int(buff_config[nome]["tempo_pausa"].get() or 1),
            "kalima": buff_config[nome]["kalima"].get()
        }

    config = {
        "margin_percent": MARGIN_PERCENT,
        "janela_selecionada": partial_title,
        "itens_ativos": itens_marcados,
        "buffs": buffs,
    }

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def aviso_customizado(mensagem):
    aviso = ctk.CTkToplevel(root)

    icon_path = os.path.join(os.path.dirname(__file__), "vkgico1.ico")
    aviso.after(250, lambda: safe_set_icon(aviso, icon_path))

    aviso.title("Aviso")
    aviso.geometry("320x140")
    aviso.resizable(False, False)
    aviso.configure(fg_color="#1A1A1A")
    aviso.grab_set()

    frame = ctk.CTkFrame(aviso, fg_color="transparent")
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    ctk.CTkLabel(frame, text="⚠", font=ctk.CTkFont("Arial", 32), text_color="#D4AF37").pack()
    ctk.CTkLabel(frame, text=mensagem, text_color="white", font=ctk.CTkFont("Arial", 14)).pack(pady=(0, 10))
    tk.Button(frame, text="Entendi", width=15, command=aviso.destroy, bg="#2a2a2a", fg="#e0e0e0", activeforeground="#ffffff").pack()

    root.update_idletasks()
    x = root.winfo_x() + root.winfo_width() + 10
    y = root.winfo_y()
    aviso.geometry(f"+{x}+{y}")

def make_lparam(x: int, y: int):
    return y << 16 | x & 0xFFFF

def find_window_handle_and_pid_by_partial_title(partial_titles):
    hwnds = []

    def enum_windows_callback(handle, _):
        window_title = win32gui.GetWindowText(handle)
        for title in partial_titles:
            if title in window_title:
                hwnds.append(handle)

    win32gui.EnumWindows(enum_windows_callback, None)
    return hwnds

def capturar_tela(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bitmap)

    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmp_info = bitmap.GetInfo()
    bmp_str = bitmap.GetBitmapBits(True)
    img = np.frombuffer(bmp_str, dtype='uint8')
    img = img.reshape((bmp_info['bmHeight'], bmp_info['bmWidth'], 4))

    win32gui.DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def left_click(hwnd, x, y, delay=0.07):
    win32gui.SendMessage(hwnd, WM_MOUSEMOVE, 0, make_lparam(x, y))
    time.sleep(0.05)
    win32gui.SendMessage(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, make_lparam(x, y))
    time.sleep(delay)
    win32gui.SendMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))
    time.sleep(0.05)

def localizar_item_na_tela(hwnd):
    frame = capturar_tela(hwnd)
    if frame is None:
        return None, None, None, None, None

    height, width = frame.shape[:2]
    margin_x = int(width * MARGIN_PERCENT)
    margin_y = int(height * MARGIN_PERCENT)

    for nome, caminho in templates.items():
        base_nome = None
        for base, nomes in base_templates.items():
            if nome in nomes:
                base_nome = base
                break
        if base_nome is None:
            continue

        if not itens_ativos.get(base_nome, tk.BooleanVar(value=True)).get():
            continue

        template = cv2.imread(caminho, cv2.IMREAD_COLOR)
        if template is None:
            continue

        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= THRESHOLD:
            item_x, item_y = max_loc

            titulo_completo = win32gui.GetWindowText(hwnd)
            titulo_parcial = next((n for n in buff_config if n in titulo_completo), None)
            kalima_var = buff_config.get(titulo_parcial, {}).get("kalima", None)
            usar_kalima = kalima_var.get() if kalima_var else False

            if nome in deslocamentos:
                desloc_x, desloc_y = deslocamentos_kalima[nome] if usar_kalima else deslocamentos[nome]
            else:
                desloc_x, desloc_y = (5, 10)

            pos_x = item_x + desloc_x
            pos_y = item_y + desloc_y

            if margin_x < pos_x < (width - margin_x) and margin_y < pos_y < (height - margin_y):
                return (nome, pos_x, pos_y, item_x, item_y)

    return None, None, None, None, None

def mover_mouse_para_centro(hwnd, offset_y=50, offset_x=7):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    center_x_rel = (right - left) // 2 - offset_x
    center_y_rel = (bottom - top) // 2 - offset_y
    lparam = make_lparam(center_x_rel, center_y_rel)
    win32gui.SendMessage(hwnd, WM_MOUSEMOVE, 0, lparam)

def rechecar_item(hwnd, nome, x, y):
    frame = capturar_tela(hwnd)
    template = cv2.imread(templates[nome], cv2.IMREAD_COLOR)

    if frame is None or template is None:
        return False

    h, w = template.shape[:2]

    if kalimas:
        desloc_x, desloc_y = deslocamentos_kalima.get(nome, (5, 10))
    else:
        desloc_x, desloc_y = deslocamentos.get(nome, (5, 10))

    # Reverte deslocamento
    top_left_x = x - desloc_x
    top_left_y = y - desloc_y

    recorte_x1 = max(0, top_left_x - 5)
    recorte_y1 = max(0, top_left_y - 5)
    recorte_x2 = top_left_x + w + 5
    recorte_y2 = top_left_y + h + 5

    recorte = frame[recorte_y1:recorte_y2, recorte_x1:recorte_x2]

    result = cv2.matchTemplate(recorte, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)

    return max_val >= THRESHOLD

def mover_mouse_para_centro(hwnd, offset_y, offset_x):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    center_x_rel = (right - left) // 2 - offset_x
    center_y_rel = (bottom - top) // 2 - offset_y
    lparam = make_lparam(center_x_rel, center_y_rel)
    win32gui.SendMessage(hwnd, WM_MOUSEMOVE, 0, lparam)

def monitorar_player(pm, endereco_montaria, endereco_interface, endereco_imp, endereco_sm, endereco_elfa, endereco_bk, endereco_mg, titulo_parcial, status_var):
    ultimo_valor_imp = None
    ultimo_valor_elfa = None
    ultimo_valor_bk = None
    ultimo_valor_mg = None
    ultimo_valor_sm = None

    ciclos_estaveis = 0
    while bot_ativo:
        try:
            valor_montaria = pm.read_int(endereco_montaria)
            valor_imp = pm.read_int(endereco_imp)
            valor_interface = pm.read_int(endereco_interface)
            valor_elfa = pm.read_int(endereco_elfa)
            valor_bk = pm.read_int(endereco_bk)
            valor_mg = pm.read_int(endereco_mg)
            valor_sm = pm.read_int(endereco_sm)

            config = buff_config.get(titulo_parcial, {})
            buff_ativado = config.get("habilitado", tk.BooleanVar(value=False)).get()
            safe_zone_value_1 = 5 if buff_ativado else 3

            imp_alterado = ultimo_valor_imp is not None and valor_imp != ultimo_valor_imp
            elfa_alterado = ultimo_valor_elfa is not None and valor_elfa != ultimo_valor_elfa
            bk_alterado = ultimo_valor_bk is not None and valor_bk != ultimo_valor_bk
            sm_alterado = ultimo_valor_sm is not None and valor_sm != ultimo_valor_sm
            mg_alterado = ultimo_valor_mg is not None and valor_mg != ultimo_valor_mg

            player_detectado = (
                valor_montaria != 0
                or imp_alterado
                or valor_interface != safe_zone_value_1
                or elfa_alterado
                or bk_alterado
                #or mg_alterado
                or sm_alterado
            )
            if player_detectado:
                ciclos_estaveis = 0
                if not zona_perigo.get(titulo_parcial, False):
                    zona_perigo[titulo_parcial] = True
                    status_player_var.set(f"{titulo_parcial} \nPLAYER DETECTADO!")
                    status_player_label.configure(text_color="#aa5959")
            else:
                ciclos_estaveis += 1
                if ciclos_estaveis >= 2:
                    if zona_perigo.get(titulo_parcial, False):
                        zona_perigo[titulo_parcial] = False
                        status_player_var.set(f"{titulo_parcial} \nZona segura")
                        status_player_label.configure(text_color="#69aa59")

            ultimo_valor_imp = valor_imp
            ultimo_valor_elfa = valor_elfa
            ultimo_valor_bk = valor_bk
            ultimo_valor_mg = valor_mg
            ultimo_valor_sm = valor_sm
        except Exception as e:
            print(f"[ERRO] monitorar_player {titulo_parcial}: {e}")
            status_var.set(f"Erro ao ler memória [{titulo_parcial}]")

        time.sleep(1)

def iniciar_bot():
    global bot_ativo, ultima_pos_bot, parar_por_movimento, tempo_parado, ultima_pos_mouse_real

    if not bot_ativo:
        return

    partial_title = janela_var.get()
    if not partial_title:
        aviso_customizado("Nenhuma janela foi selecionada.")
        return

    hwnds = find_window_handle_and_pid_by_partial_title([partial_title])
    if not hwnds:
        return
    
    coleta_pausa_timers = {}

    for hwnd in hwnds:
        titulo_completo = win32gui.GetWindowText(hwnd)
        titulo_parcial = next((nome for nome in buff_config if nome in titulo_completo), None)
        if not titulo_parcial:
            continue

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        pm = Pymem()
        pm.open_process_from_id(pid)
        modulo = pymem.process.module_from_name(pm.process_handle, "mucabrasil.exe")
        base = modulo.lpBaseOfDll

        endereco_montaria = base + 0x4295CA4 #ATT
        endereco_imp = base + 0x3BFED44 #ATT
        endereco_interface = base + 0x42991F4 #ATT
        endereco_elfa = base + 0x3BE56DC #ATUALIZADO
        endereco_bk = base + 0x3BE5874 # ATT
        endereco_mg = base + 0x3BE5940 #ATT
        endereco_sm = base + 0x3BE57A8 #ATT

        zona_perigo[titulo_parcial] = False

        if titulo_parcial not in status_vars:
            status_vars[titulo_parcial] = tk.StringVar(value="Monitorando...")

        t = threading.Thread(
            target=monitorar_player,
            args=(pm, endereco_montaria, endereco_interface, endereco_imp, endereco_sm, endereco_elfa, endereco_bk, endereco_mg, titulo_parcial, status_vars[titulo_parcial]),
            daemon=True
        )
        t.start()

    try:
        while bot_ativo:
            partial_title = janela_var.get()
            if not partial_title:
                time.sleep(1)
                continue

            hwnds = find_window_handle_and_pid_by_partial_title([partial_title])
            if not hwnds:
                time.sleep(1)
                continue

            # VERIFICAR MOVIMENTO GLOBAL
            movimento_detectado = False
            for hwnd in hwnds:
                if mouse_dentro_jogo(hwnd):
                    atual = win32gui.GetCursorPos()
                    if atual != ultima_pos_mouse_real and atual != ultima_pos_bot:
                        ultima_pos_mouse_real = atual
                        tempo_parado = time.time()
                        movimento_detectado = True
                        break

            if movimento_detectado:
                if not parar_por_movimento:
                    parar_por_movimento = True
            else:
                if parar_por_movimento and time.time() - tempo_parado >= tempo_espera:
                    parar_por_movimento = False

            if parar_por_movimento:
                time.sleep(0.05)
                continue

            # LOOP 1: janelas com desativar_coleta = True
            for hwnd in hwnds:
                titulo_completo = win32gui.GetWindowText(hwnd)
                titulo_parcial = next((nome for nome in buff_config if nome in titulo_completo), None)
                if not titulo_parcial:
                    continue

                config = buff_config[titulo_parcial]
                if not config.get("desativar_coleta", tk.BooleanVar(value=False)).get():
                    continue

                if not config.get("desativar_centralizacao", tk.BooleanVar(value=False)).get():
                    mover_mouse_para_centro(hwnd, offset_y=50, offset_x=7)
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    center_x = (right - left) // 2 - 7
                    center_y = (bottom - top) // 2 - 50
                    ultima_pos_bot = (center_x, center_y)

                if config["habilitado"].get():
                    try:
                        intervalo = int(config["intervalo"].get())
                    except (ValueError, TypeError):
                        intervalo = 240

                    tecla_buff = config["tecla_buff"].get()
                    tecla_ataque = config["tecla_ataque"].get()
                    ultimo_tempo = buff_timers.get(titulo_parcial, 0)

                    if time.time() - ultimo_tempo >= intervalo:
                        try:
                            win32gui.ShowWindow(hwnd, 9)
                            win32gui.SetForegroundWindow(hwnd)
                        except:
                            pass
                    
                        pressionar_tecla(hwnd, tecla_buff)
                        time.sleep(0.1)
                        pressionar_tecla(hwnd, tecla_ataque)
                        buff_timers[titulo_parcial] = time.time()

            # LOOP 2: janelas com coleta ativa
            for hwnd in hwnds:
                titulo_completo = win32gui.GetWindowText(hwnd)
                titulo_parcial = next((nome for nome in buff_config if nome in titulo_completo), None)
                if not titulo_parcial:
                    continue

                config = buff_config[titulo_parcial]
                em_perigo = zona_perigo.get(titulo_parcial, False)

                if config.get("desativar_coleta", tk.BooleanVar(value=False)).get() or em_perigo:
                    if em_perigo:
                        if not config.get("desativar_centralizacao", tk.BooleanVar(value=False)).get():
                            mover_mouse_para_centro(hwnd, offset_y=50, offset_x=7)
                            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                            center_x = (right - left) // 2 - 7
                            center_y = (bottom - top) // 2 - 50
                            ultima_pos_bot = (center_x, center_y)
                            pressionar_direito(hwnd)

                        if config["habilitado"].get():
                            try:
                                intervalo = int(config["intervalo"].get())
                            except (ValueError, TypeError):
                                intervalo = 240

                            tecla_buff = config["tecla_buff"].get()
                            tecla_ataque = config["tecla_ataque"].get()
                            ultimo_tempo = buff_timers.get(titulo_parcial, 0)

                            if time.time() - ultimo_tempo >= intervalo:
                                try:
                                    win32gui.ShowWindow(hwnd, 9)
                                    win32gui.SetForegroundWindow(hwnd)
                                except:
                                    pass
                                pressionar_tecla(hwnd, tecla_buff)
                                time.sleep(0.1)
                                pressionar_tecla(hwnd, tecla_ataque)
                                buff_timers[titulo_parcial] = time.time()
                    continue

                # ⏱ Inicializar temporizador de coleta/pausa
                if titulo_parcial not in coleta_pausa_timers:
                    try:
                        tempo_coleta = int(config.get("tempo_coleta", tk.StringVar(value="60")).get()) * 60
                        tempo_pausa = int(config.get("tempo_pausa", tk.StringVar(value="1")).get()) * 60
                    except (ValueError, TypeError):
                        tempo_coleta, tempo_pausa = 300, 120
                    coleta_pausa_timers[titulo_parcial] = {
                        "inicio": time.time(),
                        "em_pausa": False,
                        "tempo_coleta": tempo_coleta,
                        "tempo_pausa": tempo_pausa
                    }

                # ⏳ Atualizar tempo de pausa/coleta
                timer = coleta_pausa_timers[titulo_parcial]
                tempo_decorrido = time.time() - timer["inicio"]

                if not timer["em_pausa"]:
                    if tempo_decorrido >= timer["tempo_coleta"]:
                        timer["em_pausa"] = True
                        timer["inicio"] = time.time()
                else:
                    if tempo_decorrido >= timer["tempo_pausa"]:
                        timer["em_pausa"] = False
                        timer["inicio"] = time.time()

                # 🧠 Buff automático
                if config["habilitado"].get():
                    try:
                        intervalo = int(config["intervalo"].get())
                    except (ValueError, TypeError):
                        intervalo = 240

                    tecla_buff = config["tecla_buff"].get()
                    tecla_ataque = config["tecla_ataque"].get()
                    ultimo_tempo = buff_timers.get(titulo_parcial, 0)

                    if time.time() - ultimo_tempo >= intervalo:
                        try:
                            win32gui.ShowWindow(hwnd, 9)
                            win32gui.SetForegroundWindow(hwnd)
                        except:
                            pass
                        pressionar_tecla(hwnd, tecla_buff)
                        time.sleep(0.1)
                        pressionar_tecla(hwnd, tecla_ataque)
                        buff_timers[titulo_parcial] = time.time()

                # ⛔ Se estiver em pausa, apenas centraliza e ataca
                if timer["em_pausa"]:
                    if not config.get("desativar_centralizacao", tk.BooleanVar(value=False)).get():
                        mover_mouse_para_centro(hwnd, offset_y=50, offset_x=7)
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        center_x = (right - left) // 2 - 7
                        center_y = (bottom - top) // 2 - 50
                        ultima_pos_bot = (center_x, center_y)
                        pressionar_direito(hwnd)
                    continue

                nome, _, _, x_item, y_item = localizar_item_na_tela(hwnd)
                if nome:
                    time.sleep(0.3)
                    nome2, x2_click, y2_click, x2_item, y2_item = localizar_item_na_tela(hwnd)
                    if nome2 == nome and abs(x2_item - x_item) <= 2 and abs(y2_item - y_item) <= 2:
                        soltar_direito(hwnd)
                        time.sleep(0.02)
                        left_click(hwnd, x2_click, y2_click)
                        ultima_pos_bot = (x2_click, y2_click)
                        
                        if rechecar_item(hwnd, nome, x2_click, y2_click):
                            pressionar_direito(hwnd)
                            time.sleep(3)
                            if rechecar_item(hwnd, nome, x2_click, y2_click):
                                left_click(hwnd, x2_click, y2_click)
                            continue

                elif not config.get("desativar_centralizacao", tk.BooleanVar(value=False)).get() and not timer["em_pausa"]:
                    mover_mouse_para_centro(hwnd, offset_y=50, offset_x=7)
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    center_x = (right - left) // 2 - 7
                    center_y = (bottom - top) // 2 - 50
                    ultima_pos_bot = (center_x, center_y)
                    pressionar_direito(hwnd)
    
            time.sleep(1 / 24)

    except KeyboardInterrupt:
        print("[DEBUG] Encerrado pelo usuário.")

def alternar_bot():
    global bot_ativo, tempo_ativo, label_tempo_valor
    if not bot_ativo:
        bot_ativo = True
        tempo_ativo = 0
        status_player_var.set("Monitorando...")
        status_player_label.configure(text_color="#D4AF37")
        btn_iniciar.config(text="Desativar", bg="#2a2a2a", fg="#e0e0e0", activeforeground="#ffffff", highlightbackground="#4f9ddc",highlightthickness=2, activebackground="#3a3a3a")
        atualizar_tempo()
        threading.Thread(target=iniciar_bot, daemon=True).start()
    else:
        bot_ativo = False
        tempo_ativo = 0
        btn_iniciar.config(text="Iniciar", bg="#2a2a2a", fg="#e0e0e0", activeforeground="#ffffff", highlightbackground="#4f9ddc",highlightthickness=2, activebackground="#3a3a3a")
        label_tempo_valor.configure(text="00:00")

def atualizar_indicadores():
    global kalimas
    try:
        kalimas = any(
            cfg.get("kalima", tk.BooleanVar(value=False)).get()
            for cfg in buff_config.values()
        )
    except Exception:
        kalimas = False

# Simulando as janelas encontradas
janelas = ["[1/3] MUCABRASIL", "[2/3] MUCABRASIL", "[3/3] MUCABRASIL"]
janela_var = None
popup_config = None

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        try:
            caminho_icone = os.path.join(os.path.dirname(__file__), "vkgico.ico")
            tw.iconbitmap(caminho_icone)
        except:
            pass

        label = tk.Label(tw, text=self.text, justify='left',
                         background="#333333", foreground="white", relief='solid', borderwidth=1,
                         font=("Arial", 9))
        label.pack(ipadx=6, ipady=2)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def safe_set_icon(janela, caminho_icone):
    try:
        janela.iconbitmap(caminho_icone)
    except:
        pass

def safe_focus(janela):
    try:
        janela.focus()
        return True
    except:
        return False



def abrir_seletor_janelas():
    global popup_config

    if popup_config is not None and popup_config.winfo_exists():
        try:
            popup_config.lift()
            return
        except:
            popup_config = None

    popup_config = ctk.CTkToplevel(root)
    icon_path = os.path.join(os.path.dirname(__file__), "vkgico.ico")
    safe_set_icon(popup_config, icon_path)
    popup_config.after(250, lambda: safe_set_icon(popup_config, icon_path))

    popup_config.title("Configurações")
    popup_config.geometry("360x450")
    popup_config.resizable(False, True)
    popup_config.configure(fg_color="#1A1A1A")
    popup_config.resizable(False, False)

    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    root_w = root.winfo_width()
    popup_x = root_x + root_w + 10
    popup_y = root_y
    popup_config.geometry(f"+{popup_x}+{popup_y}")

    bg_color = "#1A1A1A"
    container = tk.Frame(popup_config, bg=bg_color)
    container.pack(fill="both", expand=True)

    tk.Label(container, text="Selecione a janela:", bg=bg_color, fg="#D4AF37", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0), padx=110)

    config_frames = {}

    itens_container = tk.Frame(container, bg=bg_color)
    itens_container.pack_forget()

    tk.Label(
        itens_container,
        text="Itens para coletar:",
        bg=bg_color,
        fg="#D4AF37",
        font=("Arial", 10, "bold"),
    ).pack(anchor="w", pady=(10, 0), padx=(10, 0))

    frame_itens = tk.Frame(itens_container, bg=bg_color)
    frame_itens.pack(pady=5)

    row_it = 0
    col_it = 0
    for base_nome in sorted(base_templates):
        nome_exibido = nomes_amigaveis.get(base_nome, base_nome.capitalize())
        if base_nome not in itens_ativos:
            itens_ativos[base_nome] = tk.BooleanVar(value=True)
        tk.Checkbutton(
            frame_itens,
            text=nome_exibido,
            variable=itens_ativos[base_nome],
            bg=bg_color,
            fg="white",
            selectcolor=bg_color,
            activebackground=bg_color,
            activeforeground="white",
        ).grid(row=row_it, column=col_it, sticky="w", padx=10, pady=2)
        col_it += 1
        if col_it > 1:
            col_it = 0
            row_it += 1

    def on_salvar():
        salvar_config()
        atualizar_indicadores()
        popup_config.destroy()

    salvar_btn = tk.Button(
        container,
        text="Salvar",
        command=on_salvar,
        width=10,
        bg="#2a2a2a",
        fg="#e0e0e0",
        activeforeground="#ffffff",
        highlightbackground="#4f9ddc",
        highlightthickness=2,
        activebackground="#3a3a3a",
    )
    salvar_btn.pack_forget()

    def mostrar_config(nome):
        # Esconde todos os componentes para garantir um estado limpo
        for fr in config_frames.values():
            fr.pack_forget()
        itens_container.pack_forget()
        salvar_btn.pack_forget()

        # Mostra os componentes relevantes se uma janela for selecionada
        if nome:
            frame = config_frames.get(nome)
            if frame:
                frame.pack(pady=5, fill="x", padx=25)
            itens_container.pack(fill="x")
            salvar_btn.pack(pady=10)

    def selecionar(value):
        janela_var.set(value)
        mostrar_config(value)

    combo = ttk.Combobox(container, values=janelas, variable=janela_var, command=selecionar, width=200)
    if janela_var.get():
        combo.set(janela_var.get())
    else:
        combo.set("Selecione")
        janela_var.set("")
    combo.pack(padx=10, pady=(5, 10))

    for nome in janelas:
        if nome not in buff_config:
            buff_config[nome] = {
                "habilitado": tk.BooleanVar(),
                "intervalo": tk.StringVar(value="240"),
                "tecla_buff": tk.StringVar(value="2"),
                "tecla_ataque": tk.StringVar(value="1"),
                "desativar_centralizacao": tk.BooleanVar(value=False),
                "desativar_coleta": tk.BooleanVar(value=False),
                "tempo_coleta": tk.StringVar(value="60"),
                "tempo_pausa": tk.StringVar(value="1"),
                "kalima": tk.BooleanVar(value=False),
            }
        else:
            for chave, valor_padrao in {
                "habilitado": tk.BooleanVar(),
                "intervalo": tk.StringVar(value="240"),
                "tecla_buff": tk.StringVar(value="2"),
                "tecla_ataque": tk.StringVar(value="1"),
                "desativar_centralizacao": tk.BooleanVar(value=False),
                "desativar_coleta": tk.BooleanVar(value=False),
                "tempo_coleta": tk.StringVar(value="5"),
                "tempo_pausa": tk.StringVar(value="2"),
                "kalima": tk.BooleanVar(value=False),
            }.items():
                if chave not in buff_config[nome]:
                    buff_config[nome][chave] = valor_padrao

        frame = tk.Frame(container, bg=bg_color)
        config_frames[nome] = frame

        checkbox_frame = tk.Frame(frame, bg=bg_color)
        checkbox_frame.pack(pady=5, fill="x")

        tk.Checkbutton(
            checkbox_frame,
            text="Des. Mouse Centro",
            variable=buff_config[nome]["desativar_centralizacao"],
            bg=bg_color,
            fg="white",
            selectcolor=bg_color,
            activebackground=bg_color,
            activeforeground="white",
        ).grid(row=0, column=1, sticky="w", padx=(0, 5))

        tk.Checkbutton(
            checkbox_frame,
            text="Desativar Coleta",
            variable=buff_config[nome]["desativar_coleta"],
            bg=bg_color,
            fg="white",
            selectcolor=bg_color,
            activebackground=bg_color,
            activeforeground="white",
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))

        tk.Checkbutton(
            checkbox_frame,
            text="Kalima",
            variable=buff_config[nome]["kalima"],
            bg=bg_color,
            fg="white",
            selectcolor=bg_color,
            activebackground=bg_color,
            activeforeground="white",
        ).grid(row=1, column=1, sticky="w", padx=(0, 5))

        tk.Checkbutton(
            checkbox_frame,
            text="Buff",
            variable=buff_config[nome]["habilitado"],
            bg=bg_color,
            fg="white",
            selectcolor=bg_color,
            activebackground=bg_color,
            activeforeground="white",
        ).grid(row=1, column=0, sticky="w", padx=(0, 5))

        linha = tk.Frame(frame, bg=bg_color)
        linha.pack(anchor="w", pady=1)

        tk.Label(linha, text="Tempo (s):", bg=bg_color, fg="white", font=("Arial", 9)).pack(side="left")
        tk.Entry(
            linha,
            textvariable=buff_config[nome]["intervalo"],
            width=4,
            bg="#333333",
            fg="white",
            insertbackground="white",
        ).pack(side="left", padx=(5, 10))

        tk.Label(linha, text="Buff:", bg=bg_color, fg="white", font=("Arial", 9)).pack(side="left")
        tk.Entry(
            linha,
            textvariable=buff_config[nome]["tecla_buff"],
            width=2,
            bg="#333333",
            fg="white",
            insertbackground="white",
        ).pack(side="left", padx=5)

        tk.Label(linha, text="Atk:", bg=bg_color, fg="white", font=("Arial", 9)).pack(side="left")
        tk.Entry(
            linha,
            textvariable=buff_config[nome]["tecla_ataque"],
            width=2,
            bg="#333333",
            fg="white",
            insertbackground="white",
        ).pack(side="left")

        linha_tempo = tk.Frame(frame, bg=bg_color)
        linha_tempo.pack(anchor="w")

        tk.Label(
            linha_tempo,
            text="Coletar (m):",
            bg=bg_color,
            fg="white",
            font=("Arial", 9),
        ).pack(side="left", pady=(10, 0))
        tk.Entry(
            linha_tempo,
            textvariable=buff_config[nome]["tempo_coleta"],
            width=3,
            bg="#333333",
            fg="white",
            insertbackground="white",
        ).pack(side="left", pady=(10, 0))

        tk.Label(
            linha_tempo,
            text="Pausa (m):",
            bg=bg_color,
            fg="white",
            font=("Arial", 9),
        ).pack(side="left", pady=(10, 0))
        tk.Entry(
            linha_tempo,
            textvariable=buff_config[nome]["tempo_pausa"],
            width=3,
            bg="#333333",
            fg="white",
            insertbackground="white",
        ).pack(side="left", pady=(10, 0))

        frame.pack_forget()

    mostrar_config(janela_var.get())

    popup_config.after(50, popup_config.deiconify)

# Interface principal
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.configure(fg_color="#1A1A1A")
janela_var = tk.StringVar(value="")
base_templates = agrupar_itens_unicos()
carregar_config()
root.title("VKG - Autopick")
root.geometry("335x160")
icon_path = os.path.join(os.path.dirname(__file__), "vkgico.ico")
root.iconbitmap(icon_path)
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", lambda: [root.destroy()])

# NOVO: variável Tk para expiração
expiracao_var = tk.StringVar(value="--/--/----")

frame_botoes = ctk.CTkFrame(root, fg_color="transparent")
frame_botoes.pack(anchor='center', pady=(20,0))

btn_iniciar = tk.Button(frame_botoes, text="Iniciar", command=alternar_bot, width=12, bg="#2a2a2a", fg="#e0e0e0", activeforeground="#ffffff", highlightbackground="#4f9ddc",highlightthickness=2, activebackground="#3a3a3a")
btn_iniciar.pack(pady=(15, 0), side='left', padx=5)

btn_janelas = tk.Button(frame_botoes, text="Configurações", command=abrir_seletor_janelas, width=12, bg="#2a2a2a", fg="#e0e0e0", activeforeground="#ffffff", highlightbackground="#4f9ddc",highlightthickness=2, activebackground="#3a3a3a")
btn_janelas.pack(pady=(15, 0), side='left', padx=5)

status_player_var = tk.StringVar(value="Boas-vindas!")
status_player_label = ctk.CTkLabel(root, textvariable=status_player_var, text_color="#D4AF37", font=("Arial", 12, "bold"))
status_player_label.pack(pady=(20, 5))

frame_status = ctk.CTkFrame(root, fg_color="transparent")
frame_status.pack(pady=(10, 10))

# Sessão
label_sessao_texto = ctk.CTkLabel(frame_status, text="Sessão:", text_color="#CCCCCC", font=("Arial", 12, "bold"), fg_color="transparent")
label_sessao_texto.pack(side="left", padx=(0, 3))

label_tempo_valor = ctk.CTkLabel(frame_status, text="00:00", text_color="#D4AF37", font=("Arial", 12, "bold"), fg_color="transparent")
label_tempo_valor.pack(side="left", padx=(0, 8))

# NOVO: Expiração (ao lado de Sessão)
label_expira_texto = ctk.CTkLabel(frame_status, text="Expira:", text_color="#CCCCCC", font=("Arial", 12, "bold"), fg_color="transparent")
label_expira_texto.pack(side="left", padx=(0, 3))

label_expira_valor = ctk.CTkLabel(frame_status, textvariable=expiracao_var, text_color="#D4AF37", font=("Arial", 12, "bold"), fg_color="transparent")
label_expira_valor.pack(side="left", padx=(0, 8))

# Versão
label_versao_texto = ctk.CTkLabel(frame_status, text="Versão:", text_color="#CCCCCC", font=("Arial", 12, "bold"))
label_versao_texto.pack(side="left", padx=(0, 3))

label_versao = ctk.CTkLabel(frame_status, text=f"{VERSAO_ATUAL}", text_color="#D4AF37", font=("Arial", 12, "bold"))
label_versao.pack(side="left", padx=(0, 8))

frame_status_individual = ctk.CTkFrame(root, fg_color="transparent")
frame_status_individual.pack(pady=(5, 10), fill="x")

# NOVO: Lê a data de expiração enviada pelo login (env var ou argumento) e aplica.
data_exp_env = os.getenv("KB_EXPIRACAO", "").strip()
if not data_exp_env:
    import sys
    if len(sys.argv) > 1:
        data_exp_env = sys.argv[1].strip()

if data_exp_env:
    set_data_expiracao(data_exp_env)

root.mainloop()
