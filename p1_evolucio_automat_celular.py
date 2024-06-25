import numpy as np
import pygame
import sys

def regla_wolfram(regla):
    """Converteix un número de regla en la seva representació binària, on cada bit representa una possible configuració de cel·les veïnes."""
    return np.array([int(x) for x in np.binary_repr(regla, width=8)])

def actualitzar(estat_actual, regla_binaria):
    """Calcula el següent estat de l'automàta cel·lular basant-se en l'estat actual i la regla binària donada. Utilitza índexs per actualitzar de forma eficient."""
    estat_nou = np.zeros_like(estat_actual)
    indices = np.arange(1, len(estat_actual) - 1)
    esquerra = estat_actual[indices - 1]
    centre = estat_actual[indices]
    dreta = estat_actual[indices + 1]
    patrons = 7 - (esquerra * 4 + centre * 2 + dreta)
    estat_nou[indices] = regla_binaria[patrons]
    return estat_nou

def combinar(estats, metode='and'):
    """Combina una llista d'estats d'automàtes cel·lulars aplicant l'operació especificada (AND, OR, XOR) bit a bit, resultant en un estat final combinat."""
    if metode == 'and':
        return np.bitwise_and.reduce(estats, axis=0)
    elif metode == 'or':
        return np.bitwise_or.reduce(estats, axis=0)
    elif metode == 'xor':
        return np.bitwise_xor.reduce(estats, axis=0)
    else:
        raise ValueError("Use 'and', 'or', o 'xor'.")

def evolucio(estats_combinats, tamany_pixel=5, temps_espera=200):
    """Dibuixa l'evolució temporal dels automàtes cel·lulars utilitzant Pygame, mostrant cada estat en una graella visual."""
    pygame.init()
    altura, anchura = estats_combinats.shape
    pantalla = pygame.display.set_mode((anchura * tamany_pixel, altura * tamany_pixel))
    pygame.display.set_caption('Evolució de l\'Automàta Cel·lular')

    for y in range(altura):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        for x in range(anchura):
            color = (0, 0, 0) if estats_combinats[y, x] == 1 else (255, 255, 255)
            pygame.draw.rect(pantalla, color, (x * tamany_pixel, y * tamany_pixel, tamany_pixel, tamany_pixel))

        pygame.display.flip()
        pygame.time.wait(temps_espera)

def automata_celular(regles, metode='and', mida=100, passos=100, tamany_pixel=5, temps_espera=500):
    """Generació, combinació i visualització d'automàtes cel·lulars per a un conjunt de regles, mostrant la seva evolució en el temps."""
    estats = []
    for regla in regles:
        regla_binaria = regla_wolfram(regla)
        estat = np.zeros((passos, mida), dtype=int)
        estat[0, mida // 2] = 1  # Estableix la condició inicial central
        
        for t in range(1, passos):
            estat[t] = actualitzar(estat[t-1], regla_binaria)
        
        estats.append(estat)

    if len(estats) > 1:
        estats_combinats = np.stack([e for e in estats], axis=0)
        estats_combinats = combinar(estats_combinats, metode)
    else:
        estats_combinats = estats[0]

    evolucio(estats_combinats, tamany_pixel, temps_espera)

# Exemple d'ús:
regles = [42, 48]  # Combinem les regles 42 i 48
metode = 'xor' # Triar: 'and', 'or', o 'xor'
automata_celular(regles, metode, mida=100, passos=100, tamany_pixel=5, temps_espera=200)