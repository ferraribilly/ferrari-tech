from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode
import os

# =========================
# CONFIG
# =========================
W, H = 900, 450

# Dados vai vim do frontend e renderizar bilhete 
numero_bilhete = "Nº 001"
evento = "Rifa Dia das Mães"
descricao = "Prêmio: R$ 150,00 via Pix"
data_sorteio = "Sorteio: sábado 05/05/2026"

nome = "William Henrique de Araujo Delduque Ferreira"
email = "williamferrari52@gmail.com"
cpf = "386.***543**-21"

link_qrcode = "https://ferrari-tech.onrender.com/meus-numeros"
caminho_logo = r"C:\\Users\\william\\Desktop\\meu-portifolio\\RIFA_DAS_MAES\\Backend\\static\\w.png"

# =========================
# FUNDO
# =========================
img = Image.new("RGB", (W, H))
draw = ImageDraw.Draw(img)

for y in range(H):
    draw.line([(0, y), (W, y)], fill=(200 - y//5, 20, 20))

# =========================
# CARD
# =========================
margin = 30
cx1, cy1 = margin, margin
cx2, cy2 = W - margin, H - margin

cw, ch = cx2 - cx1, cy2 - cy1

card = Image.new("RGB", (cw, ch), "white")
shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 100)).filter(ImageFilter.GaussianBlur(10))

img.paste(shadow, (cx1+4, cy1+4), shadow)
img.paste(card, (cx1, cy1))

draw = ImageDraw.Draw(img)

# =========================
# FONTES
# =========================
try:
    f_titulo = ImageFont.truetype("arialbd.ttf", 36)
    f_texto = ImageFont.truetype("arial.ttf", 24)
    f_label = ImageFont.truetype("arialbd.ttf", 20)
    f_num = ImageFont.truetype("arialbd.ttf", 28)
except:
    f_titulo = f_texto = f_label = f_num = ImageFont.load_default()

# =========================
# LOGO
# =========================
if os.path.exists(caminho_logo):
    logo = Image.open(caminho_logo).convert("RGBA")
    logo.thumbnail((100, 60))
    img.paste(logo, (cx1 + 20, cy1 + 20), logo)

# =========================
# TÍTULO
# =========================
draw.text((cx1 + 140, cy1 + 25), evento, font=f_titulo, fill=(0, 0, 0))
draw.text((cx1 + 140, cy1 + 70), descricao, font=f_texto, fill=(80, 80, 80))
draw.text((cx1 + 140, cy1 + 100), data_sorteio, font=f_texto, fill=(80, 80, 80))

# NOVA LINHA (ALINHADA CORRETAMENTE)
draw.text((cx1 + 140, cy1 + 130), "Sorteio pela Loteria Federal", font=f_label, fill=(180, 0, 0))

# =========================
# GRID (COLUNAS)
# =========================
left_x = cx1 + 20
right_x = cx2 - 220

# =========================
# DADOS
# =========================
start_y = cy1 + 170  # leve ajuste pra não colidir com nova linha
gap = 40

def linha(label, valor, y):
    draw.text((left_x, y), label, font=f_label, fill=(150, 0, 0))
    draw.text((left_x + 140, y), valor, font=f_texto, fill=(0, 0, 0))

linha("Nome:", nome, start_y)
linha("Email:", email, start_y + gap)
linha("CPF:", cpf, start_y + gap*2)

# linha separadora
draw.line((left_x, start_y - 15, right_x - 20, start_y - 15), fill=(200,0,0), width=2)

# =========================
# NÚMERO
# =========================
draw.rectangle([left_x, cy2 - 60, left_x + 200, cy2 - 20], fill=(200, 0, 0))
draw.text((left_x + 10, cy2 - 55), numero_bilhete, fill="white", font=f_num)

# =========================
# QR CODE
# =========================
qr = qrcode.make(link_qrcode).convert("RGB").resize((150,150))

qr_box = 180
qr_bg = Image.new("RGB", (qr_box, qr_box), "white")
qr_draw = ImageDraw.Draw(qr_bg)

qr_draw.rectangle([0,0,qr_box-1,qr_box-1], outline=(200,0,0), width=3)
qr_bg.paste(qr, (15,15))

qr_y = cy1 + (ch // 2) - (qr_box // 2)
img.paste(qr_bg, (right_x, qr_y))

# =============================================
# SALVAR 
# =============================================
os.makedirs("rifas", exist_ok=True)
path = os.path.join("rifas", f"bilhete_{numero_bilhete.replace(' ', '_')}.png")
img.save(path)

print("OK:", path)