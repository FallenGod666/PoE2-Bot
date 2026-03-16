import time
import os
import json
try:
    from screen_capture import check_threshold, is_green
    from potion_controls import use_potion
except ImportError:
    # Fallback para desenvolvimento local se os arquivos não estiverem no mesmo dir
    check_threshold = None
    is_green = None
    use_potion = print

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def run_bot(stop_event=None):
    config = load_config()
    if not config:
        print("Erro ao carregar config.json")
        return

    # Extraindo configs do preset ativo
    active_name = config.get("active_preset", "Default")
    presets = config.get("presets", {})
    
    if active_name not in presets:
        if presets:
            active_name = list(presets.keys())[0]
        else:
            print("Erro: Nenhum perfil configurado.")
            return

    data = presets[active_name]
    
    # Extração segura de campos
    try:
        hp_coords = data["hp"]["coords"]
        hp_color = data["hp"]["color"]
        hp_key = data["hp"]["key"]
        
        mana_coords = data["mana"]["coords"]
        mana_color = data["mana"]["color"]
        mana_key = data["mana"]["key"]
        
        check_interval = data.get("interval", 0.1)
        cooldown = data.get("cooldown", 1.0)
        skills = data.get("skills", [])
    except KeyError as e:
        print(f"Erro na estrutura do perfil '{active_name}': campo faltando {e}")
        return

    last_hp_use = 0.0
    last_mana_use = 0.0
    
    # Inicializa timers para skills
    skill_timers = []
    for skill in skills:
        skill_timers.append({
            "key": skill.get("key", ""),
            "interval": float(skill.get("timer", 0)),
            "last_use": 0.0,
            "enabled": skill.get("enabled", False),
            "use_pixel": skill.get("use_pixel", False),
            "pixel_coords": skill.get("pixel_coords", [0, 0]),
            "pixel_color": skill.get("pixel_color", [0, 0, 0])
        })
    
    print(f"=== Bot iniciado no perfil: {active_name} ===")
    
    try:
        while stop_event is None or not stop_event.is_set():
            now = time.time()
            
            # Checar Saúde
            if now - last_hp_use > cooldown:
                is_healthy, current_color = check_threshold(hp_coords[0], hp_coords[1], hp_color)
                if not is_healthy:
                    if not is_green(current_color):
                        print(f"HP baixo! Usando {hp_key}")
                        use_potion(hp_key)
                        last_hp_use = now
                    else:
                        print("HP Verde detectado (Veneno) - ignorando.")
            
            # Checar Mana
            if now - last_mana_use > cooldown:
                is_mana_full, _ = check_threshold(mana_coords[0], mana_coords[1], mana_color)
                if not is_mana_full:
                    print(f"Mana baixa! Usando {mana_key}")
                    use_potion(mana_key)
                    last_mana_use = now

            # Checar Skills
            for s in skill_timers:
                if not s["enabled"]: continue

                should_cast = False
                if s["use_pixel"]:
                    is_active, _ = check_threshold(s["pixel_coords"][0], s["pixel_coords"][1], s["pixel_color"])
                    if is_active and (now - s["last_use"] > 0.5):
                        should_cast = True
                elif s["interval"] >= 1.0 and (now - s["last_use"] > s["interval"]):
                    should_cast = True

                if should_cast:
                    print(f"Skill: {s['key']}")
                    use_potion(s["key"])
                    s["last_use"] = now
            
            time.sleep(check_interval)
            
    except Exception as e:
        print(f"Erro no loop do bot: {e}")

if __name__ == "__main__":
    run_bot()
