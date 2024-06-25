import p2_funcions_auxiliars
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":

    while True:
        try:
            graella_size = int(input("Insereix la mida de la graella (entre 70 i 100): "))
            if 70 <= graella_size <= 100:
                break
            else:
                print("La mida de la graella ha d'estar entre 70 i 100.")
        except ValueError:
            print("Si us plau, introdueix un nombre vàlid.")

    while True:
        try:
            numero_llacs = int(input("Insereix el nombre de llacs (entre 0 i 5): "))
            if 0 <= numero_llacs <= 5:
                break
            else:
                print("El nombre de llacs ha d'estar entre 0 i 5.")
        except ValueError:
            print("Si us plau, introdueix un nombre vàlid.")

    print("Paciència. S'estàn creant els fitxers.")

    humitat = p2_funcions_auxiliars.crear_llacs(numero_llacs, graella_size) # Quantitat d'hores que la cel·la no es crema
    p2_funcions_auxiliars.genera_fitxer_doc('humitat', humitat, 'Humitat')
    p2_funcions_auxiliars.genera_fitxer_img('humitat', humitat)
    print("S'ha creat el fitxer 'humitat.doc' i 'humitat.img' amb èxit.")
    
    vegetacio = p2_funcions_auxiliars.inicialitzar_vegetacio(graella_size) # Quantitat d'hores que triga en cremar-se
    p2_funcions_auxiliars.genera_fitxer_doc('vegetacio', vegetacio, 'Vegetació')
    p2_funcions_auxiliars.genera_fitxer_img('vegetacio', vegetacio)
    print("S'ha creat el fitxer 'vegetacio.doc' i 'vegetacio.img' amb èxit.")
    
    estat_incendi = np.zeros((graella_size, graella_size), dtype=int)  # Estat incendi: cremat/cremant-se/pendent
    p2_funcions_auxiliars.genera_fitxer_doc('incendi', estat_incendi, "Estat de l'incendi")
    p2_funcions_auxiliars.genera_fitxer_img('incendi', estat_incendi)
    print("S'ha creat el fitxer 'estat_incendi.doc' i 'estat_incendi.img' amb èxit.")

    humitat, vegetacio = p2_funcions_auxiliars.llegir_dades('humitat.img', 'vegetacio.img')

    while True:
        vent = input("Vols que hi hagi vent (y/n)? ").lower()
        if vent != 'y' and vent != 'n':
            print("Entrada invàlida. Si us plau, introdueix 'y' o 'n'.")
        else:
            break
    
    if vent == 'y':
        while True:
            direccio_vent = input("En quina direcció vols que bufi el vent (nord/sud/est/oest)? ").lower()
            if direccio_vent in ['nord', 'sud', 'est', 'oest']:
                break
            else:
                print("Entrada invàlida. Si us plau, introdueix 'nord', 'sud', 'est' o 'oest' com a direcció del vent.")
    else :
        direccio_vent = None  # Si no hi ha vent, establim la direcció del vent a None
    
    while True:
        try:
            numero_focs = int(input("Insereix el nombre de focs (entre 1 i 6): "))
            if 1 <= numero_focs <= 6:
                break
            else:
                print("El nombre de llacs ha d'estar entre 1 i 6.")
        except ValueError:
            print("Si us plau, introdueix un nombre vàlid.")

    for i in range(numero_focs):
        fila_aleatoria = np.random.randint(0, graella_size - 1)
        columna_aleatoria = np.random.randint(0, graella_size - 1)
        
        while humitat[fila_aleatoria, columna_aleatoria] == np.inf: # Verifiquem que la casella seleccionada no és un llac (humitat infinita)
            fila_aleatoria = np.random.randint(0, graella_size - 1)
            columna_aleatoria = np.random.randint(0, graella_size - 1)
        
        estat_incendi[fila_aleatoria, columna_aleatoria] = 1 # Un cop tenim una casella vàlida, inicialitzem el foc

    fig = plt.figure(figsize=(15, 5))
    pas = 0

    # Bucle infinit
    while plt.fignum_exists(fig.number):  # Verificar que la figura encara existeix
        
        p2_funcions_auxiliars.visualitzar_capes(humitat, vegetacio, estat_incendi, pas)
        humitat, vegetacio, estat_incendi, tot_apagat = p2_funcions_auxiliars.actualitzar_incendi(humitat, vegetacio, estat_incendi, graella_size, direccio_vent)
        pas += 1

        if tot_apagat: # Si tot ja s'ha apagat, sortim del bucle
            print("L'incendi s'ha extingit completament.")
            break
    plt.show()
        