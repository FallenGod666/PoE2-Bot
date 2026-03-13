import time
import os
import json
from screen_capture import check_threshold
from potion_controls import use_potion

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Erro: {CONFIG_FILE} não encontrado. Execute get_coords.py primeiro.")
        return None
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def run_bot():
    config = load_config()
    if not config:
        return

    # Extraindo configs
    hp_coords = config["hp"]["coords"]
    hp_color = tuple(config["hp"]["color"])
    hp_key = config["hp"]["key"]
    
    mana_coords = config["mana"]["coords"]
    mana_color = tuple(config["mana"]["color"])
    mana_key = config["mana"]["key"]
    
    check_interval = config.get("interval", 0.1)
    cooldown = config.get("cooldown", 1.0)

    last_hp_use = 0
    last_mana_use = 0
    
    print("=== Bot de Poções Poe Bot ===")
    print(f"Monitorando HP em {hp_coords} (Tecla: {hp_key})")
    print(f"Monitorando Mana em {mana_coords} (Tecla: {mana_key})")
    print("Pressione CTRL+C para parar.")

    try:
        while True:
            now = time.time()
            
            # Checar Saúde
            if now - last_hp_use > cooldown:
                # check_threshold retorna True se a cor capturada for similar à alvo
                # Se for similar, o globo está "cheio" naquele ponto.
                # Se NÃO for similar, o globo baixou daquele ponto -> usar poção.
                is_healthy = check_threshold(hp_coords[0], hp_coords[1], hp_color)
                if not is_healthy:
                    print("HP baixo detectado!")
                    use_potion(hp_key)
                    last_hp_use = now
            
            # Checar Mana
            if now - last_mana_use > cooldown:
                is_mana_full = check_threshold(mana_coords[0], mana_coords[1], mana_color)
                if not is_mana_full:
                    print("Mana baixa detectada!")
                    use_potion(mana_key)
                    last_mana_use = now
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\nBot parado pelo usuário.")

if __name__ == "__main__":
    run_bot()
