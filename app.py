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
import hmac
import hashlib
from io import BytesIO
import base64
import qrcode
import fitz
import re
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
from bson.objectid import ObjectId
from models import criar_usuario, users_collection, pagamentos_collection, criar_documento_pagamento, PagamentoModel,  criar_vendedor, vendedores_collection
from models import  bilhetes_collection, criar_documento_bilhete, BilheteModel
from models import criar_projeto
from models import projetos_collection
from models import criar_saque, saques_collection
from models import get_all_saques
from flask_cors import CORS
from datetime import datetime, timezone
import time
import uuid
import io
import json

load_dotenv()

app = Flask(__name__)
CORS(app)
# ---------------- MONGODB ----------------
client = MongoClient(os.getenv("MONGO_URI"))
pagamento_model = PagamentoModel()
bilhete_model = BilheteModel()
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("APP_SECRET_KEY")
notification_url = os.getenv("NOTIFICATION_URL")
premiacao1 = os.getenv("PREMIACAO1")
dt_sort = os.getenv("SORTEIO")
cfop_fora_estado = os.getenv("CFOP_FORA_ESTADO")
cfop_estado = os.getenv("CFOP_ESTADO")
codigo_servico =  os.getenv("CODIGO_SERVICO")
ncm = os.getenv("NCM")



# ---------------- CLOUDINARY ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

@app.route("/")
def produtos():
    return render_template("Produtos/minha_pagina.html")
#================================================================================
# Limpar cpf
def limpar_cpf(cpf):
    if not cpf:
        return None
    return ''.join(filter(str.isdigit, cpf))
#---------------------------------------------------------------------------------
#=================================================================================
#=================================================================================politica-privacidade
# PAGINA INICIAL DO USUARIOS OPÇOES
#/ferrari-tech/tecnlogia
@app.route("/vitoria-visonaria_franca-sp")
def options():
    return render_template("opcoes.html")
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/politica-privacidade")
def politica_privacidade():
    return render_template("termos.html")   

