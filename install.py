import subprocess

# Lista de pacotes a serem instalados
packages = ["aiohttp", "requests", "beautifulsoup4", "openpyxl", "tqdm"]

# Função para executar o comando de instalação
def install_package(package):
    subprocess.check_call(["pip", "install", package])

# Instalação das dependências
for package in packages:
    print(f"Instalando {package}...")
    install_package(package)

print("Instalação concluída.")
