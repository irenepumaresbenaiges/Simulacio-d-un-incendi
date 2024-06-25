import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.ndimage import gaussian_filter
import re

# GENERACIÓ FITXERS

def genera_fitxer_doc(nom_fitxer, dades, descripcio):
    header = f"""file title  : {descripcio}
    data type   : integer
    file type   : ascii
    columns     : {dades.shape[0]}
    rows        : {dades.shape[1]}
    ref.system  : plane
    ref.units   : m
    unit dist.  : 15
    min. X      : 0
    max. X      : 2
    min. Y      : 0
    max. Y      : 2
    pos 'n error: unknown
    resolution  : 30
    min. value  : 0
    max. value  : 2
    Value units : unspecified
    Value Error : unknown
    flag Value  : none
    flag def 'n : none
    legend cats : 0
    """
    
    with open(f'{nom_fitxer}.doc', 'w') as fitxer:
        fitxer.write(header)

def genera_fitxer_img(nom_fitxer, dades):
    # Convertir la matriu a una sola columna
    dades_columna = dades.flatten()
    
    with open(f'{nom_fitxer}.img', 'w') as fitxer:
        for valor in dades_columna:
            fitxer.write(f"{valor}\n")


# LECTURA FITXERS

def llegir_dades_doc(nom_fitxer):
    with open(nom_fitxer, 'r') as fitxer:
        lines = fitxer.readlines()
    
    # Extreure les dimensions de la graella
    columns = int(re.search(r'columns\s*:\s*(\d+)', "".join(lines)).group(1))
    rows = int(re.search(r'rows\s*:\s*(\d+)', "".join(lines)).group(1))

    return columns, rows

def llegir_fitxer_img(nom_fitxer, columns, rows):
    with open(nom_fitxer, 'r') as file:
        data = np.array([float(line.strip()) for line in file if line.strip()], dtype=np.float32)
    return data.reshape(rows, columns)

def llegir_dades(fitxer_humitat, fitxer_vegetacio):
    # Llegir els fitxers .doc
    columns_hum, rows_hum = llegir_dades_doc(fitxer_humitat.replace('.img', '.doc'))
    columns_veg, rows_veg = llegir_dades_doc(fitxer_vegetacio.replace('.img', '.doc'))
    
    # Llegir els fitxers .img
    humitat = llegir_fitxer_img(fitxer_humitat, columns_hum, rows_hum)
    vegetacio = llegir_fitxer_img(fitxer_vegetacio, columns_veg, rows_veg)
    
    return humitat, vegetacio


# SIMULACIÓ INCENDI

# Creació de llacs i humitat

def crear_llacs(num_llacs, graella_size):
    if num_llacs == 0:
        humitat = np.random.randint(0, 6, size=(graella_size, graella_size)).astype(float)
    else:
        humitat = np.random.randint(0, 4, size=(graella_size, graella_size)).astype(float)
    
        for _ in range(num_llacs):
            # Escollim una posició aleatòria per començar el llac
            fila_inicial = np.random.randint(0, graella_size)
            columna_inicial = np.random.randint(0, graella_size)
            
            # Assignem humitat infinita a la posició inicial del llac
            humitat[fila_inicial, columna_inicial] = np.inf
            
            # Determinem la mida del llac
            mida_llac = np.random.randint(400, 500)
            
            # Creem una àrea inicial del llac a partir de la posició inicial
            caselles_llac = [(fila_inicial, columna_inicial)]  # Inicialitzem la llista de caselles del llac amb la posició inicial
            num_caselles_llac = 1  # Inicialitzem el nombre de caselles del llac amb 1 per a la posició inicial
            
            while num_caselles_llac < mida_llac:
                # Escollim una casella aleatòria del llac actual
                fila_actual, columna_actual = caselles_llac[np.random.randint(0, len(caselles_llac))]
                
                # Afegim les caselles adjacents a aquesta casella al llac, si no són ja part del llac
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        nova_fila = fila_actual + di
                        nova_columna = columna_actual + dj
                        # Ens assegurem que la nova posició estigui dins la graella i no estigui ja marcada com a llac
                        if 0 <= nova_fila < graella_size and 0 <= nova_columna < graella_size and humitat[nova_fila, nova_columna] != np.inf:
                            humitat[nova_fila, nova_columna] = np.inf
                            caselles_llac.append((nova_fila, nova_columna))
                            num_caselles_llac += 1

        # Assignem humitat aleatòriament a les caselles que no són part dels llacs
        for i in range(graella_size):
            for j in range(graella_size):
                if humitat[i, j] in range(0,4):
                    distancia_minima = min([np.sqrt((i - x) ** 2 + (j - y) ** 2) for x, y in np.argwhere(humitat == np.inf)])  # Calcula la distància a la casella més propera del llac
                    probabilitat = 1 / (distancia_minima + 1)  # Proporció inversa de la distància
                    probabilitat *= 2 # Multipliquem la probabilitat per un factor constant (2 en aquest cas) per augmentar-la
                    if np.random.rand() < probabilitat:  # Comprovem si s'assigna humitat a la casella en funció de la probabilitat
                        humitat[i, j] = np.random.randint(4, 6)  # Assignem humitat aleatòria de 4 a 5
    
    return humitat


