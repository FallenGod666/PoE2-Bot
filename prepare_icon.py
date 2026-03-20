import requests
from PIL import Image
import os

def download_and_convert_icon():
    url = "https://cdn-icons-png.flaticon.com/512/14698/14698337.png"
    png_path = "icon.png"
    ico_path = "icon.ico"
    
    print(f"Baixando ícone de {url}...")
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(png_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
            print("Download concluído.")
            
            print(f"Convertendo {png_path} para {ico_path}...")
            img = Image.open(png_path)
            # Redimensionar e salvar como .ico
            img.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
            print("Conversão concluída.")
            
            # Limpar PNG temporário
            os.remove(png_path)
            return True
        else:
            print(f"Erro ao baixar: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro durante o processo: {e}")
        return False

if __name__ == "__main__":
    download_and_convert_icon()
