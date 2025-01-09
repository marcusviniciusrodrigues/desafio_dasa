from flask import Flask, jsonify, request, render_template
import pandas as pd
import logging
import os

app = Flask(__name__, template_folder="templates")

# Configuração de log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Variável global para armazenar o DataFrame
df = None

# Função para carregar o arquivo TSV
def load_data(file_path):
    global df
    try:
        logger.info(f"Carregando arquivo: {file_path}")
        df = pd.read_csv(file_path, sep="\t")
        logger.info(f"Arquivo carregado com sucesso! {len(df)} variantes encontradas.")
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo: {e}")

# Determinar o caminho absoluto do arquivo baseado no diretório do script
current_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(current_dir, "../data/annotated_variants.tsv")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/variants", methods=["GET"])
def get_all_variants():
    if df is None:
        return jsonify({"error": "Nenhum dado carregado"}), 500

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=100, type=int)
    start = (page - 1) * limit
    end = start + limit
    paginated_df = df.iloc[start:end]
    logger.info(f"Retornando página {page} com {len(paginated_df)} variantes.")
    return paginated_df.to_json(orient="records")

@app.route("/variants/filter", methods=["GET"])
def filter_variants():
    if df is None:
        return jsonify({"error": "Nenhum dado carregado"}), 500

    try:
        min_frequency = request.args.get("frequency", default=0.0, type=float)
        min_depth = request.args.get("depth", default=0, type=int)
    except ValueError:
        return jsonify({"error": "Parâmetros inválidos para frequência ou profundidade"}), 400

    if min_frequency < 0 or min_depth < 0:
        return jsonify({"error": "Frequência e profundidade devem ser valores positivos"}), 400

    filtered_df = df[(df["FREQUENCY"] >= min_frequency) & (df["DP"] >= min_depth)]
    logger.info(f"Filtro aplicado: frequência >= {min_frequency}, profundidade >= {min_depth}. {len(filtered_df)} variantes encontradas.")
    return filtered_df.to_json(orient="records")

if __name__ == "__main__":
    load_data(data_file_path)
    app.run(debug=True, host="0.0.0.0")
