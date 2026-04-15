from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
import re
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

# Carrega variáveis de ambiente
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGO_URI or not DB_NAME:
    raise ValueError("Variáveis de ambiente MONGO_URI ou DB_NAME não definidas.")

# Conexão com MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Coleções
PAGAMENTOS_COLLECTION_NAME = "pagamentos"
BILHETES_COLLECTION_NAME = "bilhetes"
users_collection = db["users"]
vendedores_collection = db["vendedores"]
bilhetes_collection = db["bilhetes"]



# Função para limpar CPF (remove pontos e traços)
def limpar_cpf(cpf: str) -> str:
    return re.sub(r"\D", "", cpf)
#------------------------------------------------------------------------------------------------------------------
# Função para validar CPF simples (somente 11 dígitos)
def validar_cpf(cpf: str) -> bool:
    cpf = limpar_cpf(cpf)
    return bool(re.fullmatch(r"\d{11}", cpf))
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
#     
#------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------
# USUARIOS
def criar_usuario(nome: str, sobrenome: str, cpf: str, dt_nascimento: str, email: str, vendedor: str, chave_pix: str) -> dict:
    cpf = limpar_cpf(cpf)

    if not nome.strip() or not validar_cpf(cpf) or not email.strip() or not dt_nascimento.strip() or not vendedor.strip() or not chave_pix.strip():
        raise ValueError("Dados inválidos para cadastro.")

    # Evita duplicado pelo CPF
    if users_collection.find_one({"cpf": cpf}):
        raise ValueError("CPF já cadastrado.")

    usuario = {
        "nome": nome.strip(),
        "sobrenome": sobrenome.strip(),
        "cpf": cpf,
        "dt_nascimento": dt_nascimento.strip(),
        "email": email.strip(),
        "vendedor": vendedor.strip(),
        "chave_pix": chave_pix.strip(),
        "criado_em": datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(usuario)

    usuario["_id"] = str(result.inserted_id)
    return usuario
#================================================================================================================================
#================================================================================================================================

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# VENDEDORES
def criar_vendedor(nome: str, sobrenome: str, cpf: str, dt_nascimento: str, email: str, chave_pix: str) -> dict:
    cpf = limpar_cpf(cpf)

    if not nome.strip() or not validar_cpf(cpf) or not email.strip() or not dt_nascimento.strip() or not chave_pix.strip():
        raise ValueError("Dados inválidos para cadastro.")

    # Evita duplicado pelo CPF
    if vendedores_collection.find_one({"cpf": cpf}):
        raise ValueError("CPF já cadastrado.")

    vendedor = {
        "nome": nome.strip(),
        "sobrenome": sobrenome.strip(),
        "cpf": cpf,
        "dt_nascimento": dt_nascimento.strip(),
        "email": email.strip(),
        "chave_pix": chave_pix.strip(),
        "criado_em": datetime.now(timezone.utc)
    }

    result = vendedores_collection.insert_one(vendedor)

    vendedor["_id"] = str(result.inserted_id)
    return vendedor
#================================================================================================================================
#================================================================================================================================



#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# PAGAMENTOS 
pagamentos_collection = db[PAGAMENTOS_COLLECTION_NAME]

def criar_documento_pagamento(payment_id, status, valor, cpf, email_user, lista_numeros=None, data_criacao=None):

    if data_criacao is None:
        data_criacao = datetime.now(timezone.utc)

    return {
        "_id": str(payment_id),
        "status": status,
        "valor": float(valor),
        "cpf": cpf,
        "email_usuario": email_user,
        "data_criacao": data_criacao,
        "data_atualizacao": None,
        "lista_numeros": lista_numeros or []
    }

class PagamentoModel:
    def __init__(self):
        self.collection = pagamentos_collection

    def create_pagamento(self, data):
        try:
            # 👇 evita erro de duplicado (_id já existe)
            existente = self.collection.find_one({"_id": data["_id"]})
            if existente:
                return data["_id"]

            result = self.collection.insert_one(data)
            return str(result.inserted_id)

        except Exception as e:
            print("ERRO MODEL INSERT:", e)
            return None

    def get_pagamento(self, pagamento_id):
        doc = self.collection.find_one({"_id": str(pagamento_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def get_pagamento_by_id(self, pagamento_id):
        return self.get_pagamento(pagamento_id)

    def get_all_pagamentos(self):
        docs = list(self.collection.find())
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

    def update_pagamento(self, pagamento_id, new_data):
        try:
            new_data["data_atualizacao"] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {"_id": str(pagamento_id)},
                {"$set": new_data}
            )
            return result.modified_count

        except Exception as e:
            print("ERRO UPDATE:", e)
            return 0


    def get_pagamentos_by_usuario(self, usuario_id):
        docs = list(self.collection.find({"usuario_id": ObjectId(usuario_id)}))
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

    

    def delete_pagamento(self, pagamento_id):
        try:
            result = self.collection.delete_one({"_id": str(pagamento_id)})
            return result.deleted_count

        except Exception as e:
            print("ERRO DELETE:", e)
            return 0
#=====================================================================================================================
#=====================================================================================================================

#---------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------
# URLS E BILHETES 
bilhetes_collection = db[BILHETES_COLLECTION_NAME]

def criar_documento_bilhete(bilhete_id, cpf, email_user, lista_numeros=None, lista_urls_img_bilhetes=None, data_criacao=None):

    if data_criacao is None:
        data_criacao = datetime.now(timezone.utc)

    return {
        "_id": str(bilhete_id),
        "cpf": cpf,
        "email_usuario": email_user,
        "data_criacao": data_criacao,
        "data_atualizacao": None,
        "lista_numeros": lista_numeros or [],
        "lista_urls_img_bilhetes": lista_urls_img_bilhetes or []
    }


class BilheteModel:
    def __init__(self):
        self.collection = bilhetes_collection

    def create_bilhete(self, data):
        try:
            # 👇 evita erro de duplicado (_id já existe)
            existente = self.collection.find_one({"_id": data["_id"]})
            if existente:
                return data["_id"]

            result = self.collection.insert_one(data)
            return str(result.inserted_id)

        except Exception as e:
            print("ERRO MODEL INSERT:", e)
            return None


    def get_bilhete(self, bilhete_id):
        doc = self.collection.find_one({"_id": str(bilhete_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

# GET BILHETE ID
    def get_bilhete_by_id(self, bilhete_id):
        return self.get_bilhete(bilhete_id)

# GET ALL BILHETES
    def get_all_bilhetes(self):
        docs = list(self.collection.find())
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

# UPDATE BILHETE
    def update_bilhete(self, bilhete_id, new_data):
        try:
            new_data["data_atualizacao"] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {"_id": str(bilhete_id)},
                {"$set": new_data}
            )
            return result.modified_count

        except Exception as e:
            print("ERRO UPDATE:", e)
            return 0

# GET BILHETE USUARIO
    def get_bilhetes_by_usuario(self, usuario_id):
        docs = list(self.collection.find({"usuario_id": ObjectId(usuario_id)}))
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

    
# DELETE BILHETE
    def delete_bilhete(self, bilhete_id):
        try:
            result = self.collection.delete_one({"_id": str(bilhete_id)})
            return result.deleted_count

        except Exception as e:
            print("ERRO DELETE:", e)
            return 0




























# lista_urls_img_bilhetes = []
# # GERADOR DE RIFAS 
# W, H = 900, 450

# @app.route("/gerar-bilhete", methods=["POST"])
# def gerar_bilhete():

#     data = request.json

#     numero_bilhete = f"Nº {data['numero']}"
#     evento = "Pix no Bolso "
#     descricao = "Prêmio: R$ 150,00 via Pix"
#     data_sorteio = "Sorteio: Quartas e domingos"

#     nome = data["nome"]
#     email = data["email"]
#     cpf = data["cpf"]
#     cpf = f"{cpf[:3]}.***.***-{cpf[9:11]}"

#     link_qrcode = "https://ferrari-tech.onrender.com"
#     caminho_logo = "static/w.png"

#     # =========================
#     # FUNDO
#     # =========================
#     img = Image.new("RGB", (W, H))
#     draw = ImageDraw.Draw(img)

#     for y in range(H):
#         draw.line([(0, y), (W, y)], fill=(200 - y//5, 20, 20))

#     # =========================
#     # CARD
#     # =========================
#     margin = 30
#     cx1, cy1 = margin, margin
#     cx2, cy2 = W - margin, H - margin

#     cw, ch = cx2 - cx1, cy2 - cy1

#     card = Image.new("RGB", (cw, ch), "white")
#     shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 100)).filter(ImageFilter.GaussianBlur(10))

#     img.paste(shadow, (cx1+4, cy1+4), shadow)
#     img.paste(card, (cx1, cy1))

#     draw = ImageDraw.Draw(img)

#     # =========================
#     # FONTES
#     # =========================
#     try:
#         f_titulo = ImageFont.truetype("arialbd.ttf", 36)
#         f_texto = ImageFont.truetype("arial.ttf", 24)
#         f_label = ImageFont.truetype("arialbd.ttf", 20)
#         f_num = ImageFont.truetype("arialbd.ttf", 28)
#     except:
#         f_titulo = f_texto = f_label = f_num = ImageFont.load_default()

#     # =========================
#     # LOGO
#     # =========================
#     if os.path.exists(caminho_logo):
#         logo = Image.open(caminho_logo).convert("RGBA")
#         logo.thumbnail((100, 60))
#         img.paste(logo, (cx1 + 20, cy1 + 20), logo)

#     # =========================
#     # TEXTOS
#     # =========================
#     draw.text((cx1 + 140, cy1 + 25), evento, font=f_titulo, fill=(0, 0, 0))
#     draw.text((cx1 + 140, cy1 + 70), descricao, font=f_texto, fill=(80, 80, 80))
#     draw.text((cx1 + 140, cy1 + 100), data_sorteio, font=f_texto, fill=(80, 80, 80))
#     draw.text((cx1 + 140, cy1 + 130), "SORTEIO PELA LOTERIA FEDERAL", font=f_label, fill=(180, 0, 0))

#     # =========================
#     # DADOS
#     # =========================
#     left_x = cx1 + 20
#     right_x = cx2 - 220

#     start_y = cy1 + 170
#     gap = 40

#     def linha(label, valor, y):
#         draw.text((left_x, y), label, font=f_label, fill=(150, 0, 0))
#         draw.text((left_x + 140, y), valor, font=f_texto, fill=(0, 0, 0))

#     linha("Nome:", nome, start_y)
#     linha("Email:", email, start_y + gap)
#     linha("CPF:", cpf, start_y + gap*2)

#     draw.line((left_x, start_y - 15, right_x - 20, start_y - 15), fill=(200,0,0), width=2)

#     # =========================
#     # NUMERO
#     # =========================
#     draw.rectangle([left_x, cy2 - 60, left_x + 200, cy2 - 20], fill=(200, 0, 0))
#     draw.text((left_x + 10, cy2 - 55), numero_bilhete, fill="white", font=f_num)

#     # =========================
#     # QR CODE
#     # =========================
#     qr = qrcode.make(link_qrcode).convert("RGB").resize((150,150))

#     qr_box = 180
#     qr_bg = Image.new("RGB", (qr_box, qr_box), "white")
#     qr_draw = ImageDraw.Draw(qr_bg)

#     qr_draw.rectangle([0,0,qr_box-1,qr_box-1], outline=(200,0,0), width=3)
#     qr_bg.paste(qr, (15,15))

#     qr_y = cy1 + (ch // 2) - (qr_box // 2)
#     img.paste(qr_bg, (right_x, qr_y))

#     # =========================
#     # SALVAR  CLOUDINARY 
#     # =========================
#     buffer = BytesIO()
#     img.save(buffer, format="PNG")
#     buffer.seek(0)

#     upload_result = cloudinary.uploader.upload(
#         buffer,
#         folder="rifas",
#         public_id=f"bilhete_{numero_bilhete}_{cpf}_{uuid.uuid4()}",
#         resource_type="image"
#     )

#     url_imagem = upload_result["secure_url"]

#     lista_urls_img_bilhetes.append(url_imagem)

#     documento = criar_documento_bilhete(
#         bilhete_id=numero_bilhete,
#         cpf=cpf,
#         email_user=email,
#         lista_numeros=[numero_bilhete],
#         lista_urls_img_bilhetes=lista_urls_img_bilhetes
#     )

#     BilheteModel().create_bilhete(documento)

#     return jsonify({
#         "img": url_imagem
#     })

