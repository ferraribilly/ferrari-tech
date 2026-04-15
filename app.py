from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from flask_socketio import SocketIO, join_room, emit
import threading
from decimal import Decimal, ROUND_HALF_UP
import matplotlib.pyplot as plt
from threading import Thread
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
from bson.objectid import ObjectId
from models import criar_usuario, users_collection, pagamentos_collection, criar_documento_pagamento, PagamentoModel,  criar_vendedor, vendedores_collection
from models import  bilhetes_collection, criar_documento_bilhete, BilheteModel
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
bilhete = BilheteModel()
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("APP_SECRET_KEY")  
premiacao1 = os.getenv("PREMIACAO1")
dt_sort = os.getenv("SORTEIO")
   
#================================================================================
# Limpar cpf
def limpar_cpf(cpf):
    if not cpf:
        return None
    return ''.join(filter(str.isdigit, cpf))
#---------------------------------------------------------------------------------
#=================================================================================
#=================================================================================
@app.route("/")
def options():
    return render_template("opcoes.html")
#=================================================================================
# REGISTRAR USUARIOS
@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        data = request.get_json(force=True)
        print("CHEGOU NO BACK:", data)

        usuario = criar_usuario(
            data.get("nome", ""),
            data.get("sobrenome", ""),
            data.get("cpf", ""),
            data.get("dt_nascimento", ""),
            data.get("email", ""),
            data.get("vendedor", ""),
            data.get("chave_pix", "")
        )

        return jsonify({"status": "sucesso", "usuario": usuario}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------
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
            data.get("chave_pix", "")
        )

        return jsonify({"status": "sucesso", "vendedor": vendedor}), 201

    except Exception as e:
        print("ERRO:", e)
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
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
#=================================================================================
#=================================================================================
# INTERFACE REGISTRO>HTML 
@app.route("/registro")
def registro():
    # aqui vai listar todos os vendedores cadastrados com nome 
    vendedores = list(vendedores_collection.find({}, {"nome": 1}))

    return render_template(
        "registro.html",
        vendedores=vendedores
    )    




#---------------------------------------------------------------------------------
#---------------------------------------------------------------------------------
# INTERACE USUARIOS LOGIN>>HTML
@app.route("/login")
def interface_login():
    return render_template("login.html")

#---------------------------------------------------------------------------------




# 🔓 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")




#------------------------------------------------------------------------------------
# ROTA DE PARTICIPACAO
@app.route("/dia_das_maes")
def index():

    usuario_id = request.args.get("id")
    if not usuario_id:
        return redirect("/")

    pagamentos = pagamento_model.get_all_pagamentos() or []

    for p in pagamentos:
        p["_id"] = str(p.get("_id"))

    total_pagamentos_approved = Decimal("0")

    pagamentos_usuario = pagamento_model.get_pagamentos_by_usuario(usuario_id) or []
    for p in pagamentos_usuario:
        p["_id"] = str(p.get("_id"))

    usuarios = []
    for u in users_collection.find():
        usuarios.append({
            "_id": str(u.get("_id")),
            "nome": u.get("nome", ""),
            "cpf": u.get("cpf", ""),
            "email": u.get("email", ""),
            "vendedor": u.get("vendedor", ""),
            "chave_pix": u.get("chave_pix", "")
        })

    numeros_aprovados = []

    for p in pagamentos:
        if p.get("status") == "approved":
            total_pagamentos_approved += Decimal(str(p.get("valor", 0)))

            try:
                lista = json.loads(p.get("lista_numeros", "[]"))
                numeros_aprovados.extend(lista)
            except:
                pass

    resumo = {
        "pagamentos": {
            "approved": float(total_pagamentos_approved)
        },
        "numeros_aprovados": len(numeros_aprovados),
        "lista_numeros_aprovados": numeros_aprovados
    }

    return render_template(
        "index.html",
        usuario_id=usuario_id,
        resumo=resumo,
        pagamentos_usuario=pagamentos_usuario,
        pagamentos=pagamentos,
        usuarios=usuarios
    )


#------------------------------------------------------------------------------------
# Rota de acesso ao gerador de numeros 
@app.route("/gerar_numero/<id>")
def numeros(id):
    usuario = users_collection.find_one({"_id": ObjectId(id)})
    
    if not usuario:
        return "Usuário não encontrado", 404

    return render_template(
        "gerar_numero.html",
        premiacao1=premiacao1,
        usuario=usuario,
        usuario_id=id
    )


# Rota de acesso a Tabela De Nomes e Gerador Bilhetes
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
    



