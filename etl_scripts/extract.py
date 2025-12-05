import asyncio
import httpx
from bs4 import BeautifulSoup
import re
from pathlib import Path 

async def extrair_links_cadernos_antigos(client, url):
    r = await client.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    botoes = soup.find_all('button', class_='siac-year-link-btn')

    pdfs = {}

    for botao in botoes:
        onclick = botao.get('onclick', '')
        m = re.search(r"siacOpenLink\('(.+?)'\)", onclick)
        if not m:
            continue

        url_pdf = m.group(1)
        ano = botao.text.strip()

        nome_pdf = f'Cadernos Resumos {ano}.pdf'
        pdfs[nome_pdf] = url_pdf

    return pdfs

async def extrair_links_cadernos_novos(client, url):
    r = await client.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    botoes = soup.find_all('div', class_='siac-year-view')

    pdfs = {}

    for botao in botoes:
            ano = botao.get("data-year")
            cadernos = botao.find_all('div', class_='siac-card')[-1]
            cadernos = cadernos.find_all('li')
            for caderno in cadernos:
                onclick = caderno.get('onclick', '')
                m = re.search(r"siacOpenLink\('(.+?)'\)", onclick)
                if not m:
                    continue

                url_pdf = m.group(1)

                nome_pdf = f"{caderno.text.strip()} {ano}.pdf"
                pdfs[nome_pdf] = url_pdf
    return pdfs

async def baixar_pdf(client, nome_pdf, path, url_pdf):
    print(f'Baixando: {nome_pdf} -> {url_pdf}')

    try:
        r = await client.get(url_pdf)
        r.raise_for_status()

        content = r.content

        if not content or len(content) < 200:  
            print(f'Arquivo ignorado (vazio ou muito pequeno): {nome_pdf}')
            return

        with open(path / nome_pdf, 'wb') as f:
            f.write(content)

        print(f'Salvo: {nome_pdf}')

    except httpx.HTTPError as e:
        print(f'❌ Erro ao baixar {nome_pdf}: {e}')


async def main():
    url = 'https://siac.ufrj.br/edicoes-anteriores-e-certificados/'
    path = Path('data')
    async with httpx.AsyncClient(timeout=30.0) as client:
        pdf_dict = await extrair_links_cadernos_antigos(client, url)
        pdf_dict.update(await extrair_links_cadernos_novos(client, url))


        print(f'Encontrados {len(pdf_dict)} PDFs:')
        for nome, link in pdf_dict.items():
            print(f' - {nome}: {link}')

        tarefas = [
            baixar_pdf(client, nome_pdf, path, url_pdf)
            for nome_pdf, url_pdf in pdf_dict.items()
        ]

        await asyncio.gather(*tarefas)


if __name__ == '__main__':
    asyncio.run(main())
