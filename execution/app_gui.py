import customtkinter as ctk
import json
import os
import subprocess
import sys
import pyautogui
import keyboard
import time
import threading
from tkinter import messagebox
from pathlib import Path
import tkinter as tk

# Configuração de caminhos para PyInstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILE = "config.json" # Mantido no root para persistência fora do EXE se necessário
# No entanto, se quisermos usar o do bundle se não existir:
# CONFIG_FILE_PATH = resource_path("config.json")

class PoEBotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PoE2 Bot")
        # Removido self.geometry fixo para permitir auto-ajuste ao conteúdo
        self.resizable(True, True)

        self.bot_thread = None
        self.stop_event = None
        # Tenta carregar config do diretório local primeiro (para persistência)
        # Se não existir, o load_config lidará com isso
        self.config: dict = self.load_config()

        # Configurar fechamento seguro
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Layout: 3 rows (Top bar, Left/Right content, Status)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- BARRA SUPERIOR (Presets) ---
        self.frame_top = ctk.CTkFrame(self)
        self.frame_top.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="ew")
        self.frame_top.grid_columnconfigure(1, weight=1)

        self.label_preset = ctk.CTkLabel(self.frame_top, text="Perfil:", font=ctk.CTkFont(weight="bold"))
        self.label_preset.grid(row=0, column=0, padx=(20, 5), pady=10)

        self.preset_list = list(self.config["presets"].keys())
        self.combo_presets = ctk.CTkComboBox(self.frame_top, values=self.preset_list, command=self.switch_preset, width=150)
        self.combo_presets.set(self.config["active_preset"])
        self.combo_presets.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.btn_add_preset = ctk.CTkButton(self.frame_top, text="+ Novo", width=80, command=self.add_preset, fg_color="forestgreen", hover_color="darkgreen")
        self.btn_add_preset.grid(row=0, column=2, padx=5, pady=10)

        self.btn_rename_preset = ctk.CTkButton(self.frame_top, text="Renomear", width=80, command=self.rename_preset)
        self.btn_rename_preset.grid(row=0, column=3, padx=5, pady=10)

        self.btn_delete_preset = ctk.CTkButton(self.frame_top, text="Excluir", width=80, command=self.delete_preset, fg_color="firebrick", hover_color="darkred")
        self.btn_delete_preset.grid(row=0, column=4, padx=(5, 20), pady=10)

        # --- CONTEUDO PRINCIPAL (Ajustado para Row 1) ---
        # --- COLUNA ESQUERDA (Configurações Gerais) ---
        self.frame_left = ctk.CTkFrame(self)
        self.frame_left.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        self.frame_left.grid_columnconfigure(0, weight=1)

        self.label_title = ctk.CTkLabel(self.frame_left, text="Controles Gerais", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=20)

        # Config de Vida
        self.frame_hp = ctk.CTkFrame(self.frame_left)
        self.frame_hp.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_hp = ctk.CTkLabel(self.frame_hp, text="Tecla Vida:")
        self.label_hp.pack(side="left", padx=10, pady=5)
        self.entry_hp_key = ctk.CTkEntry(self.frame_hp, width=50)
        self.entry_hp_key.pack(side="right", padx=10, pady=5)
        self.entry_hp_key.configure(state="readonly", cursor="hand2")
        self.entry_hp_key.bind("<Button-1>", lambda e: self.start_hotkey_capture(self.entry_hp_key))

        # Config de Mana
        self.frame_mana = ctk.CTkFrame(self.frame_left)
        self.frame_mana.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_mana = ctk.CTkLabel(self.frame_mana, text="Tecla Mana:")
        self.label_mana.pack(side="left", padx=10, pady=5)
        self.entry_mana_key = ctk.CTkEntry(self.frame_mana, width=50)
        self.entry_mana_key.pack(side="right", padx=10, pady=5)
        self.entry_mana_key.configure(state="readonly", cursor="hand2")
        self.entry_mana_key.bind("<Button-1>", lambda e: self.start_hotkey_capture(self.entry_mana_key))

        # Config de Intervalo/Cooldown General
        self.frame_interval = ctk.CTkFrame(self.frame_left)
        self.frame_interval.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.label_interval = ctk.CTkLabel(self.frame_interval, text="Intervalo Global (s):")
        self.label_interval.pack(side="left", padx=10, pady=5)
        self.entry_interval = ctk.CTkEntry(self.frame_interval, width=80)
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

        # Registrar Hotkey Global (Apenas uma vez)
        try:
            keyboard.add_hotkey('end', self.toggle_bot)
        except Exception as e:
            print(f"Erro ao registrar hotkey: {e}")

        # --- COLUNA DIREITA (Magias) ---
        self.frame_right = ctk.CTkFrame(self)
        self.frame_right.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.frame_right.grid_columnconfigure(0, weight=1)

        self.label_skills_title = ctk.CTkLabel(self.frame_right, text="Magias (Skill Timers)", font=ctk.CTkFont(size=18, weight="bold"))
        self.label_skills_title.grid(row=0, column=0, padx=20, pady=20)

        self.frame_skills_list = ctk.CTkFrame(self.frame_right)
        self.frame_skills_list.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.frame_skills_list.grid_columnconfigure(1, weight=1)
        self.frame_skills_list.grid_columnconfigure(2, weight=1)

        self.skill_entries = []
        
        # Registrar cliques fora para desfocar entries
        self.bind_all("<Button-1>", self._on_any_click)

        # O preenchimento das skills agora acontece no refresh_ui() ou init
        self.refresh_ui()

    def _on_any_click(self, event):
        """Desfoca o widget atual se o clique for fora de um campo de entrada."""
        # Se o foco atual for um Entry e o clique não for no próprio Entry, desfoca
        curr_focus = self.focus_get()
        if isinstance(curr_focus, (ctk.CTkEntry, tk.Entry)):
            # Se o clique for em algo que não seja o próprio widget em foco
            if event.widget != curr_focus:
                self.focus_set()

    def get_current_preset_data(self):
        """Retorna os dados do preset ativo."""
        active_name = self.config["active_preset"]
        return self.config["presets"].get(active_name, {})

    def start_hotkey_capture(self, widget):
        """Prepara o widget para capturar uma tecla ou clique do mouse."""
        widget.configure(state="normal", border_color="orange", fg_color="#3E3E3E")
        widget.delete(0, "end")
        widget.insert(0, "...")
        widget.focus_set()
        
        # Bind temporário para capturar qualquer tecla ou botão do mouse
        def on_key(event):
            key = event.keysym
            # Mapeamento amigável para algumas teclas
            mapping = {
                "Return": "enter", "space": "space", "BackSpace": "backspace", "Tab": "tab",
                "Escape": "esc", "Control_L": "ctrl", "Control_R": "ctrl", "Shift_L": "shift",
                "Shift_R": "shift", "Alt_L": "alt", "Alt_R": "alt"
            }
            if key in mapping: key = mapping[key]
            else: key = key.lower()

            finalize_capture(key)
            return "break"

        def on_mouse(event):
            # 1: Left, 2: Middle, 3: Right
            mouse_mapping = {1: "left", 2: "middle", 3: "right"}
            key = mouse_mapping.get(event.num, f"mouse{event.num}")
            finalize_capture(key)
            return "break"

        def finalize_capture(captured_key):
            widget.unbind("<Key>")
            widget.unbind("<Button-1>")
            widget.unbind("<Button-2>")
            widget.unbind("<Button-3>")
            widget.unbind("<FocusOut>")
            
            # Re-bind the trigger for future changes
            widget.bind("<Button-1>", lambda e: self.start_hotkey_capture(widget))
            
            widget.delete(0, "end")
            widget.insert(0, captured_key)
            widget.configure(state="readonly", border_color="#3B8ED0", fg_color=["#F9F9FA", "#343638"]) # Volta cores padrão
            self.status_label.focus_set() # Tira o foco para evitar edições acidentais

        widget.bind("<Key>", on_key)
        widget.bind("<Button-1>", on_mouse) # Sobrescreve o bind inicial temporariamente
        widget.bind("<Button-2>", on_mouse)
        widget.bind("<Button-3>", on_mouse)
        widget.bind("<FocusOut>", lambda e: finalize_capture(widget.get() if widget.get() != "..." else ""))

    def _on_mousewheel_scroll(self, event, widget):
        """Altera o valor do ComboBox com o scroll do mouse."""
        values = widget.cget("values")
        if not values: return
        
        current_val = widget.get()
        try:
            current_idx = values.index(current_val)
        except ValueError:
            current_idx = 0
            
        # event.delta > 0 é scroll para cima
        if event.delta > 0:
            new_idx = min(len(values) - 1, current_idx + 1)
        else:
            new_idx = max(0, current_idx - 1)
            
        widget.set(values[new_idx])

    def load_config(self):
        default_preset_data = {
            "hp": {"coords": [0, 0], "color": [0, 0, 0], "key": "1"},
            "mana": {"coords": [0, 0], "color": [0, 0, 0], "key": "2"},
            "interval": 0.1,
            "cooldown": 1.0,
            "skills": []
        }
        
        config_root = {
            "active_preset": "Default",
            "presets": {
                "Default": default_preset_data
            }
        }

        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    
                    if isinstance(loaded, dict):
                        # Migração do formato antigo (se não houver "presets")
                        if "presets" not in loaded:
                            config_root["presets"]["Default"] = loaded
                            self._fix_skill_fields(config_root["presets"]["Default"])
                        else:
                            # Mesclagem segura: garante que active_preset e presets existam
                            config_root.update(loaded)
                            
                            presets_dict = config_root.get("presets", {})
                            if isinstance(presets_dict, dict):
                                for p_name in presets_dict:
                                    if isinstance(presets_dict[p_name], dict):
                                        self._fix_skill_fields(presets_dict[p_name])
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
        
        # Garantia final de estrutura
        if "active_preset" not in config_root: config_root["active_preset"] = "Default"
        if "presets" not in config_root: config_root["presets"] = {"Default": default_preset_data}
        if config_root["active_preset"] not in config_root["presets"]:
            config_root["active_preset"] = list(config_root["presets"].keys())[0]

        return config_root

    def _fix_skill_fields(self, data):
        """Garante que todos os campos necessários existem no dicionário de um preset."""
        if "skills" not in data or not isinstance(data["skills"], list):
            data["skills"] = []
        
        skills = data["skills"]
        while len(skills) < 6:
            skills.append({"key": "", "timer": 1, "enabled": False, "use_pixel": False, "pixel_coords": [0,0], "pixel_color": [0,0,0]})
        
        for s in skills:
            if "enabled" not in s: s["enabled"] = False
            if "use_pixel" not in s: s["use_pixel"] = False
            if "pixel_coords" not in s: s["pixel_coords"] = [0,0]
            if "pixel_color" not in s: s["pixel_color"] = [0,0,0]
            if "timer" not in s: s["timer"] = 1

    def save_config(self, notify=True):
        try:
            # Pegar dados da UI e salvar no preset ativo
            active_name = self.config["active_preset"]
            data = self.config["presets"][active_name]
            
            data["hp"]["key"] = self.entry_hp_key.get()
            data["mana"]["key"] = self.entry_mana_key.get()
            
            interval_val = self.entry_interval.get().replace(",", ".")
            try:
                data["cooldown"] = float(interval_val)
            except ValueError:
                data["cooldown"] = 1.0
            
            new_skills = []
            for i, entries in enumerate(self.skill_entries):
                key_val = entries["entry_key"].get()
                timer_val = entries["entry_timer"].get().replace(",", ".")
                
                try:
                    timer_float = float(timer_val)
                except ValueError:
                    timer_float = 1.0
                
                new_skills.append({
                    "key": key_val,
                    "timer": timer_float,
                    "enabled": entries["switch_var"].get() == "on",
                    "use_pixel": entries["pixel_var"].get(),
                    "pixel_coords": entries["pixel_coords"],
                    "pixel_color": entries["pixel_color"]
                })
            data["skills"] = new_skills

            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            if notify:
                self.status_label.configure(text=f"Status: Config ({active_name}) salva!", text_color="green")
            return True
        except Exception as e:
            self.status_label.configure(text=f"Status: Erro ao salvar ({e})", text_color="red")
            return False

    def refresh_ui(self):
        """Atualiza todos os widgets da UI com os dados do preset ativo."""
        data = self.get_current_preset_data()
        
        # HP/Mana Keys
        self.entry_hp_key.configure(state="normal")
        self.entry_hp_key.delete(0, "end")
        self.entry_hp_key.insert(0, data.get("hp", {}).get("key", "1"))
        self.entry_hp_key.configure(state="readonly")
        
        self.entry_mana_key.configure(state="normal")
        self.entry_mana_key.delete(0, "end")
        self.entry_mana_key.insert(0, data.get("mana", {}).get("key", "2"))
        self.entry_mana_key.configure(state="readonly")
        
        # Interval
        self.entry_interval.delete(0, "end")
        self.entry_interval.insert(0, str(data.get("cooldown", 1.0)))
        
        # Skills
        # Limpar frames antigos se existirem
        for child in self.frame_skills_list.winfo_children():
            child.destroy()
            
        self.skill_entries = []
        skills_data = data.get("skills", [])
        if not isinstance(skills_data, list):
            skills_data = []
            
        # Garantir que temos 6 skills para a UI
        while len(skills_data) < 6:
            skills_data.append({"key": "", "timer": 1, "enabled": False, "use_pixel": False, "pixel_coords": [0,0], "pixel_color": [0,0,0]})
        
        for i in range(6):
            skill = skills_data[i]
            row_frame = ctk.CTkFrame(self.frame_skills_list)
            row_frame.grid(row=i, column=0, columnspan=4, padx=5, pady=2, sticky="ew")
            
            lbl = ctk.CTkLabel(row_frame, text=f"S{i+1}:", width=30)
            lbl.pack(side="left", padx=2)
            
            switch_var = ctk.StringVar(value="on" if skill.get("enabled", False) else "off")
            switch = ctk.CTkSwitch(row_frame, text="", variable=switch_var, onvalue="on", offvalue="off", progress_color="green", button_color="red", button_hover_color="darkred")
            if skill.get("enabled", False): switch.select()
            switch.pack(side="left", padx=2)
            
            entry_key = ctk.CTkEntry(row_frame, width=40, placeholder_text="Key")
            entry_key.insert(0, skill.get("key", ""))
            entry_key.pack(side="left", padx=2)
            entry_key.configure(state="readonly", cursor="hand2")
            entry_key.bind("<Button-1>", lambda e, w=entry_key: self.start_hotkey_capture(w))
            
            entry_timer = ctk.CTkEntry(row_frame, width=80)
            entry_timer.insert(0, str(skill.get("timer", 1.0)))
            entry_timer.pack(side="left", padx=2)

            pixel_var = ctk.BooleanVar(value=skill.get("use_pixel", False))
            pixel_switch = ctk.CTkCheckBox(row_frame, text="Pixel", variable=pixel_var, width=20)
            pixel_switch.pack(side="left", padx=5)

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

    def switch_preset(self, new_name):
        """Troca o preset ativo e recarrega a UI."""
        # Salva o atual antes de trocar
        self.save_config(notify=False)
        self.config["active_preset"] = new_name
        self.refresh_ui()
        self.status_label.configure(text=f"Status: Perfil '{new_name}' carregado.", text_color="royalblue")

    def add_preset(self):
        """Cria um novo preset."""
        dialog = ctk.CTkInputDialog(text="Nome do novo perfil:", title="Novo Perfil")
        name = dialog.get_input()
        if name:
            if name in self.config["presets"]:
                messagebox.showerror("Erro", "Já existe um perfil com esse nome.")
                return
            
            # Copia o atual para o novo
            current_data = self.get_current_preset_data()
            import copy
            self.config["presets"][name] = copy.deepcopy(current_data)
            self.config["active_preset"] = name
            
            # Atualiza ComboBox
            self.preset_list = list(self.config["presets"].keys())
            self.combo_presets.configure(values=self.preset_list)
            self.combo_presets.set(name)
            
            self.refresh_ui()
            self.save_config()

    def rename_preset(self):
        """Renomeia o preset ativo."""
        old_name = self.config["active_preset"]
        dialog = ctk.CTkInputDialog(text=f"Novo nome para '{old_name}':", title="Renomear Perfil")
        new_name = dialog.get_input()
        
        if new_name and new_name != old_name:
            if new_name in self.config["presets"]:
                messagebox.showerror("Erro", "Já existe um perfil com esse nome.")
                return
            
            self.config["presets"][new_name] = self.config["presets"].pop(old_name)
            self.config["active_preset"] = new_name
            
            # Atualiza ComboBox
            self.preset_list = list(self.config["presets"].keys())
            self.combo_presets.configure(values=self.preset_list)
            self.combo_presets.set(new_name)
            
            self.save_config()

    def delete_preset(self):
        """Exclui o preset ativo."""
        name = self.config["active_preset"]
        if len(self.config["presets"]) <= 1:
            messagebox.showwarning("Aviso", "Você deve ter pelo menos um perfil.")
            return
            
        if messagebox.askyesno("Confirmar", f"Deseja excluir o perfil '{name}'?"):
            self.config["presets"].pop(name)
            # Switch para o primeiro disponível
            self.config["active_preset"] = list(self.config["presets"].keys())[0]
            
            # Atualiza ComboBox
            self.preset_list = list(self.config["presets"].keys())
            self.combo_presets.configure(values=self.preset_list)
            self.combo_presets.set(self.config["active_preset"])
            
            self.refresh_ui()
            self.save_config()

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
                    entries = self.skill_entries[idx]
                    entries["pixel_coords"] = [x, y]
                    entries["pixel_color"] = list(color)
                    self.after(0, lambda: self._on_capture_done(f"Skill {idx+1}", x, y, color))
                else:
                    data = self.get_current_preset_data()
                    data[target]["coords"] = [x, y]
                    data[target]["color"] = list(color)
                    self.after(0, lambda: self._on_capture_done(target, x, y, color))
                break
            time.sleep(0.01)

    def _on_capture_done(self, target, x, y, color):
        self.save_config()
        self.status_label.configure(text=f"Status: {target.upper()} capturado!", text_color="green")

    def toggle_bot(self):
        if self.bot_thread is None or not self.bot_thread.is_alive():
            if self.save_config():
                self.status_label.configure(text="Status: Bot Rodando...", text_color="red")
                self.btn_start.configure(text="PARAR BOT", fg_color="gray")
                
                # Import dinâmico para evitar problemas de recursão se houver
                from monitor_stats import run_bot
                
                self.stop_event = threading.Event()
                self.bot_thread = threading.Thread(target=run_bot, args=(self.stop_event,), daemon=True)
                self.bot_thread.start()
        else:
            self._stop_bot()

    def _stop_bot(self):
        if self.stop_event:
            self.stop_event.set()
        self.bot_thread = None
        self._on_bot_stop()

    def _on_bot_stop(self):
        self.status_label.configure(text="Status: Bot Parado", text_color="gray")
        self.btn_start.configure(text="INICIAR BOT", fg_color="firebrick")

    def on_closing(self):
        self._stop_bot()
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = PoEBotGUI()
    app.mainloop()
