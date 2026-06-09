from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from flask_socketio import SocketIO, join_room, emit
import random
import threading
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
import matplotlib.pyplot as plt
from threading import Thread
import pandas as pd
import requests
import mercadopago
import requests
import hmac
import hashlib
from io import BytesIO
import base64
import qrcode
import fitz
import re
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson.objectid import ObjectId
from models import criar_usuario, users_collection, pagamentos_collection, criar_documento_pagamento, PagamentoModel,  criar_vendedor, vendedores_collection
from models import  bilhetes_collection, criar_documento_bilhete, BilheteModel
from models import  raspadinhas_collection, criar_documento_raspadinha, RaspadinhaModel
from models import criar_projeto
from models import projetos_collection
from models import criar_saque, saques_collection
from models import get_all_saques
from models import db 
from models import salvar_mensagem 
from models import MensagemModel
from flask_cors import CORS
from datetime import datetime, timezone
from datetime import datetime, date
import time
import uuid
import io
import json
import textwrap
import traceback

load_dotenv()

app = Flask(__name__)
CORS(app)
# ---------------- MONGODB ----------------
client = MongoClient(os.getenv("MONGO_URI"))
pagamento_model = PagamentoModel()
bilhete_model = BilheteModel()
raspadinha_model = RaspadinhaModel()
mensagem_model = MensagemModel()
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("APP_SECRET_KEY")
notification_url = os.getenv("NOTIFICATION_URL")




@app.route('/ver-logs')
def ver_logs():
    # Busca todos os logs salvos do mais novo para o mais antigo
    logs = list(db["logs_seguranca_erros"].find().sort("_id", -1))
    
    # Converte o ObjectId do MongoDB em string para o Flask conseguir gerar o JSON sem quebrar
    for log in logs:
        log["_id"] = str(log["_id"])
        
    # Retorna o JSON puro diretamente na tela
    return jsonify(logs)


# ---------------- CLOUDINARY ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

@app.route("/")
def produtos():
    return render_template("index.html")



@app.route("/gerador/curriculo")
def curriculos():
    # Renderiza o seu formulário HTML
    return render_template("produtos/gerador_curriculo.html")


# Configurações de pastas
UPLOAD_FOLDER = "static/uploads"
PDF_FOLDER = "static/pdfs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)




# =========================================================================
# CENTRALIZADOR GLOBAL DE SEGURANÇA E AUDITORIA DE ERROS
# =========================================================================
# def obter_localizacao_ip(ip):
#     """
#     Consulta a API de geolocalização para extrair cidade e estado do IP.
#     """
#     # Ignora IPs de teste local
#     if ip in ['127.0.0.1', 'localhost'] or ip.startswith('192.168.'):
#         return "Rede Local / Teste"
    
#     try:
#         # Consulta a API de forma ultra rápida (limite de 1s para não travar o site)
#         resposta = requests.get(f"http://ip-api.com{ip}?fields=status,city,regionName,country", timeout=1)
#         dados_geo = resposta.json()
        
#         if dados_geo.get("status") == "success":
#             return f"{dados_geo.get('city')}, {dados_geo.get('regionName')} - {dados_geo.get('country')}"
#     except:
#         pass
    
#     return "Não identificada"


# @app.before_request
# def monitorar_seguranca_global():
#     ip_usuario = request.headers.get('X-Forwarded-For', request.remote_addr)
#     # Se houver uma lista de IPs, pega apenas o primeiro (IP real do cliente)
#     if ip_usuario and ',' in ip_usuario:
#         ip_usuario = ip_usuario.split(',')[0].strip()

#     rotas_criticas = ['/saque', '/raspadinha/resultado']
    
#     if request.path in rotas_criticas:
#         dados = request.get_json(silent=True) or {}
#         usuario_id = dados.get("usuario_id") or request.args.get("usuario_id")
        
#         if usuario_id and not ObjectId.is_valid(str(usuario_id)):
#             # Busca a localização antes de salvar
#             localizacao = obter_localizacao_ip(ip_usuario)

#             db["logs_seguranca_erros"].insert_one({
#                 "tipo": "TENTATIVA_INVASAO_ID",
#                 "status_code": 400,
#                 "rota": request.path,
#                 "metodo": request.method,
#                 "detalhe": f"Formato de ID inválido ou tentativa de injeção: '{usuario_id}'",
#                 "ip": ip_usuario,
#                 "localizacao": localizacao, # <-- Novo campo salvo no banco
#                 "user_agent": request.headers.get("User-Agent"),
#                 "data": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
#             })
#             return jsonify({"erro": "Ação inválida. Esta tentativa foi registrada para auditoria."}), 400


# @app.errorhandler(Exception)
# def capturar_erros_500_global(e):
#     ip_usuario = request.headers.get('X-Forwarded-For', request.remote_addr)
#     if ip_usuario and ',' in ip_usuario:
#         ip_usuario = ip_usuario.split(',')[0].strip()
        
#     erro_completo = traceback.format_exc()
    
#     # Busca a localização antes de salvar
#     localizacao = obter_localizacao_ip(ip_usuario)

#     db["logs_seguranca_erros"].insert_one({
#         "tipo": "ERRO_SISTEMA_500",
#         "status_code": getattr(e, 'code', 500),
#         "rota": request.path,
#         "metodo": request.method,
#         "erro_mensagem": str(e),
#         "rastreamento_terminal": erro_completo,
#         "ip": ip_usuario,
#         "localizacao": localizacao, # <-- Novo campo salvo no banco
#         "user_agent": request.headers.get("User-Agent"),
#         "data": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
#     })
    
#     return jsonify({
#         "erro": "Ocorreu uma inconsistência interna no servidor.",
#         "mensagem": "O incidente foi registrado automaticamente para análise técnica."
#     }), 500

@app.route("/template", methods=["POST"])
def template():

    acao = request.form.get("acao")
    foto = request.files.get("foto")

    dados = {
        "nome": request.form.get("nome"),
        "objetivo": request.form.get("objetivo"),
        "email": request.form.get("email"),
        "contato": request.form.get("contato"),
        "cidade": request.form.get("cidade"),
        "resumo": request.form.get("resumo"),
        "habilidades": request.form.get("habilidades").splitlines(),
        "foto": None
    }

    caminho_foto = None

    # =====================================
    # FOTO - CORREÇÃO DE ORIENTAÇÃO INCLUÍDA
    # =====================================

    if foto and foto.filename != "":

        nome_foto = f"{uuid.uuid4().hex}_{secure_filename(foto.filename)}"

        caminho_foto = os.path.join(
            UPLOAD_FOLDER,
            nome_foto
        )

        foto.save(caminho_foto)
        
        # --- CORREÇÃO DA FOTO TORTA ---
        # Abre a imagem, corrige a rotação automática do celular (EXIF) e salva de volta
        img_fix = Image.open(caminho_foto)
        img_fix = ImageOps.exif_transpose(img_fix)
        img_fix.save(caminho_foto)
        # ------------------------------

        dados["foto"] = nome_foto

    # =====================================
    # PREVIEW
    # =====================================

    if acao != "baixar":

        return render_template(
            "produtos/preview.html",
            dados=dados
        )

    # =====================================
    # FOTO VINDO DA PREVIEW
    # =====================================

    foto_preview = request.form.get("foto_preview")

    if foto_preview:

        caminho_foto = os.path.join(
            UPLOAD_FOLDER,
            foto_preview
        )

    # =====================================
    # PDF
    # =====================================

    nome_pdf = f"{uuid.uuid4().hex}.pdf"

    caminho_pdf = os.path.join(
        PDF_FOLDER,
        nome_pdf
    )

    c = canvas.Canvas(
        caminho_pdf,
        pagesize=A4
    )

    largura, altura = A4

    azul = HexColor("#0066CC")
    cinza = HexColor("#444444")

    margem_esquerda = 50

    # =====================================
    # FOTO PDF
    # =====================================

    x_foto = largura - 140
    y_foto = altura - 140

    largura_foto = 100
    altura_foto = 100

    c.setStrokeColor(azul)

    c.setLineWidth(1)

    c.rect(
        x_foto,
        y_foto,
        largura_foto,
        altura_foto
    )

    try:

        if caminho_foto and os.path.exists(caminho_foto):

            img = Image.open(caminho_foto)

            img = img.convert("RGB")

            largura_original, altura_original = img.size

            proporcao = min(
                largura_foto / largura_original,
                altura_foto / altura_original
            )

            nova_largura = largura_original * proporcao
            nova_altura = altura_original * proporcao

            pos_x = x_foto + (
                (largura_foto - nova_largura) / 2
            )

            pos_y = y_foto + (
                (altura_foto - nova_altura) / 2
            )

            # Usando ImageReader direto na imagem processada
            imagem = ImageReader(img)

            c.drawImage(
                imagem,
                pos_x,
                pos_y,
                width=nova_largura,
                height=nova_altura,
                mask='auto'
            )

        else:
            raise Exception()

    except Exception as erro:

        print("ERRO FOTO:", erro)

        c.setFont("Helvetica", 9)

        c.drawCentredString(
            x_foto + 45,
            y_foto + 50,
            "Foto"
        )

    # =====================================
    # NOME
    # =====================================

    c.setFillColor(azul)

    c.setFont("Helvetica-Bold", 20)

    nome_linhas = textwrap.wrap(
        dados["nome"],
        width=28
    )

    y_nome = altura - 90

    for linha in nome_linhas:

        c.drawString(
            margem_esquerda,
            y_nome,
            linha
        )

        y_nome -= 24

    # =====================================
    # OBJETIVO
    # =====================================

    c.setFillColor(cinza)

    c.setFont("Helvetica", 14)

    c.drawString(
        margem_esquerda,
        y_nome - 5,
        dados["objetivo"]
    )

    # =====================================
    # LINHA
    # =====================================

    linha_y = y_nome - 30

    c.setStrokeColor(azul)

    c.setLineWidth(2)

    c.line(
        50,
        linha_y,
        largura - 50,
        linha_y
    )

    # =====================================
    # CONTATO
    # =====================================

    c.setFillColor(azul)

    c.setFont("Helvetica-Bold", 12)

    c.drawString(
        margem_esquerda,
        linha_y - 30,
        "Contato:"
    )

    c.setFillColor(cinza)

    c.setFont("Helvetica", 11)

    contato = (
        f"{dados['cidade']} | "
        f"{dados['contato']} | "
        f"{dados['email']}"
    )

    contato_linhas = textwrap.wrap(
        contato,
        width=65
    )

    y_contato = linha_y - 30

    for linha in contato_linhas:

        c.drawString(
            120,
            y_contato,
            linha
        )

        y_contato -= 16

    # =====================================
    # PERFIL
    # =====================================

    y_atual = y_contato - 35

    c.setFillColor(azul)

    c.setFont("Helvetica-Bold", 14)

    c.drawString(
        margem_esquerda,
        y_atual,
        "Perfil Profissional"
    )

    y_atual -= 25

    c.setFillColor(cinza)

    c.setFont("Helvetica", 11)

    resumo_linhas = textwrap.wrap(
        dados["resumo"],
        width=85
    )

    for linha in resumo_linhas:

        c.drawString(
            margem_esquerda,
            y_atual,
            linha
        )

        y_atual -= 18

    # =====================================
    # HABILIDADES
    # =====================================

    y_atual -= 10

    c.setFillColor(azul)

    c.setFont("Helvetica-Bold", 14)

    c.drawString(
        margem_esquerda,
        y_atual,
        "Habilidades e Diferenciais"
    )

    y_atual -= 25

    c.setFillColor(cinza)

    c.setFont("Helvetica", 11)

    for hab in dados["habilidades"]:

        if hab.strip():

            linhas_hab = textwrap.wrap(
                hab.strip(),
                width=80
            )

            for i, linha in enumerate(linhas_hab):

                prefixo = "• " if i == 0 else "  "

                c.drawString(
                    margem_esquerda + 10,
                    y_atual,
                    prefixo + linha
                )

                y_atual -= 18

                if y_atual < 80:

                    c.showPage()

                    y_atual = altura - 80

                    c.setFont("Helvetica", 11)

    # =====================================
    # RODAPÉ
    # =====================================

    c.setFont("Helvetica-Oblique", 9)

    c.setFillColor(cinza)

    c.drawCentredString(
        largura / 2,
        40,
        "Currículo gerado automaticamente em Python"
    )

    c.save()

    return send_file(
        caminho_pdf,
        as_attachment=True
    )

#================================================================================
# Limpar cpf
def limpar_cpf(cpf):
    if not cpf:
        return None
    return ''.join(filter(str.isdigit, cpf))
#---------------------------------------------------------------------------------
#=================================================================================
#=================================================================================
# PAGINA INICIAL DO USUARIOS OPÇOES
#/ferrari-tech/tecnlogia
@app.route("/access/interacao/84729163509817263549081726354908172635490817263549081726354908172635")
def options():
    return render_template("opcoes.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/termos")
def politica_privacidade():
    return render_template("termos.html")   

#=================================================================================
# REGISTRAR USUARIOS
#---------------------------------------------------------------------------------


def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def validar_maioridade(dt_nascimento_str):
    try:
        # Ajuste o formato conforme o que vier do seu front-end (ex: YYYY-MM-DD)
        data_nasc = datetime.strptime(dt_nascimento_str, "%Y-%m-%d").date()
        hoje = date.today()
        idade = hoje.year - data_nasc.year - ((hoje.month, hoje.day) < (data_nasc.month, data_nasc.day))
        return idade >= 18
    except ValueError:
        return False

# =========================
# ROUTE /registrar
# =========================

