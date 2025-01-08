import pandas as pd
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from ratelimit import limits, sleep_and_retry

# Cache para armazenar resultados de genes
gene_cache = {}

# Função para registrar erros em um arquivo de log
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# Limite de requisições por segundo (15 por segundo)
@sleep_and_retry
@limits(calls=15, period=1)
def fetch_gene_from_ensembl(chrom, pos):
    """
    Consulta a Ensembl REST API para obter genes associados a uma posição genômica.
    """
    server = "https://rest.ensembl.org"
    endpoint = f"/overlap/region/human/{chrom}:{pos}-{pos}?feature=gene"
    url = server + endpoint
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return ",".join([gene["external_name"] for gene in data if "external_name" in gene])
            else:
                return "None"  # Nenhum gene encontrado
        elif response.status_code == 400:
            log_error(f"Erro Ensembl (posição inválida): {chrom}:{pos}")
            return "No Data"
        else:
            log_error(f"Erro Ensembl para {chrom}:{pos} - Status: {response.status_code}")
            return "Error"
    except Exception as e:
        log_error(f"Erro ao acessar Ensembl para {chrom}:{pos} - Exceção: {e}")
        return "Error"

# Limite de requisições por segundo (10 por segundo para NCBI)
@sleep_and_retry
@limits(calls=10, period=1)
def fetch_gene_from_ncbi(chrom, pos):
    """
    Consulta o NCBI Gene API para obter genes associados a uma posição genômica.
    """
    server = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "gene",
        "term": f"{chrom}[Chromosome] AND {pos}[Base Position]",
        "retmode": "json",
    }
    try:
        response = requests.get(server, params=params)
        if response.status_code == 200:
            data = response.json()
            if "esearchresult" in data and "idlist" in data["esearchresult"] and data["esearchresult"]["idlist"]:
                return ",".join(data["esearchresult"]["idlist"])  # IDs dos genes
            else:
                return "None"  # Nenhum gene encontrado
        else:
            log_error(f"Erro NCBI para {chrom}:{pos} - Status: {response.status_code}")
            return "Error"
    except Exception as e:
        log_error(f"Erro ao acessar NCBI para {chrom}:{pos} - Exceção: {e}")
        return "Error"

def fetch_gene_from_multiple_sources(chrom, pos):
    """
    Consulta múltiplas fontes para buscar genes, com suporte a cache.
    """
    cache_key = f"{chrom}:{pos}"
    if cache_key in gene_cache:
        return gene_cache[cache_key]

    # Primeiro tenta a Ensembl
    gene = fetch_gene_from_ensembl(chrom, pos)
    if gene not in ["None", "Error", "No Data"]:
        gene_cache[cache_key] = gene
        return gene

    # Se falhar, tenta o NCBI
    gene = fetch_gene_from_ncbi(chrom, pos)
    gene_cache[cache_key] = gene if gene not in ["None", "Error"] else "No Data"
    return gene_cache[cache_key]

def extract_info_field(info, key):
    """
    Extrai um valor específico do campo INFO do VCF.
    Se houver múltiplos valores (separados por vírgulas), retorna o maior.
    """
    try:
        for field in info.split(";"):
            if field.startswith(key + "="):
                # Divide valores separados por vírgulas e converte para float
                values = [float(val) for val in field.split("=")[1].split(",")]
                return max(values)  # Retorna o maior valor
        return None
    except Exception as e:
        log_error(f"Erro ao extrair campo {key}: {e}")
        return None

def annotate_variants(input_vcf, output_tsv):
    print(f"Lendo o arquivo VCF: {input_vcf}")
    with open(input_vcf, 'r') as file:
        lines = file.readlines()
    print(f"Arquivo VCF lido com sucesso! Linhas totais: {len(lines)}")

    # Filtra as linhas de dados (não metadados) no VCF
    data_lines = [line for line in lines if not line.startswith("#")]
    print(f"Número de variantes encontradas: {len(data_lines)}")

    if not data_lines:
        print("Nenhuma variante encontrada. Verifique o conteúdo do arquivo.")
        return

    # Divide as colunas dos dados
    variants = [line.strip().split('\t') for line in data_lines]
    df = pd.DataFrame(variants, columns=[
        "CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "SAMPLE"
    ])
    print("DataFrame criado com sucesso!")

    # Extrai frequência e profundidade do campo INFO
    df["FREQUENCY"] = df["INFO"].apply(lambda x: extract_info_field(x, "AF") or 0.0)
    df["DP"] = df["INFO"].apply(lambda x: extract_info_field(x, "DP") or 0)

    # Prepara os dados para a paralelização
    variant_positions = [(row["CHROM"], int(row["POS"])) for _, row in df.iterrows()]

    # Executa as requisições de forma paralela com barra de progresso
    genes = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for result in tqdm(
            executor.map(lambda args: fetch_gene_from_multiple_sources(*args), variant_positions),
            total=len(variant_positions),
            desc="Anotando genes"
        ):
            genes.append(result)

    df["GENE"] = genes
    print("Anotação de genes concluída!")

    # Salva o DataFrame no formato TSV
    try:
        df.to_csv(output_tsv, sep='\t', index=False)
        print(f"Arquivo anotado salvo em: {output_tsv}")
    except Exception as e:
        log_error(f"Erro ao salvar arquivo anotado - Exceção: {e}")
        print(f"Erro ao salvar arquivo: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Uso: python annotate_variants.py <input_vcf> <output_tsv>")
    else:
        input_vcf = sys.argv[1]
        output_tsv = sys.argv[2]
        annotate_variants(input_vcf, output_tsv)
