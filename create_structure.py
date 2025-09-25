import os

# Estrutura de diretórios e arquivos
structure = {
    "data": ["__init__.py", "collectors.py", "storage.py"],
    "features": ["__init__.py", "engineering.py"],
    "labels": ["__init__.py", "triple_barrier.py"],
    "model": ["__init__.py", "train.py", "inference.py"],
    "exec": ["__init__.py", "policy.py", "broker.py"],
    "utils": ["__init__.py", "config.py", "logger.py"],
    "configs": ["config.yaml", "patterns.yaml"],
}

base_dir = "."

for folder, files in structure.items():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)
    for file in files:
        file_path = os.path.join(folder_path, file)
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                if file.endswith(".py"):
                    f.write(f"# {folder}/{file}\n# TODO: implementar funções\n")
                elif file.endswith(".yaml"):
                    f.write(f"# {folder}/{file}\n# parâmetros de configuração\n")

# Criar arquivos raiz
root_files = {
    "requirements.txt": "# dependências do projeto\nccxt\npandas\nnumpy\nxgboost\nscikit-learn\npython-dotenv\nloguru\n",
    ".env.example": "BINANCE_API_KEY=\nBINANCE_API_SECRET=\nDRY_RUN=true\nDATA_DIR=./data_parquet\nLOG_DIR=./logs\n",
    "README.md": "# IA_bot\n\nBot de trading com IA usando Binance.\n",
    ".gitignore": ".venv/\n.env\n__pycache__/\n*.log\nlogs/\ndata_parquet/\n",
}

for file, content in root_files.items():
    path = os.path.join(base_dir, file)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("Estrutura criada com sucesso ✅")
