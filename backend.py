from matplotlib.pylab import randint
import numpy as np

waga_t = 0.2
waga_h = 0.3
waga_nutrition = 0.5

def starting_point_available(grid, i, j, r_max = 0.84):
    temp = grid[i][j][0]
    hum = grid[i][j][1]
    nut = grid[i][j][2]

    r = r_max * (temp * waga_t + hum * waga_h + nut * waga_nutrition) / (waga_t + waga_h + waga_nutrition)
    if r < 0.25:
        return False
    return True


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

    if laplacian < 0:
        laplacian += density

    diffusion = D * laplacian
    
    new_density = density + dt * (growth + diffusion)

    if new_density < density:
        return density
    return new_density