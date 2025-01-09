### Desafio de Bioinformática  - DASA ###

### Objetivos ###
Este projeto foi desenvolvido para processar e anotar variantes de um arquivo VCF. 

Os principais objetivos incluem:
Anotar variantes com genes associados (usando Ensembl e NCBI).
Extrair informações de frequência (AF) e profundidade (DP) das variantes.
Criar uma API interativa para consumir os dados anotados.
Desenvolver uma interface web para visualizar e filtrar as variantes.
Empacotar a solução em um contêiner Docker, facilitando a portabilidade e a execução.

### Componentes do Projeto ###

### Pipeline de Bioinformática ###
Utiliza Snakemake para automatizar o processamento e anotação do arquivo VCF.
O pipeline gera um arquivo anotado (annotated_variants.tsv) com colunas:

CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, FORMAT, SAMPLE, GENE, FREQUENCY, DP.

### API Flask ###
Disponibiliza endpoints para:
Listar todas as variantes (com paginação).
Filtrar variantes com base em critérios (frequência e profundidade).
Visualizar dados de estatísticas básicas.

### Interface Web ### 
A interface é construída com templates HTML.
Permite visualização, pesquisa e filtragem das variantes.

### Container Docker ###
O projeto é empacotado em uma imagem Docker, simplificando sua execução e implantação.

### Estrutura do Projeto ###

A estrutura do projeto segue a seguinte organização de diretórios e arquivos:

bioinformatics-pipeline/

├── api/

│   ├── app.py                 # Código da API Flask

│   ├── templates/

│   │   └── index.html         # Interface web

├── pipeline/

│   ├── Snakefile              # Workflow do Snakemake

│   ├── scripts/

│   │   └── annotate_variants.py  # Script de anotação de variantes

├── data/                      # Diretório para arquivos de entrada/saída

│   ├── annotated_variants.tsv # Arquivo gerado pelo pipeline

│   └── NIST.vcf               # Arquivo VCF de entrada

├── requirements.txt           # Bibliotecas Python necessárias

├── Dockerfile                 # Configuração para criar a imagem Docker

└── docker-compose.yml         # Arquivo para gerenciar contêineres com Docker Compose

### Pré-Requisitos ###

Certifique-se de que as seguintes ferramentas estejam instaladas no seu sistema:

Python (>= 3.8) https://www.python.org/downloads/

Snakemake (disponível a partir da execução do arquivo requirements.txt)

Docker https://www.docker.com/

Git https://git-scm.com/downloads

Marque as opções de C++ e visual https://visualstudio.microsoft.com/visual-cpp-build-tools/

Para executar os comandos a seguir é possivel utilizar o "cmd" do Windows ou terminal de IDE, como por exemplo o visual studio code (foi testado em ambas opções)

### Configuração do Ambiente ###
1. Clone o repositório do projeto para o seu sistema após escolher a pasta de destino:

git clone https://github.com/marcusviniciusrodrigues/desafio_dasa.git

cd dasa-genomics

2. Crie e ative um ambiente virtual:

python -m venv venv

source venv/bin/activate  #Linux

venv\Scripts\activate     #Windows

3. Instale as dependências do projeto:

cd desafio_dasa

pip install -r requirements.txt


### Execução do Projeto ###

1. Executar o Pipeline
   
Para processar o arquivo VCF, execute:

snakemake --snakefile pipeline/Snakefile --cores 1

O arquivo resultante será salvo em data/annotated_variants.tsv.

2. Executar a API
Entre no diretório da API:

cd api

python app.py

A API estará disponível em http://127.0.0.1:5000.

3. Executar via Docker
   
Construa a imagem Docker:

docker build -t dasa-genomics .

Execute o contêiner:

docker run -p 5000:5000 -v "$(pwd)/data:/app/data" -e DATA_FILE_PATH=/app/data/annotated_variants.tsv dasa-genomics

Ou use o Docker Compose:

docker-compose up

Endpoints da API

http://127.0.0.1:5000

Retorna a página inicial da interface web.

Lista todas as variantes, com suporte à paginação:

http://127.0.0.1:5000/variants?page=1&limit=100

Filtra variantes com base em frequência (frequency) e profundidade (depth):

http://127.0.0.1:5000/variants/filter?frequency=0.01&depth=30

