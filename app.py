from flask import Flask, request, jsonify, render_template, redirect, session, send_file
from flask_socketio import SocketIO, join_room, emit
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
from models import criar_usuario, users_collection, pagamentos_collection, criar_documento_pagamento, PagamentoModel, NumeroModel
from flask_cors import CORS
from datetime import datetime, timezone
import time
import uuid
import io


load_dotenv()

app = Flask(__name__)
CORS(app)
# ---------------- MONGODB ----------------
client = MongoClient(os.getenv("MONGO_URI"))
db = client["rifa"]
colecao = db["participantes"]
pagamento_model = PagamentoModel()
numero_model = NumeroModel()
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = os.getenv("APP_SECRET_KEY")  
premiacao1 = os.getenv("PREMIACAO1")
dt_sort = os.getenv("SORTEIO")

# ---------------- CLOUDINARY ----------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
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

#=================================================================================
# Rota para registrar usuário
@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        data = request.json
        usuario = criar_usuario(data["nome"], data["cpf"], data["email"])
        return jsonify({"status": "sucesso", "usuario": usuario}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 400
#---------------------------------------------------------------------------------
#=================================================================================
#=================================================================================
# 🔐 LOGIN
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
# registro pagina principal 
@app.route("/")
def registro():
    return render_template("registro.html")

# 🔓 Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Rota de acesso ao Painel Principal do usuarios
@app.route("/dia_das_maes")
def index():
    usuario_id = request.args.get("id")

    if not usuario_id:
        return redirect("/")

    numeros = numero_model.get_all_numeros()

    for n in numeros:
        n["_id"] = str(n["_id"])

    total_a_pagar = sum(1 for n in numeros if n.get("status") == "pending")
    total_ok = sum(1 for n in numeros if n.get("status") == "approved")

    numeros = numero_model.get_numeros_by_usuario(usuario_id)

    usuarios_cursor = users_collection.find()

    usuarios = []
    for u in usuarios_cursor:
        usuarios.append({
            "_id": str(u.get("_id")),
            "nome": u.get("nome", ""),
            "cpf": u.get("cpf", ""),
            "email": u.get("email", "")
        })

    return render_template(
        "index.html",
        usuario_id=usuario_id,
        numeros=numeros,
        usuarios=usuarios,
        total_a_pagar=total_a_pagar,
        total_ok=total_ok
    )
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


#==============================================================================
# SALVAR NUMEROS MONGODB 
@app.route("/numeros", methods=["POST"])
def salvar_numero():
    data = request.json or {}
    data_sort_str = data.get("dataSort", "10/05/2026")

    # pega da URL OU do body
    usuario_id = request.args.get("id") or data.get("usuario_id")

    if not usuario_id:
        return jsonify({"erro": "usuario_id não informado"}), 400

    doc = {
        "usuario_id": str(usuario_id),
        "nome": data.get("nome"),
        "cpf": limpar_cpf(data.get("cpf")),
        "email": data.get("email"),
        "numero": data.get("numero"),
        "paymentId": data.get("paymentId", "aguardando gerar payment"),
        "valor": float(data.get("valor", 0.05)),
        "dataSort": datetime.strptime(data_sort_str, "%d/%m/%Y"),
        "premio": float(data.get("premio", 150.00)),
        "status": "pending",
        "criado_em": datetime.now(timezone.utc)
    }

    _id = numero_model.create_numero(doc)

    return jsonify({"id": _id})
    



@app.route("/bilhete", methods=["GET"])
def lista():
    usuario_id = request.args.get("usuario_id")

    if not usuario_id:
        return jsonify({"erro": "usuario_id não informado"}), 400

    numeros = numero_model.get_numeros_by_usuario(usuario_id)

    return jsonify(numeros)


# Aqui Lista os Numeros e soma total 
@app.route("/numeros", methods=["GET"])
def listar_numeros():
    numeros = numero_model.get_all_numeros()
    
    # Converte ObjectId para string
    for n in numeros:
        n["_id"] = str(n["_id"])

    # Contadores de status
    total_a_pagar = sum(1 for n in numeros if n.get("status") == "pending")
    total_ok = sum(1 for n in numeros if n.get("status") == "approved")

    return jsonify({
        "numeros": numeros,
        "resumo": {
            "pending": total_a_pagar,
            "approved": total_ok
        }
    })

from decimal import Decimal, ROUND_HALF_UP


@app.route("/fechamento", methods=["GET"])
def fechamento():

    usuarios = list(users_collection.find())
    numeros = numero_model.get_all_numeros()
    pagamentos = pagamento_model.get_all_pagamentos()

    for n in numeros:
        n["_id"] = str(n["_id"])
    for p in pagamentos:
        p["_id"] = str(p["_id"])

    quantidade_usuarios = len(usuarios)

    total_numeros_pending = Decimal("0")
    total_numeros_approved = Decimal("0")
    total_numeros_cancelled = Decimal("0")

    for n in numeros:
        valor = Decimal(str(n.get("valor", 0)))
        if n.get("status") == "pending":
            total_numeros_pending += valor
        elif n.get("status") == "approved":
            total_numeros_approved += valor
        elif n.get("status") == "cancelled":
            total_numeros_cancelled += valor

    total_pagamentos_pending = Decimal("0")
    total_pagamentos_approved = Decimal("0")
    total_pagamentos_cancelled = Decimal("0")

    for p in pagamentos:
        valor = Decimal(str(p.get("valor", 0)))
        if p.get("status") == "pending":
            total_pagamentos_pending += valor
        elif p.get("status") == "approved":
            total_pagamentos_approved += valor
        elif p.get("status") == "cancelled":
            total_pagamentos_cancelled += valor

    resumo = {
        "usuarios": quantidade_usuarios,
        "numeros": {
            "pending": float(total_numeros_pending),
            "approved": float(total_numeros_approved),
            "cancelled": float(total_numeros_cancelled),
            "total": float(total_numeros_pending + total_numeros_approved + total_numeros_cancelled)
        },
        "pagamentos": {
            "pending": float(total_pagamentos_pending),
            "approved": float(total_pagamentos_approved),
            "cancelled": float(total_pagamentos_cancelled)
        },
        "faturamento": float(total_pagamentos_approved)
    }

    return render_template("fechamento.html", resumo=resumo)


def get_numero_by_id(self, id):
    return self.collection.find_one({"_id": id})

@app.route("/imprimir/baixar_bilhete/<id>")
def gerar_bilhete(id):

    # ===============================
    # VALIDAR ID
    # ===============================
    try:
        obj_id = ObjectId(id)
    except:
        return "ID inválido", 400

    doc = numero_model.get_numeros_by_usuario(usuario_id)

    if not doc:
        return "Bilhete não encontrado", 404

    # DEBUG (pode remover depois)
    print("DOC:", doc)

    # ===============================
    # DADOS SEGUROS
    # ===============================
    numero_bilhete = f"Nº {doc.get('numero', '---')}"
    evento = "Rifa Dia das Mães"
    descricao = f"Prêmio: R$ {doc.get('premio', 0):.2f}"

    data_sort = doc.get("dataSort")
    if data_sort and hasattr(data_sort, "strftime"):
        data_sorteio = f"Sorteio: {data_sort.strftime('%d/%m/%Y')}"
    else:
        data_sorteio = "Sorteio: não informado"

    nome = doc.get("nome", "Não informado")
    email = doc.get("email", "Não informado")
    cpf = doc.get("cpf", "Não informado")
    valor = float(doc.get("valor", 1.00))

    # ===============================
    # CONFIG
    # ===============================
    W, H = 900, 500
    link_qrcode = "https://ferrari-tech.onrender.com/"

    # CAMINHO PORTÁVEL (FUNCIONA EM PRODUÇÃO)
    caminho_logo = os.path.join("static", "w.png")

    # ===============================
    # IMAGEM BASE
    # ===============================
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        draw.line([(0, y), (W, y)], fill=(200 - y//5, 50 + y//10, 80))

    margin = 20
    cx1, cy1 = margin, margin
    cx2, cy2 = W - margin, H - margin
    cw, ch = cx2 - cx1, cy2 - cy1

    card = Image.new("RGB", (cw, ch), "white")
    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 120)).filter(ImageFilter.GaussianBlur(12))
    img.paste(shadow, (cx1+4, cy1+4), shadow)

    mask = Image.new("L", (cw, ch), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0,0,cw,ch], radius=25, fill=255)
    img.paste(card, (cx1, cy1), mask)

    draw = ImageDraw.Draw(img)

    # ===============================
    # FONTES
    # ===============================
    try:
        f_titulo = ImageFont.truetype("arialbd.ttf", 40)
        f_texto = ImageFont.truetype("arial.ttf", 26)
        f_label = ImageFont.truetype("arialbd.ttf", 22)
        f_num = ImageFont.truetype("arialbd.ttf", 30)
    except:
        f_titulo = f_texto = f_label = f_num = ImageFont.load_default()

    def desenhar_texto(dest, texto, pos, fonte, cor, sombra=(0,0,0)):
        dest.text((pos[0]+2, pos[1]+2), str(texto), font=fonte, fill=sombra)
        dest.text(pos, str(texto), font=fonte, fill=cor)

    # ===============================
    # LOGO
    # ===============================
    if os.path.exists(caminho_logo):
        logo = Image.open(caminho_logo).convert("RGBA")
        logo.thumbnail((100, 60))
        img.paste(logo, (cx1 + 20, cy1 + 20), logo)

    # ===============================
    # TEXTO PRINCIPAL
    # ===============================
    desenhar_texto(draw, evento, (cx1 + 140, cy1 + 25), f_titulo, (0,0,0))
    desenhar_texto(draw, descricao, (cx1 + 140, cy1 + 70), f_texto, (50,50,150))
    desenhar_texto(draw, data_sorteio, (cx1 + 140, cy1 + 100), f_texto, (80,80,80))
    desenhar_texto(draw, "Sorteio pela Loteria Federal", (cx1 + 140, cy1 + 130), f_label, (180,0,0))

    # ===============================
    # DADOS CLIENTE
    # ===============================
    left_x = cx1 + 20
    start_y = cy1 + 170
    gap = 40

    def linha(label, valor_txt, y):
        desenhar_texto(draw, label, (left_x, y), f_label, (200,0,0))
        desenhar_texto(draw, valor_txt, (left_x + 140, y), f_texto, (0,0,150))

    linha("Nome:", nome, start_y)
    linha("Email:", email, start_y + gap)
    linha("CPF:", cpf, start_y + gap*2)

    valor_y = start_y + gap*3
    draw.rounded_rectangle([left_x, valor_y-5, left_x+300, valor_y+35], radius=10, fill=(255,215,0))
    desenhar_texto(draw, f"Valor: R$ {valor:.2f}", (left_x+10, valor_y), f_label, (0,0,0))

    # ===============================
    # NÚMERO
    # ===============================
    num_y_top = cy2 - 70
    num_y_bottom = cy2 - 30
    draw.rounded_rectangle([left_x, num_y_top, left_x + 220, num_y_bottom], radius=10, fill=(200, 0, 0))
    desenhar_texto(draw, numero_bilhete, (left_x + 20, num_y_top + 5), f_num, (255,255,255))

    # ===============================
    # QR CODE
    # ===============================
    qr = qrcode.make(link_qrcode).convert("RGB").resize((150,150))
    qr_box = 180
    qr_bg = Image.new("RGB", (qr_box, qr_box), "white")

    qr_draw = ImageDraw.Draw(qr_bg)
    qr_draw.rounded_rectangle([0,0,qr_box-1,qr_box-1], radius=20, outline=(200,0,0), width=4)
    qr_bg.paste(qr, (15,15))

    if os.path.exists(caminho_logo):
        logo_qr = Image.open(caminho_logo).convert("RGBA")
        logo_qr.thumbnail((50, 50))
        lx = (qr_bg.width - logo_qr.width) // 2
        ly = (qr_bg.height - logo_qr.height) // 2
        qr_bg.paste(logo_qr, (lx, ly), logo_qr)

    img.paste(qr_bg, (cx2 - 200, cy1 + 120))

    # ===============================
    # RETORNO
    # ===============================
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=True,
        download_name=f"bilhete_{doc.get('numero', 'x')}.png"
    )