@app.route("/registrar", methods=["POST"])
def registrar():

    try:

        data = request.get_json(force=True)

        print("CHEGOU NO BACK:", data)

        cpf = data.get("cpf", "")
        dt_nascimento = data.get("dt_nascimento", "")

        # --- VALIDAÇÕES ---
        if not validar_cpf(cpf):
            return jsonify({
                "status": "erro",
                "mensagem": "CPF inválido."
            }), 400

        if not validar_maioridade(dt_nascimento):
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário deve ser maior de 18 anos."
            }), 400

        # =========================
        # IP
        # =========================
        ip_usuario = request.headers.get("X-Forwarded-For", request.remote_addr)

        # =========================
        # USER AGENT
        # =========================
        user_agent_string = request.headers.get("User-Agent", "")
        user_agent = parse(user_agent_string)
        ua = user_agent_string.lower()

        # =========================
        # DETECÇÃO DE APARELHO
        # =========================
        aparelho = "Desconhecido"

        if "sm-a356" in ua:
            aparelho = "Samsung Galaxy A35"
        elif "sm-a346" in ua:
            aparelho = "Samsung Galaxy A34"
        elif "sm-a546" in ua:
            aparelho = "Samsung Galaxy A54"
        elif "sm-s918" in ua:
            aparelho = "Samsung Galaxy S23 Ultra"
        elif "sm-s926" in ua:
            aparelho = "Samsung Galaxy S24+"
        elif "sm-g990" in ua:
            aparelho = "Samsung Galaxy S21 FE"
        elif "sm-" in ua:
            aparelho = "Samsung"
        elif "2201117tg" in ua:
            aparelho = "Xiaomi Redmi Note 11"
        elif "22101316g" in ua:
            aparelho = "Xiaomi Redmi Note 12"
        elif "2312draf3" in ua:
            aparelho = "Xiaomi Redmi Note 13"
        elif "redmi" in ua or "xiaomi" in ua:
            aparelho = "Xiaomi"
        elif "moto g54" in ua:
            aparelho = "Motorola Moto G54"
        elif "moto g84" in ua:
            aparelho = "Motorola Moto G84"
        elif "moto" in ua:
            aparelho = "Motorola"
        elif "iphone" in ua:
            aparelho = "iPhone"
        elif "ipad" in ua:
            aparelho = "iPad"
        elif "huawei" in ua:
            aparelho = "Huawei"
        elif "asus" in ua:
            aparelho = "Asus"
        elif "lg-" in ua:
            aparelho = "LG"
        elif "realme" in ua:
            aparelho = "Realme"
        elif "oppo" in ua:
            aparelho = "Oppo"
        elif "vivo" in ua:
            aparelho = "Vivo"
        elif "nokia" in ua:
            aparelho = "Nokia"
        elif "windows nt" in ua:
            aparelho = "PC Windows"
        elif "macintosh" in ua or "mac os" in ua:
            aparelho = "MacBook / iMac"
        elif "linux" in ua and "android" not in ua:
            aparelho = "PC Linux"
        else:
            aparelho = f"{user_agent.device.family} | {user_agent.os.family}"

        # =========================
        # NAVEGADOR
        # =========================
        navegador = user_agent.browser.family

        usuario = criar_usuario(
            data.get("nome", ""),
            data.get("sobrenome", ""),
            cpf,
            dt_nascimento,
            data.get("email", ""),
            data.get("vendedor", "Plataforma Ferrari Tech"),
            data.get("chave_pix", ""),
            ip_usuario,
            aparelho,
            navegador
        )

        users_collection.update_one(
            {"_id": ObjectId(usuario["_id"])},
            {
                "$setOnInsert": {
                    "ganhos": 0.00,
                    "saques": 0.00,
                    "status": "online"
                }
            },
            upsert=True
        )

        session["user_id"] = usuario["_id"]

        return jsonify({
            "status": "sucesso",
            "usuario": usuario
        }), 201

    except Exception as e:

        print("ERRO:", e)

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400
#---------------------------------------------------------------------------------
@app.route("/reconhecimento_facial")
def face():
    return render_template("graficos/eventos/Admin/reconhecimento_facial.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

#=================================================================================
#=================================================================================
# 🔐 LOGIN USUARIOS
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json

        email = str(data["email"]).strip()

        usuario = users_collection.find_one({"email": email})

        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Email não encontrado"
            }), 404

        users_collection.update_one(
            {"_id": usuario["_id"]},   # já é string
            {"$set": {"status": "online"}}
        )

        return jsonify({
            "status": "sucesso",
            "usuario_id": str(usuario["_id"])
        }), 200

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400
#---------------------------------------------------------------------------------
@app.route("/logout", methods=["POST"])
def logout_user():
    try:
        data = request.json

        # Recebe o ID do usuário que quer deslogar
        usuario_id = str(data["usuario_id"]).strip()

        if not usuario_id:
            return jsonify({
                "status": "erro",
                "mensagem": "ID do usuário não fornecido"
            }), 400

        # Busca o usuário para garantir que ele existe
        usuario = users_collection.find_one({"_id": usuario_id})

        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404

        # Atualiza o status para offline
        users_collection.update_one(
            {"_id": usuario["_id"]},
            {"$set": {"status": "offline"}}
        )

        return jsonify({
            "status": "sucesso",
            "mensagem": "Logout realizado com sucesso"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400


#=================================================================================
#=================================================================================
# INTERFACE REGISTRO>HTML 
@app.route("/vitoria_vitoriosa/registro")
def registro():
    # aqui vai listar todos os vendedores cadastrados com nome 
    vendedores = list(vendedores_collection.find({}, {"nome": 1}))

    return render_template(
        "registro.html",
        vendedores=vendedores
    )    

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# INTERACE USUARIOS LOGIN>>HTML
@app.route("/vitoria_vitoriosa/login")
def interface_login():
    return render_template("login.html")

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# 🔓ROTA LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/vitoria-visonaria_franca-sp")

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# Interface projetos 

#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# 📄 PÁGINA PROJETO  PRINCIPAL
@app.route("/access/codigo_servico/1722/<vendedor_id>/<projeto_id>")
@app.route("/vitoria_visionaria/projeto-desenvolvimento-fase-teste/codigo_servico/1722/<usuario_id>/<projeto_id>")
def view_pagamentos(usuario_id=None, vendedor_id=None, projeto_id=None):

    def limpar_numero(n):
        return re.sub(r"\D", "", str(n))

    def limpar_cpf(c):
        return re.sub(r"\D", "", str(c))

    def calcular_meta_vendas(vendidos, meta):
        try:
            meta = int(meta) if meta else 0
            vendidos = int(vendidos) if vendidos else 0
            if meta <= 0:
                return 0
            return round((vendidos / meta) * 100, 2)
        except:
            return 0

    if not usuario_id and not vendedor_id:
        return redirect("/vitoria-visonaria_franca-sp")

    usuario = None
    vendedor = None

    # Busca usuário
    if usuario_id:
        usuario = users_collection.find_one({
            "_id": ObjectId(usuario_id)
        })

        if not usuario:
            return "usuário não encontrado", 404

        pessoa = usuario

    # Busca vendedor
    elif vendedor_id:
        vendedor = vendedores_collection.find_one({
            "_id": ObjectId(vendedor_id)
        })

        if not vendedor:
            return "vendedor não encontrado", 404

        pessoa = vendedor

    pessoa["_id"] = str(pessoa["_id"])

    email = (pessoa.get("email") or pessoa.get("email_usuario") or "").strip().lower()
    cpf = limpar_cpf(pessoa.get("cpf"))

    # BILHETES APROVADOS
    bilhetes_all = bilhete_model.get_all_bilhetes() or []
    bilhetes = [
        b for b in bilhetes_all
        if (
            b.get("email_usuario", "").strip().lower() == email and
            limpar_cpf(b.get("cpf")) == cpf and
            b.get("status") == "approved"
        )
    ]

    numeros_aprovados = set()
    for b in bilhetes:
        for n in b.get("lista_numeros", []):
            numeros_aprovados.add(limpar_numero(n))

    # LISTA DE TODOS OS USUÁRIOS (PARA A TABELA)
    usuarios = []
    for u in users_collection.find():
        usuarios.append({
            "_id": str(u.get("_id")),
            "nome": u.get("nome", ""),
            "cpf": limpar_cpf(u.get("cpf")),
            "estado": u.get("estado", "Sao Paulo"),
            "vendedor": u.get("vendedor", ""),
            "bilhetes": []
        })

    # BUSCA PROJETO SELECIONADO (O QUE O USUÁRIO CLICOU)
    projeto_principal = {}
    projeto_data = projetos_collection.find_one({"_id": ObjectId(projeto_id)})
    
    if projeto_data:
        projeto_data["_id"] = str(projeto_data["_id"])
        projeto_data["nome_projeto"] = projeto_data.get("nome_projeto", "")
        projeto_data["imagem_projeto"] = projeto_data.get("imagem_projeto", "")
        projeto_data["dt_sorteio"] = projeto_data.get("dt_sorteio", "")
        projeto_data["horario_sorteio"] = projeto_data.get("horario_sorteio", "")
        projeto_data["quantidade"] = projeto_data.get("quantidade", "")
        projeto_data["link_instagram"] = projeto_data.get("link_instagram", "")

        # Cálculo da meta específico para este projeto
        vendidos = len(numeros_aprovados)
        projeto_data["progresso_meta"] = calcular_meta_vendas(vendidos, projeto_data["quantidade"])

        # Formata Data
        dt = projeto_data["dt_sorteio"]
        if dt != "Meta 80%" and isinstance(dt, str) and "-" in dt:
            partes = dt.split("-")
            if len(partes) == 3:
                projeto_data["dt_sorteio"] = f"{partes[2]}/{partes[1]}/{partes[0]}"
        
        projeto_principal = projeto_data

    # LISTA DE PROJETOS (PARA O CARROSSEL/MENU)
    projetos = list(projetos_collection.find())
    for p in projetos:
        p["_id"] = str(p["_id"])

    return render_template(
        "index-1.html",
        usuario=usuario,
        vendedor=vendedor,
        usuarios=usuarios,
        projetos=projetos,
        bilhetes=bilhetes,
        projeto_principal=projeto_principal,
        projeto_id=projeto_id,
        usuario_id=usuario_id,
        vendedor_id=vendedor_id
    )

#----------------------------------------------------------------------  
#----------------------------------------------------------------------  
#----------------------------------------------------------------------  
#----------------------------------------------------------------------    
@app.route("/vitoria_visonaria/gerar_cupom/<usuario_id>/<projeto_id>")
def numeros(usuario_id, projeto_id):
    try:
        # 1. Busca o usuário
        usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
        if not usuario:
            return "Usuário não encontrado", 404

        # 2. Busca o projeto selecionado
        projeto_data = projetos_collection.find_one({"_id": ObjectId(projeto_id)})
        
        if not projeto_data:
            return "Projeto não encontrado", 404

        # 3. Organiza os dados para o template
        # Convertemos o ID para string para evitar erros no HTML/JS
        projeto_data["_id"] = str(projeto_data["_id"])
        
        # Garantimos que campos numéricos ou vazios não quebrem o render
        projeto_principal = {
            "_id": projeto_data["_id"],
            "nome_projeto": projeto_data.get("nome_projeto", "Sem nome"),
            "valor_unidade": projeto_data.get("valor_unidade", 0)
        }

        return render_template(
            "gerar_numero.html",
            usuario=usuario,
            usuario_id=usuario_id,
            projeto_id=projeto_id,
            projeto_principal=projeto_principal,  # Agora ela contém os dados!
        )

    except Exception as e:
        print(f"Erro na rota gerar_cupom: {e}")
        return "Erro interno no servidor", 500

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
# ROTA TABELA RIFA DE NOMES
@app.route("/tabela_nomes/<id>")
def tabela_nomes(id):
    usuario = users_collection.find_one({"_id": ObjectId(id)})
    
    if not usuario:
        return "Usuário não encontrado", 404

    return render_template(
        "tabela_nomes.html",
        premiacao1=premiacao1,
        usuario=usuario,
        usuario_id=id
    )
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------




def limpar_numero(n):
    return re.sub(r"\D", "", str(n))




@app.route("/controle_vendas")
def controle_vendas():
    bilhetes = BilheteModel().get_all_bilhetes() or []
    pagamentos = PagamentoModel().get_all_pagamentos() or []

    pagamentos = [p for p in pagamentos if str(p.get("status")).lower() in ["approved", "pending"]]

    # mapa numero -> imagem
    mapa = {}
    for b in bilhetes:
        nums = b.get("lista_numeros", [])
        urls = b.get("lista_urls_img_bilhetes", [])

        for i in range(len(nums)):
            n = limpar_numero(nums[i])
            url = urls[i] if i < len(urls) else None

            if n and url:
                mapa.setdefault(n, []).append(url)

    # usuarios
    usuarios = []
    for u in users_collection.find():
        usuarios.append({
            "_id": str(u.get("_id")),
            "nome": u.get("nome", ""),
            "sobrenome": u.get("sobrenome", ""),
            "dt_nascimento": u.get("dt_nascimento", ""),
            "cpf": limpar_numero(u.get("cpf", "")),
            "email": u.get("email", ""),
            "chave_pix": u.get("chave_pix", ""),
            "vendedor": u.get("vendedor", ""),
            "bilhetes": []
        })

    # liga pagamento + bilhete + usuario
    for p in pagamentos:
        lista = p.get("lista_numeros", [])

        if isinstance(lista, str):
            try:
                lista = json.loads(lista)
            except:
                lista = []

        cpf_pag = limpar_numero(p.get("cpf"))

        for n in lista:
            n_limpo = limpar_numero(n)

            img = None
            if n_limpo in mapa and mapa[n_limpo]:
                img = mapa[n_limpo].pop(0)

            for u in usuarios:
                if u["cpf"] == cpf_pag:
                    u["bilhetes"].append({
                        "numero": n_limpo,
                        "imagem": img
                    })

    # 🔥 AQUI É A ÚNICA PARTE ADICIONADA (FILTRO)
    termo = (request.args.get("q") or "").lower().strip()

    if termo:
        usuarios_filtrados = []

        for u in usuarios:
            # 📧 se for email → traz todos os bilhetes
            if termo in (u["email"] or "").lower():
                usuarios_filtrados.append(u)
                continue

            # 🔢 filtra pelos números
            bilhetes_filtrados = [
                b for b in u["bilhetes"]
                if termo in b.get("numero", "")
            ]

            if bilhetes_filtrados:
                novo = u.copy()
                novo["bilhetes"] = bilhetes_filtrados
                usuarios_filtrados.append(novo)

        usuarios = usuarios_filtrados

    return render_template(
        "graficos/controle_vendas.html",
        usuarios=usuarios,
    )
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
@app.route("/criar_evento/mobile/admins")
def projetos():
    return render_template("graficos/registro_projeto.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------    
@app.route("/criar_projeto", methods=["POST"])
def criar_projeto_route():

    try:
        data = request.get_json(force=True)
        print("CHEGOU NO BACK:", data)

        # 🔥 chamada correta da função
        projeto = criar_projeto(
            nome_projeto=data.get("nome_projeto", ""),
            valor_injetado_premiacao=data.get("valor_injetado_premiacao", ""),
            horario_sorteio=data.get("horario_sorteio", ""),
            quantidade=data.get("quantidade", ""),
            valor_unidade=data.get("valor_unidade", 0),
            dt_sorteio=data.get("dt_sorteio", ""),

            imagem_projeto=data.get("imagem_projeto", ""),
            video_instrucao=data.get("video_instrucao", ""),

            link_instagram=data.get("link_instagram", ""),
            link_youtube=data.get("link_youtube", ""),
            link_whatsapp_grupo=data.get("link_whatsapp_grupo", ""),
            link_whatsapp_canal=data.get("link_whatsapp_canal", ""),
            link_whatsapp_suporte=data.get("link_whatsapp_suporte", ""),
            link_tiktok=data.get("link_tiktok", ""),
            link_facebook=data.get("link_facebook", ""),
            link_kwai=data.get("link_kwai", ""),
            status=data.get("status", "ativo")
        )

        return jsonify({"status": "sucesso", "projeto": projeto}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400


#---------------------------------------------------------------------------------
# DELETAR PROJETO

@app.route("/deletar_projeto/<id>", methods=["DELETE"])
def deletar_projeto(id):
    try:
        print("ID RECEBIDO:", id)

        if not ObjectId.is_valid(id):
            return jsonify({"status": "erro", "mensagem": "ID inválido"}), 400

        resultado = projetos_collection.delete_one({
            "_id": ObjectId(id)
        })

        if resultado.deleted_count == 0:
            return jsonify({"status": "erro", "mensagem": "Não encontrado"}), 404

        return jsonify({"status": "sucesso"}), 200

    except Exception as e:
        print("ERRO DELETE:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------    
@app.route("/listar_projetos", methods=["GET"])
def listar_projetos():
    try:
        projetos = list(projetos_collection.find())

        for p in projetos:
            p["_id"] = str(p["_id"])

        return jsonify({
            "status": "sucesso",
            "projetos": projetos
        }), 200

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400       


@app.route("/listar_projetos", methods=["GET"])
def listar_projeto():
    try:
        # Busca todos os projetos no MongoDB
        # Dica: use .find({}, {"algum_campo": 1}) se quiser filtrar campos específicos
        projetos = list(projetos_collection.find())

        # Converte ObjectId para string de forma mais Pythonica
        for projeto in projetos:
            projeto["_id"] = str(projeto["_id"])

        return jsonify({
            "status": "sucesso",
            "quantidade": len(projetos),
            "projetos": projetos
        }), 200

    except Exception as e:
        # Log do erro aqui seria ideal (ex: print(e))
        return jsonify({
            "status": "erro",
            "mensagem": "Erro interno ao listar projetos",
            "erro_detalhe": str(e)  # Opcional: remova em produção por segurança
        }), 500
    
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#--------------------------------------------------------------------------------- 
@app.route("/upload_media", methods=["POST"])
def upload_media():

    try:
        img = request.files.get("imagem_projeto")
        video = request.files.get("video_instrucao")

        imagem_url = ""
        video_url = ""

        if img:
            res = cloudinary.uploader.upload(img, folder="projetos")
            imagem_url = res["secure_url"]

        if video:
            res = cloudinary.uploader.upload(video, resource_type="video", folder="projetos")
            video_url = res["secure_url"]

        return jsonify({
            "imagem_url": imagem_url,
            "video_url": video_url
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# ROTA DE ACESSO AO FECHAMENTO
# Aqui adcionar CFOP: Venda de PDF (Currículo/Documento): 6.108 (Venda para consumidor final fora do estado). É o padrão para infoprodutos e arquivos digitais.
# Se for Serviço (Ex: Consultoria de currículo): 9.33 (Código de serviço, se houver emissão de nota municipal).
# Imposto e Alíquota (Previsão Reforma CBS/IBS)
# Alíquota: Reserve o campo no sistema para 26,5% (Soma estimada de CBS + IBS).Em 2026 (Transição): A alíquota será de apenas 0,15% (teste). O valor cheio (26,5%) só entra em 2027.Cálculo: Valor do PDF (1,25) * 0,265 = 0,33. (Esse seria o imposto futuro)
# Aqui vai acompanhar o faturamentos dos meses e desidir qual sera conforme fatura CPF (Atual): Você é "Pessoa Física com Atividade Econômica". Isento de imposto até R$ 2.112,00 por mês.MEI (O ideal para você agora): Se passar de R 75,00**) e não paga porcentagem sobre cada venda de R$ 1,25. É o melhor cenário para o seu preço.Simples Nacional (ME): Só quando seu site faturar mais de R$ 81.000 por ano. Aqui o imposto começa em 6% sobre o faturamento.
@app.route("/graficos/resumo/sistema/detalhes", methods=["GET"])
def fechamento():
    usuarios = list(users_collection.find())
    vendedores = list(vendedores_collection.find())
    pagamentos = pagamento_model.get_all_pagamentos() or []

    for p in pagamentos:
        p["_id"] = str(p.get("_id"))

    quantidade_usuarios = len(usuarios)
    quantidade_vendedores = len(vendedores)

    usuarios_map = {u.get("email"): u for u in usuarios}
    vendedores_map = {u.get("email"): u for u in vendedores}

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    # 🔥 TOTAL TAXA MERCADO PAGO
    total_taxa_mp = Decimal("0")

    # 🔥 TOTAL COMISSAO
    total_comissao = Decimal("0")
    

    numeros_aprovados = []
    vendedores = {}

    # 🔥 faturamento por mês
    faturamento_por_mes = {
        "Jan": Decimal("0"), "Fev": Decimal("0"), "Mar": Decimal("0"),
        "Abr": Decimal("0"), "Mai": Decimal("0"), "Jun": Decimal("0"),
        "Jul": Decimal("0"), "Ago": Decimal("0"), "Set": Decimal("0"),
        "Out": Decimal("0"), "Nov": Decimal("0"), "Dez": Decimal("0")
    }

    meses_map = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    for p in pagamentos:
        valor = Decimal(str(p.get("valor", 0)))
        status = p.get("status")
        email = p.get("email_usuario")

        usuario = usuarios_map.get(email, {})
        vendedor = usuario.get("vendedor", "sem_vendedor")

        if vendedor not in vendedores:
            vendedores[vendedor] = {
                "pending": Decimal("0"),
                "approved": Decimal("0"),
                "cancelled": Decimal("0"),
                "numeros": 0,
                "comissao": Decimal("0")
            }

        if status == "pending":
            total_pagamentos_pending += valor
            vendedores[vendedor]["pending"] += valor

        elif status == "approved":
            total_pagamentos_approved += valor
            vendedores[vendedor]["approved"] += valor

            if valor > Decimal("0.50"):
                taxa_mp = valor * Decimal("0.0099")
                total_taxa_mp += taxa_mp

            comissao = valor * Decimal("0.30")
            vendedores[vendedor]["comissao"] += comissao
            

            # 🔥 SOMA TOTAL COMISSAO
            total_comissao += comissao

            data_str = p.get("data_criacao")
            if data_str:
                try:
                    data = datetime.strptime(data_str, "%a, %d %b %Y %H:%M:%S GMT")
                    mes_nome = meses_map[data.month]
                    faturamento_por_mes[mes_nome] += valor
                except:
                    pass

            lista = p.get("lista_numeros", [])
            if isinstance(lista, str):
                try:
                    lista = json.loads(lista)
                except:
                    lista = []

            if isinstance(lista, list):
                numeros_aprovados.extend(lista)
                vendedores[vendedor]["numeros"] += len(lista)

        elif status == "cancelled":
            total_pagamentos_cancelled += valor
            vendedores[vendedor]["cancelled"] += valor

    vendedores_formatado = {
        v: {
            "pending": float(d["pending"]),
            "approved": float(d["approved"]),
            "cancelled": float(d["cancelled"]),
            "numeros": d["numeros"],
            "comissao": float(d["comissao"])
        } for v, d in vendedores.items()
    }

    projetos = list(projetos_collection.find())
    total_investimento_premiacao = Decimal("0")

    projetos_formatados = []

    for pr in projetos:
        quantidade = pr.get("quantidade", "0")
        valor_inv = pr.get("valor_injetado_premiacao", "0")

        try:
            quantidade = int(quantidade)
        except:
            quantidade = 0
        
        try:
            valor_unidade = float(pr.get("valor_unidade", 0))
        except:
            quantidade = 0.0
        valor_inv = pr.get("valor_injetado_premiacao", 0)    

        try:
            total_investimento_premiacao += Decimal(str(valor_inv))
        except:
            pass    


    projetos = list(projetos_collection.find())

    for p in projetos:
        p["_id"] = str(p["_id"])
        p["quantidade"] = p.get("quantidade", "")

        # 🔥 total vendido global (ou depois posso ajustar por projeto se quiser separar certinho)
        vendidos = len(numeros_aprovados)

     

 

    faturamento_por_mes = {k: float(v) for k, v in faturamento_por_mes.items()}

    # =========================
    # 🔥 BLOCO FISCAL
    # =========================

    faturamento_total = total_pagamentos_approved

    cfop_produto = "6.103"
    codigo_servico = "17.22"

    aliquota_futura = Decimal("0.28")
    aliquota_transicao = Decimal("0.0015")

    imposto_futuro = faturamento_total * aliquota_futura
    imposto_transicao = faturamento_total * aliquota_transicao

    regime = "CPF"

    if faturamento_total > Decimal("81000") / Decimal("12"):
        regime = "Simples Nacional (ME)"
    elif faturamento_total > Decimal("2112"):
        regime = "MEI"
    else:
        regime = "CPF (Isento até 2.112/mês)"

    # 🔥 LUCRO
    lucro = faturamento_total - total_taxa_mp - total_comissao - imposto_futuro - total_investimento_premiacao

    # 🔥 USUARIO QUE MAIS COMPROU NUMEROS
    usuarios_qtd = {}

    for p in pagamentos:
        if p.get("status") != "approved":
            continue

        email = p.get("email_usuario")
        usuario = usuarios_map.get(email, {})
        nome = usuario.get("nome", "Desconhecido")
        vendedor = usuario.get("vendedor", "Desconhecido")

        lista = p.get("lista_numeros", [])

        if isinstance(lista, str):
            try:
                lista = json.loads(lista)
            except:
                lista = lista.replace("[", "").replace("]", "").replace("'", "")
                lista = [x.strip() for x in lista.split(",") if x.strip()]

        qtd = len(lista) if isinstance(lista, list) else 0

        if email not in usuarios_qtd:
            usuarios_qtd[email] = {
                "nome": nome,
                "vendedor": vendedor,
                "quantidade": 0,
            }

        usuarios_qtd[email]["quantidade"] += qtd

    top_usuario = None

    if usuarios_qtd:
        top_usuario = max(usuarios_qtd.values(), key=lambda x: x["quantidade"])

    resumo = {
        "usuarios": quantidade_usuarios,
        "vendedores": quantidade_vendedores,
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "faturamento": float(total_pagamentos_approved),
        "investimento_premiacao": float(total_investimento_premiacao),
        "total_comissao": float(total_comissao),
        "taxa_mp_total": float(total_taxa_mp),
        "lucro": float(lucro),
        "projetos": projetos_formatados,
        "numeros_aprovados": len(numeros_aprovados),
        "lista_numeros_aprovados": numeros_aprovados,
        "vendedores": vendedores_formatado,
        "faturamento_mensal": faturamento_por_mes,
        "fiscal": {
            "cfop_produto": cfop_produto,
            "codigo_servico": codigo_servico,
            "aliquota_futura": float(aliquota_futura * 100),
            "aliquota_transicao_2026": float(aliquota_transicao * 100),
            "imposto_futuro": float(imposto_futuro),
            "imposto_transicao": float(imposto_transicao),
            "regime": regime
        }
    }

    return render_template(
        "graficos/grafico_geral_sistema.html",
        usuarios=usuarios,
        vendedores=vendedores,
        resumo=resumo,
        projetos=projetos,
        top_usuario=top_usuario
    )
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
# PLANILHA USUARIO
@app.route("/players/register/acesso/afiliados/4f8c2d7e1a9b6f3d5c8e2a7d1f4b9c6e3a8d5f2c7b1e9a4d6f3c8b2e7a5d1f9/<vendedor_id>", methods=["GET"])
def clientes_usuarios_cadastrados(vendedor_id=None):
    # ========================================
    # VENDEDOR LOGADO
    # ========================================
    vendedor = vendedores_collection.find_one({
        "_id": ObjectId(vendedor_id)
    })


    usuarios = list(users_collection.find())
    quantidade_usuarios = len(usuarios)

    # --- Ajusta cada usuário ---
    usuarios_formatados = []
    for u in usuarios:
        # Formatar CPF
        cpf = u.get("cpf", "")
        cpf_limpo = re.sub(r"\D", "", cpf)
        if len(cpf_limpo) == 11:
            cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        else:
            cpf_formatado = cpf

        # Formatar data
        data_banco = u.get("dt_nascimento", "")
        data_formatada = data_banco
        if data_banco and "-" in data_banco:
            partes = data_banco.split("-")
            if len(partes) == 3:
                data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"

        # Atualiza o dicionário do usuário
        u["cpf"] = cpf_formatado
        u["dt_nascimento"] = data_formatada
        usuarios_formatados.append(u)

    resumo = {
        "usuarios": quantidade_usuarios,
    }

    return render_template(
        "graficos/clientes_usuarios_cadastrados.html",
        usuarios=usuarios_formatados,
        vendedor_id=vendedor_id,
        resumo=resumo
    )
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
# BUSCAR DADOS USUARIOS
@app.route("/api/clientes")
def get_cliente_por_cpf():
    cpf_bruto = request.args.get("cpf")

    if not cpf_bruto:
        return jsonify({"error": "CPF não informado"}), 400

    # Remove qualquer caractere que não seja número
    cpf_limpo = "".join(filter(str.isdigit, cpf_bruto))

    if len(cpf_limpo) != 11:
        return jsonify({"error": "CPF deve conter 11 dígitos"}), 400

    # Busca usuário no banco pelo CPF limpo
    usuario = users_collection.find_one({"cpf": cpf_limpo})

    if not usuario:
        return jsonify([]), 404 # Retorna 404 se não achar

    # --- LÓGICA PARA FORMATAR CPF ---
    cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"

    # --- LÓGICA PARA INVERTER A DATA (AAAA-MM-DD para DD/MM/AAAA) ---
    data_banco = usuario.get("dt_nascimento", "")
    data_formatada = data_banco
    
    if data_banco and "-" in data_banco:
        partes = data_banco.split("-")
        if len(partes) == 3:
            # Inverte para o padrão brasileiro com barras
            data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"

    # Montagem do objeto de retorno
    cliente = {
        "id": str(usuario.get("_id")),
        "nome": usuario.get("nome", ""),
        "sobrenome": usuario.get("sobrenome", ""),
        "estado": usuario.get("estado", "São Paulo"),
        "dt_nascimento": data_formatada,
        "cpf": cpf_formatado,
        "email": usuario.get("email", ""),
        "chavePix": usuario.get("chave_pix", ""),
        "vendedor": usuario.get("vendedor", "")
    }

    return jsonify([cliente])
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------     
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
#DELETAR USUARIO
@app.route("/deletar-usuario", methods=["DELETE"])
def deletar_usuario_route():
    try:
        data = request.get_json()
        user_id = str(data.get("id", "")).strip()
        senha = data.get("senha")

        if senha != app.secret_key:
            return jsonify({"sucesso": False, "erro": "Senha inválida"}), 403

        if not ObjectId.is_valid(user_id):
            return jsonify({"sucesso": False, "erro": "ID inválido"}), 400

        result = users_collection.delete_one({"_id": ObjectId(user_id)})

        if result.deleted_count == 0:
            return jsonify({"sucesso": False, "erro": "Usuário não encontrado"}), 404

        return jsonify({"sucesso": True}), 200

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
#EDITAR  USUARIO
@app.route("/editar-usuario", methods=["PUT"])
def editar_usuario():
    try:
        data = request.get_json()
        user_id = str(data.get("id", "")).strip()
        senha = data.get("senha")

        # usa app.secret_key que já foi definido no seu app.py
        if senha != app.secret_key:
            return jsonify({"sucesso": False, "erro": "Senha inválida"}), 403

        if not ObjectId.is_valid(user_id):
            return jsonify({"sucesso": False, "erro": "ID inválido"}), 400


        ganhos = float(data.get("ganhos", 0))
        email = data.get("email", "").strip()
        chave_pix = data.get("chave_pix", "").strip()


        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "ganhos": ganhos,
                "email": email,
                "chave_pix": chave_pix
            }}
        )

        return jsonify({"sucesso": True})

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500      
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route('/api/usuarios-data')
def get_usuarios_data():

    pagamentos = pagamento_model.get_all_pagamentos() or []
    usuarios = list(users_collection.find())  # sua collection de usuários

    # Mapa: email -> nome
    mapa_usuarios = {}
    for u in usuarios:
        mapa_usuarios[u.get("email")] = u.get("nome", "Sem nome")

    resultado = {}

    for p in pagamentos:
        if p.get("status") != "approved":
            continue

        email = p.get("email_usuario")
        valor = float(p.get("amount", 0))

        nome = mapa_usuarios.get(email, "Desconhecido")

        if nome not in resultado:
            resultado[nome] = 0

        resultado[nome] += valor

    # Montar resposta
    data = {}
    for nome, total in resultado.items():
        data[nome] = {"approved": round(total, 2)}

    return jsonify(data)
#=============================================================================================================================================================================
#=============================================================================================================================================================================
# FATURAMENTO
#------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/营业额", methods=["GET"])
def faturamento():
    pagamentos = pagamento_model.get_all_pagamentos() or []
    total_faturamento = Decimal("0")

    # inicializa todos os meses com 0
    faturamento_por_mes = {
        "Jan": Decimal("0"), "Fev": Decimal("0"), "Mar": Decimal("0"),
        "Abr": Decimal("0"), "Mai": Decimal("0"), "Jun": Decimal("0"),
        "Jul": Decimal("0"), "Ago": Decimal("0"), "Set": Decimal("0"),
        "Out": Decimal("0"), "Nov": Decimal("0"), "Dez": Decimal("0")
    }

    meses_map = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr",
        5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    for p in pagamentos:
        valor = Decimal(str(p.get("valor", 0)))
        status = p.get("status")

        if status == "approved":
            total_faturamento += valor
            data_str = p.get("data_criacao")
            if data_str:
                try:
                    data = datetime.strptime(data_str, "%a, %d %b %Y %H:%M:%S GMT")
                    mes_nome = meses_map[data.month]
                    faturamento_por_mes[mes_nome] += valor
                except:
                    pass

    # garante que todos os meses estão presentes como float
    faturamento_por_mes = {k: float(v) for k, v in faturamento_por_mes.items()}

    resumo = {
        "faturamento": float(total_faturamento),
        "faturamento_mensal": faturamento_por_mes
    }

    return render_template("graficos/grafico_faturamento.html", resumo=resumo)
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
def get_pagamentos_aprovados():
    """
    Retorna lista de pagamentos com status 'approved' e valor 1,25
    """
    try:
        collection = db["pagamentos"]
        query = {"status": "approved", "valor": 1.25}
        cursor = collection.find(query, {"_id": 0, "data": 1, "valor": 1})
        return list(cursor)
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return []
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
@app.route("/dados")
def dados():
    pagamentos = get_pagamentos_aprovados()
    # Preparar dados para Chart.js
    labels = [p["data"] for p in pagamentos]
    valores = [p["valor"] for p in pagamentos]
    return jsonify({"labels": labels, "valores": valores})
#----------------------------------------------------------------------------------------------------------------------
#=============================================================================================================================================================================
#=============================================================================================================================================================================
#=============================================================================================================================================================================
#=============================================================================================================================================================================
# VENDAS E CONTROLE VENDEDORES
@app.route("/销售/vendedor", methods=["GET"])
def controle_vendas_vendedores():

    usuarios = list(users_collection.find())
    pagamentos = pagamento_model.get_all_pagamentos() or []

    usuarios_map = {u.get("email"): u for u in usuarios}

    vendedores = {}

    for p in pagamentos:

        valor = Decimal(str(p.get("valor", 0)))
        status = p.get("status")
        email = p.get("email_usuario")

        usuario = usuarios_map.get(email, {})
        vendedor = usuario.get("vendedor", "sem_vendedor")

        if vendedor not in vendedores:
            vendedores[vendedor] = {
                "pending": Decimal("0"),
                "approved": Decimal("0"),
                "cancelled": Decimal("0"),
                "numeros": 0
            }

        if status == "pending":
            vendedores[vendedor]["pending"] += valor

        elif status == "approved":
            vendedores[vendedor]["approved"] += valor

            lista = p.get("lista_numeros", [])

            if isinstance(lista, str):
                try:
                    lista = json.loads(lista)
                except:
                    lista = []

            if isinstance(lista, list):
                vendedores[vendedor]["numeros"] += len(lista)

        elif status == "cancelled":
            vendedores[vendedor]["cancelled"] += valor


    vendedores_formatado = {
        v: {
            "pending": float(d["pending"]),
            "approved": float(d["approved"]),
            "cancelled": float(d["cancelled"]),
            "numeros": d["numeros"]
        } for v, d in vendedores.items()
    }

    resumo = {
        "vendedores": vendedores_formatado,
    }

    return render_template("graficos/grafico_vendas.html", vendedores=vendedores_formatado, resumo=resumo)
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
def get_pagamento_by_id(self, id):
    return self.collection.find_one({"_id": id})
#=============================================================================================================================================================================
#=============================================================================================================================================================================
#=============================================================================================================================================================================
#=============================================================================================================================================================================
# GERADOR DE BILHETES
W, H = 900, 450

from datetime import datetime

@app.route("/gerar-bilhete/<usuario_id>", methods=["POST"])
def gerar_bilhete(usuario_id):
    data = request.json
    numero_bilhete = f"Nº {data['numero']}"


    # 🔥 BUSCA PROJETO
    projeto_id = data.get("projeto_id")

    if projeto_id:
        projeto = projetos_collection.find_one({"_id": ObjectId(projeto_id)})
    else:
        projeto = projetos_collection.find_one()

    evento = projeto.get("nome_projeto", "N/A")
    descricao = f"Prêmio: R$ {projeto.get('valor_injetado_premiacao', 0)}, via Pix"
    valor_unidade = projeto.get('valor_unidade', 1.25)

    # 🔥 FORMATAÇÃO SEGURA DA DATA
    data_raw = projeto.get("dt_sorteio", "N/A")

    if isinstance(data_raw, datetime):
        data_sorteio = data_raw.strftime("%d/%m/%Y")
    elif isinstance(data_raw, str):
        try:
            data_sorteio = datetime.fromisoformat(data_raw).strftime("%d/%m/%Y")
        except:
            data_sorteio = data_raw
    else:
        data_sorteio = "N/A"

    nome = data["nome"]
    email = data["email"]
    cpf = data["cpf"]
    cpf_mask = f"{cpf[:3]}.***.***-{cpf[9:11]}"

    link_qrcode = f"https://ferrari-tech.onrender.com/sala_online/{usuario_id}"
    caminho_logo = "static/img/marca.png"

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        draw.line([(0, y), (W, y)], fill=(200 - y//5, 20, 20))

    margin = 30
    cx1, cy1 = margin, margin
    cx2, cy2 = W - margin, H - margin

    cw, ch = cx2 - cx1, cy2 - cy1

    card = Image.new("RGB", (cw, ch), "white")
    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 100)).filter(ImageFilter.GaussianBlur(10))

    img.paste(shadow, (cx1+4, cy1+4), shadow)
    img.paste(card, (cx1, cy1))

    draw = ImageDraw.Draw(img)

    try:
        f_titulo = ImageFont.truetype("static/fonts/NK57 Monospace Cd Bd It.otf", 36)
        f_texto  = ImageFont.truetype("static/fonts/NK57 Monospace Cd Bd It.otf", 24)
        f_label  = ImageFont.truetype("static/fonts/NK57 Monospace Cd Bd It.otf", 20)
        f_num    = ImageFont.truetype("static/fonts/NK57 Monospace Cd Bd It.otf", 28)
    except:
        f_titulo = f_texto = f_label = f_num = ImageFont.load_default()

    if os.path.exists(caminho_logo):
        logo = Image.open(caminho_logo).convert("RGBA")
        logo.thumbnail((100, 60))
        img.paste(logo, (cx1 + 20, cy1 + 20), logo)

    draw.text((cx1 + 140, cy1 + 25), evento, font=f_titulo, fill=(0, 0, 0))
    draw.text((cx1 + 140, cy1 + 70), descricao, font=f_texto, fill=(80, 80, 80))
    draw.text((cx1 + 140, cy1 + 100), data_sorteio, font=f_texto, fill=(80, 80, 80))
    draw.text((cx1 + 140, cy1 + 130), valor_unidade, font=f_label, fill=(180, 0, 0))

    left_x = cx1 + 20
    right_x = cx2 - 220

    start_y = cy1 + 170
    gap = 40

    def linha(label, valor, y):
        draw.text((left_x, y), label, font=f_label, fill=(150, 0, 0))
        draw.text((left_x + 140, y), valor, font=f_texto, fill=(0, 0, 0))

    linha("Nome:", nome, start_y)
    linha("Email:", email, start_y + gap)
    linha("CPF:", cpf_mask, start_y + gap*2)

    draw.line((left_x, start_y - 15, right_x - 20, start_y - 15), fill=(200,0,0), width=2)

    draw.rectangle([left_x, cy2 - 60, left_x + 200, cy2 - 20], fill=(200, 0, 0))
    draw.text((left_x + 10, cy2 - 55), numero_bilhete, fill="white", font=f_num)

    qr = qrcode.make(link_qrcode).convert("RGB").resize((150,150))

    qr_box = 180
    qr_bg = Image.new("RGB", (qr_box, qr_box), "white")
    qr_draw = ImageDraw.Draw(qr_bg)

    qr_draw.rectangle([0,0,qr_box-1,qr_box-1], outline=(200,0,0), width=3)
    qr_bg.paste(qr, (15,15))

    qr_y = cy1 + (ch // 2) - (qr_box // 2)
    img.paste(qr_bg, (right_x, qr_y))

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # 🔥 upload protegido (não trava outras rotas)
    try:
        upload_result = cloudinary.uploader.upload(
            buffer,
            folder="rifas",
            public_id=f"bilhete_{uuid.uuid4()}",
            resource_type="image"
        )
        url_imagem = upload_result["secure_url"]
    except Exception as e:
        print("ERRO CLOUDINARY:", e)
        url_imagem = ""

    # 🔥 lista LOCAL (não global)
    lista_urls_img_bilhetes = [url_imagem] if url_imagem else []
    numero_bilhete = numero_bilhete.replace("Nº ", "").strip()

    documento = criar_documento_bilhete(
        bilhete_id=str(uuid.uuid4()),  # 👈 evita conflito global
        cpf=cpf,
        nome_user=nome,
        email_user=email,
        valor_unidade=valor_unidade,
        lista_numeros=[numero_bilhete],
        lista_urls_img_bilhetes=lista_urls_img_bilhetes
    )

    # 🔥 salvar protegido (não quebra fluxo)
    try:
        BilheteModel().create_bilhete(documento)
    except Exception as e:
        print("ERRO BANCO:", e)

    return jsonify({
        "img": url_imagem
    })
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
@app.route("/cancelar-bilhetes_e_deletar_mongo_cloudinart", methods=["DELETE"])
def deletar_bilhetes():

    try:

        data = request.json
        urls_para_limpar = data.get("urls", [])

        if not urls_para_limpar:
            return jsonify({"sucesso": True, "mensagem": "Nada para deletar"})

        public_ids_para_deletar = []

        for url in urls_para_limpar:
            if url and "http" in url:
                partes = url.split('/')
                p_id = f"{partes[-2]}/{partes[-1].split('.')[0]}"
                public_ids_para_deletar.append(p_id)

        if public_ids_para_deletar:
            import cloudinary.api
            cloudinary.api.delete_resources(public_ids_para_deletar, invalidate=True)

        # 🔥 USA O QUE VOCÊ JÁ TEM IMPORTADO NO PROJETO
        db_model = BilheteModel()

        db_model.collection.delete_many({
            "lista_urls_img_bilhetes": {
                "$in": urls_para_limpar
            }
        })

        return jsonify({"sucesso": True})

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"sucesso": False, "erro": str(e)}), 500
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
# Aqui vai retornar a url 
@app.route("/rifas/<path:filename>")
def servir_imagem(filename):
    return send_file(f"rifas/{filename}")
#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================

#=============================================================================================================================================
#=============================================================================================================================================

#================================================================================================================================
#================================================================================================================================

# -LISTAR TODOS OS USUARIOS
#================================================================================================================================
#================================================================================================================================
@app.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        usuarios_cursor = users_collection.find()

        usuarios = []
        for u in usuarios_cursor:
            usuarios.append({
                "_id": str(u.get("_id")),
                "nome": u.get("nome", ""),
                "sobrenome": u.get("sobrenome", ""),
                "cpf": u.get("cpf", ""),
                "email": u.get("email", ""),
                "dt_nascimento": u.get("dt_nascimento", ""),
                "ganhos": u.get("ganhos", ""),
                "saques": u.get("saques", ""),
                "vendedor": u.get("vendedor", ""),
                "chave_pix": u.get("chave_pix", ""),
                "ip_usuario": u.get("ip_usuario", ""),
                "aparelho": u.get("aparelho", ""),
                "navegador": u.get("navegador", ""),
                "mensagem_saques": u.get("mensagem_saques", ""),
                "status": u.get("status", ""),
                "bloqueado": u.get("bloqueado", ""),
                "foto_perfil": u.get("foto_perfil", ""),
                "vendedor_id": u.get("vendedor_id", "")

                
            })

        return jsonify({"status": "sucesso", "usuarios": usuarios}), 200

    except Exception as e:
        print("ERRO /usuarios:", e)  # 👈 MUITO IMPORTANTE PRA DEBUG
        return jsonify({"status": "erro", "mensagem": str(e)}), 500


from bson import ObjectId

@app.route("/usuario/<usuario_id>", methods=["GET"])
def listar_usuarioId(usuario_id):
    try:
        usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})

        if not usuario:
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário não encontrado"
            }), 404

        usuario_formatado = {
            "_id": str(usuario.get("_id")),
            "nome": usuario.get("nome", ""),
            "sobrenome": usuario.get("sobrenome", ""),
            "cpf": usuario.get("cpf", ""),
            "email": usuario.get("email", ""),
            "dt_nascimento": usuario.get("dt_nascimento", ""),
            "ganhos": usuario.get("ganhos", ""),
            "saques": usuario.get("saques", ""),
            "vendedor": usuario.get("vendedor", ""),
            "chave_pix": usuario.get("chave_pix", "")
        }

        return jsonify({
            "status": "sucesso",
            "usuario": usuario_formatado
        }), 200

    except Exception as e:
        print("ERRO /usuario:", e)

        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 500