# Inicialització de la vegetació

def inicialitzar_vegetacio(graella_size):
    probabilitats = np.random.rand(graella_size, graella_size) # Generem una matriu base amb probabilitats aleatòries
    probabilitats_suavitzades = gaussian_filter(probabilitats, sigma=1.0) # Apliquem un filtre Gaussià per suavitzar les probabilitats

    # Normalitzem les probabilitats per tenir un rang més controlat
    min_val = probabilitats_suavitzades.min()
    print(min_val)
    max_val = probabilitats_suavitzades.max()
    print(max_val)
    probabilitats_normalitzades = (probabilitats_suavitzades - min_val) / (max_val - min_val)

    vegetacio = np.round(1 + 9 * probabilitats_normalitzades).astype(int) # Escalar las probabilitats a valores enters en el rang [1, 10]
    
    return vegetacio


# Actualització de l'incendi

def actualitzar_incendi(humitat, vegetacio, estat_incendi, graella_size, direccio_vent=None):
    nou_estat_incendi = estat_incendi.copy()
    tot_apagat = True  # Variable per seguir l'estat global del foc

    for i in range(graella_size):
        for j in range(graella_size):
            if estat_incendi[i, j] == 1:  # Caselles que estàn cremant
                tot_apagat = False  # Encara hi ha alguna cosa cremant-se

                if vegetacio[i, j] > 0:
                    vegetacio[i, j] -= 1  # Es redueix la vegetació conforme es crema
                else:
                    nou_estat_incendi[i, j] = 2  # Es marca com a cremada completament si no queda vegetació
                
                # Reduim la humitat de les caselles adjacents
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if 0 <= i + di < graella_size and 0 <= j + dj < graella_size:
                            if humitat[i + di, j + dj] > 0:
                                humitat[i + di, j + dj] -= 1

                # Propagació del foc tenint en compte la direcció del vent (si s'ha proporcionat)
                if direccio_vent is not None:
                    vent_di, vent_dj = 0, 0
                    if direccio_vent == 'nord':
                        vent_di = -3
                    elif direccio_vent == 'sud':
                        vent_di = 3
                    elif direccio_vent == 'est':
                        vent_dj = 3
                    elif direccio_vent == 'oest':
                        vent_dj = -3

                    nova_fila = i + vent_di
                    nova_columna = j + vent_dj

                    if 0 <= nova_fila < graella_size and 0 <= nova_columna < graella_size:
                        if estat_incendi[nova_fila, nova_columna] == 0 and humitat[nova_fila, nova_columna] == 0:
                            nou_estat_incendi[nova_fila, nova_columna] = 1

            elif estat_incendi[i, j] == 0:  # Caselles que poden començar a cremar
                # Intentem propagar el foc a aquesta casella si algun veïna està cremant i la humitat és 0
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if 0 <= i + di < graella_size and 0 <= j + dj < graella_size:
                            if estat_incendi[i + di, j + dj] == 1 and humitat[i, j] == 0:
                                nou_estat_incendi[i, j] = 1  # Comença a cremar
                                break  # Sortim del bucle per a no revisar més veïns

    return humitat, vegetacio, nou_estat_incendi, tot_apagat


# Visualizació dels estats

def visualitzar_capes(humitat, vegetacio, estat_incendi, pas):
    plt.clf()
    
    # Humitat
    plt.subplot(1, 3, 1)
    cmap = ListedColormap(['white', 'blue'])  # White per a les caselles normals, blue per a les caselles d'humitat infinita (llacs)
    plt.imshow(humitat == np.inf, cmap=cmap, interpolation='nearest')
    plt.imshow(humitat, cmap='Blues', interpolation='nearest')
    plt.title('Humitat')
    plt.axis('off')

    # Vegetació
    plt.subplot(1, 3, 2)
    plt.imshow(vegetacio, cmap='Greens', vmin=0, vmax=15)
    plt.title('Vegetació')
    plt.axis('off')

    # Tot
    plt.subplot(1, 3, 3)
    cmap = ListedColormap(['green', 'blue'])  # Green per a les caselles normals, blue per a les caselles d'humitat infinita (llacs)
    plt.imshow(humitat == np.inf, cmap=cmap, interpolation='nearest')
    plt.imshow(np.ma.masked_where(estat_incendi == 0, estat_incendi), cmap='Reds', vmin=0, vmax=2)
    plt.title(f"Estat de l'Incendi\nHores: {pas}")
    plt.axis('off')
    
    plt.pause(0.00001)