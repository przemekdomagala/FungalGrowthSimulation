'''
Start w S
Rozmnożenie do sąsiednich komórek gdy stan > threshold
Warunki poczatkowe dla komórki aby mogła tam rozwinąć się grzybnia
Każda nowa komórka zaczyna on 0.01 i rozwija się w czasie na podstawie wyniku równania opartego o warunki w komórce

def cell_state(self, humidity, temperature, food):
    K - 1.0 
    D - współczynnik dyfuzji
    dt - czas

    if u > threshold and minimal_conditions:
        sąsiedzi.add(sąsiedzi_cella)

    r - warunki: (waga_temp * temp + waga_hum * hum + waga_food * food)
    suma_wag = 1
    d - sąsiedzi - u

    u = u + dt * (D * d + r)
'''

from matplotlib.pylab import randint
import numpy as np

waga_t = 0.2
waga_h = 0.3
waga_nutrition = 0.5

def update_fungal_density(grid, D, r_max, K_max, dt):
    """
    Aktualizuje gęstość grzybni w każdej komórce siatki 100x100 na podstawie równania Fishera-KPP.

    Parametry:
    - grid: 3D numpy array o wymiarach (100, 100, 4), gdzie:
        - grid[i, j, 0]: temperatura w komórce (i, j),
        - grid[i, j, 1]: wilgotność w komórce (i, j),
        - grid[i, j, 2]: zasoby odżywcze w komórce (i, j),
        - grid[i, j, 3]: gęstość grzybni w komórce (i, j).
    - D: współczynnik dyfuzji.
    - r_max: maksymalne tempo wzrostu grzybni.
    - K_max: maksymalna pojemność środowiska.
    - dt: krok czasowy.

    Zwraca:
    - Zaktualizowaną siatkę.
    """
    # Wymiary siatki
    # rows, cols, _ = grid.shape
    rows = 100
    cols = 100

    # Kopia gęstości grzybni do obliczeń (aby nie nadpisywać wartości w trakcie iteracji)
    new_density = np.copy(grid[:, :, 3])

    temp = temp/15
    hum = hum/50
    nut = nut/50

    # Obliczenia dla każdej komórki
    for i in range(rows):
        for j in range(cols):
            # Parametry środowiskowe
            temp = grid[i, j, 0]
            hum = grid[i, j, 1]
            nut = grid[i, j, 2]
            density = grid[i, j, 3]

            # 1. Tempo wzrostu r(i, j) (wpływ temperatury i wilgotności)
            # r = r_max * min(
            #     np.exp(-((temp - 25)**2) / 10),  # Funkcja Gaussa dla temperatury
            #     np.exp(-((hum - 0.8)**2) / 0.02)  # Funkcja Gaussa dla wilgotności
            # )

            r = r_max * (temp * waga_t + hum * waga_h + nut * waga_nutrition)  # Wpływ wszystkich warunków

            # 2. Pojemność środowiska K(i, j) (zależna od zasobów odżywczych)
            # K = K_max * (nut / (nut + 1))  # Im więcej zasobów, tym większa pojemność

            # 3. Dyfuzja (dyskretna Laplacjan dla sąsiednich komórek)
            laplacian = 0
            if i > 0:
                laplacian += grid[i - 1, j, 3]
            if i < rows - 1:
                laplacian += grid[i + 1, j, 3]
            if j > 0:
                laplacian += grid[i, j - 1, 3]
            if j < cols - 1:
                laplacian += grid[i, j + 1, 3]
            laplacian -= 4 * density

            # 4. Obliczenie nowej gęstości grzybni
            # growth = r * density * (1 - density / K)  # Termin reakcji
            growth = r * density * (1 - density)  # Termin reakcji
            diffusion = D * laplacian  # Termin dyfuzji
            new_density[i, j] += dt * (growth + diffusion)

            # Ograniczenie gęstości do zakresu [0, K]
            # new_density[i, j] = max(0, min(new_density[i, j], K))

    # Aktualizacja siatki
    grid[:, :, 3] = new_density
    return grid


def update_fungal_density_for_one_cell(grid, D, r_max, dt, i, j, rows = 10, cols = 10):

    temp = grid[i][j][0]
    hum = grid[i][j][1]
    nut = grid[i][j][2]
    density = grid[i][j][3]

    temp = temp/30
    hum = hum/100
    nut = nut/100

    r = r_max * (temp * waga_t + hum * waga_h + nut * waga_nutrition) / (waga_t + waga_h + waga_nutrition)

    if r < 0.25:
        return 0
    
    laplacian = 0
    if i > 0:
        laplacian += grid[i - 1][j][3]
    if i < rows - 1:
        laplacian += grid[i + 1][j][3]
    if j > 0:
        laplacian += grid[i][j - 1][3]
    if j < cols - 1:
        laplacian += grid[i][j + 1][3]
    laplacian = laplacian/4 - density
    growth = r * density * (1 - density)
    
    diffusion = D * laplacian * 0.01

    new_density = density + dt * (growth + diffusion)

    if new_density < density:
        return density
    return new_density

import numpy as np
import matplotlib.pyplot as plt

# Parametry symulacji
T = 1200  # czas symulacji w godzinach
dt = 0.1  # krok czasowy w godzinach
N = int(T / dt)  # liczba iteracji

# Parametry modelu
r_max = 0.84  # maksymalne tempo wzrostu (1/h)
K_max = 1.0  # maksymalna gęstość grzybni (bez jednostek)
D = 0.1  # współczynnik dyfuzji (mm^2/h)

# Wymiary siatki
grid_size = 100  # 100x100 komórek

#NOTE: Lowkey cooked?

grid_matrix = [[[randint(0,15), randint(0, 50), randint(0,50), 0] for _ in range(grid_size)] for _ in range(grid_size)]
grid_matrix[grid_size // 2][grid_size // 2][3] = 0.01

# Iteracyjna symulacja wzrostu
def simulate_growth():
    global u
    global grid_matrix
    plt.ion()  # Włączenie interaktywnego trybu pyplot
    fig, ax = plt.subplots(figsize=(6, 6))
    img = ax.imshow(grid_matrix, cmap="viridis", origin="lower")
    plt.colorbar(img, ax=ax, label="Gęstość grzybni")
    ax.set_xlabel("X (komórki)")
    ax.set_ylabel("Y (komórki)")

    for step in range(N):

        # Równanie reakcji-dyfuzji
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                grid_matrix[i][j][3] = update_fungal_density_for_one_cell(grid_matrix, D, r_max, dt, i, j, grid_size, grid_size)

        densities = np.array([[cell[3] for cell in row] for row in grid_matrix])

        # Aktualizacja wizualizacji co pewien krok czasu
        if step % 50 == 0 or step == N - 1:
            img.set_data(densities)
            ax.set_title(f"Gęstość grzybni po {step * dt:.2f} godzinach")
            plt.pause(0.1)

    plt.ioff()  # Wyłączenie interaktywnego trybu pyplot
    plt.show()

# Uruchomienie symulacji
# simulate_growth()
if __name__ == "__main__":
    simulate_growth()

