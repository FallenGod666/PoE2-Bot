import pyautogui
import PIL.ImageGrab as ImageGrab
import numpy as np

def get_pixel_color(x, y):
    """Retorna a cor RGB de um pixel específico."""
    return pyautogui.pixel(x, y)

def is_color_in_range(color, target_rgb, tolerance=30):
    """Verifica se a cor está dentro de uma tolerância do alvo."""
    return all(abs(c - t) <= tolerance for c, t in zip(color, target_rgb))

def check_threshold(x, y, target_rgb, tolerance=30):
    """
    Verifica se a cor no ponto (x,y) corresponde à cor esperada (cheio).
    Se não corresponder, significa que o nível está abaixo desse ponto.
    """
    current_color = get_pixel_color(x, y)
    return is_color_in_range(current_color, target_rgb, tolerance)

if __name__ == "__main__":
    # Exemplo de uso:
    # check_threshold(100, 900, (200, 0, 0)) # Verifica se o ponto tem tom de vermelho
    pass