@app.route("/fechamento", methods=["GET"])
def fechamento():
    usuarios = list(users_collection.find())
    pagamentos = pagamento_model.get_all_pagamentos()

    for p in pagamentos:
        p["_id"] = str(p["_id"])

    quantidade_usuarios = len(usuarios)

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    # lista de todos os números aprovados
    numeros_aprovados = []

    for p in pagamentos:
        valor = Decimal(str(p.get("valor", 0)))
        if p.get("status") == "pending":
            total_pagamentos_pending += valor
        elif p.get("status") == "approved":
            total_pagamentos_approved += valor

            # pegar lista_numeros e somar
            lista_raw = p.get("lista_numeros", "[]")
            try:
                lista = json.loads(lista_raw)
                numeros_aprovados.extend(lista)
            except Exception:
                pass
        elif p.get("status") == "cancelled":
            total_pagamentos_cancelled += valor

    resumo = {
        "usuarios": quantidade_usuarios,
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "faturamento": float(total_pagamentos_approved),
        "numeros_aprovados": len(numeros_aprovados),   # total de números aprovados
        "lista_numeros_aprovados": numeros_aprovados   # lista completa dos números aprovados
    }

    return render_template("fechamento.html", usuarios=usuarios, resumo=resumo)


def get_pagamento_by_id(self, id):
    return self.collection.find_one({"_id": id})

#=============================================================================================================================================================================
W, H = 900, 450

@app.route("/gerar-bilhete", methods=["POST"])
def gerar_bilhete():

    data = request.json

    numero_bilhete = f"Nº {data['numero']}"
    evento = "Pix no Bolso "
    descricao = "Prêmio: R$ 150,00 via Pix"
    data_sorteio = "Sorteio: Quartas e domingos"

    nome = data["nome"]
    email = data["email"]
    cpf = data["cpf"]
    cpf_mask = f"{cpf[:3]}.***.***-{cpf[9:11]}"

    link_qrcode = "https://ferrari-tech.onrender.com"
    caminho_logo = "static/w.png"

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
        f_titulo = ImageFont.truetype("arialbd.ttf", 36)
        f_texto = ImageFont.truetype("arial.ttf", 24)
        f_label = ImageFont.truetype("arialbd.ttf", 20)
        f_num = ImageFont.truetype("arialbd.ttf", 28)
    except:
        f_titulo = f_texto = f_label = f_num = ImageFont.load_default()

    if os.path.exists(caminho_logo):
        logo = Image.open(caminho_logo).convert("RGBA")
        logo.thumbnail((100, 60))
        img.paste(logo, (cx1 + 20, cy1 + 20), logo)

    draw.text((cx1 + 140, cy1 + 25), evento, font=f_titulo, fill=(0, 0, 0))
    draw.text((cx1 + 140, cy1 + 70), descricao, font=f_texto, fill=(80, 80, 80))
    draw.text((cx1 + 140, cy1 + 100), data_sorteio, font=f_texto, fill=(80, 80, 80))
    draw.text((cx1 + 140, cy1 + 130), "SORTEIO PELA LOTERIA FEDERAL", font=f_label, fill=(180, 0, 0))

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

    documento = criar_documento_bilhete(
        bilhete_id=str(uuid.uuid4()),  # 👈 evita conflito global
        cpf=cpf_mask,
        email_user=email,
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
    
# ---------------- CLOUDINARY ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)



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
                "vendedor": u.get("vendedor", ""),
                "chave_pix": u.get("chave_pix", "")
                
            })

        return jsonify({"status": "sucesso", "usuarios": usuarios}), 200

    except Exception as e:
        print("ERRO /usuarios:", e)  # 👈 MUITO IMPORTANTE PRA DEBUG
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

#---------------------------------------------------------------------------------------------------------
# LISTAR TODOS VENDEDORES

