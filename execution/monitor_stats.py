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
    skills = config.get("skills", [])

    last_hp_use = 0.0
    last_mana_use = 0.0
    
    # Inicializa timers para skills
    skill_timers = []
    for skill in skills:
        skill_timers.append({
            "key": skill["key"],
            "interval": float(skill["timer"]),
            "last_use": 0.0,
            "enabled": skill.get("enabled", False),
            "use_pixel": skill.get("use_pixel", False),
            "pixel_coords": skill.get("pixel_coords", [0, 0]),
            "pixel_color": tuple(skill.get("pixel_color", [0, 0, 0]))
        })
    
    print("=== Bot de Poções e Magias Poe Bot ===")
    print(f"Monitorando HP em {hp_coords} (Tecla: {hp_key})")
    print(f"Monitorando Mana em {mana_coords} (Tecla: {mana_key})")
    for i, s in enumerate(skill_timers):
        status = "ON" if s["enabled"] else "OFF"
        mode = "Pixel" if s["use_pixel"] else f"Timer ({s['interval']}s)"
        print(f"Skill {i+1} [{status}]: Tecla {s['key']} ({mode})")
    print("Pressione CTRL+C para parar.")

    try:
        while True:
            now = time.time()
            
            # Checar Saúde
            if now - last_hp_use > cooldown:
                # check_threshold agora retorna (is_healthy, current_color)
                from screen_capture import is_green
                is_healthy, current_color = check_threshold(hp_coords[0], hp_coords[1], hp_color)
                
                # Se não for saudável e não for verde (veneno), então usa poção
                if not is_healthy:
                    is_poisoned = is_green(current_color)
                    if not is_poisoned:
                        print(f"HP baixo detectado! Cor: {current_color} | Alvo: {hp_color}")
                        use_potion(hp_key)
                        last_hp_use = now
                    else:
                        print(f"HP Verde (veneno) detectado, ignorando poção. Cor: {current_color}")
            
            # Checar Mana
            if now - last_mana_use > cooldown:
                is_mana_full, _ = check_threshold(mana_coords[0], mana_coords[1], mana_color)
                if not is_mana_full:
                    print("Mana baixa detectada!")
                    use_potion(mana_key)
                    last_mana_use = now

            # Checar Skills (Magias)
            for s in skill_timers:
                if not s["enabled"]:
                    continue

                should_cast = False
                
                # Prioridade 1: Pixel (Se habilitado, casta se o pixel estiver ativo)
                if s["use_pixel"]:
                    # check_threshold agora retorna (is_active, current_color)
                    is_active, _ = check_threshold(s["pixel_coords"][0], s["pixel_coords"][1], s["pixel_color"])
                    # Cooldown interno de 0.5s para não spammar enquanto o pixel brilha
                    if is_active and (now - s["last_use"] > 0.5):
                        should_cast = True
                
                # Prioridade 2: Timer (Se timer >= 1s e não estiver usando pixel ou se ambos)
                elif s["interval"] >= 1.0 and (now - s["last_use"] > s["interval"]):
                    should_cast = True

                if should_cast:
                    print(f"Usando skill: {s['key']}")
                    use_potion(s["key"])
                    s["last_use"] = now
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\nBot parado pelo usuário.")

if __name__ == "__main__":
    run_bot()