#================================================================================================================================================
#================================================================================================================================================
#================================================================================================================================================

#=============================================================================================================================================
#=============================================================================================================================================
# - ATUALIZAR STATUS CONFORME VALOR PAYMENT_ID EXEMPLO: TEM 3 NUMEROS_ID STATUS PENDING E ACABOU DE ATUALIZAR PAGAMENTO VALOR 3.00 VAI ATUALIZAR OS STATUS
@app.route("/numeros/atualizar_status/<numero_id>", methods=["POST"])
def atualizar_status_rota(numero_id):
    data = request.json
    novo_status = data.get("status")
    
    if not novo_status:
        return jsonify({"error": "Status não fornecido"}), 400

    atualizado = numero_model.atualizar_status(numero_id, novo_status)

    if atualizado == 0:
        return jsonify({"error": "Número não encontrado ou erro"}), 404

    return jsonify({"mensagem": "Status atualizado com sucesso"})
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
                "cpf": u.get("cpf", ""),
                "email": u.get("email", "")
            })

        return jsonify({"status": "sucesso", "usuarios": usuarios}), 200

    except Exception as e:
        print("ERRO /usuarios:", e)  # 👈 MUITO IMPORTANTE PRA DEBUG
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

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



#===========================================================              
# -PAGAMENTO VIA SOMENTE PIX QRCODE               
#===========================================================              
MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN")              
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)          

