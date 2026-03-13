import keyboard
import time

def use_potion(key):
    """
    Simula o pressionamento de uma tecla para usar uma poção.
    """
    try:
        keyboard.press_and_release(key)
        print(f"Poção usada: Tecla {key}")
    except Exception as e:
        print(f"Erro ao usar poção: {e}")

if __name__ == "__main__":
    # Teste rápido: usar poção na tecla 1
    print("Testando uso de poção em 2 segundos...")
    time.sleep(2)
    use_potion('1')
