import subprocess
import sys

def instalar(paquete):
    subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])

paquetes = [
    "requests",
    "beautifulsoup4",
    "tk",
    "pillow",
    "feedparser",
    "csv",
]

for paquete in paquetes:
    try:
        instalar(paquete)
    except Exception as e:
        print(f"Error al instalar {paquete}: {e}")

print("Instalacion de paquetes completa.")