# ===========================================
# GERAR QR CODE PIX
# ===========================================
from bson.objectid import ObjectId

@app.route("/payment_qrcode_pix/pagamento_pix/<id>")
def pagamento_pix(id):

    usuario_id = id

    nome = request.args.get("nome") or ""
    cpf = request.args.get("cpf") or ""
    email = request.args.get("email") or ""
    quantidade = int(request.args.get("quantidade") or 0)

    valor_total = round(quantidade * 0.05, 2)

    payment_data = {
        "transaction_amount": float(valor_total),
        "description": "Testar pg Producao",
        "payment_method_id": "pix",
        "payer": {
            "email": email,
            "first_name": nome,
            "last_name": "Cliente",
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        },
        "external_reference": usuario_id,
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

       # Aqui salva o pagamento gerados...... Mercado pago
        documento = criar_documento_pagamento(
            payment_id=payment_id,
            status=status,
            valor=valor_total,
            usuario_id=usuario_id,
            email_user=email
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
            usuario_id=usuario_id
        )

    except Exception as e:
        print("ERRO GERAL:", e)
        return f"ERRO GERAL: {str(e)}", 500




@app.route('/check-status')
def check_status():
    payment_id = request.args.get('payment_id')
    usuario_id = request.args.get('usuario_id')
    
    # Busca no MongoDB
    pagamento = collection.find_one({
        "payment_id": payment_id,
        "usuario_id": usuario_id,
        "status": "approved"
    })
    
    if pagamento:
        return jsonify({"status": "approved"})
    else:
        return jsonify({"status": "pending"})


# PAGAMENTO MERCADO PAGO 
@app.route("/compra/preference/pagamento_pix/<id>")
def pagamento_preference(id):

    usuario_id = id
    nome = request.args.get("nome") or ""
    email = request.args.get("email") or ""
    cpf = request.args.get("cpf") or ""
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
        email_user=email
    )

    PagamentoModel().create_pagamento(documento)

    link_pagamento = mp.get("init_point", "")
    return redirect(link_pagamento)