#=================================================================================
# REGISTRAR USUARIOS
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        data = request.get_json(force=True)
        print("CHEGOU NO BACK:", data)

        estado = (data.get("estado") or "").strip().upper()

        usuario = criar_usuario(
            data.get("nome", ""),
            data.get("sobrenome", ""),
            data.get("cpf", ""),
            data.get("dt_nascimento", ""),
            data.get("email", ""),
            estado,
            data.get("vendedor", "Plataforma Ferrari Tech"),
            data.get("chave_pix", "")
        )

        return jsonify({"status": "sucesso", "usuario": usuario}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
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

        cpf = str(data["cpf"]).strip()

        usuario = users_collection.find_one({"cpf": cpf})

        if not usuario:
            return jsonify({"status": "erro", "mensagem": "CPF não encontrado"}), 404

        return jsonify({
            "status": "sucesso",
            "usuario_id": str(usuario["_id"])
        }), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------
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
# 📄 PÁGINA PRINCIPAL
@app.route("/vitoria_visionaria/projeto-desenvolvimento-fase-teste/codigo_servico/1722/<usuario_id>/<projeto_id>")
def view_pagamentos(usuario_id, projeto_id):

 

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

    if not usuario_id:
        return redirect("/vitoria-visonaria_franca-sp")

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404

    email = (usuario.get("email") or usuario.get("email_usuario") or "").strip().lower()
    cpf = limpar_cpf(usuario.get("cpf"))

    # BILHETES
    bilhetes = bilhete_model.get_all_bilhetes() or []
    bilhetes = [
        b for b in bilhetes
        if (
            b.get("email_usuario", "").strip().lower() == email and
            limpar_cpf(b.get("cpf")) == cpf and
            b.get("status") == "approved"
        )
    ]

    lista_urls_img_bilhetes = set()
    for b in bilhetes:
        for img in b.get("lista_urls_img_bilhetes", []):
            lista_urls_img_bilhetes.add(img)

    numeros_aprovados = set()
    for b in bilhetes:
        for n in b.get("lista_numeros", []):
            numeros_aprovados.add(limpar_numero(n))

    # USUÁRIOS
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

    # PROJETOS
    projetos = list(projetos_collection.find())
    for p in projetos:
        p["_id"] = str(p["_id"])
        p["nome_projeto"] = p.get("nome_projeto", "")
        p["imagem_projeto"] = p.get("imagem_projeto", "")
        p["dt_sorteio"] = p.get("dt_sorteio", "")
        p["link_instagram"] = p.get("link_instagram", "")
        p["quantidade"] = p.get("quantidade", "")

        vendidos = len(numeros_aprovados)
        p["progresso_meta"] = calcular_meta_vendas(vendidos, p["quantidade"])

        if p["dt_sorteio"] != "Meta 80%" and isinstance(p["dt_sorteio"], str):
            partes = p["dt_sorteio"].split("-")
            if len(partes) == 3:
                p["dt_sorteio"] = f"{partes[2]}/{partes[1]}/{partes[0]}"

    projeto_principal = projetos[0] if projetos else {}

    return render_template(
        "index.html",
        usuario=usuario,
        usuarios=usuarios,
        projetos=projetos,
        bilhetes=bilhetes,
        projeto_principal=projeto_principal,
        projeto_id=projeto_id
    )
#----------------------------------------------------------------------    
@app.route("/vitoria_visonaria/gerar_cupom/<usuario_id>/<projeto_id>")
def numeros(usuario_id, projeto_id):

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404




    return render_template(
        "gerar_numero.html",
        usuario=usuario,
        usuario_id=usuario_id,
        projeto_id=projeto_id
    )

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
@app.route("/clientes", methods=["GET"])
def clientes_usuarios_cadastrados():
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


        estado = data.get("estado", "").strip()
        email = data.get("email", "").strip()
        chave_pix = data.get("chave_pix", "").strip()

        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "estado": estado,
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
                "estado": u.get("estado", ""),
                "vendedor": u.get("vendedor", ""),
                "chave_pix": u.get("chave_pix", "")
                
            })

        return jsonify({"status": "sucesso", "usuarios": usuarios}), 200

    except Exception as e:
        print("ERRO /usuarios:", e)  # 👈 MUITO IMPORTANTE PRA DEBUG
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

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
# ATUALIZA PAYMENT_ID NUMERO DO USUARIO "TESTADO (OK)"" 
#=============================================================================================         
@app.route("/payment_qrcode_pix/pagamento_pix/<usuario_id>")
def pagamento_pix(usuario_id):

    import json

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

    payment_data = {
        "transaction_amount": float(valor_total),
        "description": "Servico Digital",
        "payment_method_id": "pix",
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
                        "payment_id": payment_id
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

    payment_data = {
        "items": [
            {
                # "id": str(uuid.uuid4()),
                "title": "Servico Digital",
                "description": "Servico digital",
                "quantity": quantidade,
                "currency_id": "BRL",
                "unit_price": valor_unitario,
                "category_id": "services"
            }
        ],
        "payer": {
            "email": email,
            "first_name": nome,
            "last_name": sobrenome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },
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
        payment_id=str(preference_id),
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
                    "payment_id": preference_id
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
#----------------------------------------------------------------------------------------------------------------------------------------------------
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

        vendedor = criar_vendedor(
            data.get("nome", ""),
            data.get("sobrenome", ""),
            data.get("cpf", ""),
            data.get("dt_nascimento", ""),
            data.get("email", ""),
            data.get("chave_pix", ""),
            data.get("comissao", "30%")
        )

        return jsonify({"status": "sucesso", "vendedor": vendedor}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
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
            return jsonify({"status": "erro", "mensagem": "CPF não encontrado"}), 404

        return jsonify({
            "status": "sucesso",
            "vendedor_id": str(vendedor["_id"])
        }), 200

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
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
                "chave_pix": u.get("chave_pix", "")
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
@app.route("/vendedores", methods=["GET"])
def vendedores_usuarios_cadastrados():
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
    usuarios = list(users_collection.find())
    vendedores = list(vendedores_collection.find())
    pagamentos = pagamento_model.get_all_pagamentos() or []
    saques = get_all_saques() or []  # 🔥 SAQUES

    for p in pagamentos:
        p["_id"] = str(p.get("_id"))

    for s in saques:
        s["_id"] = str(s.get("_id"))

    quantidade_usuarios = len(usuarios)
    quantidade_vendedores = len(vendedores)

    usuarios_map = {u.get("email"): u for u in usuarios}

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    total_saques = Decimal("0")  # 🔥 NOVO
    total_taxa_mp = Decimal("0")

    numeros_aprovados = []
    vendedores = {}

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

    # 🔥 PAGAMENTOS
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
                "taxa_mp": Decimal("0")
            }

        if status == "pending":
            total_pagamentos_pending += valor
            vendedores[vendedor]["pending"] += valor

        elif status == "approved":
            total_pagamentos_approved += valor
            vendedores[vendedor]["approved"] += valor

            # 🔥 TAXA MP (do banco)
            taxa_mp = Decimal(str(p.get("taxa_mp", 0)))
            total_taxa_mp += taxa_mp
            vendedores[vendedor]["taxa_mp"] += taxa_mp

            # 🔥 FATURAMENTO MÊS
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

    # 🔥 SAQUES
    for s in saques:
        try:
            valor_saque = Decimal(str(s.get("valor_saque", 0)))
            total_saques += valor_saque
        except:
            pass

    vendedores_formatado = {
        v: {
            "pending": float(d["pending"]),
            "approved": float(d["approved"]),
            "cancelled": float(d["cancelled"]),
            "numeros": d["numeros"],
            "taxa_mp": float(d["taxa_mp"]),
        } for v, d in vendedores.items()
    }

    faturamento_por_mes = {k: float(v) for k, v in faturamento_por_mes.items()}

    resumo = {
        "usuarios": quantidade_usuarios,
        "vendedores": quantidade_vendedores,
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "faturamento": float(total_pagamentos_approved),
        "taxa_mp_total": float(total_taxa_mp),
        "total_saques": float(total_saques),
        "numeros_aprovados": len(numeros_aprovados),
        "lista_numeros_aprovados": numeros_aprovados,
        "vendedores": vendedores_formatado,
        "faturamento_mensal": faturamento_por_mes
    }

    return render_template(
        "graficos/extratos_mercado_pago.html",
        usuarios=usuarios,
        vendedores=vendedores,
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
    bilhetes = [b for b in bilhetes if b.get("status") == "pending"]

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
                           projeto_principal=projeto_principal) # Enviado para o HTML

# Evento para disparar o sorteio

#---------------------------------------------------------------------------------------------
# SALA ONLINE ADMIN SALA SORTEIO RESTRITA DOS USUÁRIOS

@app.route("/sala_online/admin/<projeto_id>")
def sala_ao_vivo_admin(projeto_id):

    projeto = projetos_collection.find_one({
        "_id": ObjectId(projeto_id)
    })

    if not projeto:
        return "Projeto não encontrado", 404

    # trazer nome_projeto
    nome_projeto = projeto.get("nome_projeto")

    bilhetes = BilheteModel().get_all_bilhetes() or []

    bilhetes = [
        b for b in bilhetes
        if b.get("status") == "pending"
    ]

    return render_template(
        "graficos/sala_onlline_admin.html",
        bilhetes=bilhetes,
        projeto_id=projeto_id,
        projeto=projeto,
        nome_projeto=nome_projeto
    )

# EVENTO QUE SALVA NO BANCO
@socketio.on('enviar_numero', namespace='/sorteio')
def receber_numero(data):
    numero = data.get('numero')
    projeto_id = data.get('projeto_id') # CAPTURADO DO JS

    if numero and projeto_id:
        # ATUALIZA O BANCO DE DADOS REAL
        projetos_collection.update_one(
            {"_id": ObjectId(projeto_id)},
            {"$push": {"numeros_sorteados": numero}}
        )

    # ENVIA PARA TODOS
    socketio.emit(
        'novo_numero',
        {'numero': numero},
        namespace='/sorteio'
    )


#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
# =========================
# APP.PY
# =========================

from bson.objectid import ObjectId



#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
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

    # Pega bilhetes pendentes do usuário
    bilhetes = BilheteModel().get_all_bilhetes() or []
    bilhetes_usuario = [b for b in bilhetes if b.get("usuario_id") == usuario_id and b.get("status") == "pending"]

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
# Evento para disparar o sorteio
# @socketio.on('enviar_numero', namespace='/sorteio')
# def receber_numero(data):
#     numero = data.get('numero')

#     print(f"Número enviado: {numero}")

#     socketio.emit(
#         'novo_numero',
#         {'numero': numero},
#         namespace='/sorteio'
#     )


#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------
@app.route("/vitoria_visionaria/projeto-desenvolvimento-fase-teste/codigo_servico/1722/<usuario_id>")
def eventos_semana(usuario_id):

    try:
        if not usuario_id:
            return redirect("/vitoria-visonaria_franca-sp")

        usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})

        if not usuario:
            return "usuário não encontrado", 404

        projetos = list(projetos_collection.find())

        for p in projetos:
            p["_id"] = str(p["_id"])

        return render_template(
            "graficos/eventos/eventos.html",
            projetos=projetos,
            usuario_id=usuario_id
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

@app.route('/pagamento/cartao_credito/<usuario_id>/<projeto_id>')
def home(usuario_id, projeto_id):

    usuario = users_collection.find_one({"_id": ObjectId(usuario_id)})
    if not usuario:
        return "usuário não encontrado", 404
        
    bilhetes = BilheteModel().get_all_bilhetes() or []

    bilhetes = [b for b in bilhetes if b.get("status") == "pending"]

    return render_template(
        'graficos/Pagamentos/cartao_credito.html',
        public_key=MP_PUBLIC_KEY,
        usuario=usuario,
        projeto_id=projeto_id,
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

    import json

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
            lista_numeros=lista_numeros
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
# @app.route('/payments', methods=['GET'])
# def list_payments():
#     try:
#         # Busca todos os pagamentos
#         payments = list(payments_col.find({}, {"_id": 0}))  # remove o _id interno do Mongo

#         return jsonify(payments), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#===========================================
# -Run
#===========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )








