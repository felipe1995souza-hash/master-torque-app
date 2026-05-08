from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.togglebutton import ToggleButton

import json
import os
import unicodedata
from datetime import datetime
from collections import OrderedDict

# ── Importacoes Android ──────────────────────────────────────────
try:
    from android.storage import primary_external_storage_path
    ANDROID_AVAILABLE = True
except Exception:
    ANDROID_AVAILABLE = False
    def primary_external_storage_path():
        return "/storage/emulated/0"



# ====================== VARIAVEIS GLOBAIS ======================
# Pasta de dados: mantem os JSON organizados e evita perda ao empacotar no Android/PC
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "dados_master_torque")
os.makedirs(DATA_DIR, exist_ok=True)

BACKUP_DIR = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

# Tema profissional e fonte com escala do celular
COR_FUNDO = (0.06, 0.08, 0.13, 1)
COR_CARD = (0.12, 0.15, 0.22, 1)
COR_PRIMARIA = (0.10, 0.45, 0.95, 1)
COR_SUCESSO = (0.10, 0.65, 0.35, 1)
COR_ALERTA = (0.95, 0.55, 0.12, 1)
COR_PERIGO = (0.85, 0.20, 0.20, 1)
COR_TEXTO = (0.94, 0.96, 1, 1)

def fs(tamanho):
    """Fonte escalavel: acompanha o tamanho de fonte configurado no celular."""
    return sp(tamanho)

def criar_botao(texto, cor=COR_PRIMARIA, altura=52):
    btn = Button(
        text=texto,
        size_hint_y=None,
        height=dp(altura),
        font_size=fs(15),
        bold=True,
        background_normal='',
        background_down='',
        background_color=cor,
        color=COR_TEXTO,
    )
    return btn

def aplicar_fundo(widget, cor=COR_FUNDO):
    with widget.canvas.before:
        Color(*cor)
        rect = Rectangle(pos=widget.pos, size=widget.size)
    def _atualizar(obj, val):
        rect.pos = obj.pos
        rect.size = obj.size
    widget.bind(pos=_atualizar, size=_atualizar)
    return rect

def criar_backup_arquivo(caminho):
    if not os.path.exists(caminho):
        return None
    nome = os.path.basename(caminho)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(BACKUP_DIR, f"{stamp}_{nome}")
    try:
        with open(caminho, "rb") as origem, open(destino, "wb") as saida:
            saida.write(origem.read())
        return destino
    except Exception:
        return None

ARQUIVO_USUARIOS   = os.path.join(DATA_DIR, "usuarios.json")
ARQUIVO_ESTOQUE    = os.path.join(DATA_DIR, "equipamentos.json")
ARQUIVO_HISTORICO  = os.path.join(DATA_DIR, "historico.json")
ARQUIVO_MANUTENCAO = os.path.join(DATA_DIR, "manutencao.json")
ARQUIVO_ROMANEIO   = os.path.join(DATA_DIR, "romaneios.json")
ARQUIVO_MODELO_ROMANEIO = os.path.join(BASE_DIR, "master_torque_logo.png")

# =========================
# CABEÇALHO ROMANEIO
# =========================

# ORIGEM
empresa_origem = "Master Torque"
cnpj_origem = "30.476.998/0001-77"
ie_origem = "535.695.700.114"

endereco_origem = "Avenida Cristóvão Colombo, 2869 - Bairro Vila Industrial"
cidade_origem = "Piracicaba / SP"
cep_origem = "13412-227"

telefone_origem = "(19) 3371-7408 / 99214-7401"

# CONTATO SUPERIOR
endereco_topo = "Av Cristóvão Colombo, 2869 - Vila Industrial"
cidade_topo = "Piracicaba SP - CEP 13412-227"

telefone_topo = "Fone: (19) 3371-7408 / 99214-7401"
email_topo = "comercial@mastertorque.com.br"

cnpj_topo = "30.476.998/0001-77"

# CAMPOS DO ROMANEIO
titulo_romaneio = "ROMANEIO DE SERVIÇO"

campo_numero = "N"
campo_data_servico = "Data de serviço:"
campo_destino = "Destino:"
campo_local = "Local:"
campo_operador = "Operador:"

# TABELA
colunas_tabela = [
    "Item",
    "Descrição dos Equipamentos",
    "Quant.",
    "N°. de série"
]

# ITENS PADRÃO
itens_padrao = [
    "01",
    "02",
    "03",
    "04",
    "05"
]


def gerar_backup_completo():
    criados = []
    for caminho in [ARQUIVO_USUARIOS, ARQUIVO_ESTOQUE, ARQUIVO_HISTORICO, ARQUIVO_MANUTENCAO, ARQUIVO_ROMANEIO]:
        bkp = criar_backup_arquivo(caminho)
        if bkp:
            criados.append(bkp)
    return criados

equipamentos           = []
usuarios               = {}
em_viagem              = []
em_manutencao          = []
observacoes_manutencao = {}
romaneios              = []

# Operadores que podem acessar Cadastro de Equipamento e Registrar Entrada
OPERADORES_FUNCOES_RESTRITAS = ["Master", "Wilson", "Jean", "Jean S"]

def operador_pode_cadastrar_entrada(nome):
    return texto_sem_acentos(str(nome).strip()) in [texto_sem_acentos(n) for n in OPERADORES_FUNCOES_RESTRITAS]

USUARIOS_PADRAO = {
    "Master": "master1234",
    "Felipe": "1234",
    "Ademir": "1234",
    "Aldiram": "1234",
    "Helton": "1234",
    "Geovanny": "1234",
    "Gilberto": "1234",
    "Paulo": "1234",
    "Eduardo": "1234",
    "Max": "1234",
    "Jean S": "1234",
    "Leandro": "1234",
    "Luziano": "1234"
}

def garantir_usuarios_padrao():
    """Inclui operadores padrao e atualiza a senha do Master sem apagar usuarios ja cadastrados."""
    global usuarios
    alterou = False
    for nome, senha in USUARIOS_PADRAO.items():
        if nome == "Master":
            if usuarios.get(nome) != senha:
                usuarios[nome] = senha
                alterou = True
        elif nome not in usuarios:
            usuarios[nome] = senha
            alterou = True
    if alterou:
        salvar_usuarios()


# ====================== FUNCOES DE DADOS ======================
def salvar_json_seguro(caminho, dados):
    """Salva JSON com backup automatico antes de substituir o original."""
    criar_backup_arquivo(caminho)
    tmp = caminho + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    os.replace(tmp, caminho)

def carregar_json(caminho, padrao):
    """Carrega JSON validando erro de arquivo vazio/corrompido."""
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return padrao

def normalizar_serie(valor):
    return str(valor).strip().upper()

def texto_sem_acentos(valor):
    """Remove acentos de textos exibidos/salvos, mantendo emojis e simbolos."""
    return unicodedata.normalize("NFKD", str(valor)).encode("ASCII", "ignore").decode("ASCII")

def operadores_disponiveis(incluir_todos=False):
    nomes = sorted([str(n) for n in usuarios.keys()])
    return (["Todos"] if incluir_todos else []) + nomes

def nomes_equipamentos_disponiveis():
    nomes = sorted({texto_sem_acentos(e.get("nome", "---")) for e in equipamentos})
    return ["Todos"] + nomes

def criar_spinner(valores, texto_inicial="Todos", altura=46):
    spn = Spinner(
        text=texto_inicial,
        values=valores if valores else [texto_inicial],
        size_hint_y=None,
        height=dp(altura),
        font_size=fs(14),
        background_normal='',
        background_color=(0.18, 0.22, 0.32, 1),
        color=COR_TEXTO,
    )
    return spn

def serie_ja_cadastrada(serie, nome=None):
    serie = normalizar_serie(serie)
    if not serie:
        return False

    nome_normalizado = texto_sem_acentos(nome).strip().lower() if nome is not None else None

    # Permite o mesmo N/S para equipamentos com nomes diferentes.
    # Bloqueia duplicado somente quando N/S e nome do equipamento forem iguais.
    for e in equipamentos:
        mesma_serie = normalizar_serie(e.get("numero_serie", "")) == serie
        mesmo_nome = texto_sem_acentos(e.get("nome", "")).strip().lower() == nome_normalizado
        if mesma_serie and (nome_normalizado is None or mesmo_nome):
            return True

    return False

def calcular_estoque(equip):
    estoque = int(equip.get("quantidade", 0)) + int(equip.get("entrada", 0)) - int(equip.get("saida", 0))
    equip["estoque"] = max(0, estoque)
    return equip["estoque"]

def salvar_usuarios():
    salvar_json_seguro(ARQUIVO_USUARIOS, usuarios)

def salvar_equipamentos():
    salvar_json_seguro(ARQUIVO_ESTOQUE, equipamentos)

def salvar_em_viagem():
    salvar_json_seguro(ARQUIVO_HISTORICO, em_viagem)

def salvar_em_manutencao():
    dados = {"lista": em_manutencao, "observacoes": observacoes_manutencao}
    salvar_json_seguro(ARQUIVO_MANUTENCAO, dados)

def salvar_romaneio(dados_novos=None):
    global romaneios
    if dados_novos:
        romaneios.append(dados_novos)
    salvar_json_seguro(ARQUIVO_ROMANEIO, romaneios)


def carregar_dados():
    global equipamentos, usuarios, em_viagem, em_manutencao
    global observacoes_manutencao, romaneios

    try:
        with open(ARQUIVO_USUARIOS, "r", encoding='utf-8') as f:
            usuarios = json.load(f)
    except Exception:
        usuarios = USUARIOS_PADRAO.copy()
        salvar_usuarios()

    garantir_usuarios_padrao()

    try:
        with open(ARQUIVO_ESTOQUE, "r", encoding='utf-8') as f:
            equipamentos = json.load(f)
    except Exception:
        equipamentos = []
        salvar_equipamentos()

    try:
        with open(ARQUIVO_HISTORICO, "r", encoding='utf-8') as f:
            em_viagem = json.load(f)
    except Exception:
        em_viagem = []
        salvar_em_viagem()

    try:
        with open(ARQUIVO_MANUTENCAO, "r", encoding='utf-8') as f:
            dados = json.load(f)
            em_manutencao          = dados.get("lista", [])
            observacoes_manutencao = dados.get("observacoes", {})
    except Exception:
        em_manutencao          = []
        observacoes_manutencao = {}
        salvar_em_manutencao()

    try:
        with open(ARQUIVO_ROMANEIO, "r", encoding='utf-8') as f:
            romaneios = json.load(f)
    except Exception:
        romaneios = []
        salvar_json_seguro(ARQUIVO_ROMANEIO, romaneios)



