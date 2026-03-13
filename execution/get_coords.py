import pyautogui
import keyboard
import time
import sys
import json
import os

CONFIG_FILE = "config.json"

def save_to_config(key_type, coords, color):
    if not os.path.exists(CONFIG_FILE):
        config = {
            "hp": {"coords": [0, 0], "color": [0, 0, 0], "key": "1"},
            "mana": {"coords": [0, 0], "color": [0, 0, 0], "key": "5"},
            "interval": 0.1,
            "cooldown": 1.0
        }
    else:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    
    config[key_type]["coords"] = coords
    config[key_type]["color"] = color
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuração de {key_type.upper()} salva com sucesso!")

def get_mouse_info():
    print("--- Captura de Coordenadas ---")
    print("Mova o mouse para o ponto desejado:")
    print("Pressione 'H' para capturar VIDA (HP)")
    print("Pressione 'M' para capturar MANA")
    print("Pressione 'ESC' para sair.")
    
    while True:
        if keyboard.is_pressed('h'):
            x, y = pyautogui.position()
            color = pyautogui.pixel(x, y)
            print(f"VIDA detectada: ({x}, {y}) | Cor: {color}")
            save_to_config("hp", [x, y], list(color))
            time.sleep(0.5)
        
        if keyboard.is_pressed('m'):
            x, y = pyautogui.position()
            color = pyautogui.pixel(x, y)
            print(f"MANA detectada: ({x}, {y}) | Cor: {color}")
            save_to_config("mana", [x, y], list(color))
            time.sleep(0.5)
        
        if keyboard.is_pressed('esc'):
            print("Saindo...")
            break
        
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        get_mouse_info()
    except Exception as e:
        print(f"Erro: {e}")
        sys.exit(1)
