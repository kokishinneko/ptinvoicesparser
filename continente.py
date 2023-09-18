import pdfplumber
import re


## EM TESTES


def is_categoria(linha):
    if linha.endswith(':'):
        return True
    
def is_desconto_directo(linha):
    if str(linha).startswith("DESCONTO DIRETO"):
        return True

def is_artigo(linha):
    pattern = r"^\([A-Za-z]\)"
    if re.match(pattern, linha):
        return True

def is_qtd_preco(linha):
    s = str(linha).split()
    try:
        if s[1] == "X" and len(s) == 4:
            return True
    except:
        return False

def get_preco_artigo(linha):
    s = str(linha).split()
    preco = s[len(s) - 1]
    preco1 = s[len(s) - 1].replace(",", ".")
    try:
        float(preco1)
        ss = str(linha[0]).replace(preco, "")
        return preco1
    except ValueError:
        return -1

def get_taxa_artigo(linha):
    return str(linha).split()[0]

def get_qtd(linha):
    return str(linha).split()[0].replace(",", ".")

def get_preco_unit(linha):
    return str(linha).split()[2].replace(",", ".")

def get_poupanca(linha):
    s = str(linha).split()[2]
    p = s.replace(",", ".").replace("(", "").replace(")", "")
    try:
        float(p)
        return p
    except ValueError:
        return 0

def fix_descricao(linha):
    s = str(linha).split()
    ts = []
    for x in range(1, len(s) - 1):
        ts.append(s[x])
    return " ".join(ts)

def get_raw_lines(talao):
    linhas = []
    for a in talao.extract_text_lines():
        linha = a["text"]
        linhas.append(linha)
    return linhas

def get_processed_lines(talao):
    linhas = []

    for a in talao.extract_text_lines():
        linha = a["text"]
        linhas.append(linha)

    inicio = linhas.index("IVA DESCRICAO VALOR") + 1
    fim = [i for i, item in enumerate(linhas) if re.search('TOTAL A PAGAR (\d+,\d+)', item)][0]

    categoria = ""
    desc_artigo = ""
    cod_taxa = ""
    valor_taxa = ""
    quantidade = ""
    preco_unit = ""
    poupa_imed = 0
    lista_artigos = []

    for x in range(inicio, fim):
        linha = linhas[x]
        if is_categoria(linha):
            categoria = linha.replace(':','')
            continue
        elif is_desconto_directo(linha):
            lista_artigos[len(lista_artigos) - 1][7] = get_poupanca(linha)
            continue
        elif is_artigo(linha):
            preco_total = get_preco_artigo(linha)
            cod_taxa = get_taxa_artigo(linha)
            valor_taxa = 0 # formato diferente do PD
            quantidade = 1
            desc_artigo = fix_descricao(linha)
        elif is_qtd_preco(linha):
            quantidade = get_qtd(linha)
            preco_unit = get_preco_unit(linha)
            preco_total = get_preco_artigo(linha)
        else:
            continue
        if desc_artigo != "" and preco_total != -1:
            lista_artigos.append(
                [
                    categoria,
                    desc_artigo,
                    preco_total,
                    cod_taxa,
                    valor_taxa,
                    quantidade,
                    preco_unit,
                    poupa_imed,
                ]
            )

    return lista_artigos

# def get_doc_totals(talao_src):
#     linhas = []
#     talao = talao_src
#     for a in talao.extract_text_lines():
#         linha = a["text"]
#         linhas.append(linha)

#     inicio = linhas.index("IVA DESCRICAO VALOR") + 1
#     fim = [i for i, item in enumerate(linhas) if re.search('TOTAL A PAGAR (\d+,\d+)', item)][0]

#     for x in range(fim, len(linhas) - 1):
#         l = str(linhas[x])
#         if l.startswith("TOTAL") and len(l.split()) == 2:
#             total = l.split()[1].replace(",", ".")
#         if l.startswith("TOTAL POUPANÇA") and len(l.split()) == 3:
#             poupanca = l.split()[2].replace("(", "").replace(")", "").replace(",", ".")
#         if l.startswith("TOTAL A PAGAR") and len(l.split()) == 4:
#             total_pago = l.split()[3].replace(",", ".")
#     return [total, poupanca, total_pago]

if __name__=="__main__":
    print('Modulo Continente v0.1')