#--------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# RESETAR
@app.route("/resetar_banco", methods=["GET"])
def resetar_banco():
    try:
        confirm = request.args.get("confirm")

        if confirm != "SIM":
            return jsonify({"erro": "Use ?confirm=SIM"}), 400

        users_collection.delete_many({})
        

        return jsonify({
            "status": "sucesso",
            "mensagem": "Dados apagados"
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# rota sucesso 
@app.route("/success")
def pagamento_sucesso():

    return render_template("aprovado.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# rora recusado
@app.route("/recusado")
def pagamento_recusado():
    return render_template("recusado.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# pagamento pendente
@app.route("/pendente")
def pagamento_pending():
    return render_template("pendente.html")
# SISTEMA INTEGRAÇAO MERCADO PAGO 
# PAGAMENTO QRCODE PIX E COLA => "FOI TESTADO ESTA EM PRODUÇAO (OK)"
# PAGAMENTO PREFERENCE MERCADO PAGO => "FOI TESTADO ESTA EM PRODUÇAO (OK)
# WEBHOOK => "FOI TESTADO ESTA EM PRODUÇAO (OK)
# BACKS_URL DIRECIONAMENTOS
#============================================================================================
#============================================================================================
#============================================================================================
MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN")              
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)  

#=============================================================================================
# -PAGAMENTO VIA SOMENTE PIX QRCODE => funçoes - GERAR QRCODE E PIX COLA SALVA PAGAMENTO E
# ATUALIZA PAYMENT_ID NUMERO DO USUARIO "TESTADO (OK)"
#=============================================================================================

@app.route("/payment_qrcode_pix/pagamento_pix/<usuario_id>")
def pagamento_pix(usuario_id):

    import json
    from datetime import datetime, timedelta

    lista_numeros = request.args.get("lista_numeros")

    if lista_numeros:
        lista_numeros = json.loads(lista_numeros)
    else:
        lista_numeros = []

    usuario_id = usuario_id or request.args.get("usuario_id")

    if not usuario_id:
        return jsonify({"erro": "usuario_id não informado"}), 400

    nome = request.args.get("nome") or ""
    sobrenome = request.args.get("sobrenome") or ""
    cpf = request.args.get("cpf") or ""
    email = request.args.get("email") or ""

    quantidade = int(request.args.get("quantidade") or 0)

    valor_total = round(quantidade * 0.60, 2)

    taxa_mp = round(valor_total * 0.0099, 2)

    # EXPIRA EM 15 MINUTOS
    expiration_date = (
        datetime.utcnow() + timedelta(minutes=15)
    ).strftime('%Y-%m-%dT%H:%M:%S.000-00:00')

    payment_data = {

        "transaction_amount": float(valor_total),

        "description": "Servico Digital",

        "payment_method_id": "pix",

        # EXPIRACAO PIX
        "date_of_expiration": expiration_date,

        "payer": {
            "email": email,
            "first_name": nome,
            "last_name": sobrenome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },

        "external_reference": email,

        "notification_url": notification_url,

        "statement_descriptor": "FerrariTech"
    }

    try:

        response = sdk.payment().create(payment_data)

        mp = response.get("response", {})

        if "id" not in mp:
            return f"ERRO MP: {mp}", 500

        payment_id = str(mp["id"])

        status = mp.get("status", "pending")

        tx = mp.get("point_of_interaction", {}).get("transaction_data", {})

        qr_base64 = tx.get("qr_code_base64")

        qr_code = tx.get("qr_code")

        if not qr_base64 or not qr_code:
            return f"ERRO QR: {tx}", 500

        image_bytes = base64.b64decode(qr_base64)

        image_file = BytesIO(image_bytes)

        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="qrcodes_pix",
            public_id=f"qr_{payment_id}"
        )

        qr_image_url = upload_result.get("secure_url")

        documento = criar_documento_pagamento(

            payment_id=payment_id,

            status=status,

            payment_method_id="Pix",

            valor=valor_total,

            cpf=cpf,

            email_user=email,

            lista_numeros=lista_numeros,

            qr_code=qr_code,

            qr_image_url=qr_image_url,

            taxa_mp=taxa_mp

        )

        try:
            PagamentoModel().create_pagamento(documento)

        except Exception as e:
            print("ERRO AO SALVAR:", e)

        # ATUALIZA BILHETES COM PAYMENT_ID
        try:

            bilhetes_collection.update_many(

                {
                    "cpf": cpf,
                    "status": "pending",
                    "payment_id": "aguardando gerar pagamento"
                },

                {
                    "$set": {
                        "payment_id": payment_id,
                        "expiration_date": expiration_date
                    }
                }

            )

        except Exception as e:
            print("ERRO AO ATUALIZAR BILHETES:", e)

        return render_template(

            "finalize.html",

            qrcode=qr_image_url,

            valor=f"R$ {valor_total:.2f}",

            qr_code_cola=qr_code,

            status=status,

            payment_id=payment_id,

            cpf=cpf,

            expiration_date=expiration_date

        )

    except Exception as e:

        print("ERRO GERAL:", e)

        return f"ERRO GERAL: {str(e)}", 500
#=============================================================================================
#----------------------------------------------------------------------------------------------
#=============================================================================================
#=============================================================================================
#=============================================================================================
@app.route('/aguardando_pagamento/<pagamento_id>', methods=['GET'])
def aguardando_confirmacao(pagamento_id):

    pagamento = pagamento_model.get_pagamento(pagamento_id)

    if not pagamento:
        return "Pagamento não encontrado", 404

    cpf = pagamento.get("cpf", "")

    # BUSCA NA COLLECTION CERTA: users_collection
    usuario = None
    if cpf:
        usuario = users_collection.find_one({"cpf": cpf})

    if not usuario:
        return "Usuário não encontrado", 404

    usuario_id = str(usuario["_id"])

    qr_image_url = (
        pagamento.get("qrcode") or
        pagamento.get("qr_image_url") or
        pagamento.get("qr_code_base64")
    )

    qr_code_cola = (
        pagamento.get("qr_code_cola") or
        pagamento.get("qr_code") or
        pagamento.get("copia_cola")
    )

    valor = pagamento.get("valor", 0)
    status = pagamento.get("status", "aguardando pagamento")

    return render_template(
        "finalize1.html",
        qrcode=qr_image_url,
        valor=f"R$ {float(valor):.2f}",
        qr_code_cola=qr_code_cola,
        status=status,
        payment_id=pagamento_id,
        cpf=cpf,
        usuario_id=usuario_id
    )

#=============================================================================================




@app.route('/sync_bilhetes_aprovados', methods=['POST'])
def sync_bilhetes_aprovados():
    try:
        dados = request.get_json()
        payment_id = dados.get('payment_id')

        if not payment_id:
            print("ERRO: NÃO VEIO O ID")
            return {"ok": False, "erro": "Falta ID"}, 400

        print(f"TENTANDO ATUALIZAR BILHETES COM O ID: {payment_id}")

        # BUSCA DIRETO NA COLEÇÃO DE BILHETES, NÃO IMPORTA O PAGAMENTO
        resultado = bilhete_model.collection.update_many(
            {"payment_id": payment_id}, # BUSCA EXATAMENTE O NÚMERO
            {"$set": {
                "status": "approved",
                "data_atualizacao": datetime.now(timezone.utc)
            }}
        )

        print(f"QUANTIDADE ATUALIZADA: {resultado.modified_count}")

        return {
            "ok": True,
            "atualizados": resultado.modified_count
        }

    except Exception as e:
        print(f"ERRO NO SERVER: {str(e)}")
        return {"ok": False, "erro": str(e)}, 500


#=============================================================================================
#=============================================================================================
#=============================================================================================
# -PAGAMENTO PREFERENCE MERCADO PAGO => funçoes - GERAR QRCODE E PIX COLA SALVA PAGAMENTO E
# ATUALIZA PAYMENT_ID NUMERO DO USUARIO "TESTADO (OK)"" 
#=============================================================================================    
# PAGAMENTO MERCADO PAGO 

@app.route("/compra/preference/pagamento_pix/<usuario_id>")
def pagamento_preference(usuario_id):

    import json
    import uuid
    from datetime import datetime, timedelta

    lista_numeros = request.args.get("lista_numeros")

    if lista_numeros:
        lista_numeros = json.loads(lista_numeros)
    else:
        lista_numeros = []

    usuario_id = usuario_id or request.args.get("usuario_id")

    if not usuario_id:
        return jsonify({"erro": "usuario_id não informado"}), 400

    nome = request.args.get("nome") or ""
    sobrenome = request.args.get("sobrenome") or ""
    cpf = request.args.get("cpf") or ""
    email = request.args.get("email") or ""

    quantidade = max(1, int(request.args.get("quantidade") or 1))

    valor_unitario = 0.60
    valor_total = quantidade * valor_unitario

    # EXPIRA EM 15 MINUTOS
    expiration_date = (
        datetime.utcnow() + timedelta(minutes=15)
    ).strftime('%Y-%m-%dT%H:%M:%S.000-00:00')

    payment_data = {

        "items": [
            {
                "id": str(uuid.uuid4()),
                "title": "Servico Digital",
                "description": "Servico digital",
                "quantity": quantidade,
                "currency_id": "BRL",
                "unit_price": valor_unitario,
                "category_id": "services"
            }
        ],

        # EXPIRACAO
        "expires": True,

        "date_of_expiration": expiration_date,

        "payer": {
            "email": email,
            "first_name": nome,
            "last_name": sobrenome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },

        # IDENTIFICADOR
        "external_reference": cpf,

        "statement_descriptor": "FERRARITECH",

        "back_urls": {
            "success": "https://ferrari-tech.onrender.com/success",
            "failure": "https://ferrari-tech.onrender.com/recusado"
        },

        "auto_return": "approved",

        "notification_url": notification_url
    }

    result = sdk.preference().create(payment_data)

    mp = result.get("response", {})

    if "id" not in mp:
        return f"ERRO NO MERCADO PAGO:<br><br>{mp}", 500

    preference_id = mp["id"]

    status = "pending"

    documento = criar_documento_pagamento(

        payment_id=cpf,

        status=status,

        valor=valor_total,

        cpf=cpf,

        email_user=email,

        payment_method_id="preference",

        lista_numeros=lista_numeros

    )

    PagamentoModel().create_pagamento(documento)

    try:

        bilhetes_collection.update_many(

            {
                "cpf": cpf,
                "status": "pending",
                "payment_id": "aguardando gerar pagamento"
            },

            {
                "$set": {
                    "payment_id": cpf,
                    "preference_id": preference_id,
                    "expiration_date": expiration_date
                }
            }

        )

    except Exception as e:

        print("ERRO AO ATUALIZAR BILHETES:", e)

    link_pagamento = mp.get("init_point", "")

    return redirect(link_pagamento)



#==============================================================================================
# WEBHOOK MECADO PAGO => RECEBE NOTIFIÇAO MERCADO PAGO E DISPARA SOCKET 
# # AO CAPTAR PAGAMENTO VIA QRCODE ATUALIZA STATUS PAGAMENTO  "TESTADO (OK)"
#==============================================================================================
@app.route("/notificacoes", methods=["POST"])
def handle_webhook():
    data = request.json

    if not data:
        return "", 200

    payment_id = data.get("data", {}).get("id") or data.get("id")
    if not payment_id:
        return "", 200

    payment_details = get_payment_details(payment_id)
    if not payment_details:
        return "", 200

    status = payment_details.get("status")
    usuario_id = payment_details.get("external_reference")
    valor_pago = float(payment_details.get("transaction_amount", 0))

    # Emite atualização via socket
    socketio.emit(
        "payment_update",
        {
            "status": status,
            "payment_id": str(payment_id),
            "usuario_id": usuario_id
        },
        room=str(payment_id)
    )

    # Atualiza pagamento
    pagamento_model.update_pagamento(payment_id, {"status": status})
  
    return "", 200
#-----------------------------------------------------------------------------------------------  
def get_payment_details(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else None  
#-----------------------------------------------------------------------------------------------
@socketio.on("join_payment")
def join_payment_room(data):
    join_room(data["payment_id"]) 
#-----------------------------------------------------------------------------------------------
# =======================================================
# =======================================================
# READ (1)
# =======================================================
@app.route('/pagamentos/completo/<pagamento_id>', methods=['GET'])
def get_pagamento(pagamento_id):
    pagamentos = pagamento_model.get_pagamento(pagamento_id)

    if pagamentos:
        return jsonify(pagamentos), 200
    else:
        return jsonify({"erro": "Pagamento não encontrado"}), 404
# =======================================================
# READ (2)
# =======================================================
@app.route('/pagamentos/<payment_id>', methods=['GET'])
def verificar_status_pagamento(payment_id):
    pagamento = pagamento_model.get_pagamento_by_id(payment_id)

    if pagamento:
        # Forçamos a conversão para string e pegamos o valor real
        # Se for um objeto, usamos pagamento.status. Se dicionário, pagamento.get
        status_raw = getattr(pagamento, 'status', None) or pagamento.get('status')
        return jsonify({"status": str(status_raw).lower().strip()}), 200
    
    return jsonify({"status": "not_found"}), 404
      
# =======================================================
# READ (3)
# =======================================================
@app.route("/支付列表")
def listar_pagamentos():
    pagamentos = pagamento_model.get_all_pagamentos() or []
    for n in pagamentos:
        n["_id"] = str(n["_id"])

    saques = get_all_saques() or []
    for s in saques:
        s["_id"] = str(s["_id"])
   

    return jsonify({
        "pagamentos": pagamentos,
        "saques": saques
    })

# =======================================================
# LISTAR BILHETES
# =======================================================
@app.route("/cupons")
def listar_bilhetes():

    bilhetes = bilhete_model.get_all_bilhetes()
     # Converte ObjectId para string
    for n in bilhetes:
        n["_id"] = str(n["_id"])


    return jsonify({
        "bilhetes": bilhetes, 
    })
# ================================================
# CREATE
# ================================================
@app.route('/pagamentos', methods=['POST'])
def criar_pagamento():
    try:
        data = request.json

        payment_id = str(uuid.uuid4())

        doc = criar_documento_pagamento(
            payment_id=payment_id,
            status=data.get("status", "pendente"),
            valor=data.get("valor"),
            usuario_id=data.get("usuario_id"),
            email_user=data.get("email_usuario")
        )

        result = pagamento_model.create_pagamento(doc)

        if result:
            return jsonify({"msg": "Pagamento criado", "id": result}), 201
        else:
            return jsonify({"erro": "Erro ao criar pagamento"}), 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
# =========================================================
# UPDATE
# =========================================================
@app.route('/pagamentos/<pagamento_id>', methods=['PUT'])
def update_pagamento(pagamento_id):
    try:
        data = request.json

        updated = pagamento_model.update_pagamento(pagamento_id, data)

        if updated:
            return jsonify({"msg": "Pagamento atualizado"}), 200
        else:
            return jsonify({"erro": "Nada foi atualizado"}), 400

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# =========================
# DELETE
# =========================
@app.route('/pagamentos/<pagamento_id>', methods=['DELETE'])
def delete_pagamento(pagamento_id):
    deleted = pagamento_model.delete_pagamento(pagamento_id)

    if deleted:
        return jsonify({"msg": "Pagamento deletado"}), 200
    else:
        return jsonify({"erro": "Pagamento não encontrado"}), 404

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# REGISTRAR VENDEDORES
@app.route("/registrar/vendedores", methods=["POST"])
def registrar_vendedor():
    try:
        data = request.get_json(force=True)
        print("CHEGOU NO BACK:", data)

        cpf = data.get("cpf", "")
        dt_nascimento = data.get("dt_nascimento", "")

        # --- VALIDAÇÕES ---
        if not validar_cpf(cpf):
            return jsonify({
                "status": "erro",
                "mensagem": "CPF inválido."
            }), 400

        if not validar_maioridade(dt_nascimento):
            return jsonify({
                "status": "erro",
                "mensagem": "Usuário deve ser maior de 18 anos."
            }), 400

        # =========================
        # IP
        # =========================
        ip_usuario = request.headers.get("X-Forwarded-For", request.remote_addr)

        # =========================
        # USER AGENT
        # =========================
        user_agent_string = request.headers.get("User-Agent", "")
        user_agent = parse(user_agent_string)
        ua = user_agent_string.lower()

        # =========================
        # DETECÇÃO DE APARELHO
        # =========================
        aparelho = "Desconhecido"

        if "sm-a356" in ua:
            aparelho = "Samsung Galaxy A35"
        elif "sm-a346" in ua:
            aparelho = "Samsung Galaxy A34"
        elif "sm-a546" in ua:
            aparelho = "Samsung Galaxy A54"
        elif "sm-s918" in ua:
            aparelho = "Samsung Galaxy S23 Ultra"
        elif "sm-s926" in ua:
            aparelho = "Samsung Galaxy S24+"
        elif "sm-g990" in ua:
            aparelho = "Samsung Galaxy S21 FE"
        elif "sm-" in ua:
            aparelho = "Samsung"
        elif "2201117tg" in ua:
            aparelho = "Xiaomi Redmi Note 11"
        elif "22101316g" in ua:
            aparelho = "Xiaomi Redmi Note 12"
        elif "2312draf3" in ua:
            aparelho = "Xiaomi Redmi Note 13"
        elif "redmi" in ua or "xiaomi" in ua:
            aparelho = "Xiaomi"
        elif "moto g54" in ua:
            aparelho = "Motorola Moto G54"
        elif "moto g84" in ua:
            aparelho = "Motorola Moto G84"
        elif "moto" in ua:
            aparelho = "Motorola"
        elif "iphone" in ua:
            aparelho = "iPhone"
        elif "ipad" in ua:
            aparelho = "iPad"
        elif "huawei" in ua:
            aparelho = "Huawei"
        elif "asus" in ua:
            aparelho = "Asus"
        elif "lg-" in ua:
            aparelho = "LG"
        elif "realme" in ua:
            aparelho = "Realme"
        elif "oppo" in ua:
            aparelho = "Oppo"
        elif "vivo" in ua:
            aparelho = "Vivo"
        elif "nokia" in ua:
            aparelho = "Nokia"
        elif "windows nt" in ua:
            aparelho = "PC Windows"
        elif "macintosh" in ua or "mac os" in ua:
            aparelho = "MacBook / iMac"
        elif "linux" in ua and "android" not in ua:
            aparelho = "PC Linux"
        else:
            aparelho = f"{user_agent.device.family} | {user_agent.os.family}"

        # =========================
        # NAVEGADOR
        # =========================
        navegador = user_agent.browser.family

        # =========================
        # LOCALIZAÇÃO (Tratando Lat/Lng enviadas do Front)
        # =========================
        lat = data.get("latitude")
        lng = data.get("longitude")
        
        if lat and lng:
            localizacao = f"Lat: {lat}, Lng: {lng}"
        else:
            localizacao = "Não autorizada / Não capturada"

        # Criando o vendedor com a variável localizacao preenchida
        vendedor = criar_vendedor(
            data.get("nome", ""),
            data.get("sobrenome", ""),
            data.get("cpf", ""),
            data.get("dt_nascimento", ""),
            data.get("email", ""),
            data.get("chave_pix", ""),
            data.get("comissao", "30%"),
            ip_usuario,
            aparelho,
            localizacao, # <--- Agora está definida!
            navegador
        )

        return jsonify({"status": "sucesso", "vendedor": vendedor}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route("/termos_contrato")
def politica_uso():
    return render_template("graficos/eventos/Admin/termo_admin.html")   

@app.route("/galeria/acesso/afiliados/4f8c2d7e1a9b6f3d5c8e2a7d1f4b9c6e3a8d5f2c7b1e9a4d6f3c8b2e7a5d1f9/<vendedor_id>")
def galeria(vendedor_id=None):
    return render_template("graficos/eventos/galeria.html", vendedor_id=vendedor_id)

@app.route("/black/acesso/afiliados/4f8c2d7e1a9b6f3d5c8e2a7d1f4b9c6e3a8d5f2c7b1e9a4d6f3c8b2e7a5d1f9/<vendedor_id>")
def roleta_black_jack(vendedor_id=None):
    return render_template("graficos/eventos/roleta_black_jack.html", vendedor_id=vendedor_id)
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# 🔐 LOGIN VENDEDORES
@app.route("/login/vendedores", methods=["POST"])
def login_vendedor():
    try:
        data = request.json

        cpf = str(data["cpf"]).strip()

        vendedor = vendedores_collection.find_one({"cpf": cpf})

        if not vendedor:
            return jsonify({
                "status": "erro",
                "mensagem": "CPF não encontrado"
            }), 404

        vendedores_collection.update_one(
            {"cpf": cpf},
            {
                "$set": {
                    "status": "online"
                }
            }
        )

        return jsonify({
            "status": "sucesso",
            "vendedor_id": str(vendedor["_id"])
        }), 200

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400


# LOGOUT VENDEDOR
@app.route("/logout/vendedor", methods=["POST"])
def logout_vendedor():
    try:

        data = request.json
        vendedor_id = data["vendedor_id"]

        vendedores_collection.update_one(
            {"_id": ObjectId(vendedor_id)},
            {
                "$set": {
                    "status": ["visto por último"],
                    "ultima_atividade": datetime.utcnow()
                }
            }
        )

        return jsonify({
            "status": "sucesso"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "erro",
            "mensagem": str(e)
        }), 400        
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# LISTAR TODOS VENDEDORES
@app.route("/listar/vendedores", methods=["GET"])
def listar_vendedor():
    try:
        vendedores_cursor = vendedores_collection.find()
        vendedores = []
        for u in vendedores_cursor:
            vendedores.append({
                "_id": str(u.get("_id")),
                "nome": u.get("nome", ""),
                "sobrenome": u.get("sobrenome", ""),
                "cpf": u.get("cpf", ""),
                "email": u.get("email", ""),
                "dt_nascimento": u.get("dt_nascimento", ""),
                "chave_pix": u.get("chave_pix", ""),
                "bloqueado": u.get("bloqueado", ""),
                "mensagem_usuarios": u.get("mensagem_usuarios", ""),
                "ip_usuario": u.get("ip_usuario", ""),
                "aparelho": u.get("aparelho", ""),
                "navegador": u.get("navegador", ""),
                "localizacao": u.get("localizacao", ""),
                "status": u.get("status", "")
            })
        return jsonify({"status": "sucesso", "vendedores": vendedores}), 200
    except Exception as e:
        print("ERRO /vendedores:", e)  
        return jsonify({"status": "erro", "mensagem": str(e)}), 500        
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------   
# PLANILHA VENDEDORES
@app.route("/afiliados/register/acesso/afiliados/4f8c2d7e1a9b6f3d5c8e2a7d1f4b9c6e3a8d5f2c7b1e9a4d6f3c8b2e7a5d1f9/<vendedor_id>", methods=["GET"])
def vendedores_usuarios_cadastrados(vendedor_id=None):
    # ========================================
    # VENDEDOR LOGADO
    # ========================================
    vendedor = vendedores_collection.find_one({
        "_id": ObjectId(vendedor_id)
    })    
    vendedores = list(vendedores_collection.find())

    quantidade_vendedores = len(vendedores)
    vendedores_vendas = {}

    resumo = {
        "vendedores": quantidade_vendedores,
    }

    return render_template(
        "graficos/vendedores_cadastrados.html",
        vendedores=vendedores,
        resumo=resumo
    )    
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# BUSCAR DADOS VENDEDORES
@app.route("/api/vendedores")
def get_vendedor_por_cpf():
    cpf_bruto = request.args.get("cpf")

    if not cpf_bruto:
        return jsonify({"error": "CPF não informado"}), 400

    cpf_limpo = "".join(filter(str.isdigit, cpf_bruto))

    if len(cpf_limpo) == 11:
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    else:
        return jsonify({"error": "CPF deve conter 11 dígitos"}), 400

    vendedor = vendedores_collection.find_one({"cpf": cpf_limpo})

    if not vendedor:
        return jsonify([]), 200

    # --- LÓGICA PARA INVERTER A DATA ---
    data_banco = vendedor.get("dt_nascimento", "") # Ex: "2026-04-21"
    data_formatada = data_banco
    
    if data_banco and "-" in data_banco:
        partes = data_banco.split("-") # Quebra em ['2026', '04', '21']
        if len(partes) == 3:
            # Reorganiza para ['21', '04', '2026'] e junta com "-"
            data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]}"
    # -----------------------------------

    return jsonify([{
        "id": str(vendedor.get("_id")),
        "nome": vendedor.get("nome", ""),
        "sobrenome": vendedor.get("sobrenome", ""),
        "dt_nascimento": data_formatada, # Data agora sai 21-04-2026
        "cpf": cpf_formatado,
        "email": vendedor.get("email", ""),
        "chavePix": vendedor.get("chave_pix", "")
    }])
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#DELETAR VENDEDORES
@app.route("/deletar-vendedor", methods=["DELETE"])
def deletar_vendedores_route():
    try:
        data = request.get_json()
        vendedor_id = str(data.get("id", "")).strip()
        senha = data.get("senha")

        if senha != app.secret_key:
            return jsonify({"sucesso": False, "erro": "Senha inválida"}), 403

        if not ObjectId.is_valid(vendedor_id):
            return jsonify({"sucesso": False, "erro": "ID inválido"}), 400

        result = vendedores_collection.delete_one({"_id": ObjectId(vendedor_id)})

        if result.deleted_count == 0:
            return jsonify({"sucesso": False, "erro": "Vendedor não encontrado"}), 404

        return jsonify({"sucesso": True}), 200

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#EDITAR  VENDEDORES
@app.route("/editar-vendedor", methods=["PUT"])
def editar_vendedor():
    try:
        data = request.get_json()
        vendedor_id = str(data.get("id", "")).strip()
        senha = data.get("senha")

        # usa app.secret_key que já foi definido no seu app.py
        if senha != app.secret_key:
            return jsonify({"sucesso": False, "erro": "Senha inválida"}), 403

        if not ObjectId.is_valid(vendedor_id):
            return jsonify({"sucesso": False, "erro": "ID inválido"}), 400


        email = data.get("email", "").strip()
        chave_pix = data.get("chave_pix", "").strip()

        vendedores_collection.update_one(
            {"_id": ObjectId(vendedor_id)},
            {"$set": {
                "email": email,
                "chave_pix": chave_pix,
                "comissao": data.get("comissao", "").strip()
            }}
        )

        return jsonify({"sucesso": True})

    except Exception as e:
        return jsonify({"sucesso": False, "erro": str(e)}), 500  
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# TEMPLATE TELA LOGIN VENDEDORES
@app.route('/vitoria_visionaria/login/vendedor')   
def interface_login_vendedor():
    return render_template("login_vendedores.html")
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# TEMPLATE TELA REGISTRAR VENDEDORES
@app.route("/vitoria_visionaria/registrar/vendedor")
def interface_registrar_vendedor():
    return render_template("registro-vendedores.html")
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route("/projetos")
def tables_projetos():
    projetos = list(projetos_collection.find())

    projetos_formatados = []

    # 🔥 detecta se existe conteúdo em cada coluna
    colunas_links = {
        "link_instagram": False,
        "link_whatsapp_suporte": False,
        "link_whatsapp_grupo": False,
        "link_whatsapp_canal": False,
        "link_youtube": False,
        "link_facebook": False,
        "link_tiktok": False,
        "link_kwai": False,
        "imagem_projeto": False,
        "video_instrucao": False,
    }

    for p in projetos:
        projeto = dict(p)
        projeto["_id"] = str(projeto.get("_id"))

        # marca se existe conteúdo
        for key in colunas_links.keys():
            if projeto.get(key):
                colunas_links[key] = True

        projetos_formatados.append(projeto)

    return render_template(
        "graficos/projetos_cadastrados.html",
        projetos=projetos_formatados,
        colunas_links=colunas_links
    )
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
def extrair_public_id(url):
    try:
        partes = url.split("/upload/")
        if len(partes) < 2:
            return None

        caminho = partes[1].split(".")[0]
        return caminho
    except:
        return None
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route("/atualizar_imagem/<id>", methods=["POST"])
def atualizar_imagem(id):
    try:
        img = request.files.get("imagem_projeto")
        projeto = projetos_collection.find_one({"_id": ObjectId(id)})

        if not img:
            return jsonify({"erro": "sem imagem"}), 400

        antiga = projeto.get("imagem_projeto")
        if antiga:
            public_id = extrair_public_id(antiga)
            if public_id:
                cloudinary.uploader.destroy(public_id)

        res = cloudinary.uploader.upload(img, folder="projetos")

        projetos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"imagem_projeto": res["secure_url"]}}
        )

        return jsonify({"status": "imagem atualizada"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/atualizar_video/<id>", methods=["POST"])
def atualizar_video(id):
    try:
        video = request.files.get("video_instrucao")
        projeto = projetos_collection.find_one({"_id": ObjectId(id)})

        if not video:
            return jsonify({"erro": "sem video"}), 400

        antiga = projeto.get("video_instrucao")
        if antiga:
            public_id = extrair_public_id(antiga)
            if public_id:
                cloudinary.uploader.destroy(public_id, resource_type="video")

        res = cloudinary.uploader.upload(
            video,
            resource_type="video",
            folder="projetos"
        )

        projetos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"video_instrucao": res["secure_url"]}}
        )

        return jsonify({"status": "video atualizado"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/atualizar_dados/<id>", methods=["POST"])
def atualizar_dados(id):
    try:
        data = request.get_json()

        update_data = {
            "nome_projeto": data.get("nome_projeto"),
            "valor_injetado_premiacao": data.get("valor_injetado_premiacao"),
            "horario_sorteio": data.get("horario_sorteio"),
            "quantidade": data.get("quantidade"),
            "valor_unidade": data.get("valor_unidade"),
            "dt_sorteio": data.get("dt_sorteio"),

            "link_instagram": data.get("link_instagram"),
            "link_youtube": data.get("link_youtube"),
            "link_whatsapp_grupo": data.get("link_whatsapp_grupo"),
            "link_whatsapp_canal": data.get("link_whatsapp_canal"),
            "link_whatsapp_suporte": data.get("link_whatsapp_suporte"),
            "link_tiktok": data.get("link_tiktok"),
            "link_facebook": data.get("link_facebook"),
            "link_kwai": data.get("link_kwai"),
        }

        projetos_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )

        return jsonify({"status": "dados atualizados"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# EXTRATOS DETALHADO MOVIMENTAÇOES SISTEMA (COM TAXA MP + SAQUES)
@app.route("/extratos")
def extratos():
    pagamentos = pagamento_model.get_all_pagamentos() or []
    saques = get_all_saques() or []  # 🔥 SAQUES

    for p in pagamentos:
        p["_id"] = str(p.get("_id"))

    for s in saques:
        s["_id"] = str(s.get("_id"))

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    total_saques = Decimal("0")  # 🔥 NOVO
    total_taxa_mp = Decimal("0")

    # 🔥 SAQUES
    for s in saques:
        try:
            valor_saque = Decimal(str(s.get("valor_saque", 0)))
            total_saques += valor_saque
        except:
            pass

    resumo = {
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "taxa_mp_total": float(total_taxa_mp),
        "total_saques": float(total_saques),
    }

    return render_template(
        "graficos/extratos_mercado_pago.html",
        usuarios=usuarios,
        resumo=resumo
    )
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------    
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# BUSCAR DADOS USUARIOS E VENDEDORES
@app.route("/api/clientes/vendedores/saque")
def get_cliente_vendedores_por_cpf():
    cpf = request.args.get("cpf")
    if not cpf:
        return jsonify({"error": "CPF não informado"}), 400

    usuario = users_collection.find_one({"cpf": cpf})
    vendedor = vendedores_collection.find_one({"cpf": cpf})

    if not usuario and not vendedor:
        return jsonify({"error": "Nenhum registro encontrado"}), 404

    resposta = {
        "cpf": cpf,

        "nomeUsuario": usuario.get("nome") if usuario else None,
        "emailUsuario": usuario.get("email") if usuario else None,
        "chavePixUsuario": usuario.get("chave_pix") if usuario else None,

        "nomeVendedor": vendedor.get("nome") if vendedor else None,
        "emailVendedor": vendedor.get("email") if vendedor else None,
        "chavePixVendedor": vendedor.get("chave_pix") if vendedor else None
    }

    return jsonify(resposta)
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/saques_projeto", methods=["POST"])
def saques_projeto_route():
    try:
        data = request.get_json(force=True)

        senha = data.get("senha")

        # 🔐 validação direta (corrigida)
        if not senha or str(senha).strip() != str(app.secret_key).strip():
            return jsonify({"sucesso": False, "erro": "Senha inválida"}), 403

        print("CHEGOU NO BACK:", data)

        saque = criar_saque(
            nome_favorecido=data.get("nome_favorecido", ""),
            cpf_favorecido=data.get("cpf_favorecido", ""),
            email_favorecido=data.get("email_favorecido", ""),
            identificacao=data.get("identificacao", ""),
            descricao=data.get("descricao", ""),
            valor_saque=data.get("valor_unidade", 0),
            status=data.get("status", "saque")
        )

        return jsonify({"status": "sucesso", "saque": saque}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------        

from datetime import datetime, timedelta
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
def to_float(v):
    try:
        if v is None or v == "":
            return 0.0
        return float(str(v).replace(",", "."))
    except:
        return 0.0
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# def to_int(v):
#     try:
#         if v is None or v == "":
#             return 0
#         return int(float(str(v).replace(",", ".")))
#     except:
#         return 0
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route('/calcular-rifa', methods=['POST'])
def calcular_lucro_rifa():
    dados = request.form if request.form else request.json

    try:
        nome_rifa = dados.get("nome")

        qtd = to_int(dados.get("qtd"))
        valor = to_float(dados.get("valor"))
        investimento = to_float(dados.get("investimento"))
        despesas = to_float(dados.get("despesas"))
        aliquota_imposto = to_float(dados.get("aliquota_imposto"))
        taxa_mp = to_float(dados.get("taxa_mp"))

        # 📅 DATA / HORA
        data_sorteio = dados.get("data_sorteio")
        hora_sorteio = dados.get("hora_sorteio")

        dias_restantes = 0
        bilhetes_por_dia = 0

        if data_sorteio and hora_sorteio:
            try:
                data_hora_sorteio = datetime.strptime(
                    f"{data_sorteio} {hora_sorteio}", "%Y-%m-%d %H:%M"
                )
                agora = datetime.now()

                # 🔥 limite = 4h antes
                limite_vendas = data_hora_sorteio - timedelta(hours=4)

                delta = limite_vendas - agora
                dias_restantes = delta.days if delta.days > 0 else 0

                # inclui o dia atual (se ainda dá tempo)
                if delta.total_seconds() > 0:
                    dias_restantes += 1

                if dias_restantes > 0:
                    bilhetes_por_dia = int(qtd / dias_restantes)
                else:
                    bilhetes_por_dia = qtd

            except:
                dias_restantes = 0
                bilhetes_por_dia = qtd

        # 💰 FINANCEIRO
        receita_total = qtd * valor

        valor_taxas = receita_total * (taxa_mp / 100)
        valor_impostos = receita_total * (aliquota_imposto / 100)

        custo_total = investimento + despesas + valor_taxas + valor_impostos
        lucro = receita_total - custo_total
        margem = (lucro / receita_total * 100) if receita_total > 0 else 0

        cor_lucro = "green" if lucro >= 0 else "red"

        data = {
            "Item": [
                "Valor Total Bilhetes",
                "- Taxas (MP)",
                "- Impostos",
                "- Investimento",
                "- Despesas",
                "= Custo Total",
                "= Lucro Final",
                "Margem (%)",
                "📅 Dias restantes (até -4h)",
                "🎯 Meta de vendas por dia"
            ],
            "Valor": [
                f"<span style='color:blue;'>+ R$ {receita_total:,.2f}</span>",
                f"<span style='color:red;'>- R$ {valor_taxas:,.2f}</span>",
                f"<span style='color:red;'>- R$ {valor_impostos:,.2f}</span>",
                f"<span style='color:red;'>- R$ {investimento:,.2f}</span>",
                f"<span style='color:red;'>- R$ {despesas:,.2f}</span>",
                f"<span style='color:orange;'>= R$ {custo_total:,.2f}</span>",
                f"<span style='color:{cor_lucro}; font-weight:bold;'>= R$ {lucro:,.2f}</span>",
                f"<span style='color:{cor_lucro};'>{margem:.2f}%</span>",
                f"{dias_restantes} dias",
                f"{bilhetes_por_dia} bilhetes/dia"
            ]
        }

        df = pd.DataFrame(data)

        return jsonify({
            "status": "sucesso",
            "tabela_html": df.to_html(index=False, escape=False, classes="table table-bordered"),
            "lucro": round(lucro, 2)
        })

    except Exception as e:
        return jsonify({"erro": str(e)}), 400
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# SALA ONLINE ACESSO PROS USUARIOS
# SALA ONLINE ACESSO PROS USUARIOS
@app.route("/sala_online/<usuario_id>/<projeto_id>")
def sala_ao_vivo_usuarios(usuario_id, projeto_id):
    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404    

    bilhetes = BilheteModel().get_all_bilhetes() or []
    bilhetes = [b for b in bilhetes if b.get("status") == "approved"]

    # Busca o projeto específico para pegar os números salvos
    projeto_principal = projetos_collection.find_one({"_id": ObjectId(projeto_id)})
    if projeto_principal:
        projeto_principal["_id"] = str(projeto_principal["_id"])
        # Garante que numeros_sorteados exista
        if "numeros_sorteados" not in projeto_principal:
            projeto_principal["numeros_sorteados"] = []

    return render_template("graficos/sala_online.html", 
                           bilhetes=bilhetes, 
                           usuario=usuario, 
                           usuario_id=usuario_id, 
                           projeto_id=projeto_id,
                           projeto_principal=projeto_principal) 

# Evento para disparar o sorteio

#---------------------------------------------------------------------------------------------
# SALA ONLINE ADMIN SALA SORTEIO RESTRITA DOS USUÁRIOS

@app.route("/sala/privaty/acesso/afiliados//sorteios/4f8c2d7e1a9b6f3d5c8e2a7d1f4b9c6e3a8d5f2c7b1e9a4d6f3c8b2e7a5d1f9/<vendedor_id>")
def sala_ao_vivo_admin(vendedor_id=None):

    # projeto = projetos_collection.find_one({
    #     "_id": ObjectId(projeto_id)
    # })

    # if not projeto:
    #     return "Projeto não encontrado", 404

    # # trazer nome_projeto
    # nome_projeto = projeto.get("nome_projeto")

    bilhetes = BilheteModel().get_all_bilhetes() or []

    bilhetes = [
        b for b in bilhetes
        if b.get("status") == "approved"
    ]

    return render_template(
        "graficos/sala_onlline_admin.html",
        bilhetes=bilhetes,
        # projeto_id=projeto_id,
        # projeto=projeto,
        vendedor_id=vendedor_id
        # nome_projeto=nome_projeto
    )


    

# EVENTO SORTEIO ENVIA NUMERO SALVA VERIFICA NUMEROS E APRESENTA GANHADOR
@socketio.on('enviar_numero', namespace='/sorteio')
def receber_numero(data):
    numero = data.get('numero')
    projeto_id = data.get('projeto_id')
    mensagem = ""
    bilhete_ganhador = None

    if numero and projeto_id:
        # Mantém seu update original
        projetos_collection.update_one(
            {"_id": ObjectId(projeto_id)},
            {"$push": {"numeros_sorteados": numero}}
        )

        projeto = projetos_collection.find_one(
            {"_id": ObjectId(projeto_id)}
        )

        # Aqui pegamos TODOS os sorteados até agora
        todos_numeros_sorteados = projeto.get("numeros_sorteados", [])
        total_numeros = len(todos_numeros_sorteados)

        # Mantém sua regra de só verificar de 4 em 4
        if total_numeros > 0 and total_numeros % 4 == 0:
            ultimos_4 = todos_numeros_sorteados[-4:]
            mensagem = (
                f"Aguarde estamos fazendo verificação. "
                f"Números: {', '.join(map(str, ultimos_4))}"
            )

            # BUSCA BILHETES
            bilhetes = BilheteModel().get_all_bilhetes() or []
            bilhetes = [b for b in bilhetes if b.get("status") == "pending"]

            # VERIFICA GANHADOR
            for bilhete in bilhetes:
                lista_numeros = bilhete.get("lista_numeros", [])
                
                for numero_bilhete in lista_numeros:
                    acertos = 0
                    # CORREÇÃO AQUI: Em vez de olhar só os 'ultimos_4', 
                    # verificamos se cada número do bilhete está no HISTÓRICO COMPLETO
                    for n_bilhete in numero_bilhete:
                        if n_bilhete in todos_numeros_sorteados:
                            acertos += 1

                    # 4 ACERTOS (Considerando o acumulado)
                    if acertos == 4:
                        mensagem = (
                            f"Bilhete ganhador encontrado. "
                            f"Participante: {bilhete.get('nome_usuario')} "
                            f"Bilhete: {numero_bilhete}"
                        )
                        bilhete_ganhador = bilhete
                        break
                
                if bilhete_ganhador:
                    break

    # MONTA PAYLOAD COMPLETO (Exatamente como o seu original)
    payload = {
        'numero': numero,
        'mensagem': mensagem
    }

    if bilhete_ganhador:
        payload['bilhete'] = {
            '_id': str(bilhete_ganhador.get('_id')),
            'nome_usuario': bilhete_ganhador.get('nome_usuario'),
            'cpf': bilhete_ganhador.get('cpf'),
            'email_usuario': bilhete_ganhador.get('email_usuario'),
            'lista_numeros': bilhete_ganhador.get('lista_numeros'),
            'lista_urls_img_bilhetes': bilhete_ganhador.get('lista_urls_img_bilhetes'),
            'valor': bilhete_ganhador.get('valor'),
            'status': bilhete_ganhador.get('status'),
        }

    socketio.emit('novo_numero', payload, namespace='/sorteio')



#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
usuarios_conectados = []

@socketio.on('connect', namespace='/sorteio')
def usuario_entrou():
    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        return

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return

    # Pega bilhetes approved do usuário
    bilhetes = BilheteModel().get_all_bilhetes() or []
    bilhetes_usuario = [b for b in bilhetes if b.get("usuario_id") == usuario_id and b.get("status") == "approved"]

    # Monta objeto que será enviado ao front
    participante = {
        "nome_usuario": usuario.get("nome"),
        "payment_id": usuario.get("payment_id"),
        "lista_urls_img_bilhetes": [b.get("lista_urls_img_bilhetes")[0] for b in bilhetes_usuario if b.get("lista_urls_img_bilhetes")]
    }

    usuarios_conectados.append(participante)

    socketio.emit('usuarios_atualizados', {'usuarios': usuarios_conectados}, namespace='/sorteio')


@socketio.on('disconnect', namespace='/sorteio')
def usuario_saiu():
    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        return

    # Remove o usuário da lista
    usuarios_conectados[:] = [u for u in usuarios_conectados if u.get("payment_id") != usuario_id]

    socketio.emit('usuarios_atualizados', {'usuarios': usuarios_conectados}, namespace='/sorteio')
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route("/access/codigo_servico/1722/<vendedor_id>")
@app.route("/vitoria_visionaria/projeto-desenvolvimento-fase-teste/codigo_servico/1722/<usuario_id>")
def eventos_semana(usuario_id=None, vendedor_id=None):
    try:

        usuario = None
        vendedor = None

        if usuario_id:
            usuario = users_collection.find_one(
                {"_id": ObjectId(usuario_id)}
            )

            if not usuario:
                return "usuário não encontrado", 404

        elif vendedor_id:
            vendedor = vendedores_collection.find_one(
                {"_id": ObjectId(vendedor_id)}
            )

            if not vendedor:
                return "vendedor não encontrado", 404

        else:
            return redirect("/rooms")

        projetos = list(projetos_collection.find())

        for p in projetos:
            p["_id"] = str(p["_id"])

        return render_template(
            "graficos/eventos/eventos.html",
            projetos=projetos,
            usuario_id=usuario_id,
            vendedor_id=vendedor_id,
            usuario=usuario,
            vendedor=vendedor
        )

    except Exception as e:
        print("ERRO:", e)
        return "Erro ao carregar eventos", 500
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# API MERCADO PAGO 
# PAGAMENTOS CARTAO CREDITO

MP_PUBLIC_KEY = os.environ.get("MP_PUBLIC_KEY")

@app.route('/pagamento/cartao_credito/<usuario_id>')
def home(usuario_id):

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404
        
    bilhetes = BilheteModel().get_all_bilhetes() or []

    bilhetes = [b for b in bilhetes if b.get("status") == "pending"]

    return render_template(
        'graficos/Pagamentos/cartao_credito.html',
        public_key=MP_PUBLIC_KEY,
        usuario=usuario,
        bilhetes=bilhetes,
        usuario_id=usuario_id
    )
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route('/process_payment/<usuario_id>', methods=['POST'])
def add_income(usuario_id):


    try:
        request_values = request.get_json()

        lista_numeros = request.args.get("lista_numeros")
        if lista_numeros:
            lista_numeros = json.loads(lista_numeros)
        else:
            lista_numeros = []

        usuario_id = usuario_id or request.args.get("usuario_id")
        if not usuario_id:
            return jsonify({"erro": "usuario_id não informado"}), 400

        cpf = request_values.get("payer", {}).get("identification", {}).get("number", "")
        email = request_values.get("payer", {}).get("email", "")

        payment_data = {
            "transaction_amount": float(request_values["transaction_amount"]),
            "token": request_values["token"],
            "installments": int(request_values["installments"]),
            "payment_method_id": request_values["payment_method_id"],
            "issuer_id": request_values["issuer_id"],
            "payer": {
                "email": email,
                "identification": {
                    "type": request_values["payer"]["identification"]["type"],
                    "number": cpf
                }
            }
        }

        taxa_mp = round(transaction_amount * 0.0499, 2)

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        pagamento_model = PagamentoModel()

        dados_pagamento = criar_documento_pagamento(
            payment_id=payment["id"],
            status=payment["status"],
            valor=payment["transaction_amount"],
            cpf=cpf,
            email_user=email,
            payment_method_id=request_values.get("payment_method_id"),
            lista_numeros=lista_numeros,
            taxa_mp=taxa_mp
        )

        dados_pagamento["usuario_id"] = usuario_id

        pagamento_model.create_pagamento(dados_pagamento)

        try:
            bilhetes_collection.update_many(
                {
                    "cpf": cpf,
                    "status": "pendente",
                    "payment_id": "aguardando gerar pagamento"
                },
                {
                    "$set": {
                        "payment_id": payment["id"]
                    }
                }
            )
        except Exception as e:
            print("ERRO AO ATUALIZAR BILHETES:", e)

        return jsonify(payment), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------



#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# SISTEMA OPERACIONAL DAS RASPADINHAS ONLINES 
#---------------------------------------------------------------------------------------------
@app.route('/raspadinha', defaults={'usuario_id': None})
@app.route('/raspadinha/<usuario_id>')
def raspadinhas(usuario_id):

    vendedores = list(
        vendedores_collection.find({}, {
            "nome": 1,
            "vendedor_id": 1
        })
    )

    usuario = None
    vendedor_id = None

    if usuario_id:
        usuario = users_collection.find_one({
            "_id": ObjectId(usuario_id)
        })

        if usuario:
            vendedor_id = usuario.get("vendedor_id")

    # Apenas CPF
    cpf = limpar_cpf(usuario.get("cpf", "")) if usuario else ""

    raspadinhas_all = raspadinha_model.get_all_raspadinhas() or []

    raspadinhas = [
        r for r in raspadinhas_all
        if (
            limpar_cpf(r.get("cpf", "")) == cpf and
            r.get("status") == "approved"
        )
    ]

    total_quantidade = sum(
        int(r.get("quantidade_raspadinhas", 0))
        for r in raspadinhas
    )
    # =========================
    # IP
    # =========================
    ip_usuario = request.headers.get("X-Forwarded-For", request.remote_addr)

    # =========================
    # USER AGENT
    # =========================
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)
    ua = user_agent_string.lower()

    # =========================
    # DETECÇÃO DE APARELHO
    # =========================
    aparelho = "Desconhecido"

    if "sm-a356" in ua:
        aparelho = "Samsung Galaxy A35"
    elif "sm-a346" in ua:
        aparelho = "Samsung Galaxy A34"
    elif "sm-a546" in ua:
        aparelho = "Samsung Galaxy A54"
    elif "sm-s918" in ua:
        aparelho = "Samsung Galaxy S23 Ultra"
    elif "sm-s926" in ua:
        aparelho = "Samsung Galaxy S24+"
    elif "sm-g990" in ua:
        aparelho = "Samsung Galaxy S21 FE"
    elif "sm-" in ua:
        aparelho = "Samsung"
    elif "2201117tg" in ua:
        aparelho = "Xiaomi Redmi Note 11"
    elif "22101316g" in ua:
        aparelho = "Xiaomi Redmi Note 12"
    elif "2312draf3" in ua:
        aparelho = "Xiaomi Redmi Note 13"
    elif "redmi" in ua or "xiaomi" in ua:
        aparelho = "Xiaomi"
    elif "moto g54" in ua:
        aparelho = "Motorola Moto G54"
    elif "moto g84" in ua:
        aparelho = "Motorola Moto G84"
    elif "moto" in ua:
        aparelho = "Motorola"
    elif "iphone" in ua:
        aparelho = "iPhone"
    elif "ipad" in ua:
        aparelho = "iPad"
    elif "huawei" in ua:
        aparelho = "Huawei"
    elif "asus" in ua:
        aparelho = "Asus"
    elif "lg-" in ua:
        aparelho = "LG"
    elif "realme" in ua:
        aparelho = "Realme"
    elif "oppo" in ua:
        aparelho = "Oppo"
    elif "vivo" in ua:
        aparelho = "Vivo"
    elif "nokia" in ua:
        aparelho = "Nokia"
    elif "windows nt" in ua:
        aparelho = "PC Windows"
    elif "macintosh" in ua or "mac os" in ua:
        aparelho = "MacBook / iMac"
    elif "linux" in ua and "android" not in ua:
        aparelho = "PC Linux"
    else:
        aparelho = f"{user_agent.device.family} | {user_agent.os.family}"

    # =========================
    # NAVEGADOR
    # =========================
    navegador = user_agent.browser.family

    # =========================
    # CIDADE PELO IP
    # =========================
    cidade = "Desconhecida"
    try:
        resposta = requests.get(f"http://ip-api.com/json/{ip_usuario}").json()
        cidade = f"{resposta.get('city', '')} - {resposta.get('regionName', '')}"
    except:
        pass

    return render_template(
        "graficos/eventos/raspadinha-1.html",
        raspadinhas=raspadinhas,
        total_quantidade=total_quantidade,
        vendedores=vendedores,
        usuario=usuario,
        vendedor_id=vendedor_id,
        usuario_id=usuario_id,
        ip_usuario=ip_usuario,
        cidade=cidade,
        aparelho=aparelho,
        navegador=navegador        
    )

import random
from flask import jsonify

# Lista corrigida com foco em prêmios pequenos (0.05 a 0.30) saindo muito mais fácil
PREMIOS = [
    # Sem prêmio (Essencial para equilibrar o custo de R$ 0,60)
    {"id": 0, "valor": "R$ 0,00", "numero": 0.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1780455026/Gemini_Generated_Image_yern2fyern2fyern_a3p5r2.png", "probabilidade": 35.0},
    
    # Prêmios Pequenos (MUITO FÁCEIS - Totalizam 55% de chance)
    {"id": 1, "valor": "R$ 0,05", "numero": 0.05, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778621532/1778621069295_byxfmy.png", "probabilidade": 25.0},
    {"id": 2, "valor": "R$ 0,10", "numero": 0.10, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778622997/1778622360189_cyixsr.png", "probabilidade": 18.0},
    {"id": 3, "valor": "R$ 0,25", "numero": 0.25, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778614222/file_000000000ca4720e8a65a4b4966cee89_kxhcbd.png", "probabilidade": 8.0},
    {"id": 4, "valor": "R$ 0.30", "numero": 0.30, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778621531/1778621356505_k6jsgw.png", "probabilidade": 4.0},
    
    # Prêmios Médios (MÉDIOS/RAROS - Totalizam 7.4% de chance)
    {"id": 5, "valor": "R$ 0.50", "numero": 0.50, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778621531/1778621422435_w6l0n6.png", "probabilidade": 4.0},
    {"id": 6, "valor": "R$ 1.00", "numero": 1.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778621531/1778621498747_xhi8ad.png", "probabilidade": 2.0},
    {"id": 7, "valor": "R$ 5.00", "numero": 5.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778622997/1778622293971_v0zpku.png", "probabilidade": 1.0},
    {"id": 8, "valor": "R$ 10.00", "numero": 10.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778623662/1778623446472_mx8vbn.png", "probabilidade": 0.4},
    
    # Grandes Prêmios (MUITO RAROS - Totalizam 0.6% de chance)
    {"id": 9, "valor": "R$ 20.00", "numero": 20.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1779221189/file_0000000063ac720e965131493b7e6f41_u1oc0r.png", "probabilidade": 0.2},
    {"id": 10, "valor": "R$ 30.00", "numero": 30.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1779218486/file_000000008a7c71f5bac286bab3ba1f1a_smqhkr.png", "probabilidade": 0.1},
    {"id": 11, "valor": "R$ 50.00", "numero": 50.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1779222836/file_00000000d3ec71fbbd04e208192b8157_moyivw.png", "probabilidade": 0.1},
    {"id": 12, "valor": "R$ 100.00", "numero": 100.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1779217595/file_00000000514c71fbacfcc7e2d6ab0f1b_bib4aa.png", "probabilidade": 0.1},
    {"id": 13, "valor": "R$ 200.00", "numero": 200.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1778615047/file_000000006b3871fb9a60d2812e6ce8df_d0zmmi.png", "probabilidade": 0.09},
    {"id": 14, "valor": "R$ 1.000.00", "numero": 1000.00, "imagem": "https://res.cloudinary.com/dptprh0xk/image/upload/v1779217595/file_0000000013b471f9a0c8b0e9e02ccb7a_udhftc.png", "probabilidade": 0.01}
]


#---------------------------------------------------------------------------------------------
# NOVA RASPADINHA AQUI 
@app.route('/raspadinha/novo')
def nova_raspadinha():
    # Sorteia o prêmio baseado nas novas probabilidades (Soma exata de 100)
    sorteado = random.choices(PREMIOS, weights=[p["probabilidade"] for p in PREMIOS], k=1)[0]
    
    return jsonify({
        "id_premio": sorteado["id"],
        "valor": sorteado["valor"],
        "imagem": sorteado["imagem"]
    })

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# Lista global simplificada apenas para armazenar os logs recentes de atividades
usuarios = []


@socketio.on('usuario_entrou')
def handle_usuario_entrou(data):
    usuario_id = data.get("usuario_id")

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return

    usuario = users_collection.find_one({
        "_id": ObjectId(usuario_id)
    })

    if not usuario:
        return

    nome_usuario = usuario.get("nome", "Usuário")
    foto_perfil = usuario.get(
        "foto_perfil",
       ""
    )

    # AQUI VAI O HTML DA IMAGEM
    mensagem = f'''
    <img src="{ foto_perfil }"
         style="width:32px;height:32px;vertical-align:middle;margin-right:5px;">

    {nome_usuario} entrou no jogo
    '''

    # REMOVE DUPLICADOS
    usuarios[:] = [
        u for u in usuarios
        if u.get("id") != usuario_id
    ]

    # ADICIONA
    usuarios.append({
        "id": usuario_id,
        "texto": mensagem
    })

    # LIMITE
    if len(usuarios) > 8000:
        usuarios.pop(0)

    # ENVIA
    socketio.emit('notificacao_geral', {
        'lista': [u["texto"] for u in usuarios]
    })
    
@socketio.on('enviar_mensagem')
def handle_mensagem_jogo(dados):
    nome_usuario = usuario.get("nome", "Usuário")
    foto_perfil = usuario.get(
        "foto_perfil",
       ""
    )
    
    # Recebe do usuário e repassa para TODOS os jogadores conectados
    emit('receber_mensagem', dados, broadcast=True)


@socketio.on('disconnect')
def usuario_saiu_jogo():
    usuario_id = request.args.get("usuario_id")
    if not usuario_id:
        return

    usuarios[:] = [u for u in usuarios if u.get("id") != usuario_id]
    socketio.emit('notificacao_geral', {'lista': [u["texto"] for u in usuarios]})



@app.route('/raspadinha/resultado', methods=['POST'])
def resultado_raspadinha():
    dados = request.get_json() or {}
    usuario_id = dados.get("usuario_id")

    
    if not usuario_id:
        referer = request.headers.get("Referer", "")
        if "/raspadinha/" in referer:
            usuario_id = referer.split("/raspadinha/")[1].split("/")[0]

    if not usuario_id or usuario_id == "None":
        return jsonify({"error": "Usuário não detectado"}), 400
    
    try:
        oid = ObjectId(str(usuario_id))
    except:
        return jsonify({"error": "ID inválido"}), 400

    usuario = users_collection.find_one({"_id": oid})
    if not usuario:
        return jsonify({"error": "Usuário não encontrado no banco"}), 404

    # 1. BUSCA AS RASPADINHAS ATIVAS DO USUÁRIO VIA CPF
    cpf_usuario = limpar_cpf(usuario.get("cpf", ""))
    
    # Busca um registro aprovado que pertença ao CPF e tenha quantidade maior que 0
    # Modifique o nome da coleção se não for 'raspadinhas_collection'
    raspadinha_disponivel = raspadinhas_collection.find_one({
        "cpf": cpf_usuario, # Ou o formato que estiver salvo no banco
        "status": "approved",
        "quantidade_raspadinhas": {"$gt": 0} # Garante que é maior que zero
    })

    if not raspadinha_disponivel:
        return jsonify({"error": "Você não possui raspadinhas disponíveis"}), 400

    # 2. SE TEM RASPADINHA, SUBTRAI 1 DO BANCO DE DADOS
    raspadinhas_collection.update_one(
        {"_id": raspadinha_disponivel["_id"]},
        {"$inc": {"quantidade_raspadinhas": -1}} # Diminui 1 unidade
    )

    # O restante da lógica de prêmios permanece idêntico
    id_premio = dados.get("id_premio")
    premio = next((p for p in PREMIOS if str(p.get("id")) == str(id_premio)), None)

    if not premio:
        return jsonify({"valorTexto": "R$ 0,00", "valorNumerico": 0.0, "error": "Prêmio inválido"})

    valor_triplicado = float(premio["numero"]) * 1
    texto_triplicado = f"R$ {valor_triplicado:.2f}".replace(".", ",")

    # Atualiza o saldo de ganhos do usuário
    users_collection.update_one(
        {"_id": oid},
        {
            "$set": {"ganhos": round(float(usuario.get("ganhos", 0.0)) + valor_triplicado, 2)},
            "$push": {"entradas": {"tipo": "raspadinha", "valor": round(valor_triplicado, 2), "data": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")}}
        }
    )

    msg = f'''
    <img src="https://res.cloudinary.com/dptprh0xk/image/upload/v1765407065/bitcoin_pjo40b.png"
        style="width:32px;height:32px;vertical-align:middle;margin-right:5px;">

    {usuario.get("nome", "Usuário")} ganhou {texto_triplicado}!
    '''
    usuarios.append({"id": str(usuario_id), "texto": msg})
    if len(usuarios) > 8000: usuarios.pop(0)
    socketio.emit('notificacao_geral', {'lista': [u["texto"] for u in usuarios]})
    
    usuario_atualizado = users_collection.find_one({"_id": oid})
    saldo_atual = float(usuario_atualizado.get("ganhos", 0.0))
    saldo_formatado = f"R$ {saldo_atual:.2f}".replace(".", ",")
    
    # 3. PEGA A NOVA QUANTIDADE RESTANTE PARA RETORNAR PRO JAVASCRIPT
    # Refaz a soma de todas as raspadinhas restantes do CPF do usuário
    raspadinhas_all = raspadinha_model.get_all_raspadinhas() or []
    nova_quantidade_total = sum(int(r.get("quantidade_raspadinhas") or 0) for r in raspadinhas_all if limpar_cpf(r.get("cpf", "")) == cpf_usuario and r.get("status") == "approved")

    return jsonify({
        "valorTexto": texto_triplicado, 
        "valorNumerico": valor_triplicado,
        "novoSaldoTexto": saldo_formatado,
        "novaQuantidadeTotal": nova_quantidade_total # Envia o novo total para atualizar a tela
    })


# =========================
# SAQUE (COM HISTÓRICO)
# =========================
@app.route('/saque', methods=['POST'])
def saque():

    dados = request.get_json() or {}

    valor_saque = float(dados.get("valor", 0))

    # Sistema de segurança triplo para capturar o ID correto
    usuario_id = session.get("usuario_id") or dados.get("usuario_id")
    
    if not usuario_id or usuario_id == "None" or isinstance(usuario_id, dict):

        # Fallback: pega o ID da URL da página anterior
        referer = request.headers.get("Referer", "")

        if "/raspadinha/" in referer:

            usuario_id = referer.split("/raspadinha/")[1].split("/")[0]

    if not usuario_id or usuario_id == "None" or not ObjectId.is_valid(str(usuario_id)):

        return jsonify({
            "erro": "Usuário inválido ou não autenticado"
        }), 400

    oid = ObjectId(str(usuario_id))

    usuario = users_collection.find_one({
        "_id": oid
    })
    
    if not usuario:

        return jsonify({
            "erro": "Usuário não encontrado no banco de dados"
        }), 404

    ganhos = float(usuario.get("ganhos", 0.0))

    # =========================
    # VALIDAÇÕES
    # =========================
    if valor_saque < 3:

        return jsonify({
            "erro": "Valor mínimo é R$ 3,00"
        }), 400

    if valor_saque > ganhos:

        return jsonify({
            "erro": "Saldo insuficiente"
        }), 400

    # =========================
    # DADOS USUÁRIO
    # =========================
    nome_usuario = usuario.get("nome", "Usuário")

    cpf_usuario = usuario.get("cpf", "")

    email_usuario = usuario.get("email", "")

    pix_usuario = usuario.get("pix", "")

    data_saque = datetime.now(timezone.utc)

    # =========================
    # SALVA HISTÓRICO SAQUE
    # =========================
    mensagem_saque = f'''
    💰 SOLICITAÇÃO DE SAQUE 💰

    🆔 ID: {usuario_id}

    👤 Nome: {nome_usuario}

    🪪 CPF: {cpf_usuario}

    🏦 PIX: {pix_usuario}

    💵 Valor: R$ {f"{valor_saque:.2f}".replace(".", ",")}

    📅 Data/Hora: {data_saque.strftime("%d/%m/%Y %H:%M:%S")}
    '''

    criar_saque(

        nome_favorecido=nome_usuario,

        cpf_favorecido=cpf_usuario,

        email_favorecido=email_usuario,

        valor_saque=valor_saque,

        identificacao=usuario_id,

        descricao="Solicitação de saque",

        status="pendente"
    )

    # SALVA MENSAGEM DENTRO DA COLLECTION
    saques_collection.update_one(

        {
            "identificacao": str(usuario_id)
        },

        {
            "$push": {
                "mensagens_solicitando_saques": mensagem_saque
            }
        }
    )

    # =========================
    # ATUALIZA USUÁRIO
    # =========================
    users_collection.update_one(

        {
            "_id": oid
        },

        {
            "$inc": {

                "ganhos": -valor_saque,

                "saques": valor_saque
            },

            "$push": {

                "saidas": {

                    "status": "pendente",

                    "valor": round(valor_saque, 2),

                    "data": data_saque.strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        }
    )

    usuario_atualizado = users_collection.find_one({
        "_id": oid
    })

    # =========================
    # SOCKET FEED
    # =========================
    msg_saque = f'''
    <img src="https://res.cloudinary.com/dptprh0xk/image/upload/v1778720610/saque_k5hlcq.png"
        style="width:32px;height:32px;vertical-align:middle;margin-right:5px;">

    {nome_usuario} solicitou saque de R$ {f"{valor_saque:.2f}".replace(".", ",")}
    '''

    usuarios.append({

        "id": str(usuario_id),

        "texto": msg_saque
    })

    if len(usuarios) > 15:

        usuarios.pop(0)

    lista_texto = [u["texto"] for u in usuarios]

    socketio.emit('notificacao_geral', {

        'lista': lista_texto
    })

    # =========================
    # RETORNO
    # =========================
    return jsonify({

        "success": True,

        "ganhos": float(
            usuario_atualizado.get("ganhos", 0.0)
        ),

        "saques": float(
            usuario_atualizado.get("saques", 0.0)
        )
    })



# # ===========================================================================
# # TRANSFERENCIAS DE GANHOS PARA OUTRO USUARIO_ID (COM HISTÓRICO)
# # ===========================================================================
@app.route('/transferencia', methods=['POST'])
def transferencia():
    dados = request.get_json() or {}

    valor = str(dados.get("valor", "0")).replace(",", ".").strip()
    favorecido = str(dados.get("favorecido", "")).strip()

    try:
        valor = float(valor)
    except:
        return jsonify({
            "erro": "Valor inválido"
        }), 400

    usuario_id = session.get("usuario_id") or dados.get("usuario_id")

    if not usuario_id or usuario_id == "None" or isinstance(usuario_id, dict):

        referer = request.headers.get("Referer", "")

        if "/raspadinha/" in referer:
            usuario_id = referer.split("/raspadinha/")[1].split("/")[0]

    if not usuario_id or not ObjectId.is_valid(str(usuario_id)):
        return jsonify({
            "erro": "Usuário inválido ou não autenticado"
        }), 400

    remetente = users_collection.find_one({
        "_id": ObjectId(usuario_id)
    })

    if not remetente:
        return jsonify({
            "erro": "Usuário não encontrado"
        }), 404

    saldo = float(remetente.get("ganhos", 0))

    if valor < 0.60:
        return jsonify({
            "erro": "Valor mínimo R$ 0,60"
        }), 400

    if valor > 1000:
        return jsonify({
            "erro": "Valor máximo R$ 1.000,00"
        }), 400

    if valor > saldo:
        return jsonify({
            "erro": "Saldo insuficiente"
        }), 400

    destinatario = None

    # Procura por ObjectId
    if ObjectId.is_valid(favorecido):
        destinatario = users_collection.find_one({
            "_id": ObjectId(favorecido)
        })

    # Procura por chave_pix
    if not destinatario:
        destinatario = users_collection.find_one({
            "chave_pix": favorecido
        })

    # Procura por email
    if not destinatario:
        destinatario = users_collection.find_one({
            "email": favorecido
        })

    # Procura por CPF
    if not destinatario:
        destinatario = users_collection.find_one({
            "cpf": favorecido
        })

    if not destinatario:
        return jsonify({
            "erro": "Favorecido não encontrado"
        }), 404

    if str(destinatario["_id"]) == str(usuario_id):
        return jsonify({
            "erro": "Não é permitido transferir para sua própria conta"
        }), 400

    data_transferencia = datetime.now(timezone.utc)
    data_formatada = data_transferencia.strftime("%d/%m/%Y %H:%M:%S")

    nome_remetente = remetente.get("nome", "Usuário")
    nome_destinatario = destinatario.get("nome", "Usuário")

    # Debita remetente
    users_collection.update_one(
        {"_id": ObjectId(usuario_id)},
        {
            "$inc": {
                "ganhos": -valor
            },
            "$push": {
                "saidas": {
                    "status": destinatario,
                    "valor": round(valor, 2),
                    "data": data_formatada,
                    "destinatario_id": str(destinatario["_id"]),
                    "destinatario_nome": nome_destinatario
                }
            }
        }
    )

    # Credita destinatário
    users_collection.update_one(
        {"_id": destinatario["_id"]},
        {
            "$inc": {
                "ganhos": valor
            },
            "$push": {
                "entradas": {
                    "tipo": "transferencia",
                    "valor": round(valor, 2),
                    "data": data_formatada,
                    "origem_id": str(usuario_id),
                    "origem_nome": nome_remetente
                }
            }
        }
    )

    usuario_atualizado = users_collection.find_one({
        "_id": ObjectId(usuario_id)
    })

    #Saldo atualizado remetente

    socketio.emit(
    "saldo_atualizado",
    {
    "usuario_id": str(usuario_id),
    "ganhos": float(usuario_atualizado.get("ganhos", 0))
    }
    )

    #Saldo atualizado destinatário

    destinatario_atualizado = users_collection.find_one({
    "_id": destinatario["_id"]
    })

    socketio.emit(
    "saldo_atualizado",
    {
    "usuario_id": str(destinatario["_id"]),
    "ganhos": float(destinatario_atualizado.get("ganhos", 0))
    }
    )

    #Notificação de transferência

    socketio.emit(
    "transferencia_recebida",
    {
    "usuario_id": str(destinatario["_id"]),
    "valor": round(valor, 2),
    "nome": nome_remetente
    }
    )

    return jsonify({
        "success": True,
        "mensagem": f"Transferência realizada para {nome_destinatario}",
        "ganhos": float(usuario_atualizado.get("ganhos", 0))
    })


# =========================
# LISTAR MENSAGENS SAQUES
# =========================
@app.route('/listar_mensagens_saques')
def listar_mensagens_saques_todos():

    saques = get_all_saques() or []

    mensagens = []

    for s in saques:

        s["_id"] = str(s["_id"])

        lista = s.get(
            "mensagens_solicitando_saques",
            []
        )

        mensagens.extend(lista)

    return jsonify({

        "mensagens": mensagens

    })


@app.route("/movimentacoes", methods=["GET"])
def movimentacoes():
    # Sistema de segurança triplo para capturar o ID correto
    usuario_id = session.get("usuario_id")
    
    # Se nao achar na sessao, tenta pegar via request args (caso seja enviado na URL)
    if not usuario_id:
        usuario_id = request.args.get("usuario_id")

    # Fallback: pega o ID da URL da página anterior
    if not usuario_id:
        referer = request.headers.get("Referer", "")
        if "/raspadinha/" in referer:
            try:
                usuario_id = referer.split("/raspadinha/")[1].split("/")[0]
            except:
                usuario_id = None

    if not usuario_id or not ObjectId.is_valid(usuario_id):
        return jsonify({"entradas": [], "saidas": [], "ganhos": 0.0})

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})

    if not usuario:
        return jsonify({"entradas": [], "saidas": [], "ganhos": 0.0})

    return jsonify({
        "entradas": usuario.get("entradas", []),
        "saidas": usuario.get("saidas", []),
        "ganhos": usuario.get("ganhos", 0.0)
    })


#---------------------------------------------------------------------------------------------

@app.route('/status/payment_preference/<pref_id>')
def verificar_pagamento(pref_id):

    filtros = {
        "preference_id": pref_id
    }

    resultado_busca = sdk.payment().search(filtros)

    pagamentos = resultado_busca.get("response", {}).get("results", [])

    if not pagamentos:
        return jsonify({
            "preference_id": pref_id,
            "status": "not_found",
            "message": "Nenhum pagamento iniciado para esta preferência."
        }), 404

    pagamento_atual = pagamentos[0]

    payment_id = pagamento_atual.get("id")
    status = pagamento_atual.get("status")
    cpf = pagamento_atual.get("external_reference")

    # SALVA PAYMENT_ID REAL
    bilhetes_collection.update_many(
        {
            "cpf": cpf,
            "payment_id": pref_id
        },
        {
            "$set": {
                "payment_id": str(payment_id),
                "status": status
            }
        }
    )

    return jsonify({
        "payment_id": payment_id,
        "status": status,
        "status_detail": pagamento_atual.get("status_detail"),
        "external_reference": cpf
    }), 200

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# - PAGAMENTO CARTAO CREDITO
@app.route('/pagamento/cartao_credito/ferrari-tech/<usuario_id>')
def home_raspadinha(usuario_id):

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404
        
    # raspadinhas = RaspadinhaModel().get_all_raspadinhas() or []

    # raspadinhas = [r for r in raspadinhas if r.get("status") == "pending"]

    return render_template(
        'graficos/eventos/Pagamentos/Cartao/cartao_credito_raspadinha.html',
        public_key=MP_PUBLIC_KEY,
        usuario=usuario,
        # raspadinhas=raspadinhas,
        usuario_id=usuario_id
    )

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# - PAGAMENTO CARTAO CREDITO API
@app.route('/process_payment/ferrari-tech/<usuario_id>', methods=['POST'])
def add_income_raspadinha(usuario_id):


    try:
        request_values = request.get_json()

        quantidade_raspadinhas = request.args.get("quantidade_raspadinhas")
        if quantidade_raspadinhas:
            quantidade_raspadinhas = json.loads(quantidade_raspadinhas)
        else:
            quantidade_raspadinhas = []

        usuario_id = usuario_id or request.args.get("usuario_id")
        if not usuario_id:
            return jsonify({"erro": "usuario_id não informado"}), 400

        cpf = request_values.get("payer", {}).get("identification", {}).get("number", "")
        email = request_values.get("payer", {}).get("email", "")

        payment_data = {
            "transaction_amount": float(request_values["transaction_amount"]),
            "token": request_values["token"],
            "installments": int(request_values["installments"]),
            "payment_method_id": request_values["payment_method_id"],
            "issuer_id": request_values["issuer_id"],
            "payer": {
                "email": email,
                "identification": {
                    "type": request_values["payer"]["identification"]["type"],
                    "number": cpf
                }
            }
        }

        taxa_mp = round(transaction_amount * 0.0499, 2)

        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        pagamento_model = PagamentoModel()

        dados_pagamento = criar_documento_pagamento(
            payment_id=payment["id"],
            status=payment["status"],
            valor=payment["transaction_amount"],
            cpf=cpf,
            email_user=email,
            payment_method_id=request_values.get("payment_method_id"),
            taxa_mp=taxa_mp
        )


        dados_pagamento["usuario_id"] = usuario_id

        pagamento_model.create_pagamento(dados_pagamento)

        try:
            raspadinhas_collection.update_many(
                {
                    "cpf": cpf,
                    "status": "pendente",
                    "payment_id": "aguardando gerar pagamento"
                },
                {
                    "$set": {
                        "payment_id": payment["id"]
                    }
                }
            )
        except Exception as e:
            print("ERRO AO ATUALIZAR RASPADINHAS:", e)

        return jsonify(payment), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# - SISTEMA PROCESSAMENTO DE PAGAMENTO DAS RASPADINHAS
# - PAGAMENTO QRCODE PIX E COLA
#---------------------------------------------------------------------------------------------

@app.route("/payment_qrcode_pix/pagamento_pix/ferrari-tech/<usuario_id>")
def pagamentosqrcode(usuario_id=None):
    import json
    from datetime import datetime, timedelta

    usuario_id = usuario_id or request.args.get("usuario_id")

    if not usuario_id:
        return jsonify({
            "erro": "usuario_id não informado"
        }), 400

    nome = request.args.get("nome") or ""
    sobrenome = request.args.get("sobrenome") or ""
    cpf = request.args.get("cpf") or ""
    email = request.args.get("email") or ""
    vendedor = request.args.get("vendedor") or ""
    quantidade = int(request.args.get("quantidade") or 0)

    if quantidade <= 0:
        quantidade = 1

    valor_total = round(quantidade * 0.60, 2)
    taxa_mp = round(valor_total * 0.0099, 2)

    expiration_date = (
        datetime.utcnow() + timedelta(minutes=15)
    ).strftime('%Y-%m-%dT%H:%M:%S.000-00:00')

    payment_data = {
        "transaction_amount": float(valor_total),
        "description": "Servico Digital",
        "payment_method_id": "pix",
        "date_of_expiration": expiration_date,
        "payer": {
            "email": email,
            "first_name": nome,
            "last_name": sobrenome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },
        "external_reference": email,
        "notification_url": notification_url,
        "statement_descriptor": "FerrariTech"
    }

    try:
        response = sdk.payment().create(payment_data)
        mp = response.get("response", {})

        if "id" not in mp:
            return f"ERRO MP: {mp}", 500

        payment_id = str(mp["id"])
        status = mp.get("status", "pending")

        tx = mp.get("point_of_interaction", {}).get("transaction_data", {})

        qr_base64 = tx.get("qr_code_base64")
        qr_code = tx.get("qr_code")

        if not qr_base64 or not qr_code:
            return f"ERRO QR: {tx}", 500

        image_bytes = base64.b64decode(qr_base64)
        image_file = BytesIO(image_bytes)

        upload_result = cloudinary.uploader.upload(
            image_file,
            folder="qrcodes_pix",
            public_id=f"qr_{payment_id}"
        )

        qr_image_url = upload_result.get("secure_url")

        documento_pagamento = {
            "_id": payment_id,
            "payment_id": payment_id,
            "status": status,
            "payment_method_id": "Pix",
            "valor": valor_total,
            "cpf": cpf,
            "vendedor": vendedor,
            "email_usuario": email,
            "nome_usuario": nome,
            "qr_code": qr_code,
            "qr_image_url": qr_image_url,
            "taxa_mp": taxa_mp,
            "quantidade_raspadinhas": quantidade,
            "data_criacao": datetime.utcnow().strftime("%a, %d de %B de %Y %H:%M:%S GMT"),
            "data_de_expiração": expiration_date
        }

        try:
            PagamentoModel().create_pagamento(documento_pagamento)
        except Exception as e:
            print("ERRO AO SALVAR:", e)

        documentos_raspadinhas = []

        for _ in range(quantidade):
            documentos_raspadinhas.append({
                "raspadinha_id": payment_id,
                "payment_id": payment_id,
                "usuario_id": usuario_id,
                "cpf": cpf,
                "nome_user": nome,
                "vendedor": vendedor,
                "valor_unidade": 0.60,
                "valor_total": valor_total,
                "email_user": email,
                "quantidade_raspadinhas": 1,
                "status": "pending",
                "data_criacao": datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"),
                "expiration_date": expiration_date
            })

        try:
            raspadinhas_collection.insert_many(documentos_raspadinhas)
        except Exception as e:
            print("ERRO AO SALVAR RASPADINHAS:", e)

        # SOCKET
        nome_usuario = nome if nome else "Usuário"

        msg_saque = f'''
        <img src="https://res.cloudinary.com/dptprh0xk/image/upload/v1778012674/icone-de-carrinho-de-compras-3d-em-fundo-de-circulo-azul-simbolo-de-varejo-online_84443-55705_dfmhp8.png"
        style="width:32px;height:32px;vertical-align:middle;margin-right:5px;">
        {nome_usuario} acabou de comprar {quantidade} pix!
        '''

        usuarios.append({
            "id": str(usuario_id),
            "texto": msg_saque
        })

        if len(usuarios) > 8000:
            usuarios.pop(0)

        lista_texto = [u["texto"] for u in usuarios]

        socketio.emit('notificacao_geral', {
            'lista': lista_texto
        })

        return render_template(
            "graficos/eventos/Pagamentos/Pix/qrcode-pix.html",
            qrcode=qr_image_url,
            valor=f"R$ {valor_total:.2f}",
            qr_code_cola=qr_code,
            status=status,
            payment_id=payment_id,
            cpf=cpf,
            expiration_date=expiration_date
        )

    except Exception as e:
        print("ERRO GERAL:", e)
        return f"ERRO GERAL: {str(e)}", 500
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#=============================================================================================
@app.route('/aguardando_pagamento/pix/<pagamento_id>', methods=['GET'])
def aguardando_confirmacao_pagamento_pix_cola(pagamento_id):

    pagamento = pagamento_model.get_pagamento(pagamento_id)

    if not pagamento:
        return "Pagamento não encontrado", 404

    cpf = pagamento.get("cpf", "")

    # BUSCA NA COLLECTION CERTA: users_collection
    usuario = None
    if cpf:
        usuario = users_collection.find_one({"cpf": cpf})

    if not usuario:
        return "Usuário não encontrado", 404

    usuario_id = str(usuario["_id"])

    qr_image_url = (
        pagamento.get("qrcode") or
        pagamento.get("qr_image_url") or
        pagamento.get("qr_code_base64")
    )

    qr_code_cola = (
        pagamento.get("qr_code_cola") or
        pagamento.get("qr_code") or
        pagamento.get("copia_cola")
    )

    valor = pagamento.get("valor", 0)
    status = pagamento.get("status", "aguardando pagamento")

    return render_template(
        "graficos/eventos/Pagamentos/Pix/aguardando_pagamento_pix_cola.html",
        qrcode=qr_image_url,
        valor=f"R$ {float(valor):.2f}",
        qr_code_cola=qr_code_cola,
        status=status,
        payment_id=pagamento_id,
        cpf=cpf,
        usuario_id=usuario_id
    )

#=============================================================================================


#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# - BUSCANDO PAGAMENTOS APROVADOS VIA PIX COLA 
# - OPERA NA PAGINA AGUARDANDO_CONFIRMARCAO_PAGAMENTO.HTML
@app.route('/sync_raspadinhas_aprovados', methods=['POST'])
def sync_raspadinhas_aprovados():
    try:
        dados = request.get_json()
        payment_id = dados.get('payment_id')

        if not payment_id:
            print("ERRO: NÃO VEIO O ID")
            return {"ok": False, "erro": "Falta ID"}, 400

        print(f"TENTANDO ATUALIZAR RASPADINHA COM O ID: {payment_id}")

        # BUSCA DIRETO NA COLEÇÃO DE RASPADINHA, NÃO IMPORTA O PAGAMENTO
        resultado = raspadinha_model.collection.update_many(
            {"payment_id": payment_id}, # BUSCA EXATAMENTE O NÚMERO
            {"$set": {
                "status": "approved",
                "data_atualizacao": datetime.now(timezone.utc)
            }}
        )

        print(f"QUANTIDADE ATUALIZADA: {resultado.modified_count}")

        return {
            "ok": True,
            "atualizados": resultado.modified_count
        }

    except Exception as e:
        print(f"ERRO NO SERVER: {str(e)}")
        return {"ok": False, "erro": str(e)}, 500

#---------------------------------------------------------------------------------------------
# - COMPRA SALDO CONTA
#---------------------------------------------------------------------------------------------

@app.route('/raspadinha/compra-saldo', methods=['POST'])
def compra_raspadinha_saldo():

    dados = request.get_json() or {}

    quantidade = int(dados.get("quantidade", 1))

    PRECO_UNITARIO = 0.60

    valor_total = round(quantidade * PRECO_UNITARIO, 2)

    usuario_id = dados.get("usuario_id")

    if not usuario_id or usuario_id == "None" or not ObjectId.is_valid(str(usuario_id)):

        return jsonify({
            "erro": "Usuário inválido ou não autenticado."
        }), 400

    oid = ObjectId(str(usuario_id))

    usuario = users_collection.find_one({
        "_id": oid
    })

    if not usuario:

        return jsonify({
            "erro": "Usuário não localizado."
        }), 404

    ganhos_atuais = float(usuario.get("ganhos", 0.0))

    # Verifica saldo
    if ganhos_atuais < valor_total:

        return jsonify({
            "erro": f"Saldo insuficiente! Você possui R$ {ganhos_atuais:.2f} e precisa de R$ {valor_total:.2f}."
        }), 400

    # Desconta saldo
    users_collection.update_one(

        {"_id": oid},

        {
            "$inc": {
                "ganhos": -valor_total
            },

            "$push": {
                "entradas": {
                    "tipo": "compra_com_saldo",
                    "valor": -valor_total,
                    "data": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
                }
            }
        }
    )

    # Cria raspadinhas
    cpf_usuario = usuario.get("cpf", "")
    nome = usuario.get("nome", "Usuário")

    documentos = []

    for _ in range(quantidade):

        documentos.append({

            "usuario_id": str(usuario_id),
            "cpf": cpf_usuario,
            "quantidade_raspadinhas": 1,
            "status": "approved",
            "data_compra": datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")

        })

    db["raspadinhas"].insert_many(documentos)

    # Busca usuário atualizado
    usuario_atualizado = users_collection.find_one({
        "_id": oid
    })

    novo_saldo = float(usuario_atualizado.get("ganhos", 0.0))

    saldo_formatado = f"R$ {novo_saldo:.2f}".replace(".", ",")

    # Conta raspadinhas aprovadas
    total_raspadinhas_ativas = db["raspadinhas"].count_documents({

        "cpf": cpf_usuario,
        "status": "approved"

    })


    # SOCKET
    nome_usuario = usuario.get("nome", "Usuário")

    msg_saque = f'''
    <img src="https://res.cloudinary.com/dptprh0xk/image/upload/v1778012674/icone-de-carrinho-de-compras-3d-em-fundo-de-circulo-azul-simbolo-de-varejo-online_84443-55705_dfmhp8.png"
    style="width:32px;height:32px;vertical-align:middle;margin-right:5px;">

    {nome_usuario} acabou de comprar {quantidade} saldo!
    '''

    usuarios.append({
        "id": str(usuario_id),
        "texto": msg_saque
    })

    if len(usuarios) > 8000:
        usuarios.pop(0)

    lista_texto = [u["texto"] for u in usuarios]

    socketio.emit('notificacao_geral', {
        'lista': lista_texto
    })

    return jsonify({

        "success": True,
        # "mensagem": f"🎉 Sucesso! {quantidade} raspadinha(s) comprada(s) com saldo.",
        "novoSaldoTexto": saldo_formatado,
        "novaQuantidadeTotal": total_raspadinhas_ativas

    })
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# - LISTAGEN DE TODOS OS `PAGAMENTOS`
@app.route("/raspadinhas")
def listar_raspadinhas():

    raspadinhas = raspadinha_model.get_all_raspadinhas()

    for n in raspadinhas:
        n["_id"] = str(n["_id"])

        if "usuario_id" in n and n["usuario_id"] is not None:
            n["usuario_id"] = str(n["usuario_id"])

        if "payment_id" in n and isinstance(n["payment_id"], ObjectId):
            n["payment_id"] = str(n["payment_id"])

    return jsonify({
        "raspadinhas": raspadinhas
    })
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------


@app.route("/admin", defaults={'vendedor_id': None})
@app.route("/admin/<vendedor_id>", methods=["GET"])
def fechamento_vendedores(vendedor_id=None):

    vendedor = None
    if vendedor_id:
        vendedor = vendedores_collection.find_one({
            "_id": ObjectId(vendedor_id)
        })

    cpf_vendedor = limpar_cpf(vendedor.get("cpf", "")) if vendedor else ""

    usuarios = list(users_collection.find())
    vendedores_lista = list(vendedores_collection.find())
    pagamentos = pagamento_model.get_all_pagamentos() or []
    saques = list(saques_collection.find())

    for p in pagamentos:
        p["_id"] = str(p.get("_id"))

    for s in saques:
        s["_id"] = str(s.get("_id"))

    quantidade_usuarios = len(usuarios)
    quantidade_vendedores = len(vendedores_lista)

    # Mapas de usuários para buscas rápidas
    usuarios_map = {u.get("email"): u for u in usuarios}
    usuarios_map_by_cpf = {u.get("cpf"): u for u in usuarios if u.get("cpf")}

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    total_comissao = Decimal("0")
    total_saques = Decimal("0")
    total_taxa_mp = Decimal("0")
    
    # Inicializa o resumo com base nos vendedores cadastrados
    vendedores_resumo = {}
    for v in vendedores_lista:
        nome_vendedor = v.get("nome")
        if nome_vendedor:
            vendedores_resumo[nome_vendedor] = {
                "pending": Decimal("0"),
                "approved": Decimal("0"),
                "cancelled": Decimal("0"),
                "quantidade_raspadinhas": 0,
                "comissao": Decimal("0"),
                "ganhos": Decimal("0"),  
                "saques": Decimal("0")   
            }
            
    if "vendedor" not in vendedores_resumo:
        vendedores_resumo["vendedor"] = {
            "pending": Decimal("0"), "approved": Decimal("0"), "cancelled": Decimal("0"),
            "quantidade_raspadinhas": 0, "comissao": Decimal("0"), "ganhos": Decimal("0"), "saques": Decimal("0")
        }

    faturamento_por_dia = {}
    total_quantidade_raspadinhas = 0
    usuarios_qtd = {}

    # =========================================================================
    # NOVA LÓGICA: PUXAR GANHOS E SAQUES DIRETO DO PERFIL DO USUÁRIO NO BANCO
    # =========================================================================
    for u in usuarios:
        vendedor_nome = u.get("vendedor") or "sem_vendedor"
        
        # Pega os valores direto do seu JSON de usuário (garantindo que se for nulo vira 0)
        u_ganhos = Decimal(str(u.get("ganhos", 0) or 0))
        u_saques = Decimal(str(u.get("saques", 0) or 0))
        
        if vendedor_nome not in vendedores_resumo:
            vendedores_resumo[vendedor_nome] = {
                "pending": Decimal("0"), "approved": Decimal("0"), "cancelled": Decimal("0"),
                "quantidade_raspadinhas": 0, "comissao": Decimal("0"), "ganhos": Decimal("0"), "saques": Decimal("0")
            }
            
        # Acumula no respectivo vendedor os dados reais que você precisava
        vendedores_resumo[vendedor_nome]["ganhos"] += u_ganhos
        vendedores_resumo[vendedor_nome]["saques"] += u_saques
        
        # Alimenta os totais globais do painel
        total_saques += u_saques

        # Estrutura base para a tabela auxiliar de usuários detalhados
        cpf_user = u.get("cpf")
        if cpf_user:
            usuarios_qtd[cpf_user] = {
                "nome": u.get("nome", "Desconhecido"),
                "vendedor": vendedor_nome,
                "quantidade": 0,
                "ganhos": float(u_ganhos),
                "saques": float(u_saques)
            }

    # 1. PROCESSAMENTO DE PAGAMENTOS (Apenas faturamento, quantidade e datas)
    for p in pagamentos:
        valor = Decimal(str(p.get("valor", 0)))
        status = p.get("status")
        email = p.get("email_usuario")
        usuario = usuarios_map.get(email, {})
        vendedor_nome = usuario.get("vendedor") or "sem_vendedor"

        if vendedor_nome not in vendedores_resumo:
            vendedores_resumo[vendedor_nome] = {
                "pending": Decimal("0"), "approved": Decimal("0"), "cancelled": Decimal("0"),
                "quantidade_raspadinhas": 0, "comissao": Decimal("0"), "ganhos": Decimal("0"), "saques": Decimal("0")
            }

        if status == "pending":
            total_pagamentos_pending += valor
            vendedores_resumo[vendedor_nome]["pending"] += valor

        elif status == "approved":
            total_pagamentos_approved += valor
            vendedores_resumo[vendedor_nome]["approved"] += valor

            if valor > Decimal("0.50"):
                taxa_mp = valor * Decimal("0.0099")
                taxa_arredondada = taxa_mp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_taxa_mp += taxa_arredondada

            quantidade_raspadinhas = int(p.get("quantidade_raspadinhas", 0))
            vendedores_resumo[vendedor_nome]["quantidade_raspadinhas"] += quantidade_raspadinhas
            total_quantidade_raspadinhas += quantidade_raspadinhas

            # Atualiza a contagem de raspadinhas no dicionário detalhado do usuário
            cpf_user = p.get("cpf") or usuario.get("cpf")
            if cpf_user and cpf_user in usuarios_qtd:
                usuarios_qtd[cpf_user]["quantidade"] += quantidade_raspadinhas

            data_str = p.get("data_criacao")
            if data_str:
                try:
                    data = datetime.strptime(data_str, "%a, %d %b %Y %H:%M:%S GMT")
                    dia_formatado = data.strftime("%d/%m")
                    if dia_formatado not in faturamento_por_dia:
                        faturamento_por_dia[dia_formatado] = Decimal("0")
                    faturamento_por_dia[dia_formatado] += valor
                except:
                    pass

        elif status == "cancelled":
            total_pagamentos_cancelled += valor
            vendedores_resumo[vendedor_nome]["cancelled"] += valor


    # 2. CÁLCULO DA COMISSÃO LÍQUIDA (Faturamento - Ganhos - Saques) * 20%
    for v_nome, dados in vendedores_resumo.items():
        faturamento_liquido = dados["approved"] - dados["ganhos"] - dados["saques"]
        
        if faturamento_liquido > Decimal("0"):
            comissao_calculada = faturamento_liquido * Decimal("0.20")
            dados["comissao"] = comissao_calculada
            total_comissao += comissao_calculada
        else:
            dados["comissao"] = Decimal("0")

    # 3. ENCONTRAR TOP USUÁRIO
    top_usuario = None
    if usuarios_qtd:
        top_usuario = max(
            usuarios_qtd.values(),
            key=lambda x: x["quantidade"]
        )

    # 4. FORMATAÇÃO DOS RESULTADOS DO VENDEDOR PARA O HTML
    vendedores_formatado = {
        v: {
            "pending": float(d["pending"]),
            "approved": float(d["approved"]),
            "cancelled": float(d["cancelled"]),
            "quantidade_raspadinhas": d["quantidade_raspadinhas"],
            "comissao": float(d["comissao"]),
            "ganhos": float(d["ganhos"]),
            "saques": float(d["saques"])
        }
        for v, d in vendedores_resumo.items()
    }

    # Tratamento de Projetos
    projetos = list(projetos_collection.find())
    total_investimento_premiacao = Decimal("0")
    projetos_formatados = []

    for pr in projetos:
        quantidade = pr.get("quantidade", "0")
        try:
            quantidade = int(quantidade)
        except:
            quantidade = 0

        try:
            valor_unidade = float(pr.get("valor_unidade", 0))
        except:
            valor_unidade = 0.0

        valor_inv = pr.get("valor_injetado_premiacao", 0)
        try:
            total_investimento_premiacao += Decimal(str(valor_inv))
        except:
            pass
        
        pr_copia = pr.copy()
        pr_copia["_id"] = str(pr_copia["_id"])
        projetos_formatados.append(pr_copia)

    projetos = list(projetos_collection.find())
    for p in projetos:
        p["_id"] = str(p["_id"])
        p["quantidade"] = p.get("quantidade", "")

    faturamento_por_dia = {k: float(v) for k, v in faturamento_por_dia.items()}

    # Bloco Fiscal
    faturamento_total = total_pagamentos_approved
    cfop_produto = "6.103"
    codigo_servico = "17.22"
    aliquota_futura = Decimal("0.28")
    aliquota_transicao = Decimal("0.0015")
    imposto_futuro = faturamento_total * aliquota_futura
    imposto_transicao = faturamento_total * aliquota_transicao

    if faturamento_total > Decimal("81000") / Decimal("12"):
        regime = "Simples Nacional (ME)"
    elif faturamento_total > Decimal("2112"):
        regime = "MEI"
    else:
        regime = "CPF (Isento até 2.112/mês)"

    lucro = (faturamento_total - total_taxa_mp - total_comissao - imposto_futuro)

    resumo = {
        "usuarios": quantidade_usuarios,
        "vendedores_total": quantidade_vendedores,
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "faturamento": float(total_pagamentos_approved),
        "investimento_premiacao": float(total_investimento_premiacao),
        "total_comissao": float(total_comissao),
        "taxa_mp_total": float(total_taxa_mp),
        "total_saques": float(total_saques),
        "lucro": float(lucro),
        "projetos": projetos_formatados,
        "quantidade_raspadinhas": total_quantidade_raspadinhas,
        "vendedores": vendedores_formatado,
        "faturamento_diario": faturamento_por_dia,
        "usuarios_detalhado": usuarios_qtd,
        "fiscal": {
            "cfop_produto": cfop_produto,
            "codigo_servico": codigo_servico,
            "aliquota_futura": float(aliquota_futura * 100),
            "aliquota_transicao_2026": float(aliquota_transicao * 100),
            "imposto_futuro": float(imposto_futuro),
            "imposto_transicao": float(imposto_transicao),
            "regime": regime
        }
    }

    # =========================
    # IP
    # =========================
    ip_usuario = request.headers.get("X-Forwarded-For", request.remote_addr)

    # =========================
    # USER AGENT
    # =========================
    user_agent_string = request.headers.get("User-Agent", "")
    user_agent = parse(user_agent_string)
    ua = user_agent_string.lower()

    # =========================
    # DETECÇÃO DE APARELHO
    # =========================
    aparelho = "Desconhecido"

    if "sm-a356" in ua:
        aparelho = "Samsung Galaxy A35"
    elif "sm-a346" in ua:
        aparelho = "Samsung Galaxy A34"
    elif "sm-a546" in ua:
        aparelho = "Samsung Galaxy A54"
    elif "sm-s918" in ua:
        aparelho = "Samsung Galaxy S23 Ultra"
    elif "sm-s926" in ua:
        aparelho = "Samsung Galaxy S24+"
    elif "sm-g990" in ua:
        aparelho = "Samsung Galaxy S21 FE"
    elif "sm-" in ua:
        aparelho = "Samsung"
    elif "2201117tg" in ua:
        aparelho = "Xiaomi Redmi Note 11"
    elif "22101316g" in ua:
        aparelho = "Xiaomi Redmi Note 12"
    elif "2312draf3" in ua:
        aparelho = "Xiaomi Redmi Note 13"
    elif "redmi" in ua or "xiaomi" in ua:
        aparelho = "Xiaomi"
    elif "moto g54" in ua:
        aparelho = "Motorola Moto G54"
    elif "moto g84" in ua:
        aparelho = "Motorola Moto G84"
    elif "moto" in ua:
        aparelho = "Motorola"
    elif "iphone" in ua:
        aparelho = "iPhone"
    elif "ipad" in ua:
        aparelho = "iPad"
    elif "huawei" in ua:
        aparelho = "Huawei"
    elif "asus" in ua:
        aparelho = "Asus"
    elif "lg-" in ua:
        aparelho = "LG"
    elif "realme" in ua:
        aparelho = "Realme"
    elif "oppo" in ua:
        aparelho = "Oppo"
    elif "vivo" in ua:
        aparelho = "Vivo"
    elif "nokia" in ua:
        aparelho = "Nokia"
    elif "windows nt" in ua:
        aparelho = "PC Windows"
    elif "macintosh" in ua or "mac os" in ua:
        aparelho = "MacBook / iMac"
    elif "linux" in ua and "android" not in ua:
        aparelho = "PC Linux"
    else:
        aparelho = f"{user_agent.device.family} | {user_agent.os.family}"

    # =========================
    # NAVEGADOR
    # =========================
    navegador = user_agent.browser.family

    # =========================
    # CIDADE PELO IP
    # =========================
    cidade = "Desconhecida"
    try:
        resposta = requests.get(f"http://ip-api.com/json/{ip_usuario}").json()
        cidade = f"{resposta.get('city', '')} - {resposta.get('regionName', '')}"
    except:
        pass


    return render_template(
        "graficos/eventos/Admin/index.html",
        usuarios=usuarios,
        vendedores=vendedores_lista,
        resumo=resumo,
        projetos=projetos,
        top_usuario=top_usuario,
        vendedor=vendedor,
        vendedor_id=vendedor_id,
        ip_usuario=ip_usuario,
        cidade=cidade,
        aparelho=aparelho,
        navegador=navegador        
    )


#---------------------------------------------------------------------------------------------
# - DASHBOARD FATURURAMENTO | PAGAMENTOS vs SAQUES | VENDAS POR COLABORADORES "VENDEDORES"
#---------------------------------------------------------------------------------------------
def converter_data_dashboard(string_data):
    if not string_data:
        return None
        
    # Se o banco já trouxe como objeto datetime nativo do Python, usa direto
    if isinstance(string_data, datetime):
        return string_data

    try:
        string_suja = str(string_data).strip()
        
        # Tenta o formato ISO comum: "2026-05-21 16:17:45"
        try:
            return datetime.strptime(string_suja, "%Y-%m-%d %H:%M:%S")
        except:
            pass
            
        try:
            return datetime.strptime(string_suja, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            pass

        # Fallback do Regex do Copilot para o formato "Thu, 21 May 2026 16:17:45 GMT"
        match = re.search(r'(\d{2}).*?(\d{4})\s+(\d{2}):(\d{2}):(\d{2})', string_suja)
        if match:
            dia = int(match.group(1))
            ano = int(match.group(2))
            hora = int(match.group(3))
            minuto = int(match.group(4))
            segundo = int(match.group(5))
            
            mes = 5  # Maio fixo baseado no seu banco
            if "Jun" in string_suja: mes = 6
            elif "Jul" in string_suja: mes = 7
            elif "Apr" in string_suja: mes = 4
            
            return datetime(ano, mes, dia, hora, minuto, segundo)
            
    except Exception as e:
        print(f"Erro na conversão de data: {e}")
        
    return None

#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

@app.route("/api/dados-dashboard")
def dados_dashboard():
    pagamentos = pagamento_model.get_all_pagamentos() or []
    saques = get_all_saques() or []

    # --- 1. FATURAMENTO ---
    labels_faturamento = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '23:59']
    valores_faturamento = [0.0] * 7
    hoje = datetime.today().date()

    for p in pagamentos:
        if p.get("status") == "approved":
            data_pg = converter_data_dashboard(p.get("data_criacao"))
            if data_pg and data_pg.date() == hoje:
                hora = data_pg.hour
                valor = float(p.get("valor", 0))
                if hora < 4: valores_faturamento[0] += valor
                elif hora < 8: valores_faturamento[1] += valor
                elif hora < 12: valores_faturamento[2] += valor
                elif hora < 16: valores_faturamento[3] += valor
                elif hora < 20: valores_faturamento[4] += valor
                elif hora < 24: valores_faturamento[5] += valor

    # --- 2. SEMANAL (SAQUES E PAGAMENTOS) ---
    labels_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    dados_pagamentos_semana = [0.0] * 7
    dados_saques_semana = [0.0] * 7

    for p in pagamentos:
        if p.get("status") == "approved":
            data_pg = converter_data_dashboard(p.get("data_criacao"))
            if data_pg:
                dados_pagamentos_semana[data_pg.weekday()] += float(p.get("valor", 0))

    for s in saques:
        # Se os saques não usarem "criado_em", ele tenta buscar por "data_criacao" igual aos pagamentos
        data_origem = s.get("criado_em") or s.get("data_criacao")
        data_sq = converter_data_dashboard(data_origem) 
        
        if data_sq:
            # Garante que pegue a chave certa do valor do saque que está no banco (valor_saque)
            valor_s = s.get("valor_saque") or s.get("valor", 0)
            dados_saques_semana[data_sq.weekday()] += float(valor_s)

    return jsonify({
        "faturamento": {
            "labels": labels_faturamento,
            "data": [float(round(v, 2)) for v in valores_faturamento]
        },
        "semanal": {
            "labels": labels_semana,
            "pagamentos": [float(round(p, 2)) for p in dados_pagamentos_semana],
            "saques": [float(round(s, 2)) for s in dados_saques_semana]
        }
    })


from user_agents import parse
import requests


# =============================================
# UPLOAD ARQUIVOS
# =============================================
@app.route('/upload', methods=['POST'])
def upload_arquivo():

    try:

        if 'file' not in request.files:

            return jsonify({
                "erro": "Arquivo não enviado"
            }), 400

        file = request.files['file']

        if file.filename == '':

            return jsonify({
                "erro": "Arquivo vazio"
            }), 400

        # =====================================
        # MIME TYPE
        # =====================================
        mimetype = file.mimetype

        resource_type = "raw"

        if mimetype.startswith("image/"):

            resource_type = "image"

        elif (
            mimetype.startswith("video/")
            or
            mimetype.startswith("audio/")
        ):

            resource_type = "video"

        # =====================================
        # CLOUDINARY
        # =====================================
        upload_result = cloudinary.uploader.upload(

            file,

            resource_type=resource_type,

            folder="saques"

        )

        secure_url = upload_result.get(
            "secure_url"
        )

        return jsonify({

            "url": secure_url,
            "tipo": mimetype

        })

    except Exception as e:

        print("ERRO UPLOAD:", e)

        return jsonify({
            "erro": str(e)
        }), 500

@app.route('/saques/mensagens/<usuario_id>')
def listar_mensagens_saques(usuario_id):

    saques = get_all_saques() or []

    mensagens = []

    for s in saques:

        # filtra só do usuário correto
        if str(s.get("identificacao")) != str(usuario_id):
            continue

        msgs = s.get("mensagens_solicitando_saques", [])
        mensagens.extend(msgs)

    return jsonify({
        "mensagens": mensagens
    })
#--------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# Armazena todas as mensagens enviadas pelos usuários para vendedores
mensagens = []
connected_clients = {}

def get_private_room(usuario_id, vendedor_id):
    return f"chat_{usuario_id}_{vendedor_id}"


# ========================================
# CHAT DO VENDEDOR
# ========================================
@app.route("/chat/vendedor/<vendedor_id>")
@app.route("/chat/vendedor/<vendedor_id>/<usuario_id>")
def chat_vendedores(vendedor_id=None, usuario_id=None):

    # ========================================
    # VENDEDOR LOGADO
    # ========================================
    vendedor = vendedores_collection.find_one({
        "_id": ObjectId(vendedor_id)
    })

    # ========================================
    # USUÁRIO SELECIONADO
    # ========================================
    usuario = None

    if usuario_id:

        usuario = users_collection.find_one({
            "_id": ObjectId(usuario_id)
        })

    # ========================================
    # LISTA USUÁRIOS
    # ========================================
    usuarios = list(users_collection.find())

    # ========================================
    # RENDER
    # ========================================
    return render_template(

        "graficos/eventos/sala_saques_admin.html",

        # VENDEDOR LOGADO
        vendedor=vendedor,

        # USUÁRIO ATUAL
        usuario=usuario,

        # LISTA
        usuarios=usuarios,

        # IDS CORRETOS
        vendedor_id=str(vendedor["_id"]),

        usuario_id=str(usuario["_id"])
        if usuario else "",

        # NOMES
        nome_vendedor=vendedor["nome"]
        if vendedor else "Vendedor",

        nome_usuario=usuario["nome"]
        if usuario else "Usuário",

        # FIXO
        tipo="vendedor",

        # ID REAL LOGADO
        meu_id=str(vendedor["_id"])
    )

# ========================================
# CHAT DO USUÁRIO
# ========================================
@app.route("/chat/usuario/<usuario_id>")
@app.route("/chat/usuario/<usuario_id>/<vendedor_id>")
def chat_users(usuario_id=None, vendedor_id=None):

    # ========================================
    # USUÁRIO LOGADO
    # ========================================
    usuario = users_collection.find_one({
        "_id": ObjectId(usuario_id)
    })

    # ========================================
    # VENDEDOR SELECIONADO
    # ========================================
    vendedor = None

    if vendedor_id:

        vendedor = vendedores_collection.find_one({
            "_id": ObjectId(vendedor_id)
        })

    # ========================================
    # LISTAS SIDEBAR
    # ========================================
    vendedores = list(vendedores_collection.find())

    usuarios = list(users_collection.find())
    # texto = request.args.get("text")
    # ========================================
    # RENDER
    # ========================================
    return render_template(

        "graficos/eventos/sala_saque_usuarios.html",

        # USUÁRIO LOGADO
        usuario=usuario,

        # LISTAS
        usuarios=usuarios,
        vendedores=vendedores,

        # VENDEDOR ATUAL
        vendedor=vendedor,

        # IDS
        usuario_id=str(usuario["_id"]),
        vendedor_id=str(vendedor["_id"]) if vendedor else "",

        # NOMES
        nome_usuario=usuario["nome"] if usuario else "Usuário",
        nome_vendedor=vendedor["nome"] if vendedor else "Vendedor",

        # TIPO FIXO
        tipo="usuario",
        # texto=texto,
        

        # ID REAL DE QUEM ESTÁ LOGADO
        meu_id=str(usuario["_id"])
    )




# VEJA O (vendedor_id) DENTRO DA FUNÇÃO ABAIXO:
@app.route("/conversa/<vendedor_id>")
def conversas(vendedor_id):  # <- Faltava colocar o vendedor_id aqui!
    try:
        # Seu código que busca no banco...
        vendedor = vendedores_collection.find_one({"_id": vendedor_id})
        lista_usuarios = list(users_collection.find({"vendedor_id": str(vendedor_id)}))

        for usuario in lista_usuarios:
            usuario["_id"] = str(usuario["_id"])

        return render_template(
            "graficos/eventos/Admin/conversas.html", 
            vendedor=vendedor, 
            usuarios=lista_usuarios
        )
    except Exception as e:
        print("ERRO NA ROTA DE CONVERSAS:", e)
        return f"Erro interno: {str(e)}", 500


# =============================================
# ROTA PARA BUSCAR HISTÓRICO DE MENSAGENS
# =============================================
@app.route('/historico/<id_usuario>/<id_vendedor>', methods=['GET'])
def obter_historico_chat(id_usuario, id_vendedor):
    try:
        # Busca no banco
        mensagens_raw = mensagem_model.get_historico_chat(str(id_usuario), str(id_vendedor))
        
        # Garante que cada mensagem tenha o campo 'lida'
        historico = []
        for msg in mensagens_raw:
            # Em vez de dict(msg), acesse explicitamente os campos
            msg_final = {
                "id": str(msg.get("_id", "")),
                "from_id": str(msg.get("from_id", "")),
                "mensagem": msg.get("mensagem", ""),
                "arquivo": msg.get("arquivo", ""),
                "arquivo_tipo": msg.get("arquivo_tipo", ""),
                "timestamp": msg.get("criado_em"), 
                "lida": bool(msg.get("lida", False)) 
            }
            historico.append(msg_final)
            
        return jsonify(historico), 200
    except Exception as e:
        print("ERRO NA ROTA:", e)
        return jsonify({"erro": str(e)}), 500

# =============================================
# ENVIO DE MENSAGENS PRIVADAS
# =============================================
@socketio.on("private_message")
def handle_private_message(data):
    from_tipo = data.get("from_tipo")
    from_id = str(data.get("from_id"))
    to_tipo = data.get("to_tipo")
    to_id = str(data.get("to_id"))
    mensagem = data.get("mensagem", "")
    arquivo = data.get("arquivo", "")
    arquivo_tipo = data.get("arquivo_tipo", "")

    if not all([from_tipo, from_id, to_tipo, to_id]):
        emit("error", {"msg": "Dados de envio incompletos."})
        return

    try:
        # 1. SALVA NO MONGODB (Usando a estrutura do seu models.py)
        # Passa a URL do Cloudinary (arquivo) e o tipo se houver
        salvar_mensagem(
            from_tipo=from_tipo,
            from_id=from_id,
            to_tipo=to_tipo,
            to_id=to_id,
            mensagem=mensagem,
            arquivo=arquivo,
            arquivo_tipo=arquivo_tipo
        )
    except Exception as e:
        print("ERRO AO SALVAR MENSAGEM NO BANCO:", e)
        # Mesmo se o banco falhar, o chat envia em tempo real para não travar a experiência


    # 2. PREPARA O PACOTE PARA O FRONTEND
    agora = datetime.now()
    dados_mensagem = {
        "from_tipo": from_tipo,
        "from_id": from_id,
        "to_tipo": to_tipo,
        "to_id": to_id,
        "mensagem": mensagem,
        "data_hora": agora.strftime("%d/%m/%Y %H:%M"),
        "hora": agora.strftime("%H:%M"),
        "arquivo": arquivo,          # Link do Cloudinary limpo enviado via socket
        "arquivo_tipo": arquivo_tipo  # 'imagem', 'video', 'audio', 'pdf'
    }

    # Pega o ID da sala combinada
    room = get_private_room(from_id, to_id)

    # Envia para todos conectados dentro desta sala privada específica
    socketio.emit("new_message", dados_mensagem, room=room)


# Função auxiliar crucial para unificar as salas
def get_private_room(id1, id2):
    # Organiza os IDs em ordem alfabética para que a sala seja idêntica para os dois
    ordenados = sorted([str(id1), str(id2)])
    return f"room_{ordenados[0]}_{ordenados[1]}"

# =============================================
# REGISTRO SOCKET
# =============================================
@socketio.on("register")
def handle_register(data):
    tipo = data.get("tipo")
    id_ = str(data.get("id"))
    conversando_com_id = data.get("conversando_com_id") 

    if not tipo or not id_:
        emit("error", {"msg": "Dados inválidos no registro"})
        return

    print(f"Cliente registrado: {tipo} {id_}")

    # Se ele está com um chat aberto, coloca ele na sala privada correta
    if conversando_com_id and str(conversando_com_id).strip() != "":
        room = get_private_room(id_, str(conversando_com_id))
        join_room(room)
        print(f"ID {id_} entrou na sala privada ativa: {room}")

# =============================================
# DESCONECTAR
# =============================================
@socketio.on("disconnect")
def handle_disconnect():
    for key, sid in list(connected_clients.items()):
        if sid == request.sid:
            del connected_clients[key]
            print(f"Cliente {key} desconectado.")
            break



# =============================================
# EVENTO DE DIGITAÇÃO (USUÁRIO <-> VENDEDOR)
# =============================================
@socketio.on("typing_status")
def handle_typing_status(data):
    from_id = data.get("from_id")
    to_id = data.get("to_id")
    is_typing = data.get("is_typing")
    
    room = get_private_room(from_id, to_id)
    # Repassa o status de digitação para a outra pessoa na sala privada
    socketio.emit("user_typing", {"from_id": from_id, "is_typing": is_typing}, room=room, include_self=False)
#---------------------------------------------------------------------------------------------



@socketio.on('message_read')
def handle_message_read(data):
    message_id = data.get('message_id')
    from_id = data.get('from_id')
    to_id = data.get('to_id')
    
    if not message_id:
        return

    from bson import ObjectId
    try:
        query_id = ObjectId(message_id)
        
        # ACESSO CORRETO: Usando a collection dentro do model que você instanciou
        resultado = mensagem_model.collection.update_one(
            {"_id": query_id},
            {"$set": {"lida": True}}
        )
        
        if resultado.matched_count > 0:
            room = get_private_room(from_id, to_id)
            socketio.emit('message_read_confirm', {'message_id': message_id}, room=room, include_self=False)
        else:
            print(f"DEBUG: Nenhuma mensagem encontrada com o ID {message_id}")
            
    except Exception as e:
        print(f"ERRO NO UPDATE: {e}")
        
from bson import json_util
from flask import Response

@app.route('/debug/ver_mensagens', methods=['GET'])
def debug_mensagens_reais():
    try:
        # Acessa a collection através da instância que você já usa no projeto
        docs = list(mensagem_model.collection.find({}))
        
        from bson import json_util
        from flask import Response
        
        json_data = json_util.dumps({"quantidade": len(docs), "dados": docs})
        return Response(json_data, mimetype='application/json')
    except Exception as e:
        return str(e), 500

#---------------------------------------------------------------------------------------------
@socketio.on('conectar_chamada')
def handle_conectar_chamada(data):
    # O front-end envia quem está logado no momento (pode ser o usuario_id ou vendedor_id)
    meu_id = data['meu_id']
    join_room(str(meu_id))
    print(f"ID {meu_id} entrou na sala de sinalização de voz.")

@socketio.on('enviar-convite-chamada')
def handle_call_offer(data):
    # Quem está recebendo a chamada (se o usuario ligou, o destino é vendedor_id e vice-versa)
    destino_id = data['destino_id']
    emit('receber-convite-chamada', {
        'origem_id': data['origem_id'],
        'dadosConexao': data['dadosConexao']
    }, room=str(destino_id))

@socketio.on('responder-chamada')
def handle_call_answer(data):
    destino_id = data['destino_id']
    emit('chamada-aceita', {
        'dadosConexao': data['dadosConexao']
    }, room=str(destino_id))

@socketio.on('enviar-ice-candidate')
def handle_ice_candidate(data):
    destino_id = data['destino_id']
    emit('receber-ice-candidate', {
        'candidate': data['candidate']
    }, room=str(destino_id))
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )

