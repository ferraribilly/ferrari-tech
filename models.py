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
RASPADINHAS_COLLECTION_NAME = "raspadinhas"
MENSAGENS_COLLECTION_NAME = "mensagens"
users_collection = db["users"]
vendedores_collection = db["vendedores"]
saques_collection = db["saques"]
mensagens_collection = db[MENSAGENS_COLLECTION_NAME]





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
# =========================
# models.py / modal.py
# =========================

def criar_usuario(
    nome: str,
    sobrenome: str,
    cpf: str,
    dt_nascimento: str,
    email: str,
    vendedor: str,
    chave_pix: str,
    ip_usuario: str,
    aparelho: str,
    navegador: str
) -> dict:

    cpf = limpar_cpf(cpf)

    if (
        not nome.strip()
        or not validar_cpf(cpf)
        or not email.strip()
        or not dt_nascimento.strip()
        or not vendedor.strip()
        or not chave_pix.strip()
    ):
        raise ValueError("Dados inválidos para cadastro.")

    if users_collection.find_one({"cpf": cpf}):
        raise ValueError("CPF já cadastrado.")

    usuario = {
        "nome": nome.strip(),
        "sobrenome": sobrenome.strip(),
        "cpf": cpf,
        "dt_nascimento": dt_nascimento.strip(),
        "email": email.strip(),
        "vendedor_id": vendedor.strip(),
        "vendedor": vendedor.strip(),
        "chave_pix": chave_pix.strip(),

        "ganhos": 0.00,
        "saques": 0.00,
        "mensagem_saques": [],
        "bloqueado": "ativo",
        "foto_perfil": "https://res.cloudinary.com/dptprh0xk/image/upload/v1780883398/307ce493-b254-4b2d-8ba4-d12c080d6651_qaihst.png",

        "ip_usuario": ip_usuario,
        "aparelho": aparelho,
        "navegador": navegador,
        "status": "offline",  


        "criado_em": datetime.now(timezone.utc)
    }

    result = users_collection.insert_one(usuario)

    usuario["_id"] = str(result.inserted_id)
    return usuario


#================================================================================
class UsuarioModel:
    def __init__(self):
        self.collection = users_collection  # corrigido aqui

    def create_usuario(self, data):
        try:
            existente = self.collection.find_one({"cpf": data.get("cpf")})
            if existente:
                return str(existente["_id"])

            result = self.collection.insert_one(data)
            return str(result.inserted_id)

        except Exception as e:
            print("ERRO MODEL INSERT:", e)
            return None


    def deletar_usuario(user_id: str) -> bool:
        try:
            if not ObjectId.is_valid(user_id):
                return False
            result = users_collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print("ERRO AO DELETAR:", e)
            return False

    def update_usuario(self, user_id, new_data):
        try:
            new_data["data_atualizacao"] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {"_id": str(user_id)},
                {"$set": new_data}
            )
            return result.modified_count

        except Exception as e:
            print("ERRO UPDATE:", e)
            return 0

#================================================================================================================================
#================================================================================================================================


# =========================
# MODELS.PY
# =========================


# PROJETO
projetos_collection = db["projetos"]


def criar_projeto(
    nome_projeto: str,
    quantidade: str,
    valor_unidade: float,
    dt_sorteio: str,
    valor_injetado_premiacao: str = "",
    horario_sorteio: str = "",
    imagem_projeto: str = "",
    video_instrucao: str = "",
    link_instagram: str = "",
    link_youtube: str = "",
    link_whatsapp_grupo: str = "",
    link_whatsapp_canal: str = "",
    link_whatsapp_suporte: str = "",
    link_tiktok: str = "",
    link_facebook: str = "",
    link_kwai: str = "",
    status: str = ""
) -> dict:

    projeto = {
        "nome_projeto": nome_projeto.strip(),
        "quantidade": quantidade.strip(),
        "valor_unidade": valor_unidade,
        "dt_sorteio": dt_sorteio.strip(),
        "valor_injetado_premiacao": valor_injetado_premiacao.strip(),
        "horario_sorteio": horario_sorteio.strip(),
        "imagem_projeto": imagem_projeto.strip(),
        "video_instrucao": video_instrucao.strip(),
        "link_instagram": link_instagram.strip(),
        "link_youtube": link_youtube.strip(),
        "link_whatsapp_grupo": link_whatsapp_grupo.strip(),
        "link_whatsapp_canal": link_whatsapp_canal.strip(),
        "link_whatsapp_suporte": link_whatsapp_suporte.strip(),
        "link_tiktok": link_tiktok.strip(),
        "link_facebook": link_facebook.strip(),
        "link_kwai": link_kwai.strip(),
        "status": status.strip(),
        "numeros_sorteados": [],
        "criado_em": datetime.now(timezone.utc)
    }

    result = projetos_collection.insert_one(projeto)

    projeto["_id"] = str(result.inserted_id)

    return projeto


def get_all_projetos():
    return list(projetos_collection.find())
#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# VENDEDORES
def criar_vendedor(
    nome: str, 
    sobrenome: str, 
    cpf: str, 
    dt_nascimento: str, 
    email: str, 
    chave_pix: str, 
    comissao: str, 
    ip_usuario: str, 
    aparelho: str,
    localizacao: str,  # 📍 Adicionado o parâmetro da localização aqui
    navegador: str     # 🌐 Adicionado o parâmetro do navegador aqui
) -> dict:
    
    cpf = limpar_cpf(cpf)

    if not nome.strip() or not validar_cpf(cpf) or not email.strip() or not dt_nascimento.strip() or not chave_pix.strip():
        raise ValueError("Dados inválidos para cadastro.")

    if vendedores_collection.find_one({"cpf": cpf}):
        raise ValueError("CPF já cadastrado.")

    vendedor = {
        "nome": nome.strip(),
        "sobrenome": sobrenome.strip(),
        "cpf": cpf,
        "dt_nascimento": dt_nascimento.strip(),
        "email": email.strip(),
        "chave_pix": chave_pix.strip(),
        "comissao": comissao.strip(),
        "mensagem_usuarios": [],
        "bloqueado": "ativo",
        "ip_usuario": ip_usuario,
        "aparelho": aparelho,
        "localizacao": localizacao.strip(),  # 💾 Salvando a localização no banco de dados
        "navegador": navegador,     
        "status": "offline",  
        "criado_em": datetime.now(timezone.utc)
    }

    result = vendedores_collection.insert_one(vendedor)
    vendedor["_id"] = str(result.inserted_id)

    return vendedor
#================================================================================================================================
#================================================================================================================================

#--------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------
# models.py trecho relacionado pagamentos 
#  PAGAMENTOS 

pagamentos_collection = db[PAGAMENTOS_COLLECTION_NAME]


def criar_documento_pagamento(payment_id, status, valor, cpf, email_user,
                              payment_method_id,
                              lista_numeros=None,
                              vendedor=None,
                              qr_code=None,
                              qr_image_url=None,
                              taxa_mp=None,
                              data_criacao=None):

    if data_criacao is None:
        data_criacao = datetime.now(timezone.utc)

    return {
        "_id": str(payment_id),
        "status": status,
        "valor": float(valor),
        "cpf": cpf,
        "vendedor": vendedor,
        "email_usuario": email_user,
        "qr_code": qr_code,
        "payment_method_id": payment_method_id,
        "qr_image_url": qr_image_url,
        "data_criacao": data_criacao,
        "data_atualizacao": None,
        "taxa_mp": float(taxa_mp) if taxa_mp is not None else None,
        "lista_numeros": lista_numeros or []
    }

class PagamentoModel:

    def __init__(self):
        self.collection = pagamentos_collection

    def create_pagamento(self, data):
        try:
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

