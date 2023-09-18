import pdfplumber
import re

'''
Definimos duas constantes, com a posição "x0" onde se encontra a categoria, 
assim como uma lista de palavras a ignorar visto que também surgem na posição 20
'''
CAT_POS = 20
CAT_IGNORE = ["TOTAL", "Taxa", "Isenção", "Descontos"]


'''
Validamos se é uma categoria lendo o ficheiro original e comparando com a linha original
Isto é necessário porque na primeira leitura obtemos linhas completas, mas como precisamos 
de validar a posição foi necessário usar o "extract_words"
'''
def is_categoria(pdfdoc, linha):
    flag = False
    for x in pdfdoc.extract_words():
        if (x["x0"] == CAT_POS) and (x["text"] not in CAT_IGNORE):
            if str(linha).startswith(x["text"]):
                flag = True
        if flag:
            return True
    return False

'''
Confirmamos se a linha é uma Poupança Imediata de forma a extrair o valor posteriormente
'''
def is_desconto_directo(linha):
    if str(linha).startswith("Poupança Imediata"):
        return True

'''
Uma vez que todas as linhas de artigos têm a taxa de IVA no ínicio, usamos uma expressão
regular para validar se é um artigo; Se existe algo tipo C 23%, assumimos que é uma linha de
artigo normal e que será tratada posteriormente
'''
def is_artigo(linha):
    pattern = r"[A-Z] \d{1,3}%"
    if re.match(pattern, linha):
        return True

'''
Um ugly-hack, funciona mas é susceptível de dar asneira se eventualmente houver um artigo com a descrição X
Funciona com o exemplo dado, validamos se a linha tem 4 elementos (separados por espaços) e se a 2ª posição
é a letra X, por norma esta linha tem: quantidade X preco unitario
A quantidade e o preço unitário é extraído posteriormente noutra função
'''
def is_qtd_preco(linha):
    s = str(linha).split()
    try:
        if s[1] == "X" and len(s) == 4:
            return True
    except:
        return False

'''
Obtemos o preço do artigo quebrando a string em partes, dado que o preço é sempre a posição final
usamos len -1 e verificamos se é possível converter para float
A substituição de ',' para '.' foi a forma mais rápida que encontrei para garantir a conversão em float
possivelmente há formas mais correctas de fazer isto. Em caso de falha, devolve -1 e sabemos que algo correu mal
'''
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

'''
Quebramos a linha do artigo para obter a descrição da taxa de IVA na 1ª posição
'''
def get_taxa_artigo(linha):
    return str(linha).split()[0]

'''
Quebramos a linha do artigo para obter a taxa de IVA na 2ª posição
'''
def get_taxavalor_artigo(linha):
    return str(linha).split()[1]

'''
Nas linhas de quantidade + preço unitário, aplicamos o mesmo método e devolvemos a 1º posição (quantidade)
'''
def get_qtd(linha):
    return str(linha).split()[0].replace(",", ".")

'''
Nas linhas de quantidade + preço unitário, aplicamos o mesmo método e devolvemos a 3º posição (preco unitario)
'''
def get_preco_unit(linha):
    return str(linha).split()[2].replace(",", ".")

'''
Quando a linha é identificada como Poupança Imediata, obtemos o seu valor na 3ª posição 
e retiramos os () da string original para poder ser tratado como float
'''
def get_poupanca(linha):
    s = str(linha).split()[2]
    p = s.replace(",", ".").replace("(", "").replace(")", "")
    try:
        float(p)
        return p
    except ValueError:
        return 0

'''
Quebramos a linha original do artigo e vamos ler da 2ª posição ao final -1 dado que
nas primeiras posições temos a informação do IVA e no final o preço
Voltamos a juntar tudo numa string e é devolvida como a descrição final do artigo
'''
def fix_descricao(linha):
    s = str(linha).split()
    ts = []
    for x in range(2, len(s) - 1):
        ts.append(s[x])
    return " ".join(ts)

'''
Método para obter uma lista com todas as linhas do talão sem qualquer tratamento adicional
Poderá ser útil para retirar outro tipo de informações ou apenas validar se o código está a ler
o ficheiro conforme esperado
'''
def get_raw_lines(talao):
    linhas = []
    for a in talao.extract_text_lines():
        linha = a["text"]
        linhas.append(linha)
    return linhas

'''
Processamos a informação no talão, lendo linha a linha e validando cada uma delas
Uma vez que neste passo só nos interessam as linhas de artigos e categorias definimos um "inicio" e um "fim"
Os documentos do Pingo Doce têm esse "separador"; após a linha "Artigos" inicia efectivamente a lista de compras
Finaliza com "Resumo", a partir deste ponto encontram-se as informações de IVA, etc... 
Se tudo for validado é adicionado o artigo e respectivos valores à lista "lista_artigos" que será
utilizada posteriormente pelo programa principal. Poderei eventualmente trocar de lista para dicionário se encontrar
alguma vantagem, para efeitos de teste, devolver no tipo List é suficiente.
'''
def get_processed_lines(talao):
    linhas = []

    for a in talao.extract_text_lines():
        linha = a["text"]
        linhas.append(linha)

    inicio = linhas.index("Artigos") + 1
    fim = linhas.index("Resumo") + 1

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
        if is_categoria(talao, linha):
            categoria = linha
            continue
        elif is_desconto_directo(linha):
            lista_artigos[len(lista_artigos) - 1][7] = get_poupanca(linha)
            continue
        elif is_artigo(linha):
            preco_total = get_preco_artigo(linha)
            cod_taxa = get_taxa_artigo(linha)
            valor_taxa = get_taxavalor_artigo(linha)
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

'''
Opcional, uma vez que os dados podem ser calculados a partir do momento em que temos a lista com preços, descontos, etc...
Pode servir para validar; devolve uma lista com 3 elementos: Total do documento, Total de Poupança, Total efectivamente pago
'''
def get_doc_totals(talao_src):
    linhas = []
    talao = talao_src
    for a in talao.extract_text_lines():
        linha = a["text"]
        linhas.append(linha)

    inicio = linhas.index("Artigos") + 1
    fim = linhas.index("Resumo") + 1

    for x in range(fim, len(linhas) - 1):
        l = str(linhas[x])
        if l.startswith("TOTAL") and len(l.split()) == 2:
            total = l.split()[1].replace(",", ".")
        if l.startswith("TOTAL POUPANÇA") and len(l.split()) == 3:
            poupanca = l.split()[2].replace("(", "").replace(")", "").replace(",", ".")
        if l.startswith("TOTAL A PAGAR") and len(l.split()) == 4:
            total_pago = l.split()[3].replace(",", ".")
    return [total, poupanca, total_pago]

if __name__=="__main__":
    print('Modulo Pingo Doce v1.0')