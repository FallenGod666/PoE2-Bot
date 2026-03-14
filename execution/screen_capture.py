import pyautogui
import PIL.ImageGrab as ImageGrab
import numpy as np

def get_pixel_color(x, y):
    """Retorna a cor RGB de um pixel específico, com verificação de limites."""
    width, height = pyautogui.size()
    if 0 <= x < width and 0 <= y < height:
        return pyautogui.pixel(x, y)
    else:
        print(f"Aviso: Coordenadas ({x}, {y}) fora dos limites da tela ({width}x{height}).")
        return (0, 0, 0)

def is_color_in_range(color, target_rgb, tolerance=30):
    """Verifica se a cor está dentro de uma tolerância do alvo."""
    return all(abs(c - t) <= tolerance for c, t in zip(color, target_rgb))

def is_green(color):
    """
    Heurística para detectar o verde do veneno no PoE2.
    O veneno no PoE2 transforma a barra de vida em um tom de verde ou verde-azulado.
    """
    r, g, b = color
    # Heurística mais robusta: O canal Verde (G) deve ser o maior de todos
    # e ter uma intensidade mínima para não ser confundido com preto.
    return g > r and g >= b and g > 40

def check_threshold(x, y, target_rgb, tolerance=30):
    """
    Verifica se a cor no ponto (x,y) corresponde à cor esperada (cheio).
    Se não corresponder, significa que o nível está abaixo desse ponto.
    Retorna (is_similar, current_color)
    """
    current_color = get_pixel_color(x, y)
    is_similar = is_color_in_range(current_color, target_rgb, tolerance)
    return is_similar, current_color

if __name__ == "__main__":
    # Exemplo de uso:
    # check_threshold(100, 900, (200, 0, 0)) # Verifica se o ponto tem tom de vermelho
    pass
