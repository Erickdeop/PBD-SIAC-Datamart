from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError
from pathlib import Path
from tqdm import tqdm
import re
import json
import re
from utils_text import limpar_texto, padronizar_autor

def extrair(bloco, campos, campo):
    indice = campos.index(campo)
    if indice < len(campos) - 1:
        proximo = campos[indice + 1]
        padrao = rf"{campo}:\s*([\s\S]*?)(?={proximo}:)"
    else:
        padrao = rf"{campo}:\s*([\s\S]*)$"
    m = re.search(padrao, bloco, flags=re.DOTALL)
    return m.group(1).strip() if m else None

def parse_artigos(texto):
    padrao_blocos = r"ARTIGO:\s*\d+[\s\S]*?(?=ARTIGO:|$)"
    blocos = re.findall(padrao_blocos, texto, flags=re.DOTALL)
    campos = ["ARTIGO", "TITULO", "RESUMO", "PARTICIPANTES"]
    artigos = []
    for bloco in tqdm(blocos):
        artigo = {}
        for campo in campos:
            artigo[campo.lower()] = extrair(bloco, campos, campo)
        artigos.append(artigo)
    return artigos

def separa_nomes_autores(linha_nomes):
    arrumado = re.sub(r'([a-zá-ú])([A-Z])', r'\1\n\2', linha_nomes)
    nomes = [linha.strip() for linha in arrumado.split("\n") if linha.strip()]
    nomes = [linha.split("-")[0].strip() for linha in nomes]
    nomes = [padronizar_autor(nome) for nome in nomes]
    return nomes

def parse_trabalhos(texto):
    blocos = re.split(r"(?=T\s*-\s*\d{3})", texto)
    blocos = [b.strip() for b in blocos if b.strip()]
    resultados = []
    for bloco in blocos[1:]:
        linhas = [l.strip() for l in bloco.splitlines() if l.strip()]
        id_trab = linhas[0]
        partes_titulo = []
        unidade = next((l.replace("Unidade:", "").strip()
                        for l in linhas if l.startswith("Unidade:")), None)
        centro = next((l.replace("Centro:", "").strip()
                       for l in linhas if l.startswith("Centro:")), None)
        linha_contato = next((l for l in linhas if l.startswith("Contato:")), None)
        if linha_contato:
            contato = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', linha_contato)
        else:
            contato = []
            
        try:
            idx_unidade = next(i for i, l in enumerate(linhas) if l.startswith("Unidade:"))
        except StopIteration:
            idx_unidade = None

        try:
            idx_centro = next(i for i, l in enumerate(linhas) if l.startswith("Centro:"))
        except StopIteration:
            idx_centro = None

        try:
            idx_contato = next(i for i, l in enumerate(linhas) if l.startswith("Contato:"))
        except StopIteration:
            idx_contato = len(linhas)

        try:
            inicio_autores = next(i for i, l in enumerate(linhas) if "Autor(es):" in l)
        except StopIteration:
            if idx_centro is not None:
                inicio_autores = idx_centro + 1
            else:
                inicio_autores = idx_unidade + 1 if idx_unidade is not None else 2

        autores = []
        resumo_linhas = []

        for i in range(1, idx_unidade if idx_unidade else 2):
            partes_titulo.append(linhas[i])
        
        titulo = " ".join(partes_titulo)
        nome_autor = True if idx_unidade else False
        for i in range(inicio_autores, idx_contato):
            if any(s in linhas[i] for s in ["- Técnico", "- Externo", "- Estudante de Graduação", "- Docente", "- Discente", " - Outro"]):
                nomes_separados = separa_nomes_autores(linhas[i])
                autores += nomes_separados
            elif "Autor(es):" in linhas[i]:
                    nomes_separados = separa_nomes_autores(linhas[i].split("Autor(es):")[1].strip())
                    autores += nomes_separados
                    if not nome_autor:
                        nome_autor = True
            elif nome_autor:
                    if len(linhas[i].split(" ")) > 10:
                        resumo_linhas.append(linhas[i].strip())
                        nome_autor = False
                    else:
                        autores += separa_nomes_autores(linhas[i])
            else:
                resumo_linhas.append(linhas[i])
    
        resumo = " ".join(resumo_linhas).strip()
        resultados.append({
            "id": id_trab,
            "titulo": titulo,
            "unidade": unidade,
            "centro": centro,
            "autores": autores,
            "resumo": resumo,
            "contato": contato
        })
    return resultados

def main():
    path = Path('data')
    for arquivo in tqdm(path.glob('*.pdf'), total=len(list(path.glob('*.pdf')))):
        ano = arquivo.stem[-4:]
        try:
            reader = PdfReader(arquivo)
        except PdfReadError:
            print(f"PDF invalido - {arquivo}")
            continue
        texto = ""
        for pagina in tqdm(reader.pages):
            texto += pagina.extract_text() or ""
        texto = limpar_texto(texto)
        parsed = parse_trabalhos(texto) if ano != '2016' else parse_artigos(texto)
        with open(path / f'caderno_parsed_{ano}.json', 'w', encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    main()
