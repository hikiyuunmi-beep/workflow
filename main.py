import tkinter as tk
import requests
import hashlib
import os
import socket
from datetime import datetime
import base64
import sys
import customtkinter as ctk
import json
import time
import uuid
import platform
import getpass
from tkinter import messagebox

# URLs GitHub
URL_CREDENCIAIS = "https://raw.githubusercontent.com/araujorick/kb_credentials/main/dbcred_v1.json"
GITHUB_API_MACHINES = "https://api.github.com/repos/araujorick/kb_credentials/contents/users_machines.json"
GITHUB_API_LOG = "https://api.github.com/repos/araujorick/kb_credentials/contents/access_log.txt"
auth_key = "ghp_" + "KbBPGHpcYYU4n8LL" + "hrU3lMgSawo65x1yRbBn"
VERSAO_ATUAL = "1.2.8-MG"
CLASSE_ATUAL = "MG"

def get_machine_id():
    base = f"{uuid.getnode()}|{socket.gethostname()}|{getpass.getuser()}|{platform.platform()}"
    return hashlib.sha256(base.encode()).hexdigest()[:16]

def obter_data_servidor():
    fontes_tempo = [
        "https://worldtimeapi.org/api/timezone/America/Sao_Paulo",
        "http://worldclockapi.com/api/json/utc/now",
        "http://worldtimeapi.org/api/ip"
    ]
    for url in fontes_tempo:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                j = r.json()
                if "datetime" in j:
                    # worldtimeapi: ISO 8601 (possível 'Z' no final)
                    return datetime.fromisoformat(j["datetime"].replace("Z", "+00:00"))
                if "currentDateTime" in j:
                    # worldclockapi: 'YYYY-MM-DDTHH:MMZ'
                    return datetime.strptime(j["currentDateTime"], "%Y-%m-%dT%H:%MZ")
        except:
            continue
    return datetime.now()

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def carregar_credenciais():
    try:
        r = requests.get(URL_CREDENCIAIS, timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def _norm_ids(seq):
    """Normaliza IDs para comparação robusta (lowercase e sem espaços), removendo duplicados."""
    if not isinstance(seq, list):
        return []
    norm = [str(x).strip().lower() for x in seq if x]
    return list(dict.fromkeys(norm))

def obter_estado_por_ip():
    """Retorna o estado/UF pelo IP público. Vazio se falhar."""
    try:
        r = requests.get("http://ip-api.com/json", timeout=5)
        if r.status_code == 200:
            j = r.json()
            # 'region' costuma trazer UF (ex.: 'SP'); 'regionName' é o nome (ex.: 'São Paulo')
            return j.get("region") or j.get("regionName") or ""
    except:
        pass
    return ""

def salvar_log_acesso(app_user, status):
    """
    Acrescenta linha no access_log.txt no GitHub.
    Se for admin, oculta informações sensíveis.
    """
    headers = {
        "Authorization": f"Bearer {auth_key}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "VKG-Auth/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if app_user.strip().lower() == "admin":
        linha = f"{datetime.now():%Y-%m-%d %H:%M:%S} | appuser: admin | {status}\n"
    else:
        pc_user = getpass.getuser()
        estado = obter_estado_por_ip()
        machine_id = get_machine_id()
        linha = f"{datetime.now():%Y-%m-%d %H:%M:%S} | winuser: {pc_user} | appuser: {app_user} | estado: {estado} | {status} | {machine_id}\n"

    try:
        r = requests.get(GITHUB_API_LOG, headers=headers, timeout=10)
        if r.status_code == 200:
            j = r.json()
            content = base64.b64decode((j.get("content") or "").encode()).decode("utf-8") + linha
            body = {
                "message": f"Log acesso: {app_user} ({status})",
                "content": base64.b64encode(content.encode()).decode(),
                "sha": j.get("sha")
            }
        elif r.status_code == 404:
            body = {
                "message": "Criando log de acessos",
                "content": base64.b64encode(linha.encode()).decode()
            }
        else:
            return
        requests.put(GITHUB_API_LOG, headers=headers, json=body, timeout=15)
    except:
        pass


def verificar_versao():
    """
    Verifica versão remota SEM cache e mostra popup sempre que houver versão mais nova.
    """
    try:
        if CLASSE_ATUAL == "SM":
            url_versao = "https://raw.githubusercontent.com/araujorick/kb_credentials/main/versao_sm.txt"
            link_download = "https://github.com/vkgproject/vkgupdate-sm/releases/latest"
        elif CLASSE_ATUAL == "MG":
            url_versao = "https://raw.githubusercontent.com/araujorick/kb_credentials/main/versao_mg.txt"
            link_download = "https://github.com/vkgproject/vkgupdate-mg/releases/latest"
        else: 
            url_versao = "https://raw.githubusercontent.com/araujorick/kb_credentials/main/versao.txt"
            link_download = "https://github.com/vkgproject/vkgupdate/releases/latest"

        # evita cache da CDN/CDN proxy
        url_versao_ts = f"{url_versao}?t={int(time.time())}"

        r = requests.get(url_versao_ts, timeout=5)
        if r.status_code == 200:
            versao_remota = (r.text or "").strip()
            if versao_remota and versao_remota != VERSAO_ATUAL:
                aviso_nova_versao(versao_remota, link_download)
    except Exception as e:
        print(f"[AVISO] Não foi possível verificar nova versão: {e}")


def aviso_nova_versao(nova_versao, link_download):
    popup = ctk.CTkToplevel(janela)
    popup.title("Atualização")
    popup.geometry("360x150")
    popup.configure(fg_color="#242424")
    popup.resizable(False, False)
    popup.transient(janela)
    popup.attributes("-topmost", True)

    try:
        icon_path = os.path.join(os.path.dirname(__file__), "vkgico.ico")
        if os.path.exists(icon_path):
            popup.iconbitmap(icon_path)
            popup.after(200, lambda: popup.iconbitmap(icon_path))
    except Exception:
        pass

    frame = ctk.CTkFrame(popup, fg_color="transparent")
    frame.pack(expand=True, fill="both", padx=15, pady=15)

    ctk.CTkLabel(
        frame, text="Nova versão disponível!",
        text_color="orange", font=ctk.CTkFont("Arial", 16, "bold")
    ).pack(pady=(0, 10))

    ctk.CTkLabel(
        frame, text=f"Versão atual: {VERSAO_ATUAL}\nNova versão: {nova_versao}",
        text_color="white", font=("Arial", 12)
    ).pack(pady=(0, 10))

    def abrir_site():
        import webbrowser
        webbrowser.open(link_download)

    tk.Button(frame, text="Baixar agora", command=abrir_site, width=12).pack(pady=(10, 0))
    popup.grab_set()



def carregar_maquinas():
    """
    Lê users_machines.json via GitHub API.
    Retorna (data_dict, sha_str_ou_None, ok_bool).
    ok_bool = True só quando o GET 200 trouxe conteúdo atual OU 404 (arquivo ainda não existe).
    """
    headers = {
        "Authorization": f"Bearer {auth_key}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "VKG-Auth/1.0"
    }
    try:
        r = requests.get(GITHUB_API_MACHINES, headers=headers, timeout=10)
    except Exception:
        return {}, None, False

    if r.status_code == 200:
        try:
            j = r.json()
            content_b64 = (j.get("content") or "")
            content = base64.b64decode(content_b64.encode("utf-8")).decode("utf-8") if content_b64 else ""
            data = json.loads(content) if content.strip() else {}
            return data, j.get("sha"), True
        except Exception:
            return {}, None, False

    if r.status_code == 404:
        # arquivo ainda não existe no repo
        return {}, None, True  # ok=True: estado “vazio” legítimo (criamos no primeiro save)

    # 403/429/5xx etc -> falha temporária/perm de leitura
    return {}, None, False

def salvar_maquinas(data, sha, msg="Atualizando máquinas"):
    """
    Cria/atualiza users_machines.json.
    Retorna True/False conforme sucesso.
    Tenta 1 retry automático em caso de 409 (sha desatualizado).
    """
    headers = {
        "Authorization": f"Bearer {auth_key}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "VKG-Auth/1.0"
    }

    def _put(_sha):
        content = base64.b64encode(
            json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        ).decode("utf-8")
        body = {"message": msg, "content": content}
        if _sha:
            body["sha"] = _sha
        try:
            resp = requests.put(GITHUB_API_MACHINES, headers=headers, json=body, timeout=15)
            return resp
        except Exception:
            return None

    # 1ª tentativa
    resp = _put(sha)
    if resp is None:
        return False

    # sucesso (201 criado ou 200 atualizado)
    if resp.status_code in (200, 201):
        return True

    # sha desatualizado: refaz GET, atualiza sha e tenta de novo
    if resp.status_code == 409:
        data_atual, novo_sha, ok = carregar_maquinas()
        # mantemos nosso 'data' (pois queremos escrever nossa mudança), só atualizamos o sha
        resp2 = _put(novo_sha if ok else None)
        return bool(resp2 and resp2.status_code in (200, 201))

    # outros erros
    return False

# ---- util para pegar a data de expiração com chaves alternativas
def _extrair_data_expiracao(assinatura: dict) -> str:
    if not isinstance(assinatura, dict):
        return ""
    return str(
        assinatura.get("expira_em") or
        assinatura.get("expiracao") or
        assinatura.get("validade") or
        assinatura.get("data_expiracao") or
        assinatura.get("expira") or
        ""
    )

def fazer_login(event=None):
    usuario = entrada_usuario.get()
    senha = entrada_senha.get()
    senha_hash = gerar_hash_senha(senha)
    machine_id = get_machine_id().strip().lower()  # normalizado

    credenciais = carregar_credenciais()
    if not credenciais:
        salvar_log_acesso(usuario, "FALHA: erro ao carregar credenciais")
        mensagem_label.configure(text="Erro ao carregar credenciais.", text_color="#aa5959")
        return

    for cred in credenciais.get("usuario", []):
        if cred.get("usuario") == usuario:
            if cred.get("senha") != senha_hash:
                salvar_log_acesso(usuario, "FALHA: senha incorreta")
                mensagem_label.configure(text="Usuário ou senha incorretos.", text_color="#aa5959")
                return
            if cred.get("bloqueado", False):
                salvar_log_acesso(usuario, "FALHA: usuário bloqueado")
                mensagem_label.configure(text="Usuário bloqueado.", text_color="#aa5959")
                return

            assinatura = cred.get("assinatura", {})
            if not assinatura.get("ativa", False):
                salvar_log_acesso(usuario, "FALHA: assinatura inativa/expirada")
                mensagem_label.configure(text="Assinatura expirada ou inativa", text_color="#aa5959")
                return

            # Exporta a data de expiração (usada pelo checksvc.py)
            os.environ["KB_EXPIRACAO"] = _extrair_data_expiracao(assinatura).strip()

            # Lê mapa remoto
            maquinas_data, sha, ok = carregar_maquinas()
            if not ok:
                salvar_log_acesso(usuario, "FALHA: não foi possível consultar autorização remota")
                mensagem_label.configure(text="Tente novamente.", text_color="#aa5959")
                return

            # Normaliza estrutura do usuário (aceita formato antigo: lista simples)
            lista_user = maquinas_data.get(usuario)
            if lista_user is None or isinstance(lista_user, list):
                if isinstance(lista_user, list):
                    lista_user = {"autorizadas": _norm_ids(lista_user), "pendentes": []}
                else:
                    lista_user = {"autorizadas": [], "pendentes": []}
                maquinas_data[usuario] = lista_user

            # Normaliza listas vindas do GitHub (garante comparação robusta)
            autorizadas = _norm_ids(lista_user.get("autorizadas", []))
            pendentes = _norm_ids(lista_user.get("pendentes", []))

            # Se já autorizado (inclusive se você adicionou manualmente no GitHub)
            if machine_id in autorizadas:
                salvar_log_acesso(usuario, "SUCESSO: máquina autorizada")
                janela.destroy()
                abrir_menu()
                return

            # Se já está pendente
            if machine_id in pendentes:
                salvar_log_acesso(usuario, "FALHA: máquina pendente")
                mensagem_label.configure(text="Acesso não autorizado.", text_color="#aa5959")
                return

            # Sem máquinas autorizadas -> autoriza a primeira automaticamente
            if len(autorizadas) == 0:
                autorizadas.append(machine_id)
                lista_user["autorizadas"] = autorizadas
                lista_user["pendentes"] = pendentes
                maquinas_data[usuario] = lista_user
                if salvar_maquinas(maquinas_data, sha, f"Autorizando primeira máquina para {usuario}"):
                    salvar_log_acesso(usuario, "SUCESSO: primeira máquina autorizada")
                    janela.destroy()
                    abrir_menu()
                else:
                    salvar_log_acesso(usuario, "FALHA: não conseguiu salvar autorização no GitHub")
                    mensagem_label.configure(text="Não foi possível salvar autorização (GitHub).", text_color="#aa5959")
                return

            # Já existe 1 autorizada -> esta vira pendente
            if machine_id not in pendentes:
                pendentes.append(machine_id)
                lista_user["pendentes"] = pendentes
                lista_user["autorizadas"] = autorizadas
                maquinas_data[usuario] = lista_user
                if not salvar_maquinas(maquinas_data, sha, f"Solicitação de nova máquina para {usuario}"):
                    salvar_log_acesso(usuario, "FALHA: não conseguiu registrar pendência no GitHub")
                    mensagem_label.configure(text="Falha ao registrar pendência (GitHub).", text_color="#aa5959")
                    return

            salvar_log_acesso(usuario, "FALHA: acesso não autorizado (pendente)")
            mensagem_label.configure(text="Acesso não autorizado", text_color="#aa5959")
            return

    salvar_log_acesso(usuario, "FALHA: usuário não encontrado/senha incorreta")
    mensagem_label.configure(text="Usuário ou senha incorretos.", text_color="#aa5959")

def abrir_menu():
    # importa no MESMO processo, já com a env KB_EXPIRACAO setada
    import checksvc

# ================== Interface ==================
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

janela = ctk.CTk()
janela.title("Login")
janela.geometry("320x160")
try:
    icon_path = os.path.join(os.path.dirname(__file__), "vkgico.ico")
    if os.path.exists(icon_path):
        janela.iconbitmap(icon_path)
except Exception:
    pass
janela.configure(fg_color="#242424")
janela.resizable(False, False)

ctk.CTkLabel(
    janela, text="Usuário:", fg_color="transparent", text_color="white",
    font=ctk.CTkFont(family="Arial", size=12, weight="bold")
).pack()
entrada_usuario = tk.Entry(janela)
entrada_usuario.pack()

ctk.CTkLabel(
    janela, text="Senha:", fg_color="transparent", text_color="white",
    font=ctk.CTkFont(family="Arial", size=12, weight="bold")
).pack()
entrada_senha = tk.Entry(janela, show="*")
entrada_senha.pack()

mensagem_label = ctk.CTkLabel(janela, text="", text_color="white")
mensagem_label.pack()

botao_login = tk.Button(janela, text="Iniciar", command=fazer_login, width=10)
janela.bind("<Return>", fazer_login)
botao_login.pack()

janela.after(300, verificar_versao)  # checa sempre que a tela de login abrir

janela.mainloop()
