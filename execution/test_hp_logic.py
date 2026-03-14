
import sys
import os

# Adiciona o diretório atual ao path para importar os módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from screen_capture import is_green, is_color_in_range

def test_logic():
    # Cores de teste
    RED = (200, 20, 20)      # Vida cheia (Vermelho)
    GREEN = (50, 210, 50)    # Vida com veneno (Verde)
    BLACK = (10, 10, 10)     # Fundo da barra (Vida baixa)
    GRAY = (128, 128, 128)   # Outra cor qualquer
    
    target_hp = (180, 0, 0) # Cor alvo configurada
    
    print("--- Testando Lógica de HP ---")
    
    for name, color in [("RED", RED), ("GREEN", GREEN), ("BLACK", BLACK), ("GRAY", GRAY)]:
        is_healthy = is_color_in_range(color, target_hp, tolerance=50)
        poisoned = is_green(color)
        
        should_use_potion = not is_healthy and not poisoned
        
        print(f"Cor: {name} {color}")
        print(f"  Similar ao Alvo: {is_healthy}")
        print(f"  Detectado como Veneno: {poisoned}")
        print(f"  Usaria Poção? {'SIM' if should_use_potion else 'NÃO'}")
        print("-" * 30)

if __name__ == "__main__":
    test_logic()