# rota sucesso 
@app.route("/success")
def sucesso():
    return render_template("aprovado.html")

# rora recusado
@app.route("/recusado")
def recusados():
    return render_template("recusado.html")

# pagamento pendente

@app.route("/pendente")
def pending():
    return render_template("pendente.html")


@app.route("/aprovado")
def aprovado():
    return render_template(
        "aprovado.html"
    )

@app.route("/recusado/<id>")
def negada(id):
    usuario = users_collection.find_one({"_id": ObjectId(id)})

    if not usuario:
        return "Usuário não encontrado", 404

    return render_template(
        "recusado.html",
        usuario=usuario,
        usuario_id=id

    )   




#     return "", 200
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

    # 🔥 REGRA PRINCIPAL
    if status == "approved":

        VALOR_NUMERO = 0.05

        # Quantidade de números pagos
        quantidade = int(valor_pago / VALOR_NUMERO)

        # Busca números pendentes do usuário
        numeros_pendentes = numero_model.buscar_por_status(usuario_id, "pending")

        # Garante que não ultrapasse
        numeros_para_atualizar = numeros_pendentes[:quantidade]

        for numero in numeros_para_atualizar:
            numero_model.atualizar_status(
                numero_id=numero["id"],
                novo_status="approved",
                payment_id=payment_id
            )

    return "", 200
  


def get_payment_details(payment_id):
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}"
    headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=10)
    return r.json() if r.status_code == 200 else None  


@socketio.on("join_payment")
def join_payment_room(data):
    join_room(data["payment_id"]) 


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






# ================================================
# UPLOADS DE IMAGENS PARA CLOUDINARY
# ================================================
@app.route('/api/save-comprovante-pagamento', methods=['POST'])
def save_comprovante_pagamento():
    data = request.get_json()
    comprovante_pagamento = data.get('comprovante')
    if comprovante_pagamento:
        print(f"URL: {comprovante}")
        return jsonify({"message": "URL salva com sucesso"}), 200
    return jsonify({"error": "URL não fornecida"}), 400


# =======================================================
# READ (1)
# =======================================================
@app.route('/pagamentos/<pagamento_id>', methods=['GET'])
def get_pagamento(pagamento_id):
    pagamento = pagamento_model.get_pagamento(pagamento_id)

    if pagamento:
        return jsonify(pagamento), 200
    else:
        return jsonify({"erro": "Pagamento não encontrado"}), 404


@app.route('/pagamentos', methods=['GET'])
def get_pagamentos():
    pagamentos = pagamento_model.get_all_pagamentos()

    if pagamentos:
        return jsonify(pagamentos), 200
    else:
        return jsonify({"erro": "Pagamentos não encontrado"}), 404

# 
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


    # @app.route("/notificacoes", methods=["POST"])
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
    
    