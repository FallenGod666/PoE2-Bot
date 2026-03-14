import customtkinter as ctk
import json
import os
import subprocess
import threading
import sys
import pyautogui
import keyboard
import time
from pathlib import Path

# Configuração de aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_FILE = "config.json"

class PoEBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PoE2 Bot")
        # Removido self.geometry fixo para permitir auto-ajuste ao conteúdo
        self.resizable(True, True)

        self.bot_process = None
        self.config = self.load_config()

        # Configurar fechamento seguro
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Layout: 2 colunas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- COLUNA ESQUERDA (Configurações Gerais) ---
        self.frame_left = ctk.CTkFrame(self)
        self.frame_left.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self.frame_left, text="Controles Gerais", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # Config de Vida
        self.frame_hp = ctk.CTkFrame(self.frame_left)
        self.frame_hp.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_hp = ctk.CTkLabel(self.frame_hp, text="Tecla Vida:")
        self.label_hp.pack(side="left", padx=10, pady=5)
        self.entry_hp_key = ctk.CTkEntry(self.frame_hp, width=50)
        self.entry_hp_key.insert(0, self.config.get("hp", {}).get("key", "1"))
        self.entry_hp_key.pack(side="right", padx=10, pady=5)

        # Config de Mana
        self.frame_mana = ctk.CTkFrame(self.frame_left)
        self.frame_mana.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_mana = ctk.CTkLabel(self.frame_mana, text="Tecla Mana:")
        self.label_mana.pack(side="left", padx=10, pady=5)
        self.entry_mana_key = ctk.CTkEntry(self.frame_mana, width=50)
        self.entry_mana_key.insert(0, self.config.get("mana", {}).get("key", "2"))
        self.entry_mana_key.pack(side="right", padx=10, pady=5)

        # Config de Intervalo/Cooldown General
        self.frame_interval = ctk.CTkFrame(self.frame_left)
        self.frame_interval.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_interval = ctk.CTkLabel(self.frame_interval, text="Intervalo Global (s):")
        self.label_interval.pack(side="left", padx=10, pady=5)
        self.entry_interval = ctk.CTkEntry(self.frame_interval, width=50)
        self.entry_interval.insert(0, str(self.config.get("cooldown", 1.0)))
        self.entry_interval.pack(side="right", padx=10, pady=5)

        # Botões de Captura
        self.frame_capture = ctk.CTkFrame(self.frame_left)
        self.frame_capture.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        
        self.btn_capture_hp = ctk.CTkButton(self.frame_capture, text="Cap. VIDA (H)", command=lambda: self.start_capture("hp"), fg_color="forestgreen", hover_color="darkgreen")
        self.btn_capture_hp.pack(side="left", padx=5, pady=10, expand=True)

        self.btn_capture_mana = ctk.CTkButton(self.frame_capture, text="Cap. MANA (M)", command=lambda: self.start_capture("mana"), fg_color="royalblue", hover_color="darkblue")
        self.btn_capture_mana.pack(side="right", padx=5, pady=10, expand=True)

        # Botão Salvar
        self.btn_save = ctk.CTkButton(self.frame_left, text="Salvar Todas Configs", command=self.save_config)
        self.btn_save.grid(row=5, column=0, padx=20, pady=10, sticky="ew")

        # Botão Start/Stop
        self.btn_start = ctk.CTkButton(self.frame_left, text="INICIAR BOT", command=self.toggle_bot, font=ctk.CTkFont(weight="bold"), fg_color="firebrick", hover_color="darkred")
        self.btn_start.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self.frame_left, text="Status: Pronto", text_color="gray")
        self.status_label.grid(row=7, column=0, padx=20, pady=5)

        # Painel Informativo de Teclas
        self.frame_info = ctk.CTkFrame(self.frame_left, fg_color="transparent")
        self.frame_info.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        
        info_text = (
            "Atalhos de Captura:\n"
            "• Tecla [H]: Captura VIDA\n"
            "• Tecla [M]: Captura MANA\n"
            "• Tecla [P]: Captura PIXEL Skill\n\n"
            "Atalho Global:\n"
            "• Tecla [END]: Ligar/Desligar Bot"
        )
        self.label_info = ctk.CTkLabel(self.frame_info, text=info_text, justify="left", font=ctk.CTkFont(size=12))
        self.label_info.pack(padx=10, pady=10)

        # Registrar Hotkey Global
        try:
            keyboard.add_hotkey('end', self.toggle_bot)
        except Exception as e:
            print(f"Erro ao registrar hotkey: {e}")

        # --- COLUNA DIREITA (Magias) ---
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_right.grid_columnconfigure(0, weight=1)

        self.label_skills_title = ctk.CTkLabel(self.frame_right, text="Magias (Skill Timers)", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_skills_title.grid(row=0, column=0, padx=20, pady=20)

        self.frame_skills_list = ctk.CTkFrame(self.frame_right)
        self.frame_skills_list.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_skills_list.grid_columnconfigure(1, weight=1)
        self.frame_skills_list.grid_columnconfigure(2, weight=1)

        self.skill_entries = []
        skills_data = self.config.get("skills", [])
        while len(skills_data) < 6:
            skills_data.append({"key": "", "timer": 0, "enabled": False, "use_pixel": False, "pixel_coords": [0,0], "pixel_color": [0,0,0]})

        for i in range(6):
            skill = skills_data[i]
            
            # Row Frame
            row_frame = ctk.CTkFrame(self.frame_skills_list)
            row_frame.grid(row=i, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
            
            # Slot Label
            lbl = ctk.CTkLabel(row_frame, text=f"S{i+1}:", width=30)
            lbl.pack(side="left", padx=2)
            
            # Switch ON/OFF
            switch_var = ctk.StringVar(value="on" if skill.get("enabled", False) else "off")
            switch = ctk.CTkSwitch(row_frame, text="", command=None, variable=switch_var, onvalue="on", offvalue="off", progress_color="green", button_color="red", button_hover_color="darkred")
            if skill.get("enabled", False): switch.select()
            switch.pack(side="left", padx=2)
            
            # Key Entry
            entry_key = ctk.CTkEntry(row_frame, width=40, placeholder_text="Key")
            entry_key.insert(0, skill.get("key", ""))
            entry_key.pack(side="left", padx=2)
            
            # Timer Entry
            entry_timer = ctk.CTkEntry(row_frame, width=50, placeholder_text="Segs")
            entry_timer.insert(0, str(skill.get("timer", 0)))
            entry_timer.pack(side="left", padx=2)

            # Use Pixel Switch
            pixel_var = ctk.BooleanVar(value=skill.get("use_pixel", False))
            pixel_switch = ctk.CTkCheckBox(row_frame, text="Pixel", variable=pixel_var, width=20)
            pixel_switch.pack(side="left", padx=5)

            # Capture Pixel Button
            btn_pixel = ctk.CTkButton(row_frame, text="Cap", width=40, command=lambda idx=i: self.start_skill_pixel_capture(idx), fg_color="purple", hover_color="indigo")
            btn_pixel.pack(side="left", padx=2)
            
            self.skill_entries.append({
                "switch_var": switch_var,
                "entry_key": entry_key,
                "entry_timer": entry_timer,
                "pixel_var": pixel_var,
                "pixel_coords": skill.get("pixel_coords", [0, 0]),
                "pixel_color": skill.get("pixel_color", [0, 0, 0])
            })

    def load_config(self):
        default_config = {
            "hp": {"coords": [0, 0], "color": [0, 0, 0], "key": "1"},
            "mana": {"coords": [0, 0], "color": [0, 0, 0], "key": "2"},
            "interval": 0.1,
            "cooldown": 1.0,
            "skills": []
        }
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        if isinstance(v, dict) and k in default_config and isinstance(default_config[k], dict):
                            default_config[k].update(v)
                        else:
                            default_config[k] = v
                    
                    # Garantir campos novos nas skills carregadas
                    if "skills" in default_config:
                        for s in default_config["skills"]:
                            if "enabled" not in s: s["enabled"] = False
                            if "use_pixel" not in s: s["use_pixel"] = False
                            if "pixel_coords" not in s: s["pixel_coords"] = [0,0]
                            if "pixel_color" not in s: s["pixel_color"] = [0,0,0]
            except:
                pass
        return default_config

    def save_config(self):
        try:
            self.config["hp"]["key"] = self.entry_hp_key.get()
            self.config["mana"]["key"] = self.entry_mana_key.get()
            self.config["cooldown"] = float(self.entry_interval.get())
            
            new_skills = []
            for i, entries in enumerate(self.skill_entries):
                key_val = entries["entry_key"].get()
                timer_val = entries["entry_timer"].get()
                
                new_skills.append({
                    "key": key_val,
                    "timer": float(timer_val) if timer_val else 0.0,
                    "enabled": entries["switch_var"].get() == "on",
                    "use_pixel": entries["pixel_var"].get(),
                    "pixel_coords": entries["pixel_coords"],
                    "pixel_color": entries["pixel_color"]
                })
            self.config["skills"] = new_skills

            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.status_label.configure(text="Status: Configurações salvas!", text_color="green")
            return True
        except Exception as e:
            self.status_label.configure(text=f"Status: Erro ao salvar ({e})", text_color="red")
            return False

    def start_capture(self, target):
        key = 'h' if target == 'hp' else 'm'
        self.status_label.configure(text=f"Status: Mova mouse e aperte '{key.upper()}'", text_color="orange")
        threading.Thread(target=self._capture_task, args=(target, key), daemon=True).start()

    def start_skill_pixel_capture(self, idx):
        self.status_label.configure(text=f"Status: Mova mouse no SLOT {idx+1} e aperte 'P'", text_color="orange")
        threading.Thread(target=self._capture_task, args=("skill", "p", idx), daemon=True).start()

    def _capture_task(self, target, key, idx=None):
        while True:
            if keyboard.is_pressed(key):
                x, y = pyautogui.position()
                time.sleep(0.1)
                
                # Prevenção de OSError: verificar se está dentro da tela
                screen_w, screen_h = pyautogui.size()
                if 0 <= x < screen_w and 0 <= y < screen_h:
                    try:
                        color = pyautogui.pixel(x, y)
                    except:
                        color = (0, 0, 0)
                else:
                    color = (0, 0, 0)
                
                if target == "skill" and idx is not None:
                    self.skill_entries[idx]["pixel_coords"] = [x, y]
                    self.skill_entries[idx]["pixel_color"] = list(color)
                    self.after(0, lambda: self._on_capture_done(f"Skill {idx+1}", x, y, color))
                else:
                    self.config[target]["coords"] = [x, y]
                    self.config[target]["color"] = list(color)
                    self.after(0, lambda: self._on_capture_done(target, x, y, color))
                break
            time.sleep(0.01)

    def _on_capture_done(self, target, x, y, color):
        self.save_config()
        self.status_label.configure(text=f"Status: {target.upper()} capturado!", text_color="green")

    def toggle_bot(self):
        if self.bot_process is None:
            if self.save_config():
                self.status_label.configure(text="Status: Bot Rodando...", text_color="red")
                self.btn_start.configure(text="PARAR BOT", fg_color="gray")
                threading.Thread(target=self._run_bot_thread, daemon=True).start()
        else:
            self._stop_bot()

    def _run_bot_thread(self):
        python_exe = sys.executable
        venv_python = Path(".venv/Scripts/python.exe")
        if venv_python.exists():
            python_exe = str(venv_python)
            
        try:
            # shell=False e creationflags para evitar janelas extras no Windows
            self.bot_process = subprocess.Popen([python_exe, "execution/monitor_stats.py"], 
                                               stdout=subprocess.PIPE, 
                                               stderr=subprocess.PIPE,
                                               text=True)
            self.bot_process.wait()
        except Exception as e:
            print(f"Erro ao iniciar processo do bot: {e}")
        finally:
            self.bot_process = None
            self.after(0, self._on_bot_stop)

    def _on_bot_stop(self):
        self.status_label.configure(text="Status: Bot Parado", text_color="gray")
        self.btn_start.configure(text="INICIAR BOT", fg_color="firebrick")

    def _stop_bot(self):
        if self.bot_process:
            try:
                # kill() é mais agressivo no Windows
                self.bot_process.kill()
                self.bot_process.terminate()
            except:
                pass
            self.bot_process = None

    def on_closing(self):
        self._stop_bot()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = PoEBotGUI()
    app.mainloop()
