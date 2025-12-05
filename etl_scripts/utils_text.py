import re
import unicodedata
from ftfy import fix_text

def normalizar_espacos(texto):
    if not texto:
        return texto
    texto = re.sub(r'[ \t\r\f\v]+', ' ', texto)
    return texto.strip()

def normalizar_ids_trabalhos(texto):
    padrao_ids = re.compile(r'\bT\s*-\s*(\d+)\b', re.IGNORECASE)
    texto = padrao_ids.sub(lambda m: f"T-{m.group(1)}", texto)
    return texto

def limpar_texto(texto):
    if not texto:
        return texto

    texto = fix_text(texto)

    texto = unicodedata.normalize("NFC", texto)

    texto = normalizar_espacos(texto)

    texto = normalizar_ids_trabalhos(texto)

    return texto

def padronizar_autor(nome):
    if not nome:
        return nome

    nome = normalizar_espacos(nome)

    partes = nome.split()
    nome = " ".join(p.capitalize() for p in partes)

    return nome
