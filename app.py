import csv
import pdfplumber
import pingodoce as pd
import continente as cnt

'''
Ficheiro de exemplo; alterar path/nome conforme necessário.
Futuramente, poderá vir directamente do e-mail ou ler todos os existentes numa pasta a definir
'''
#ficheiro = "pdfs\\pd\\fatura1.pdf"
ficheiro_pd = "pdfs\\pd\\fatura1.pdf"
ficheiro_cnt = "pdfs\\continente\\1.pdf"

def main():

    with pdfplumber.open(ficheiro_pd) as pdf:
       talao = pdf.pages[0]

       # Obtemos apenas os totais do documento (Total Documento; Total Poupança; Total Pago)
       totais = pd.get_doc_totals(talao)
       # Obtemos uma lista de artigos com todas as características (ver abaixo a estrutura)
       artigos = pd.get_processed_lines(talao)
       # Obtemos todas as linhas do documento; serve essencialmente para validação e testes
       linhas = pd.get_raw_lines(talao)


    # Mostramos a informação obtida para fins de validação
    print('\n\n==== LINHAS ====')
    for linha in linhas:
        print(linha)

    print('\n\n==== ARTIGOS ====')
    for artigo in artigos:
        print(artigo)

    print('\n\n==== TOTAIS ====')
    print(f'Total do documento {totais[0]} Euros')
    print(f'Total de poupança {totais[1]} Euros')
    print(f'Total pago {totais[2]} Euros')

# continente - em testes

    with pdfplumber.open(ficheiro_cnt) as pdf:
       talao = pdf.pages[0]
       artigos = cnt.get_processed_lines(talao)

    print('\n\n==== ARTIGOS ====')
    for artigo in artigos:
        print(artigo)

    '''
    Apenas a título de exemplo, conversão simples para CSV
    Futuramente, podemos percorrer a lista de artigos e escrever a informação em base de dados
    '''
    # campos = ['Categoria', 'Artigo', 'Preco', 'Taxa', 'TaxaValor', 'Quantidade', 'PrecoUnitario','PoupancaImediata'] 
    # with open('fatura.csv', 'w', newline='', encoding='utf-8') as csv_file:
    #     writer = csv.writer(csv_file, delimiter=';',quotechar='"', quoting=csv.QUOTE_ALL)
    #     writer.writerow(campos)
    #     writer.writerows(artigos)
        

if __name__=="__main__":
    main()