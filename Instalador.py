import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

packages = [
    "requests",
    "beautifulsoup4",
    "tk",
    "pillow",
    "feedparser",
    "csv",
]

for package in packages:
    try:
        install(package)
    except Exception as e:
        print(f"Error al instalar {package}: {e}")

print("Instalacion de paquetes completa.")