def salvar_bloco_notas(texto_conteudo, nome_arquivo):
    caminhos = []
    if ANDROID_AVAILABLE:
        try:
            caminhos.append(os.path.join(primary_external_storage_path(), "Download"))
        except Exception:
            pass
    caminhos.append(os.path.dirname(os.path.abspath(__file__)))
    ultimo_erro = ""
    for pasta in caminhos:
        try:
            os.makedirs(pasta, exist_ok=True)
            caminho = os.path.join(pasta, nome_arquivo)
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(texto_conteudo)
            return caminho
        except Exception as e:
            ultimo_erro = str(e)
    return f"ERRO: {ultimo_erro}"




def agrupar_itens_romaneio(itens):
    """Agrupa equipamentos iguais na mesma linha do romaneio.
    Soma a quantidade e junta os números de série.
    """
    agrupados = OrderedDict()

    for item in itens:
        nome = texto_sem_acentos(item.get("nome", ""))
        milimetros = texto_sem_acentos(item.get("milimetros", ""))
        chave = (nome, milimetros)

        if chave not in agrupados:
            novo = dict(item)
            novo["quantidade"] = int(item.get("quantidade", 0) or 0)
            novo["numero_serie"] = str(item.get("numero_serie", "")).strip()
            agrupados[chave] = novo
        else:
            agrupados[chave]["quantidade"] += int(item.get("quantidade", 0) or 0)
            serie = str(item.get("numero_serie", "")).strip()
            if serie and serie not in agrupados[chave]["numero_serie"].split(", "):
                if agrupados[chave]["numero_serie"]:
                    agrupados[chave]["numero_serie"] += ", " + serie
                else:
                    agrupados[chave]["numero_serie"] = serie

    return list(agrupados.values())