# Editar PUT
@app.route("/usuarios/<usuario_id>", methods=["PUT"])
def editar_usuario(usuario_id):
    try:
        data = request.json

        update_data = {}

        if "nome" in data:
            update_data["nome"] = data["nome"].strip()

        if "cpf" in data:
            cpf = limpar_cpf(data["cpf"])
            if not validar_cpf(cpf):
                return jsonify({"status": "erro", "mensagem": "CPF inválido"}), 400
            update_data["cpf"] = cpf

        if "email" in data:
            update_data["email"] = data["email"].strip()

        if not update_data:
            return jsonify({"status": "erro", "mensagem": "Nenhum dado para atualizar"}), 400

        result = users_collection.update_one(
            {"_id": ObjectId(usuario_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"status": "erro", "mensagem": "Usuário não encontrado"}), 404

        return jsonify({"status": "sucesso", "mensagem": "Usuário atualizado"})

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400

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



# rota sucesso 
@app.route("/success")
def pagamento_sucesso():
    return render_template("aprovado.html")

# rora recusado
@app.route("/recusado")
def pagamento_recusado():
    return render_template("recusado.html")

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
    lista_numeros = request.args.get("lista_numeros") or ""
    quantidade = int(request.args.get("quantidade") or 0)

    valor_total = round(quantidade * 0.05, 2)


    payment_data = {
        "transaction_amount": float(valor_total),
        "description": "Testar pg Producao",
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
        "notification_url": "https://ferrari-tech.onrender.com/notificacoes",
        "statement_descriptor": "FerrariTech"
    }

    try:
        response = sdk.payment().create(payment_data)
        mp = response.get("response", {})

        print("MP RESPONSE:", mp)

        if "id" not in mp:
            return f"ERRO MP: {mp}", 500

        payment_id = str(mp["id"])
        status = mp.get("status", "pending")

        # salva pagamento Mercado Pago
        documento = criar_documento_pagamento(
            payment_id=payment_id,
            status=status,
            valor=valor_total,
            cpf=cpf,
            email_user=email,
            lista_numeros=lista_numeros
        )

        try:
            PagamentoModel().create_pagamento(documento)
        except Exception as e:
            print("ERRO AO SALVAR:", e)

        tx = mp.get("point_of_interaction", {}).get("transaction_data", {})

        qr_base64 = tx.get("qr_code_base64")
        qr_code = tx.get("qr_code")

        if not qr_base64 or not qr_code:
            return f"ERRO QR: {tx}", 500



        return render_template(
            "finalize.html",
            qrcode=f"data:image/png;base64,{qr_base64}",
            valor=f"R$ {valor_total:.2f}",
            qr_code_cola=qr_code,
            status=status,
            payment_id=payment_id,
            cpf=cpf,
        )

    except Exception as e:
        print("ERRO GERAL:", e)
        return f"ERRO GERAL: {str(e)}", 500


# # Thread para monitorar pagamentos
# def monitorar_pagamento(payment_id):
#     while True:
#         try:
#             doc = pagamentos_collection.find_one({"_id": str(payment_id)})
#             if doc and doc.get("status") == "approved":
#                 socketio.emit("pagamento_aprovado", {"payment_id": payment_id})
#                 break
#         except Exception as e:
#             print(f"Erro ao consultar MongoDB: {e}")
#         time.sleep(2)  # Evita sobrecarga no banco

# # Evento WebSocket para iniciar monitoramento
# @socketio.on("monitorar_pagamento")
# def handle_monitorar_pagamento(data):
#     payment_id = data.get("payment_id")
#     if not payment_id:
#         emit("erro", {"mensagem": "payment_id não fornecido"})
#         return
#     threading.Thread(target=monitorar_pagamento, args=(payment_id,), daemon=True).start()
#=============================================================================================
# -PAGAMENTO PREFERENCE MERCADO PAGO => funçoes - GERAR QRCODE E PIX COLA SALVA PAGAMENTO E
# ATUALIZA PAYMENT_ID NUMERO DO USUARIO "TESTADO (OK)"" 
#=============================================================================================    
# PAGAMENTO MERCADO PAGO 
@app.route("/compra/preference/pagamento_pix/<id>")
def pagamento_preference(usuario_id):

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
    lista_numeros = request.args.get("lista_numeros") or ""
    quantidade = int(request.args.get("quantidade") or 0)

    valor_total = quantidade * 1

    payment_data = {
        "items": [
            {
                "id": str(uuid.uuid4()),
                "title": "Assinatura Análise de Dados",
                "description": "Acesso ao sistema para gerar relatórios por 5 horas",
                "quantity": quantidade,
                "currency_id": "BRL",
                "unit_price": 1,
                "category_id": "services"
            }
        ],
        "external_reference": usuario_id,
        "back_urls": {
            "success": "https://ferrari-tech.onrender.com/sucesso",
            "failure": "https://ferrari-tech.onrender.com/recusada",
            "pending": "https://ferrari-tech.onrender.com/pendente",
        },
        "auto_return": "approved",
        "notification_url": "https://ferrari-tech.onrender.com/notificacoes"
    }

    result = sdk.preference().create(payment_data)
    mp = result.get("response", {})

    if "id" not in mp:
        return f"ERRO NO MERCADO PAGO:<br><br>{mp}", 500

    payment_id = mp["id"]
    status = "pending"

    documento = criar_documento_pagamento(
        payment_id=str(payment_id),
        status=status,
        valor=valor_total,
        usuario_id=usuario_id,
        email_user=email,
        lista_numeros=lista_numeros
    )

    PagamentoModel().create_pagamento(documento)

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
# ================================================
# UPLOADS DE IMAGENS PARA CLOUDINARY
# ================================================
# @app.route('/api/save-comprovante-pagamento', methods=['POST'])
# def save_comprovante_pagamento():
#     data = request.get_json()
#     comprovante_pagamento = data.get('comprovante')
#     if comprovante_pagamento:
#         print(f"URL: {comprovante}")
#         return jsonify({"message": "URL salva com sucesso"}), 200
#     return jsonify({"error": "URL não fornecida"}), 400


# =======================================================
# READ (1)
# =======================================================
@app.route('/pagamentos/<pagamento_id>', methods=['GET'])
def get_pagamento(pagamento_id):
    pagamentos = pagamento_model.get_pagamento(pagamento_id)

    if pagamentos:
        return jsonify(pagamentos), 200
    else:
        return jsonify({"erro": "Pagamento não encontrado"}), 404



@app.route('/pagamentos/<payment_id>', methods=['GET'])
def verificar_status_pagamento(payment_id):
    # Aqui buscamos o pagamento específico no seu model
    pagamento = pagamento_model.get_pagamento_by_id(payment_id)

    if pagamento:
        # Verifica se o status no banco é 'approved' ou 'pago'
        # Ajuste 'status' conforme o nome da coluna no seu banco
        return jsonify({"status": pagamento.get('status')}), 200
    else:
        return jsonify({"status": "not_found"}), 404
      


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



#DELETE NUMEROS USUARIO PELO ID
# app.py
@app.route("/numeros/<id>", methods=["DELETE"])
def deletar_numero(id):
    try:
        deletado = numero_model.delete_numero(id)

        if not deletado:
            return jsonify({"erro": "Número não encontrado"}), 404

        return jsonify({"msg": "Número deletado com sucesso"}), 200

    except Exception as e:
        print("ERRO DELETE:", e)
        return jsonify({"erro": str(e)}), 500    



@app.route("/vendedores", methods=["GET"])
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

@app.route("/login/vendedor")
def interface_login_vendedor():
    return render_template("registro-vendedores.html")
        
#===========================================
# -Run
#===========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # socketio.start_background_task(background_tasks)
    socketio.run(
        app,
        host="0.0.0.0",
        port=port,
        debug=True,
        allow_unsafe_werkzeug=True
    )


#@app.route("/notificacoes", methods=["POST"])
# def handle_webhook():
#     data = request.json
#     if not data:
#         return "", 200

#     payment_id = data.get("data", {}).get("id") or data.get("id")
#     if not payment_id:
#         return "", 200

#     payment_details = get_payment_details(payment_id)
#     if not payment_details:
#         return "", 200

#     status = payment_details.get("status")
#     usuario_id = payment_details.get("external_reference")
    
#     # Emite atualização via socket
#     socketio.emit(
#         "payment_update",
#         {
#             "status": status,
#             "payment_id": str(payment_id),
#             "usuario_id": usuario_id
#         },
#         room=str(payment_id)  # ou room=str(usuario_id), dependendo da lógica do front
#     )

#     # Atualiza no banco
#     pagamento_model.update_pagamento(payment_id, {"status": status})
#     # Calcular o total de numeros e status = "pending" for igual = ao valor pagamento approved atualiza o payment_id dos numeros e status = "approved" conforme valor approved 
#     # atualizado = numero_model.atualizar_status(numero_id, novo_status)
    
    


# @app.route("/payment_qrcode_pix/pagamento_pix/<id>")
# def pagamento_pix(id):

#     usuario_id = id

#     nome = request.args.get("nome") or ""
#     cpf = request.args.get("cpf") or ""
#     email = request.args.get("email") or ""
#     quantidade = int(request.args.get("quantidade") or 0)

#     valor_total = round(quantidade * 0.05, 2)

#     payment_data = {
#         "transaction_amount": float(valor_total),
#         "description": "Testar pg Producao",
#         "payment_method_id": "pix",
#         "payer": {
#             "email": email,
#             "first_name": nome,
#             "last_name": "Cliente",
#             "identification": {
#                 "type": "CPF",
#                 "number": cpf
#             }
#         },
#         "external_reference": usuario_id,
#         "notification_url": "https://ferrari-tech.onrender.com/notificacoes",
#         "statement_descriptor": "FerrariTech"
#     }

#     try:
#         response = sdk.payment().create(payment_data)
#         mp = response.get("response", {})

#         print("MP RESPONSE:", mp)

#         if "id" not in mp:
#             return f"ERRO MP: {mp}", 500

#         payment_id = str(mp["id"])
#         status = mp.get("status", "pending")

#        # Aqui salva o pagamento gerados...... Mercado pago
#         documento = criar_documento_pagamento(
#             payment_id=payment_id,
#             status=status,
#             valor=valor_total,
#             usuario_id=usuario_id,
#             email_user=email
#         )

       
#         try:
#             PagamentoModel().create_pagamento(documento)
#         except Exception as e:
#             print("ERRO AO SALVAR:", e)

        
#         tx = mp.get("point_of_interaction", {}).get("transaction_data", {})

#         qr_base64 = tx.get("qr_code_base64")
#         qr_code = tx.get("qr_code")

#         if not qr_base64 or not qr_code:
#             return f"ERRO QR: {tx}", 500

#         # Aqui vai atualizar numero.model o campo payment_id = ""    de todos com status = "pending" com a criacao do mesmo dia 


#         return render_template(
#             "finalize.html",
#             qrcode=f"data:image/png;base64,{qr_base64}",
#             valor=f"R$ {valor_total:.2f}",
#             qr_code_cola=qr_code,
#             status=status,
#             payment_id=payment_id,
#             usuario_id=usuario_id
#         )

#     except Exception as e:
#         print("ERRO GERAL:", e)
#         return f"ERRO GERAL: {str(e)}", 500

    




# @socketio.on('connect')
# def test_connect():
#     print('Cliente conectado')


# @socketio.on("join")
# def on_join(data):
#     usuario_id = data.get("usuario_id")
#     if usuario_id:
#         # Adiciona o cliente a uma "sala" específica
#         from flask_socketio import join_room
#         join_room(str(usuario_id))
#         emit("joined", {"room": usuario_id})


# def background_tasks():
#     while True:
#         time.sleep(10)
#         socketio.emit('nova_mensagem', {'data': 'Nova mensagem recebida!'}, namespace='/')
#         print("Mensagem emitida")

# # Rodar em thread separada
# thread = Thread(target=background_tasks)
# thread.daemon = True
# thread.start()    




# Aqui Lista os Numeros e soma total 
# @app.route("/numeros", methods=["GET"])
# def listar_numeros():
#     numeros = numero_model.get_all_numeros()
    
#     # Converte ObjectId para string
#     for n in numeros:
#         n["_id"] = str(n["_id"])

#     # Contadores de status
#     total_a_pagar = sum(1 for n in numeros if n.get("status") == "pending")
#     total_ok = sum(1 for n in numeros if n.get("status") == "approved")

#     return jsonify({
#         "numeros": numeros,
#         "resumo": {
#             "pending": total_a_pagar,
#             "approved": total_ok
#         }
#     })


#==============================================================================
# # SALVAR NUMEROS MONGODB 
# @app.route("/numeros", methods=["POST"])
# def salvar_numero():
#     data = request.json or {}
#     data_sort_str = data.get("dataSort", "10/05/2026")

#     # pega da URL OU do body
#     usuario_id = request.args.get("id") or data.get("usuario_id")

#     if not usuario_id:
#         return jsonify({"erro": "usuario_id não informado"}), 400

#     doc = {
#         "usuario_id": str(usuario_id),
#         "nome": data.get("nome"),
#         "cpf": limpar_cpf(data.get("cpf")),
#         "email": data.get("email"),
#         "numero": data.get("numero"),
#         "paymentId": data.get("paymentId", "aguardando gerar payment"),
#         "valor": float(data.get("valor", 0.05)),
#         "dataSort": datetime.strptime(data_sort_str, "%d/%m/%Y"),
#         "premio": float(data.get("premio", 150.00)),
#         "status": "pending",
#         "criado_em": datetime.now(timezone.utc)
#     }

#     _id = numero_model.create_numero(doc)

#     return jsonify({"id": _id})


        # ===============================================
        # ATUALIZA TODOS NUMEROS PENDING DO MESMO USUARIO
        # ===============================================
        # try:
        #     NumeroModel().atualizar_payment_em_lote(
        #         cpf=cpf,
        #         payment_id=payment_id
        #     )
        # except Exception as e:
        #     print("ERRO AO ATUALIZAR NUMEROS:", e)