def criar_documento_bilhete(bilhete_id, cpf, nome_user, valor_unidade, email_user, lista_numeros=None, lista_urls_img_bilhetes=None, data_criacao=None):

    if data_criacao is None:
        data_criacao = datetime.now(timezone.utc)

    return {
        "_id": str(bilhete_id),
        "cpf": cpf,
        "nome_usuario": nome_user,
        "email_usuario": email_user,
        "data_criacao": data_criacao,
        "status": "pending",
        "valor": valor_unidade,
        "payment_id": "aguardando gerar pagamento",
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

    # BUSCAR POR EMAIL (para pegar as URLs do Cloudinary antes de apagar)
    def find_by_email(self, email):
        try:
            # Retorna todos os documentos que possuem esse email
            return list(self.collection.find({"email_usuario": email}))
        except Exception as e:
            print("ERRO BUSCA POR EMAIL:", e)
            return []

    # DELETAR TODOS POR EMAIL (MongoDB)
    def delete_many_by_email(self, email):
        try:
            result = self.collection.delete_many({"email_usuario": email})
            return result.deleted_count
        except Exception as e:
            print("ERRO DELETE MANY:", e)
            return 0


#=====================================================================================================================
# RASPADINHAS
#=====================================================================================================================
raspadinhas_collection = db[RASPADINHAS_COLLECTION_NAME]

def criar_documento_raspadinha(raspadinha_id, cpf, nome_user, valor_unidade, email_user, vendedor, quantidade_raspadinha=None, data_criacao=None):

    if data_criacao is None:
        data_criacao = datetime.now(timezone.utc)

    return {
        "_id": str(raspadinha_id),
        "cpf": cpf,
        "nome_usuario": nome_user,
        "email_usuario": email_user,
        "data_criacao": data_criacao,
        "status": "pending",
        "vendedor": vendedor,
        "valor": valor_unidade,
        "payment_id": "aguardando gerar pagamento",
    }

class RaspadinhaModel:
    def __init__(self):
        self.collection = raspadinhas_collection

    def create_raspadinha(self, data):
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


    def get_raspadinha_by_id(self, raspadinha_id):
        return self.get_raspadinha(raspadinha_id)


    def get_all_raspadinhas(self):
        docs = list(self.collection.find())
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs


    def update_raspadinha(self, raspadinha_id, new_data):
        try:
            new_data["data_atualizacao"] = datetime.now(timezone.utc)

            result = self.collection.update_one(
                {"_id": str(raspadinha_id)},
                {"$set": new_data}
            )
            return result.modified_count

        except Exception as e:
            print("ERRO UPDATE:", e)
            return 0


    def get_raspadinhas_by_usuario(self, usuario_id):
        docs = list(self.collection.find({"usuario_id": ObjectId(usuario_id)}))
        for d in docs:
            d["_id"] = str(d["_id"])
        return docs

    def delete_raspadinha(self, raspadinha_id):
        try:
            result = self.collection.delete_one({"_id": str(raspadinha_id)})
            return result.deleted_count

        except Exception as e:
            print("ERRO DELETE:", e)
            return 0

    # BUSCAR POR EMAIL (para pegar as URLs do Cloudinary antes de apagar)
    def find_by_email(self, email):
        try:
            # Retorna todos os documentos que possuem esse email
            return list(self.collection.find({"email_usuario": email}))
        except Exception as e:
            print("ERRO BUSCA POR EMAIL:", e)
            return []

    # DELETAR TODOS POR EMAIL (MongoDB)
    def delete_many_by_email(self, email):
        try:
            result = self.collection.delete_many({"email_usuario": email})
            return result.deleted_count
        except Exception as e:
            print("ERRO DELETE MANY:", e)
            return 0



# MODELS.PY
# SAQUES
saques_collection = db["saques"]

def criar_saque(
    nome_favorecido,
    cpf_favorecido,
    email_favorecido,
    valor_saque,
    identificacao,
    descricao,
    status=""
) -> dict:

    saque = {
        "identificacao": str(identificacao).strip(),
        "valor_saque": float(valor_saque), 
        "descricao": str(descricao).strip(),
        "nome_favorecido": str(nome_favorecido).strip(),
        "cpf_favorecido": str(cpf_favorecido).strip(),
        "email_favorecido": str(email_favorecido).strip(),
        "status": str(status).strip(),
        "mensagens_solicitando_saques": [],
        "mensagens_resposta_saques": [],
        "criado_em": datetime.now(timezone.utc)
    }

    result = saques_collection.insert_one(saque)
    saque["_id"] = str(result.inserted_id)

    return saque

def get_all_saques():
    return list(saques_collection.find())




# ====================================================================================================================
# ADICIONADO: HISTÓRICO DE MENSAGENS CHAT (SOCKET.IO)
# ====================================================================================================================

def salvar_mensagem(from_tipo, from_id, to_tipo, to_id, mensagem, arquivo="", arquivo_tipo=""):
    doc_mensagem = {
        "from_tipo": from_tipo.strip(),
        "from_id": from_id.strip(),
        "to_tipo": to_tipo.strip(),
        "to_id": to_id.strip(),
        "mensagem": mensagem.strip(),
        "arquivo": arquivo.strip(),
        "arquivo_tipo": arquivo_tipo.strip(),
        "criado_em": datetime.now(timezone.utc),
        "lida": False 
    }
    result = mensagens_collection.insert_one(doc_mensagem)
    doc_mensagem["_id"] = str(result.inserted_id)
    return doc_mensagem

class MensagemModel:
    def __init__(self):
        self.collection = mensagens_collection

    def get_historico_chat(self, id_usuario: str, id_vendedor: str):
        """
        Busca e ordena de forma cronológica todas as mensagens trocadas 
        entre um Usuário específico e um Vendedor específico.
        """
        try:
            query = {
                "$or": [
                    {"from_id": id_usuario, "to_id": id_vendedor},
                    {"from_id": id_vendedor, "to_id": id_usuario}
                ]
            }
            # Traz o histórico do mais antigo para o mais recente
            docs = list(self.collection.find(query).sort("criado_em", ASCENDING))
            for d in docs:
                d["_id"] = str(d["_id"])
            return docs
        except Exception as e:
            print("ERRO AO BUSCAR HISTÓRICO CHAT:", e)
            return []

    def deletar_conversa(self, id_usuario: str, id_vendedor: str) -> int:
        """
        Deleta todo o histórico de mensagens entre as duas partes envolvidas.
        """
        try:
            query = {
                "$or": [
                    {"from_id": id_usuario, "to_id": id_vendedor},
                    {"from_id": id_vendedor, "to_id": id_usuario}
                ]
            }
            result = self.collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            print("ERRO AO DELETAR HISTÓRICO CHAT:", e)
            return 0