def salvar_pdf_romaneio_com_imagem(romaneios_selecionados, nome_arquivo, modelo_imagem=ARQUIVO_MODELO_ROMANEIO):
    """Gera PDF A4 com modelo igual ao romaneio da imagem: logo no topo,
    dados da empresa, blocos Origem/Destino/Data/Operador, tabela com 29 linhas
    e marca d'agua grande ao centro.
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.utils import ImageReader
    except Exception as e:
        return f"ERRO: instale reportlab para gerar PDF ({e})"

    caminhos = []
    if ANDROID_AVAILABLE:
        try:
            caminhos.append(os.path.join(primary_external_storage_path(), "Download"))
        except Exception:
            pass
    caminhos.append(os.path.dirname(os.path.abspath(__file__)))

    ultimo_erro = ""

    for pasta in caminhos:
        try:
            os.makedirs(pasta, exist_ok=True)
            caminho_pdf = os.path.join(pasta, nome_arquivo)

            c = canvas.Canvas(caminho_pdf, pagesize=A4)
            largura_pg, altura_pg = A4

            logo_reader = None
            if os.path.exists(ARQUIVO_MODELO_ROMANEIO):
                try:
                    logo_reader = ImageReader(ARQUIVO_MODELO_ROMANEIO)
                except Exception:
                    logo_reader = None

            def txt(valor):
                return texto_sem_acentos(str(valor))

            def draw_center(texto, x, y, fonte="Helvetica", tamanho=8):
                c.setFont(fonte, tamanho)
                c.drawCentredString(x, y, txt(texto))

            def draw_left(texto, x, y, fonte="Helvetica", tamanho=8):
                c.setFont(fonte, tamanho)
                c.drawString(x, y, txt(texto))

            def draw_right(texto, x, y, fonte="Helvetica", tamanho=8):
                c.setFont(fonte, tamanho)
                c.drawRightString(x, y, txt(texto))

            def desenhar_modelo(rom):
                numero = str(rom.get('_numero_romaneio', ''))
                operador = txt(rom.get('operador', rom.get('usuario', '---')))
                data_servico = str(rom.get('data_hora', '---')).split()[0]

                # Fundo branco
                c.setFillColorRGB(1, 1, 1)
                c.rect(0, 0, largura_pg, altura_pg, fill=1, stroke=0)

                # Logo superior esquerdo
                if logo_reader:
                    c.drawImage(
                        logo_reader,
                        85,
                        altura_pg - 105,
                        width=120,
                        height=65,
                        preserveAspectRatio=True,
                        mask='auto'
                    )

                # Dados superiores à direita, igual ao modelo da imagem
                c.setFillColorRGB(0, 0, 0)
                x_info = 285
                y_info = altura_pg - 55
                draw_left(endereco_topo, x_info, y_info, "Helvetica-Bold", 8)
                draw_left(cidade_topo, x_info, y_info - 12, "Helvetica-Bold", 8)
                draw_left(telefone_topo, x_info, y_info - 24, "Helvetica-Bold", 8)
                draw_left(f"E-mail: {email_topo}", x_info, y_info - 36, "Helvetica-Bold", 8)
                draw_left(f"CNPJ: {cnpj_topo}", x_info, y_info - 48, "Helvetica-Bold", 8)

                # Título
                draw_center(titulo_romaneio, largura_pg / 2, altura_pg - 140, "Helvetica-Bold", 15)
                draw_center(campo_numero, largura_pg - 195, altura_pg - 140, "Helvetica-Bold", 15)
                draw_left(numero, largura_pg - 175, altura_pg - 140, "Helvetica-Bold", 10)

                # Coordenadas principais do formulário
                x0 = 35
                x1 = largura_pg - 35
                x_div = 385
                y_top = altura_pg - 145
                y_origem_fim = altura_pg - 225
                y_destino_fim = altura_pg - 275
                y_cab_tabela = altura_pg - 295
                y_bottom = 105

                # Caixa superior: origem / data
                c.setLineWidth(1.2)
                c.rect(x0, y_origem_fim, x1 - x0, y_top - y_origem_fim, fill=0, stroke=1)
                c.line(x_div, y_top, x_div, y_origem_fim)

                # Caixa destino / operador
                c.rect(x0, y_destino_fim, x1 - x0, y_origem_fim - y_destino_fim, fill=0, stroke=1)
                c.line(x_div, y_origem_fim, x_div, y_destino_fim)

                # Origem
                draw_left(f"Origem :   {empresa_origem}", x0 + 3, y_top - 14, "Helvetica-Bold", 8)
                draw_left(f"CNPJ: {cnpj_origem}          I.E: {ie_origem}", x0 + 45, y_top - 28, "Helvetica-Bold", 8)
                draw_left(endereco_origem, x0 + 45, y_top - 42, "Helvetica-Bold", 8)
                draw_left(f"{cidade_origem}      CEP {cep_origem}", x0 + 45, y_top - 56, "Helvetica-Bold", 8)
                draw_left(f"Telefone: {telefone_origem}", x0 + 45, y_top - 70, "Helvetica-Bold", 8)

                # Data de serviço
                draw_center(campo_data_servico, (x_div + x1) / 2, y_top - 48, "Helvetica-Bold", 8)
                draw_center(data_servico, (x_div + x1) / 2, y_top - 62, "Helvetica-Bold", 8)

                # Destino / Local / Operador
                draw_left(campo_destino, x0 + 3, y_origem_fim - 22, "Helvetica-Bold", 8)
                draw_left(campo_local, x0 + 3, y_origem_fim - 35, "Helvetica-Bold", 8)
                draw_center(campo_operador, (x_div + x1) / 2, y_origem_fim - 25, "Helvetica-Bold", 8)
                draw_center(operador, (x_div + x1) / 2, y_origem_fim - 39, "Helvetica-Bold", 8)

                # Marca d'água grande no centro, atrás da tabela
                if logo_reader:
                    c.saveState()
                    try:
                        c.setFillAlpha(0.18)
                    except Exception:
                        pass
                    largura_logo = largura_pg * 0.78
                    altura_logo = largura_logo * 0.78
                    c.drawImage(
                        logo_reader,
                        (largura_pg - largura_logo) / 2,
                        160,
                        width=largura_logo,
                        height=altura_logo,
                        preserveAspectRatio=True,
                        mask='auto'
                    )
                    c.restoreState()

                # Tabela
                c.setLineWidth(1.0)
                c.rect(x0, y_bottom, x1 - x0, y_destino_fim - y_bottom, fill=0, stroke=1)

                # Cabeçalho cinza
                c.setFillColorRGB(0.62, 0.62, 0.62)
                c.rect(x0, y_cab_tabela, x1 - x0, y_destino_fim - y_cab_tabela, fill=1, stroke=0)
                c.setFillColorRGB(0, 0, 0)

                # Colunas
                x_item = x0
                x_desc = 90
                x_qtd = 390
                x_serie = 440
                for x in [x_desc, x_qtd, x_serie]:
                    c.line(x, y_destino_fim, x, y_bottom)

                draw_center(colunas_tabela[0], (x_item + x_desc) / 2, y_cab_tabela + 7, "Helvetica-Bold", 10)
                draw_center(colunas_tabela[1], (x_desc + x_qtd) / 2, y_cab_tabela + 7, "Helvetica-Bold", 10)
                draw_center(colunas_tabela[2], (x_qtd + x_serie) / 2, y_cab_tabela + 7, "Helvetica-Bold", 10)
                draw_center(colunas_tabela[3], (x_serie + x1) / 2, y_cab_tabela + 7, "Helvetica-Bold", 10)

                # Linhas da tabela: 29 itens
                total_linhas = 29
                altura_linha = (y_cab_tabela - y_bottom) / total_linhas
                itens = agrupar_itens_romaneio(rom.get('itens', []))

                c.setFont("Helvetica", 7)
                for pos in range(1, total_linhas + 1):
                    y1 = y_cab_tabela - (pos * altura_linha)
                    c.line(x0, y1, x1, y1)

                    item_codigo = str(pos).zfill(2)
                    draw_center(item_codigo, (x_item + x_desc) / 2, y1 + 4, "Helvetica-Bold", 7)

                    if pos <= len(itens):
                        item = itens[pos - 1]
                        nome = txt(f"{item.get('nome', '')} {item.get('milimetros', '')}")[:55]
                        qtd = str(item.get('quantidade', ''))
                        serie = str(item.get('numero_serie', '') or '')[:25]

                        draw_left(nome, x_desc + 4, y1 + 4, "Helvetica", 7)
                        draw_center(qtd, (x_qtd + x_serie) / 2, y1 + 4, "Helvetica", 7)
                        draw_left(serie, x_serie + 4, y1 + 4, "Helvetica", 7)

            for rom in romaneios_selecionados:
                desenhar_modelo(rom)
                c.showPage()

            c.save()
            return caminho_pdf

        except Exception as e:
            ultimo_erro = str(e)

    return f"ERRO: {ultimo_erro}"


def registrar_pdf_salvo(caminho_arquivo, label_retorno):
    label_retorno.text = f"✅ PDF salvo em:\n{caminho_arquivo}"
    return True


def registrar_txt_salvo(caminho_arquivo, label_retorno):
    label_retorno.text = f"✅ TXT salvo em:\n{caminho_arquivo}"
    return True


# ====================== TELAS ======================
class TelaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        layout.add_widget(Label(
            text="MASTER TORQUE ROMANEIO",
            font_size=fs(24), bold=True, color=(1, 1, 1, 1)
        ))
        self.usuario_input = TextInput(
            hint_text="Operador", size_hint_y=None, height=dp(50)
        )
        layout.add_widget(self.usuario_input)
        senha_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))

        self.senha_input = TextInput(
            hint_text="Senha",
            password=True,
            multiline=False
        )

        self.btn_ver_senha = ToggleButton(
            text="👁",
            size_hint_x=None,
            width=dp(60),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.btn_ver_senha.bind(on_press=self.alternar_senha)

        senha_layout.add_widget(self.senha_input)
        senha_layout.add_widget(self.btn_ver_senha)

        layout.add_widget(senha_layout)
        btn_entrar = Button(
            text="ENTRAR", size_hint_y=None, height=dp(50),
            background_color=(0.2, 0.6, 1, 1)
        )
        btn_entrar.bind(on_press=self.fazer_login)
        layout.add_widget(btn_entrar)

        btn_trocar_senha = Button(
            text="TROCAR SENHA", size_hint_y=None, height=dp(50),
            background_color=(0.18, 0.35, 0.80, 1),
            color=(1, 1, 1, 1)
        )
        btn_trocar_senha.bind(on_press=lambda x: setattr(self.manager, 'current', 'trocar_senha'))
        layout.add_widget(btn_trocar_senha)

        self.msg = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.msg)
        self.add_widget(layout)

    def alternar_senha(self, instance):
        self.senha_input.password = not self.senha_input.password
        self.btn_ver_senha.text = "🙈" if not self.senha_input.password else "👁"

    def fazer_login(self, instance):
        usuario = self.usuario_input.text.strip()
        senha   = self.senha_input.text.strip()
        if usuario in usuarios and usuarios[usuario] == senha:
            self.manager.usuario_logado = usuario
            self.msg.text = ""
            self.usuario_input.text = ""
            self.senha_input.text   = ""
            self.manager.current = 'menu'
        else:
            self.msg.text = "❌ Operador ou senha incorretos!"


class TelaMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._root = BoxLayout(orientation='vertical', padding=dp(14), spacing=dp(10))
        aplicar_fundo(self._root, (0.02, 0.08, 0.14, 1))
        self.add_widget(self._root)

    def _criar_card(self, titulo, subtitulo, icone, cor, tela):
        card = Button(
            text=f"{icone}\n[b]{titulo}[/b]\n[size={int(fs(12))}]{subtitulo}[/size]",
            markup=True,
            size_hint_y=None,
            height=dp(108),
            font_size=fs(18),
            bold=True,
            halign='center',
            valign='middle',
            background_normal='',
            background_down='',
            background_color=cor,
            color=COR_TEXTO,
        )
        card.bind(size=lambda b, s: setattr(b, 'text_size', (b.width - dp(12), None)))
        card.bind(on_press=lambda x: setattr(self.manager, 'current', tela))
        return card

    def _resumo(self):
        total = len(equipamentos)
        manut = len(em_manutencao)
        viagem = sum(int(i.get('quantidade', 0)) for i in em_viagem)
        disponivel = sum(int(e.get('estoque', 0)) for e in equipamentos)
        return (
            f"[b]RESUMO DO ESTOQUE[/b]\n\n"
            f"Total cadastrados: {total}\n"
            f"Disponiveis em estoque: {disponivel}\n"
            f"Em viagem: {viagem}\n"
            f"Em manutencao: {manut}"
        )

    def on_enter(self):
        self._root.clear_widgets()

        topo = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(118), padding=dp(8), spacing=dp(2))
        aplicar_fundo(topo, (0.01, 0.10, 0.20, 1))
        topo.add_widget(Label(
            text="MASTER TORQUE [color=1e88ff]ROMANEIO[/color]",
            markup=True, font_size=fs(28), bold=True, color=COR_TEXTO,
            halign='center', valign='middle'
        ))
        topo.add_widget(Label(
            text="GESTAO DE ESTOQUE E ROMANEIOS",
            font_size=fs(14), bold=True, color=(0.72, 0.78, 0.86, 1),
            size_hint_y=None, height=dp(34)
        ))
        self._root.add_widget(topo)

        scroll = ScrollView()
        conteudo = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        conteudo.bind(minimum_height=conteudo.setter('height'))
        scroll.add_widget(conteudo)

        grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        botoes_comuns = []

        # Somente Wilson, Master e Jean podem ver estas funções
        if operador_pode_cadastrar_entrada(self.manager.usuario_logado):
            botoes_comuns.extend([
                ("CADASTRAR\nEQUIPAMENTO", "Adicionar novo equipamento", "+", (0.05, 0.43, 1.0, 1), "cadastrar"),
                ("REGISTRAR\nENTRADA", "Registrar entrada", "↓", (0.05, 0.55, 0.18, 1), "entrada"),
            ])

        botoes_comuns.extend([
            ("REGISTRAR\nSAIDA", "Registrar saida / viagem", "↑", (1.0, 0.50, 0.05, 1), "saida"),
            ("LISTAR\nEQUIPAMENTOS", "Ver equipamentos", "☷", (0.45, 0.15, 0.92, 1), "listar"),
            ("EQUIPAMENTOS\nEM VIAGEM", "Equipamentos em saida", "▣", (0.03, 0.65, 0.78, 1), "viagem"),
            ("CONTROLE DE\nMANUTENCAO", "Equipamentos em manutencao", "🔧", (0.95, 0.65, 0.04, 1), "manutencao"),
            ("ROMANEIO\nDE SAIDA", "Gerar romaneio", "📋", (0.90, 0.20, 0.22, 1), "romaneio"),
        ])

        for titulo, sub, icone, cor, tela in botoes_comuns:
            grid.add_widget(self._criar_card(titulo, sub, icone, cor, tela))

        if self.manager.usuario_logado == "Master":
            grid.add_widget(self._criar_card("CADASTRO DE\nOPERADOR", "Gerenciar operadores", "👤", (0.02, 0.68, 0.58, 1), "criar_user"))
            grid.add_widget(self._criar_card("LISTA DE\nOPERADORES", "Ver operadores", "👥", (0.55, 0.20, 0.75, 1), "lista_usuarios"))
            grid.add_widget(self._criar_card("APAGAR\nEQUIPAMENTOS", "Remover itens", "🗑", (0.75, 0.12, 0.12, 1), "apagar"))

        conteudo.add_widget(grid)

        resumo = Label(
            text=self._resumo(), markup=True,
            size_hint_y=None, height=dp(142),
            font_size=fs(14), color=COR_TEXTO,
            halign='center', valign='middle'
        )
        resumo.bind(size=lambda l, s: setattr(l, 'text_size', (l.width - dp(20), None)))
        aplicar_fundo(resumo, (0.02, 0.14, 0.24, 1))
        conteudo.add_widget(resumo)

        rodape = Label(
            text=f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}    |    Usuario: {self.manager.usuario_logado or '---'}",
            size_hint_y=None, height=dp(58), font_size=fs(13), color=(0.86, 0.90, 0.96, 1),
            halign='center', valign='middle'
        )
        rodape.bind(size=lambda l, s: setattr(l, 'text_size', s))
        aplicar_fundo(rodape, (0.02, 0.14, 0.24, 1))
        conteudo.add_widget(rodape)

        btn_sair = criar_botao("SAIR DO SISTEMA", (0.35, 0.38, 0.45, 1), 52)
        btn_sair.bind(on_press=lambda x: App.get_running_app().stop())
        conteudo.add_widget(btn_sair)

        self._root.add_widget(scroll)


# ── Tela de Backup ───────────────────────────────────────────────
class TelaConfig(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(12))
        aplicar_fundo(layout)
        layout.add_widget(Label(
            text="💾 Backups e Arquivos TXT",
            font_size=fs(22), bold=True, color=(1, 0.85, 0.35, 1),
            size_hint_y=None, height=dp(48)
        ))
        layout.add_widget(Label(
            text="O sistema mantem backup automatico dos dados JSON antes de cada gravacao. Tambem e possivel gerar um backup manual aqui.",
            font_size=fs(14), color=COR_TEXTO, halign='center', valign='middle'
        ))
        self.msg = Label(text="", font_size=fs(13), color=(0.4, 1, 0.6, 1))
        btn_backup = criar_botao("💾 GERAR BACKUP AGORA", COR_SUCESSO)
        btn_backup.bind(on_press=self.gerar_backup)
        layout.add_widget(btn_backup)
        layout.add_widget(self.msg)
        btn_voltar = criar_botao("⬅ VOLTAR", (0.35, 0.38, 0.45, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        self.msg.text = f"📁 Dados: {DATA_DIR}\n📁 Backups: {BACKUP_DIR}"

    def gerar_backup(self, instance):
        criados = gerar_backup_completo()
        self.msg.text = f"✅ Backup gerado: {len(criados)} arquivo(s)\n📁 {BACKUP_DIR}" if criados else "⚠ Nenhum arquivo encontrado para backup."


class TelaCadastrar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_interface()


    def on_enter(self):
        if not operador_pode_cadastrar_entrada(self.manager.usuario_logado):
            self.manager.current = 'menu'
            return

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Cadastrar Equipamento", font_size=fs(20), bold=True))
        self.nome    = TextInput(hint_text="Nome do equipamento", size_hint_y=None, height=dp(40))
        self.qtd = TextInput(
            hint_text="Quantidade inicial",
            size_hint_y=None,
            height=dp(40),
            input_filter='int'
        )

        self.serie = TextInput(
            hint_text="N/S (ex: 101 102)",
            size_hint_y=None,
            height=dp(40)
        )
        self.medida = TextInput(
            hint_text="Milimetros (opcional)",
            size_hint_y=None,
            height=dp(40)
        )

        for w in [self.nome, self.medida, self.qtd, self.serie]:
            layout.add_widget(w)
        btn_salvar = Button(text="SALVAR", size_hint_y=None, height=dp(50),
                            background_color=(0.2, 0.6, 1, 1))
        btn_salvar.bind(on_press=self.salvar)
        layout.add_widget(btn_salvar)
        self.msg = Label(text="", color=(0, 1, 0, 1))
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def salvar(self, instance):
        try:
            nome    = self.nome.text.strip()
            qtd     = int(self.qtd.text    or 0)
            estoque = qtd
            series  = self.serie.text.replace(',', ' ').split()
            if not nome:
                self.msg.text = "⚠ Preencha o nome!"
                return
            # N/S no cadastro e opcional. Se ficar vazio, salva o equipamento sem numero de serie.
            if not series:
                series = [""]
            duplicados = [normalizar_serie(num) for num in series if str(num).strip() and serie_ja_cadastrada(num, nome)]
            if duplicados:
                self.msg.text = "⚠ N/S ja cadastrado(s): " + ", ".join(duplicados)
                return
            for num in series:
                equipamentos.append({
                    "nome": nome, "quantidade": qtd,
                    "entrada": 0, "saida": 0,
                    "milimetros": self.medida.text.strip(),
                    "estoque": estoque, "numero_serie": normalizar_serie(num) if str(num).strip() else ""
                })
            salvar_equipamentos()
            self.msg.text = "✅ Salvo com sucesso!"
            self.nome.text = self.qtd.text = self.medida.text = self.serie.text = ""
        except Exception as e:
            self.msg.text = f"❌ Erro: {str(e)}"


class TelaListar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        layout.add_widget(Label(text="Lista de Equipamentos", font_size=fs(20), bold=True))
        scroll = ScrollView()
        self.conteudo = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.conteudo.bind(minimum_height=self.conteudo.setter('height'))
        scroll.add_widget(self.conteudo)
        btn_atualizar = Button(text="🔄 ATUALIZAR", size_hint_y=None, height=dp(50),
                               background_color=(0.3, 0.6, 1, 1))
        btn_atualizar.bind(on_press=self.carregar)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_atualizar)
        layout.add_widget(scroll)
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        self.carregar(None)

    def carregar(self, instance):
        self.conteudo.clear_widgets()
        if not equipamentos:
            self.conteudo.add_widget(Label(text="Nenhum equipamento cadastrado."))
            return
        for i, equip in enumerate(equipamentos, 1):
            serie  = equip['numero_serie']
            status = "🔧 EM MANUTENCAO" if serie in em_manutencao else "✅ Disponivel"
            if serie in observacoes_manutencao:
                status += f" | Obs: {observacoes_manutencao[serie]}"
            box = BoxLayout(size_hint_y=None, height=dp(80), padding=5, spacing=2)
            box.add_widget(Label(text=str(i), size_hint_x=None, width=dp(30)))
            box.add_widget(Label(text=(
                f"Nome: {equip['nome']}\n"
                f"Qtd: {equip['quantidade']} | Ent: {equip['entrada']} | Sai: {equip['saida']}\n"
                f"Estoque: {equip['estoque']} | N/S: {serie} | {status}"
            )))
            self.conteudo.add_widget(box)


class TelaAtualizar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="Atualizar Estoque", font_size=fs(20), bold=True))
        self.indice = TextInput(hint_text="Numero do item na lista",
                                size_hint_y=None, height=dp(40), input_filter='int')
        layout.add_widget(self.indice)
        self.novo_valor = TextInput(hint_text="Novo valor do estoque",
                                    size_hint_y=None, height=dp(40), input_filter='int')
        layout.add_widget(self.novo_valor)
        btn = Button(text="ATUALIZAR", size_hint_y=None, height=dp(50),
                     background_color=(1, 0.7, 0.2, 1))
        btn.bind(on_press=self.atualizar)
        layout.add_widget(btn)
        self.msg = Label(text="", color=(0, 1, 0, 1))
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def atualizar(self, instance):
        if not self.indice.text.strip() or not self.novo_valor.text.strip():
            self.msg.text = "⚠ Preencha os dois campos!"
            return
        try:
            idx   = int(self.indice.text.strip()) - 1
            valor = int(self.novo_valor.text.strip())
            if 0 <= idx < len(equipamentos):
                equipamentos[idx]['estoque'] = valor
                salvar_equipamentos()
                self.msg.text = f"✅ Atualizado! Novo estoque: {valor}"
            else:
                self.msg.text = f"❌ Numero invalido! Total: {len(equipamentos)}"
        except ValueError:
            self.msg.text = "❌ Digite apenas numeros!"
        except Exception as e:
            self.msg.text = f"❌ Erro: {str(e)}"


class TelaManutencao(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selecionados = []
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        layout.add_widget(Label(text="🔧 Controle de Manutencao",
                                font_size=fs(20), bold=True, color=(1, 0.6, 0.2, 1)))
        scroll_lista = ScrollView()
        self.lista_geral = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.lista_geral.bind(minimum_height=self.lista_geral.setter('height'))
        scroll_lista.add_widget(self.lista_geral)
        layout.add_widget(scroll_lista)
        self.observacao = TextInput(
            hint_text="📝 Observacao (motivo, defeito, data...)",
            size_hint_y=None, height=dp(60), multiline=True
        )
        layout.add_widget(self.observacao)
        botoes_acao = BoxLayout(size_hint_y=None, height=dp(50), spacing=10)
        btn_add = Button(text="🔧 COLOCAR EM MANUTENCAO",
                         background_color=(0.9, 0.4, 0.1, 1))
        btn_add.bind(on_press=self.colocar)
        btn_remove = Button(text="✅ RETIRAR DE MANUTENCAO",
                            background_color=(0.2, 0.7, 0.2, 1))
        btn_remove.bind(on_press=self.retirar)
        botoes_acao.add_widget(btn_add)
        botoes_acao.add_widget(btn_remove)
        layout.add_widget(botoes_acao)
        self.msg = Label(text="")
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        self.selecionados.clear()
        self.observacao.text = ""
        self.carregar_lista()

    def carregar_lista(self):
        self.lista_geral.clear_widgets()
        if not equipamentos:
            self.lista_geral.add_widget(Label(text="Nenhum equipamento cadastrado."))
            return
        for i, equip in enumerate(equipamentos, 1):
            serie  = equip['numero_serie']
            status = "🔧 EM MANUTENCAO" if serie in em_manutencao else "✅ Disponivel"
            if serie in observacoes_manutencao:
                status += f" | Obs: {observacoes_manutencao[serie]}"
            linha = BoxLayout(size_hint_y=None, height=dp(60), padding=5, spacing=2)
            cb = CheckBox(size_hint_x=None, width=dp(40))
            cb.bind(on_press=lambda cb, idx=i-1: self.marcar_desmarcar(idx))
            linha.add_widget(cb)
            linha.add_widget(Label(text=f"{i}. {equip['nome']} | N/S: {serie} | {status}"))
            self.lista_geral.add_widget(linha)

    def marcar_desmarcar(self, idx):
        if idx in self.selecionados:
            self.selecionados.remove(idx)
        else:
            self.selecionados.append(idx)

    def colocar(self, instance):
        if not self.selecionados:
            self.msg.text = "⚠ Selecione pelo menos um item!"
            return
        obs = self.observacao.text.strip()
        contador = 0
        for idx in self.selecionados:
            if 0 <= idx < len(equipamentos):
                serie = equipamentos[idx]['numero_serie']
                if serie not in em_manutencao:
                    em_manutencao.append(serie)
                    if obs:
                        observacoes_manutencao[serie] = obs
                    contador += 1
        salvar_em_manutencao()
        self.msg.text = f"✅ {contador} equipamento(s) em manutencao!"
        self.selecionados.clear()
        self.observacao.text = ""
        self.carregar_lista()

    def retirar(self, instance):
        if not self.selecionados:
            self.msg.text = "⚠ Selecione pelo menos um item!"
            return
        contador = 0
        for idx in self.selecionados:
            if 0 <= idx < len(equipamentos):
                serie = equipamentos[idx]['numero_serie']
                if serie in em_manutencao:
                    em_manutencao.remove(serie)
                    observacoes_manutencao.pop(serie, None)
                    contador += 1
        salvar_em_manutencao()
        self.msg.text = f"✅ {contador} equipamento(s) retirado(s)!"
        self.selecionados.clear()
        self.observacao.text = ""
        self.carregar_lista()
        

# -- TelaSaida - botoes + / - por item, com filtro de operador/equipamento --
class TelaSaida(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quantidades = {}   # idx_equip -> qtd escolhida
        self.labels_qtd = {}
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        aplicar_fundo(layout)
        layout.add_widget(Label(text="Registrar Saida", font_size=fs(20), bold=True, color=COR_TEXTO,
                                size_hint_y=None, height=dp(38)))

        self.filtro_operador = criar_spinner(["Operador"], "Operador", altura=44)
        self.filtro_operador.bind(text=lambda *args: None)
        layout.add_widget(Label(text="Selecione o operador da saida", font_size=fs(12), color=COR_TEXTO,
                                size_hint_y=None, height=dp(22)))
        layout.add_widget(self.filtro_operador)

        self.filtro_operador_2 = criar_spinner(["Nenhum"], "Nenhum", altura=44)
        self.filtro_operador_2.bind(text=lambda *args: None)
        layout.add_widget(Label(text="Adicionar mais um operador (opcional)", font_size=fs(12), color=COR_TEXTO,
                                size_hint_y=None, height=dp(22)))
        layout.add_widget(self.filtro_operador_2)

        layout.add_widget(Label(text="Filtro de equipamento", font_size=fs(12), color=COR_TEXTO,
                                size_hint_y=None, height=dp(22)))
        self.filtro_equipamento = criar_spinner(["Todos"], "Todos", altura=44)
        self.filtro_equipamento.bind(text=lambda *args: self.carregar_lista())
        layout.add_widget(self.filtro_equipamento)

        scroll = ScrollView()
        self.lista_equipamentos = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.lista_equipamentos.bind(minimum_height=self.lista_equipamentos.setter('height'))
        scroll.add_widget(self.lista_equipamentos)
        layout.add_widget(scroll)

        btn = criar_botao("CONFIRMAR SAIDA", COR_PERIGO, 52)
        btn.bind(on_press=self.sair)
        layout.add_widget(btn)
        self.msg = Label(text="", font_size=fs(13), color=COR_TEXTO, size_hint_y=None, height=dp(44))
        layout.add_widget(self.msg)
        btn_voltar = criar_botao("VOLTAR", (0.35, 0.38, 0.45, 1), 50)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        self.quantidades.clear()
        self.labels_qtd.clear()
        self.msg.text = ""
        valores_operador = operadores_disponiveis(False)
        if not valores_operador:
            valores_operador = [self.manager.usuario_logado or "Operador"]
        self.filtro_operador.values = valores_operador
        self.filtro_operador.text = self.manager.usuario_logado if self.manager.usuario_logado in valores_operador else valores_operador[0]

        self.filtro_operador_2.values = ["Nenhum"] + valores_operador
        self.filtro_operador_2.text = "Nenhum"

        self.filtro_equipamento.values = nomes_equipamentos_disponiveis()
        if self.filtro_equipamento.text not in self.filtro_equipamento.values:
            self.filtro_equipamento.text = "Todos"
        self.carregar_lista()

    def _equipamento_visivel(self, equip):
        filtro = self.filtro_equipamento.text
        if filtro in ("", "Todos"):
            return True
        return texto_sem_acentos(equip.get('nome', '')) == filtro

    def carregar_lista(self):
        self.lista_equipamentos.clear_widgets()
        self.labels_qtd.clear()

        if not equipamentos:
            self.lista_equipamentos.add_widget(Label(
                text="Nenhum equipamento cadastrado.",
                font_size=fs(14),
                color=COR_TEXTO
            ))
            return

        encontrou = False

        for i, equip in enumerate(equipamentos):
            if not self._equipamento_visivel(equip):
                continue

            serie = equip.get('numero_serie', '---')
            estoque_atual = int(equip.get('estoque', 0))
            em_manut = serie in em_manutencao

            # Na aba Saida, mostra somente equipamento realmente disponivel:
            # estoque maior que zero e fora da manutencao.
            if estoque_atual <= 0 or em_manut:
                continue

            encontrou = True

            if i not in self.quantidades:
                self.quantidades[i] = 0

            linha = BoxLayout(
                size_hint_y=None,
                height=dp(62),
                padding=(dp(4), dp(2)),
                spacing=dp(4)
            )

            info_txt = (
                f"{texto_sem_acentos(equip.get('nome', '---'))} {equip.get('milimetros', '')}\n"
                f"Estoque: {estoque_atual}" + (f"  N/S: {serie}" if str(serie).strip() not in ("", "---") else "")
            )

            lbl_info = Label(
                text=info_txt,
                font_size=fs(12),
                color=COR_TEXTO,
                size_hint_x=0.55,
                halign='left',
                valign='middle'
            )
            lbl_info.bind(size=lambda l, s: setattr(l, 'text_size', s))
            linha.add_widget(lbl_info)

            btn_menos = Button(
                text="-",
                font_size=fs(22),
                size_hint_x=None,
                width=dp(46),
                background_color=COR_PERIGO
            )
            btn_menos.bind(on_press=lambda x, idx=i: self._alterar(idx, -1))
            linha.add_widget(btn_menos)

            lbl_qtd = Label(
                text=str(self.quantidades[i]),
                font_size=fs(20),
                bold=True,
                color=(0.3, 1, 0.6, 1),
                size_hint_x=None,
                width=dp(44),
                halign='center',
                valign='middle'
            )
            lbl_qtd.bind(size=lambda l, s: setattr(l, 'text_size', s))
            self.labels_qtd[i] = lbl_qtd
            linha.add_widget(lbl_qtd)

            btn_mais = Button(
                text="+",
                font_size=fs(22),
                size_hint_x=None,
                width=dp(46),
                background_color=COR_SUCESSO
            )
            btn_mais.bind(on_press=lambda x, idx=i: self._alterar(idx, +1))
            linha.add_widget(btn_mais)

            self.lista_equipamentos.add_widget(linha)

        if not encontrou:
            self.lista_equipamentos.add_widget(Label(
                text="Nenhum equipamento disponivel para saida.",
                font_size=fs(14),
                color=COR_TEXTO
            ))

    def _alterar(self, idx, delta):
        equip = equipamentos[idx]
        novo  = max(0, min(self.quantidades.get(idx, 0) + delta, int(equip.get('estoque', 0))))
        self.quantidades[idx] = novo
        if idx in self.labels_qtd:
            self.labels_qtd[idx].text = str(novo)

    def sair(self, instance):
        operador = self.filtro_operador.text.strip()
        operador_2 = self.filtro_operador_2.text.strip() if hasattr(self, 'filtro_operador_2') else "Nenhum"

        if not operador or operador == "Operador":
            self.msg.text = "Selecione o operador."
            return

        operador_romaneio = operador
        if operador_2 and operador_2 not in ("Nenhum", "Operador") and operador_2 != operador:
            operador_romaneio = f"{operador} / {operador_2}"
        itens = {i: q for i, q in self.quantidades.items() if q > 0}
        if not itens:
            self.msg.text = "Use + para definir a quantidade de cada item."
            return
        try:
            erros = ""
            itens_romaneio = []
            for idx, qtd in itens.items():
                equip = equipamentos[idx]
                if equip.get('numero_serie') in em_manutencao:
                    erros += f"{texto_sem_acentos(equip.get('nome', '---'))} em manutencao.\n"
                    continue
                if qtd > int(equip.get('estoque', 0)):
                    erros += f"{texto_sem_acentos(equip.get('nome', '---'))}: estoque insuficiente.\n"
                    continue
                equip['saida'] = int(equip.get('saida', 0)) + qtd
                calcular_estoque(equip)
                itens_romaneio.append({
                    "nome": texto_sem_acentos(equip.get('nome', '---')),
                    "milimetros": equip.get('milimetros', ''),
                    "quantidade": qtd,
                    "numero_serie": equip.get('numero_serie', '---'),
                    "estoque_apos": equip.get('estoque', 0)
                })
                em_viagem.append({
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "equipamento": texto_sem_acentos(equip.get('nome', '---')),
                    "milimetros": equip.get('milimetros', ''),
                    "numero_serie": equip.get('numero_serie', '---'),
                    "quantidade": qtd, "esta_com": texto_sem_acentos(operador_romaneio)
                })
            if itens_romaneio:
                salvar_romaneio({
                    "operador": texto_sem_acentos(operador_romaneio),
                    "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "itens": itens_romaneio
                })
            salvar_equipamentos()
            salvar_em_viagem()
            self.msg.text = "Saida registrada.\n" + erros
            self.quantidades.clear()
            self.carregar_lista()
        except Exception as e:
            self.msg.text = f"Erro: {str(e)}"


# ── TelaEntrada — botoes + / − por item ──────────────────────────
class TelaEntrada(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quantidades = {}
        self.labels_qtd = {}
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        aplicar_fundo(layout)
        layout.add_widget(Label(text="Registrar Entrada", font_size=fs(20), bold=True,
                                color=COR_TEXTO, size_hint_y=None, height=dp(38)))

        layout.add_widget(Label(text="Filtro por operador", font_size=fs(12), color=COR_TEXTO,
                                size_hint_y=None, height=dp(22)))
        self.filtro_operador = criar_spinner(["Todos"], "Todos", altura=44)
        self.filtro_operador.bind(text=lambda *args: self._alterar_filtro())
        layout.add_widget(self.filtro_operador)

        scroll_viagem = ScrollView()
        self.lista_viagem = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(6))
        self.lista_viagem.bind(minimum_height=self.lista_viagem.setter('height'))
        scroll_viagem.add_widget(self.lista_viagem)
        layout.add_widget(scroll_viagem)

        btn = criar_botao("CONFIRMAR ENTRADA", COR_SUCESSO, 52)
        btn.bind(on_press=self.entrar)
        layout.add_widget(btn)

        self.msg = Label(text="", font_size=fs(13), color=COR_TEXTO, size_hint_y=None, height=dp(44))
        layout.add_widget(self.msg)

        btn_voltar = criar_botao("VOLTAR", (0.35, 0.38, 0.45, 1), 50)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        if not operador_pode_cadastrar_entrada(self.manager.usuario_logado):
            self.manager.current = 'menu'
            return
        self.quantidades.clear()
        self.labels_qtd.clear()
        self.msg.text = ""
        self.filtro_operador.values = operadores_disponiveis(True)
        if self.filtro_operador.text not in self.filtro_operador.values:
            self.filtro_operador.text = "Todos"
        self.carregar_lista_viagem()

    def _alterar_filtro(self):
        self.quantidades.clear()
        self.labels_qtd.clear()
        self.carregar_lista_viagem()

    def _item_visivel(self, item):
        filtro = self.filtro_operador.text.strip()
        if filtro in ("", "Todos"):
            return True
        return texto_sem_acentos(item.get('esta_com', '')) == texto_sem_acentos(filtro)

    def carregar_lista_viagem(self):
        self.lista_viagem.clear_widgets()
        self.labels_qtd.clear()
        if not em_viagem:
            self.lista_viagem.add_widget(Label(text="Nenhum equipamento em viagem.", font_size=fs(14), color=COR_TEXTO))
            return

        encontrou = False
        for i, item in enumerate(em_viagem):
            if not self._item_visivel(item):
                continue
            encontrou = True
            if i not in self.quantidades:
                self.quantidades[i] = 0

            linha = BoxLayout(size_hint_y=None, height=dp(62), padding=(dp(4), dp(2)), spacing=dp(4))
            info_txt = (
                f"{texto_sem_acentos(item.get('equipamento', '---'))} {item.get('milimetros', '')}\n"
                + (f"N/S: {item.get('numero_serie', '---')} | " if str(item.get('numero_serie', '')).strip() not in ("", "---") else "")
                + f"Operador: {texto_sem_acentos(item.get('esta_com', '---'))} | Qtd: {item.get('quantidade', 0)}"
            )
            lbl_info = Label(text=info_txt, font_size=fs(12), color=COR_TEXTO,
                             size_hint_x=0.55, halign='left', valign='middle')
            lbl_info.bind(size=lambda l, s: setattr(l, 'text_size', s))
            linha.add_widget(lbl_info)

            btn_menos = Button(text="-", font_size=fs(22), size_hint_x=None, width=dp(46),
                               background_color=COR_PERIGO)
            btn_menos.bind(on_press=lambda x, idx=i: self._alterar(idx, -1))
            linha.add_widget(btn_menos)

            lbl_qtd = Label(text=str(self.quantidades[i]), font_size=fs(20), bold=True,
                            color=(0.3, 1, 0.6, 1), size_hint_x=None, width=dp(44),
                            halign='center', valign='middle')
            lbl_qtd.bind(size=lambda l, s: setattr(l, 'text_size', s))
            self.labels_qtd[i] = lbl_qtd
            linha.add_widget(lbl_qtd)

            btn_mais = Button(text="+", font_size=fs(22), size_hint_x=None, width=dp(46),
                              background_color=COR_SUCESSO)
            btn_mais.bind(on_press=lambda x, idx=i: self._alterar(idx, +1))
            linha.add_widget(btn_mais)

            self.lista_viagem.add_widget(linha)

        if not encontrou:
            self.lista_viagem.add_widget(Label(text="Nenhum equipamento encontrado para este operador.", font_size=fs(14), color=COR_TEXTO))

    def _alterar(self, idx, delta):
        qtd_em_viagem = int(em_viagem[idx].get('quantidade', 1)) if 0 <= idx < len(em_viagem) else 0
        novo = max(0, min(self.quantidades.get(idx, 0) + delta, qtd_em_viagem))
        self.quantidades[idx] = novo
        if idx in self.labels_qtd:
            self.labels_qtd[idx].text = str(novo)

    def entrar(self, instance):
        itens = {i: q for i, q in self.quantidades.items() if q > 0 and 0 <= i < len(em_viagem) and self._item_visivel(em_viagem[i])}
        if not itens:
            self.msg.text = "Use + para definir a quantidade de cada item."
            return
        try:
            erros = ""
            indices_remover = []
            for idx, qtd in itens.items():
                item_viagem  = em_viagem[idx]
                numero_serie = item_viagem.get('numero_serie', '')
                qtd_em_viagem = int(item_viagem.get('quantidade', 1))
                qtd_recebida = min(qtd, qtd_em_viagem)
                equip = next((e for e in equipamentos
                              if normalizar_serie(e.get('numero_serie', '')) == normalizar_serie(numero_serie)), None)
                if equip:
                    equip['entrada'] = int(equip.get('entrada', 0)) + qtd_recebida
                    calcular_estoque(equip)
                    restante = qtd_em_viagem - qtd_recebida
                    if restante <= 0:
                        indices_remover.append(idx)
                    else:
                        item_viagem['quantidade'] = restante
                        erros += f"Entrada parcial de {numero_serie}: ainda restam {restante}.\n"
                    if qtd > qtd_em_viagem:
                        erros += f"Quantidade ajustada para o maximo em viagem: {qtd_em_viagem}.\n"
                else:
                    erros += f"N/S {numero_serie} nao encontrado.\n"
            for idx in sorted(indices_remover, reverse=True):
                del em_viagem[idx]
            salvar_equipamentos()
            salvar_em_viagem()
            self.msg.text = "Entrada registrada.\n" + erros
            self.quantidades.clear()
            self.carregar_lista_viagem()
        except Exception as e:
            self.msg.text = f"Erro: {str(e)}"
class TelaViagem(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6))
        aplicar_fundo(layout)
        layout.add_widget(Label(text="Equipamentos em Viagem", font_size=fs(20), bold=True,
                                color=COR_TEXTO, size_hint_y=None, height=dp(38)))
        layout.add_widget(Label(text="Filtro por operador", font_size=fs(12), color=COR_TEXTO,
                                size_hint_y=None, height=dp(22)))
        self.filtro_operador = criar_spinner(["Todos"], "Todos", altura=44)
        self.filtro_operador.bind(text=lambda *args: self.carregar(None))
        layout.add_widget(self.filtro_operador)

        scroll = ScrollView()
        self.conteudo = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.conteudo.bind(minimum_height=self.conteudo.setter('height'))
        scroll.add_widget(self.conteudo)
        btn_atualizar = criar_botao("ATUALIZAR", COR_PRIMARIA, 50)
        btn_atualizar.bind(on_press=self.carregar)
        btn_voltar = criar_botao("VOLTAR", (0.35, 0.38, 0.45, 1), 50)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_atualizar)
        layout.add_widget(scroll)
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        nomes = sorted({texto_sem_acentos(item.get('esta_com', '---')) for item in em_viagem if item.get('esta_com')})
        if not nomes:
            nomes = [texto_sem_acentos(n) for n in usuarios.keys()]
        self.filtro_operador.values = ["Todos"] + nomes
        if self.filtro_operador.text not in self.filtro_operador.values:
            self.filtro_operador.text = "Todos"
        self.carregar(None)

    def carregar(self, instance):
        self.conteudo.clear_widgets()
        filtro = self.filtro_operador.text
        lista = []
        for item in em_viagem:
            operador = texto_sem_acentos(item.get('esta_com', '---'))
            if filtro == "Todos" or operador == filtro:
                lista.append(item)
        if not lista:
            self.conteudo.add_widget(Label(text="Nenhum item em viagem para este filtro.", font_size=fs(14), color=COR_TEXTO))
            return
        for i, item in enumerate(lista, 1):
            box = BoxLayout(size_hint_y=None, height=dp(86), padding=dp(6), spacing=dp(2))
            aplicar_fundo(box, COR_CARD)
            box.add_widget(Label(text=str(i), font_size=fs(13), color=COR_TEXTO, size_hint_x=None, width=dp(30)))
            lbl_viagem = Label(text=(
                f"Data: {item.get('data', '---')}\n"
                f"Equipamento: {texto_sem_acentos(item.get('equipamento', '---'))}\n"
                f"Qtd: {item.get('quantidade', 0)} | N/S: {item.get('numero_serie', '---')} | Operador: {texto_sem_acentos(item.get('esta_com', '---'))}"
            ), font_size=fs(12), color=COR_TEXTO, halign='left', valign='middle')
            lbl_viagem.bind(size=lambda l, s: setattr(l, 'text_size', s))
            box.add_widget(lbl_viagem)
            self.conteudo.add_widget(box)


# ── TelaRomaneio — selecionar salva e envia automaticamente ──────
class TelaRomaneio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selecionados = []
        self._paineis = {}

        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        layout.add_widget(Label(
            text="📄 Romaneio de Saidas",
            font_size=fs(20), bold=True, color=(0.2, 0.5, 0.8, 1)
        ))

        linha_botoes = BoxLayout(size_hint_y=None, height=dp(50), spacing=6)
        btn_atualizar = Button(text="🔄 ATUALIZAR", background_color=(0.2, 0.5, 0.8, 1))
        btn_atualizar.bind(on_press=self.carregar)
        btn_sel_todos = Button(text="☑ TODOS", background_color=(0.5, 0.3, 0.8, 1))
        btn_sel_todos.bind(on_press=self.selecionar_todos)
        btn_salvar_txt = Button(text="💾 SALVAR TXT", background_color=(0.1, 0.65, 0.35, 1))
        btn_salvar_txt.bind(on_press=self.salvar_txt_selecionados)
        btn_salvar_pdf = Button(text="📄 SALVAR PDF", background_color=(0.85, 0.20, 0.20, 1))
        btn_salvar_pdf.bind(on_press=self.salvar_pdf_selecionados)
        linha_botoes.add_widget(btn_atualizar)
        linha_botoes.add_widget(btn_sel_todos)
        linha_botoes.add_widget(btn_salvar_txt)
        linha_botoes.add_widget(btn_salvar_pdf)
        layout.add_widget(linha_botoes)

        self.lbl_contador = Label(
            text="Nenhum romaneio selecionado",
            font_size=fs(12), color=(1, 0.85, 0.3, 1),
            size_hint_y=None, height=dp(22)
        )
        layout.add_widget(self.lbl_contador)


        scroll = ScrollView()
        self.conteudo = BoxLayout(orientation='vertical', size_hint_y=None, spacing=8)
        self.conteudo.bind(minimum_height=self.conteudo.setter('height'))
        scroll.add_widget(self.conteudo)
        layout.add_widget(scroll)

        self.msg_export = Label(
            text="", font_size=fs(13), color=(0.2, 1, 0.4, 1),
            size_hint_y=None, height=dp(40)
        )
        layout.add_widget(self.msg_export)

        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        self.selecionados.clear()
        self.msg_export.text = ""
        self.carregar(None)

    def marcar_desmarcar(self, idx):
        if idx in self.selecionados:
            self.selecionados.remove(idx)
        else:
            self.selecionados.append(idx)
        self._atualizar_contador()
        # Atualiza apenas a cor do painel sem recarregar toda a lista
        self._atualizar_cores_paineis()

    def selecionar_todos(self, instance):
        lista_rev = list(reversed(romaneios))
        if len(self.selecionados) == len(lista_rev):
            self.selecionados.clear()
        else:
            self.selecionados = list(range(len(lista_rev)))
        self._atualizar_contador()
        self.carregar(None)
    def _atualizar_contador(self):
        n = len(self.selecionados)
        if n == 0:
            self.lbl_contador.text = "Nenhum romaneio selecionado"
        elif n == 1:
            self.lbl_contador.text = "✅ 1 romaneio selecionado"
        else:
            self.lbl_contador.text = f"✅ {n} romaneios selecionados"

    def _atualizar_cores_paineis(self):
        """Atualiza a cor de fundo dos paineis sem recarregar toda a lista."""
        if not hasattr(self, '_paineis'):
            return
        for idx, (painel, rect) in self._paineis.items():
            cor = (0.1, 0.3, 0.15, 1) if idx in self.selecionados else (0.15, 0.15, 0.25, 1)
            rect.source = None
            # Reaplica cor via canvas
            from kivy.graphics import Color, Rectangle
            painel.canvas.before.clear()
            with painel.canvas.before:
                Color(*cor)
                r = Rectangle(pos=painel.pos, size=painel.size)
            def _bind(obj, val, r=r):
                r.pos = obj.pos
                r.size = obj.size
            painel.bind(pos=_bind, size=_bind)
            self._paineis[idx] = (painel, r)

    def salvar_txt_selecionados(self, instance=None):
        if not self.selecionados:
            self.msg_export.text = "⚠ Selecione pelo menos um romaneio para salvar em TXT."
            return
        texto    = self.gerar_texto_romaneio(self.selecionados)
        nome_arq = f"romaneio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        caminho  = salvar_bloco_notas(texto, nome_arq)
        if caminho.startswith("ERRO"):
            self.msg_export.text = caminho
            return
        registrar_txt_salvo(caminho, self.msg_export)

    def salvar_pdf_selecionados(self, instance=None):
        if not self.selecionados:
            self.msg_export.text = "⚠ Selecione pelo menos um romaneio para salvar em PDF."
            return

        lista_rev = list(reversed(romaneios))
        roms = []
        for idx in sorted(self.selecionados):
            if 0 <= idx < len(lista_rev):
                rom = dict(lista_rev[idx])
                rom['_numero_romaneio'] = len(romaneios) - idx
                roms.append(rom)

        nome_arq = f"romaneio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        caminho = salvar_pdf_romaneio_com_imagem(roms, nome_arq)
        if caminho.startswith("ERRO"):
            self.msg_export.text = caminho
            return
        registrar_pdf_salvo(caminho, self.msg_export)

    def gerar_texto_romaneio(self, indices_selecionados):
        """Gera o romaneio em formato de formulario, semelhante ao modelo impresso da Master Torque."""
        lista_rev = list(reversed(romaneios))

        def linha_sep():
            return "+" + "-" * 6 + "+" + "-" * 56 + "+" + "-" * 9 + "+" + "-" * 22 + "+"

        def celula(texto, largura):
            texto = texto_sem_acentos(str(texto))
            if len(texto) > largura:
                texto = texto[:largura]
            return texto.ljust(largura)

        linhas = []
        for idx in sorted(indices_selecionados):
            rom = lista_rev[idx]
            num_rom = len(romaneios) - idx
            operador = texto_sem_acentos(rom.get('operador', rom.get('usuario', '---')))
            data_servico_bruto = str(rom.get('data_hora', '---'))
            # Mostra apenas a data no romaneio, sem hora
            data_servico = data_servico_bruto.split()[0] if data_servico_bruto != '---' else '---'

            linhas.extend([
                "",
                empresa_origem.upper().center(96),
                texto_sem_acentos(f"{endereco_topo} - {cidade_origem}").center(96),
                texto_sem_acentos(f"Telefone: {telefone_origem}").center(96),
                f"CNPJ: {cnpj_origem}".center(96),
                "",
                texto_sem_acentos(titulo_romaneio).center(78) + f"  {campo_numero} {num_rom}",
                "+" + "-" * 96 + "+",
                texto_sem_acentos(f"| Origem: {empresa_origem}").ljust(66) + texto_sem_acentos(f"| {campo_data_servico} {data_servico}").ljust(31) + "|",
                texto_sem_acentos(f"| CNPJ: {cnpj_origem}    IE: {ie_origem}").ljust(66) + "|" + " ".ljust(30) + "|",
                texto_sem_acentos(f"| {endereco_origem}").ljust(66) + "|" + " ".ljust(30) + "|",
                texto_sem_acentos(f"| {cidade_origem}    CEP {cep_origem}").ljust(66) + "|" + " ".ljust(30) + "|",
                texto_sem_acentos(f"| Telefone: {telefone_origem}").ljust(66) + "|" + " ".ljust(30) + "|",
                "+" + "-" * 64 + "+" + "-" * 31 + "+",
                texto_sem_acentos(f"| {campo_destino}").ljust(66) + texto_sem_acentos(f"| {campo_operador} {operador}").ljust(31) + "|",
                texto_sem_acentos(f"| {campo_local}").ljust(66) + "|" + " ".ljust(30) + "|",
                "+" + "-" * 64 + "+" + "-" * 31 + "+",
                linha_sep(),
                "| " + celula(colunas_tabela[0], 4) + " |" + celula(colunas_tabela[1], 56) + "|" + celula(colunas_tabela[2], 9) + "|" + celula(colunas_tabela[3], 22) + "|",
                linha_sep(),
            ])

            itens = agrupar_itens_romaneio(rom.get('itens', []))
            for pos in range(1, 30):
                if pos <= len(itens):
                    item = itens[pos - 1]
                    nome = item.get('nome', '---')
                    qtd = item.get('quantidade', '')
                    serie = item.get('numero_serie', '')
                else:
                    nome = ""
                    qtd = ""
                    serie = ""
                linhas.append(
                    "| " + str(pos).zfill(2) + "   |" +
                    celula(nome, 56) + "|" +
                    celula(qtd, 9) + "|" +
                    celula(serie, 22) + "|"
                )
            linhas.extend([
                linha_sep(),
                "",
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y')}",
                "\n" + "=" * 98 + "\n"
            ])
        return "\n".join(linhas)

    def carregar(self, instance):
        self.conteudo.clear_widgets()
        self._paineis = {}
        if not romaneios:
            self.conteudo.add_widget(
                Label(text="📭 Nenhum romaneio registrado.", font_size=fs(14)))
            self._atualizar_contador()
            return

        lista_rev = list(reversed(romaneios))
        for i, rom in enumerate(lista_rev):
            esta_marcado  = (i in self.selecionados)
            altura_painel = dp(56 + (len(rom['itens']) * 24))

            linha_rom = BoxLayout(orientation='horizontal',
                                  size_hint_y=None, height=altura_painel, spacing=4)

            cb = CheckBox(size_hint_x=None, width=dp(44), active=esta_marcado)
            cb.bind(on_press=lambda cb, idx=i: self.marcar_desmarcar(idx))
            linha_rom.add_widget(cb)

            painel = BoxLayout(orientation='vertical', size_hint_y=None,
                               padding=(6, 4), spacing=2, height=altura_painel)
            cor_fundo = (0.1, 0.3, 0.15, 1) if esta_marcado else (0.15, 0.15, 0.25, 1)
            with painel.canvas.before:
                Color(*cor_fundo)
                rect = Rectangle(pos=painel.pos, size=painel.size)

            def _bind(obj, val, r=rect):
                r.pos  = obj.pos
                r.size = obj.size
            painel.bind(pos=_bind, size=_bind)
            self._paineis[i] = (painel, rect)

            num_rom  = len(romaneios) - i
            operador = rom.get('operador', rom.get('usuario', '---'))
            painel.add_widget(Label(
                text=f"#{num_rom}  👷 {operador}  |  📅 {rom['data_hora']}",
                font_size=fs(13), bold=True, color=(0.2, 0.85, 1, 1),
                size_hint_y=None, height=dp(24),
                halign='left', valign='middle'
            ))
            painel.add_widget(Label(
                text="  Equipamento                    Qtd   N/S",
                font_size=fs(10), color=(1, 0.85, 0.3, 1),
                size_hint_y=None, height=dp(18),
                halign='left', valign='middle'
            ))

            for item in rom['itens']:
                nome  = item.get('nome', '---')
                qtd   = str(item.get('quantidade', '?'))
                serie = item.get('numero_serie', '---')

                linha_item = BoxLayout(size_hint_y=None, height=dp(22), spacing=4)

                lbl_n = Label(text=nome, font_size=fs(12), color=(1, 1, 1, 1),
                              size_hint_x=0.52, halign='left', valign='middle')
                lbl_n.bind(size=lambda l, s: setattr(l, 'text_size', s))

                lbl_q = Label(text=qtd, font_size=fs(12), color=(0.4, 1, 0.6, 1),
                              size_hint_x=0.12, halign='center', valign='middle')
                lbl_q.bind(size=lambda l, s: setattr(l, 'text_size', s))

                lbl_s = Label(text=serie, font_size=fs(12), color=(1, 0.8, 0.3, 1),
                              size_hint_x=0.36, halign='left', valign='middle')
                lbl_s.bind(size=lambda l, s: setattr(l, 'text_size', s))

                linha_item.add_widget(lbl_n)
                linha_item.add_widget(lbl_q)
                linha_item.add_widget(lbl_s)
                painel.add_widget(linha_item)

            linha_rom.add_widget(painel)
            self.conteudo.add_widget(linha_rom)

        self._atualizar_contador()



class TelaApagar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selecionados = []
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="🗑 Apagar Equipamentos", font_size=fs(20), bold=True,
                                size_hint_y=None, height=dp(40)))
        scroll_lista = ScrollView()
        self.lista_geral = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.lista_geral.bind(minimum_height=self.lista_geral.setter('height'))
        scroll_lista.add_widget(self.lista_geral)
        layout.add_widget(scroll_lista)
        btn = Button(text="APAGAR SELECIONADOS", size_hint_y=None, height=dp(50),
                     background_color=(1, 0.2, 0.2, 1))
        btn.bind(on_press=self.apagar)
        layout.add_widget(btn)
        self.msg = Label(text="")
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        if self.manager.usuario_logado != "Master":
            self.manager.current = 'menu'
            return
        self.selecionados.clear()
        self.carregar_lista()

    def carregar_lista(self):
        self.lista_geral.clear_widgets()
        if not equipamentos:
            self.lista_geral.add_widget(Label(text="Nenhum equipamento cadastrado."))
            return
        for i, equip in enumerate(equipamentos, 1):
            status = "🔧 EM MANUTENCAO" if equip['numero_serie'] in em_manutencao else "✅ Disponivel"
            linha  = BoxLayout(size_hint_y=None, height=dp(50), padding=5, spacing=2)
            cb = CheckBox(size_hint_x=None, width=dp(40))
            cb.bind(on_press=lambda cb, idx=i-1: self.marcar_desmarcar(idx))
            linha.add_widget(cb)
            linha.add_widget(Label(
                text=f"{i}. {equip['nome']} | N/S: {equip['numero_serie']} | {status}"))
            self.lista_geral.add_widget(linha)

    def marcar_desmarcar(self, idx):
        if idx in self.selecionados:
            self.selecionados.remove(idx)
        else:
            self.selecionados.append(idx)

    def apagar(self, instance):
        if self.manager.usuario_logado != "Master":
            self.msg.text = "❌ Apenas Master pode apagar!"
            return
        if not self.selecionados:
            self.msg.text = "⚠ Selecione pelo menos um item!"
            return
        try:
            total = len(self.selecionados)
            for idx in sorted(self.selecionados, reverse=True):
                serie = equipamentos[idx]['numero_serie']
                if serie in em_manutencao:
                    em_manutencao.remove(serie)
                    observacoes_manutencao.pop(serie, None)
                    salvar_em_manutencao()
                del equipamentos[idx]
            salvar_equipamentos()
            self.msg.text = f"✅ {total} item(s) apagado(s)!"
            self.selecionados.clear()
            self.carregar_lista()
        except Exception as e:
            self.msg.text = f"❌ Erro: {str(e)}"


class TelaCriarUser(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="👤 Criar Novo Operador", font_size=fs(20), bold=True))
        self.novo_user  = TextInput(hint_text="Nome do operador",
                                    size_hint_y=None, height=dp(40))
        self.nova_senha = TextInput(hint_text="Senha", password=True,
                                    size_hint_y=None, height=dp(40))
        layout.add_widget(self.novo_user)
        layout.add_widget(self.nova_senha)
        btn = Button(text="CRIAR", size_hint_y=None, height=dp(50),
                     background_color=(0.2, 0.6, 1, 1))
        btn.bind(on_press=self.criar)
        layout.add_widget(btn)
        self.msg = Label(text="")
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def criar(self, instance):
        if self.manager.usuario_logado != "Master":
            self.msg.text = "❌ Apenas Master pode criar operadores!"
            return
        nome  = self.novo_user.text.strip()
        senha = self.nova_senha.text.strip()
        if not nome or not senha:
            self.msg.text = "❌ Preencha todos os campos!"
            return
        if nome in usuarios:
            self.msg.text = "⚠ Operador ja existe!"
            return
        try:
            usuarios[nome] = senha
            salvar_usuarios()
            self.msg.text = "✅ Operador criado!"
            self.novo_user.text = self.nova_senha.text = ""
        except Exception as e:
            self.msg.text = f"❌ Erro: {str(e)}"


class TelaListaUsuarios(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text="📋 Lista de Operadores",
                                font_size=fs(20), bold=True, color=(0.8, 0.2, 0.2, 1),
                                size_hint_y=None, height=dp(40)))
        scroll_lista = ScrollView()
        self.lista = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        self.lista.bind(minimum_height=self.lista.setter('height'))
        scroll_lista.add_widget(self.lista)
        layout.add_widget(scroll_lista)
        self.indice_apagar = TextInput(
            hint_text="Numero do operador para excluir",
            size_hint_y=None, height=dp(40), input_filter='int'
        )
        layout.add_widget(self.indice_apagar)
        btn_apagar = Button(text="🗑 EXCLUIR OPERADOR", size_hint_y=None, height=dp(50),
                            background_color=(1, 0.2, 0.2, 1))
        btn_apagar.bind(on_press=self.excluir_usuario)
        layout.add_widget(btn_apagar)
        self.msg = Label(text="")
        layout.add_widget(self.msg)
        btn_voltar = Button(text="VOLTAR", size_hint_y=None, height=dp(50),
                            background_color=(0.5, 0.5, 0.5, 1))
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(btn_voltar)
        self.add_widget(layout)

    def on_enter(self):
        if self.manager.usuario_logado != "Master":
            self.manager.current = 'menu'
            return
        self.carregar_lista()

    def carregar_lista(self):
        self.lista.clear_widgets()
        for i, nome in enumerate(list(usuarios.keys()), 1):
            if nome == "Master":
                texto = f"{i}. {nome} 🔒 (Administrador)"
                cor   = (0.2, 0.8, 0.2, 1)
            else:
                texto = f"{i}. {nome}"
                cor   = (1, 1, 1, 1)
            box = BoxLayout(size_hint_y=None, height=dp(45), padding=5)
            box.add_widget(Label(text=texto, color=cor))
            self.lista.add_widget(box)

    def excluir_usuario(self, instance):
        if self.manager.usuario_logado != "Master":
            self.msg.text = "❌ Apenas Master pode excluir!"
            return
        if not self.indice_apagar.text.strip():
            self.msg.text = "⚠ Digite o numero do operador!"
            return
        try:
            lista_users = list(usuarios.keys())
            idx = int(self.indice_apagar.text.strip()) - 1
            if 0 <= idx < len(lista_users):
                nome_excluir = lista_users[idx]
                if nome_excluir == "Master":
                    self.msg.text = "❌ Nao pode excluir o administrador!"
                    return
                del usuarios[nome_excluir]
                salvar_usuarios()
                self.msg.text = f"✅ Operador '{nome_excluir}' excluido!"
                self.indice_apagar.text = ""
                self.carregar_lista()
            else:
                self.msg.text = f"❌ Numero invalido! Total: {len(lista_users)}"
        except ValueError:
            self.msg.text = "❌ Digite apenas numeros!"
        except Exception as e:
            self.msg.text = f"❌ Erro: {str(e)}"


class TelaTrocarSenha(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.criar_interface()

    def criar_interface(self):
        layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(12))
        aplicar_fundo(layout)

        layout.add_widget(Label(
            text="🔑 Trocar Senha",
            font_size=fs(22), bold=True, color=(1, 0.85, 0.35, 1),
            size_hint_y=None, height=dp(48)
        ))

        layout.add_widget(Label(
            text="Selecione um operador ja cadastrado e informe a senha atual.",
            font_size=fs(13), color=COR_TEXTO,
            size_hint_y=None, height=dp(38),
            halign='center', valign='middle'
        ))

        self.operador = criar_spinner(["Selecione o Operador"], "Selecione o Operador", altura=46)

        self.senha_atual = TextInput(
            hint_text="Senha atual",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )
        self.nova_senha = TextInput(
            hint_text="Nova senha",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )
        self.confirmar_senha = TextInput(
            hint_text="Confirmar nova senha",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(46)
        )

        layout.add_widget(self.operador)
        layout.add_widget(self.senha_atual)
        layout.add_widget(self.nova_senha)
        layout.add_widget(self.confirmar_senha)

        btn_ver = criar_botao("👁 VER / OCULTAR SENHAS", (0.20, 0.45, 0.85, 1), 48)
        btn_ver.bind(on_press=self.alternar_senhas)
        layout.add_widget(btn_ver)

        btn_salvar = criar_botao("SALVAR NOVA SENHA", COR_SUCESSO, 52)
        btn_salvar.bind(on_press=self.trocar_senha)
        layout.add_widget(btn_salvar)

        self.msg = Label(text="", font_size=fs(13), color=COR_TEXTO)
        layout.add_widget(self.msg)

        btn_voltar = criar_botao("VOLTAR PARA LOGIN", (0.35, 0.38, 0.45, 1), 50)
        btn_voltar.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(btn_voltar)

        self.add_widget(layout)

    def on_enter(self):
        operadores = operadores_disponiveis(False)
        self.operador.values = operadores if operadores else ["Selecione o Operador"]
        self.operador.text = "Selecione o Operador"
        self.senha_atual.text = ""
        self.nova_senha.text = ""
        self.confirmar_senha.text = ""
        self.msg.text = ""
        self.senha_atual.password = True
        self.nova_senha.password = True
        self.confirmar_senha.password = True

    def alternar_senhas(self, instance):
        novo_estado = not self.senha_atual.password
        self.senha_atual.password = novo_estado
        self.nova_senha.password = novo_estado
        self.confirmar_senha.password = novo_estado

    def trocar_senha(self, instance):
        usuario = self.operador.text.strip()
        senha_atual = self.senha_atual.text.strip()
        nova = self.nova_senha.text.strip()
        confirmar = self.confirmar_senha.text.strip()

        if usuario not in usuarios:
            self.msg.text = "⚠ Selecione um operador valido."
            return
        if not senha_atual or not nova or not confirmar:
            self.msg.text = "⚠ Preencha todos os campos."
            return
        if usuarios.get(usuario) != senha_atual:
            self.msg.text = "❌ Senha atual incorreta."
            return
        if nova != confirmar:
            self.msg.text = "⚠ A nova senha e a confirmacao nao conferem."
            return
        if len(nova) < 4:
            self.msg.text = "⚠ A nova senha precisa ter pelo menos 4 caracteres."
            return

        usuarios[usuario] = nova
        salvar_usuarios()
        self.manager.usuario_logado = None
        self.msg.text = "✅ Senha alterada com sucesso! Volte e entre com a nova senha."
        self.senha_atual.text = ""
        self.nova_senha.text = ""
        self.confirmar_senha.text = ""


# ====================== GERENCIADOR DE TELAS ======================
class GerenciadorTelas(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.usuario_logado = None
        self.add_widget(TelaLogin(name='login'))
        self.add_widget(TelaMenu(name='menu'))
        self.add_widget(TelaCadastrar(name='cadastrar'))
        self.add_widget(TelaListar(name='listar'))
        self.add_widget(TelaAtualizar(name='atualizar'))
        self.add_widget(TelaManutencao(name='manutencao'))
        self.add_widget(TelaSaida(name='saida'))
        self.add_widget(TelaEntrada(name='entrada'))
        self.add_widget(TelaViagem(name='viagem'))
        self.add_widget(TelaRomaneio(name='romaneio'))
        self.add_widget(TelaApagar(name='apagar'))
        self.add_widget(TelaCriarUser(name='criar_user'))
        self.add_widget(TelaListaUsuarios(name='lista_usuarios'))
        self.add_widget(TelaTrocarSenha(name='trocar_senha'))
        self.add_widget(TelaConfig(name='config'))


# ====================== CLASSE PRINCIPAL ======================
class SistemaEstoqueApp(App):
    def build(self):
        Window.clearcolor = (0.06, 0.07, 0.12, 1)
        Window.title = "MASTER TORQUE ROMANEIO"
        Window.softinput_mode = "below_target"
        carregar_dados()
        return GerenciadorTelas()


if __name__ == "__main__":
    SistemaEstoqueApp().run()