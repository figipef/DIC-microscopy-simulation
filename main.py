"""
Código realizado por:
Afonso Santos nº 102912
André Filipe nº 102821
Diogo Esteves nº 102905
Gonçalo Torres nº 102831
Maria Maló nº 102994
Instituto Superior Técnico
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import math
import pygame
from scipy import fftpack
from scipy.interpolate import CubicSpline

from leitorfile import ler_dados #Ficheiro que permite ler os dados da MTF

PI = np.pi # Definição de pi
"""
Alterar o código do evento do pygame "pressionar s" caso
se pretenda ver a ft e a ft após MTF da imagem dos OPD's

    --Instruções--
"+" - Escurecer Pincel (Aumentar o OPD)
"-" - Aclarear o Pincel (Diminuir o OPD)
"t" - Diminuir o Comprimento de onda
"y" - Aumentar o Comprimento de onda
"u" - Diminuir o raio do lápis
"i" - Aumentar o raio do lápis
    --------------
"""

# Dados da MTF
inter_x, inter_y = ler_dados("MTF_More_Fun.txt")
for i in range(len(inter_x)):
    inter_x[i] = inter_x[i]*1000 #cicle/mm -> cicle/m

lam = 400 #Comprimento de onda em nm

# Parametros
wavelength = lam*10**(-9) # Comprimento de onda em m
f=0.003285 # Distância focal em m
system_size= 0.00005 # Tamanho real do Canvas
N_mask = 100 # Resolução
pixsize_mask = system_size / N_mask # Tamanho real dos pixeis

#---------Código do Sebastião------- (Basicamente obter as frequência em x e y a partir dos parâmetros)
#Real grid
x = np.linspace(-system_size / 2, system_size / 2, num=N_mask)
y = np.linspace(-system_size / 2, system_size / 2, num=N_mask)
xx, yy = np.meshgrid(x, y)

#x and y frequencies
freq_x = fftpack.fftshift(fftpack.fftfreq(N_mask, d=pixsize_mask))
freq_y = fftpack.fftshift(fftpack.fftfreq(N_mask, d=pixsize_mask))

x_freq=freq_x*wavelength*f
y_freq=freq_y*wavelength*f

xx_freq, yy_freq = np.meshgrid(x_freq, y_freq)

#-----------Fim da ajuda do Sebastião-----------

cs = CubicSpline(inter_x, inter_y) # Interpolação da MTF

MTF =  np.zeros((N_mask, N_mask))
MTF = cs(np.sqrt(xx_freq**2+yy_freq**2)) # Criar a "mascara" da MTF

def phase(opd):
    opd_ = 0.2989 * opd[0] + 0.5870 * opd[1] + 0.1140 * opd[2] #Obter a intensidade da cor
    opd_ = opd_ * 113.7254902 + 13000 # OPD ajustado para ficar entre (13 a 42) * 10^-6
    phase = 2*PI*opd_/lam
    return phase

def dif(phase1,phase2): 
    # Calcular a diferença entre as fases para o DIC
	dphase = phase1-phase2
	while dphase >= PI:
		dphase += -2*PI 
	while dphase <= -PI:
		dphase += 2 * PI	
	return dphase

def png_to_ndarray(image_path):
    # Função redundante mas que preferimos deixar (legacy)
    # Load da imagem
    image = Image.open(image_path)
    # Conversão da imagem
    image_array = np.array(image)
    return image_array

def calculate_2dft(input):
    # Calcular a transformada de Fourier
    ft = np.fft.fft2(input)
    return np.fft.fftshift(ft)

def calculate_inv_2dft(input):
    # Calcular a transformada de Fourier inversa
    return np.fft.ifft2(input)

def make_fft(image_path):
    # Ler e processar a imagem

    img = Image.open(image_path) # Abrir a imagem
    img = img.resize((N_mask,N_mask), Image.ANTIALIAS) # Alterar as dimensões da imagem
    img.save("resize.png")

    image = plt.imread("resize.png")
    image = image[:, :, :3].mean(axis=2)  # Converter em grayscale
    plt.set_cmap("gray")

    # Espaço de fourier imagem original
    ft = calculate_2dft(image)

    # Espaço de fourier imagem pelo MTF (tirar o # para escolher uma MTF 0 ou 1)
    #MTF =  np.zeros((N_mask, N_mask)) # MTF = 0
    #MTF =  np.ones((N_mask, N_mask)) # MTF = 1
    output_ft = ft * MTF

    # Espaço das imagens, imagem final outuput
    output_field = calculate_inv_2dft(ft*MTF)

    # Plot de tudo
    plt.subplot(231)
    plt.imshow(image)
    plt.axis("off")
    plt.subplot(232)
    plt.imshow(abs(ft))
    plt.axis("off")
    plt.subplot(233)
    plt.imshow(abs(MTF))
    plt.axis("off")
    plt.subplot(234)
    plt.imshow(abs(output_ft))
    plt.axis("off")
    plt.subplot(235)
    plt.imshow(abs(output_field))
    plt.axis("off")
    plt.subplot(236)
    plt.imshow((abs(output_field)-image))
    plt.axis("off")
    plt.show()

    # Observar o valor da diferença entre o output e a imagem inicial

    mi = 1000000
    ma = 0
    for i in (abs(output_field)-image):
        for j in i:
            if j > ma:
                ma = j
            elif j < mi:
                mi = j

    print(ma, "Maximo\n", mi, "Minimo\n", "\n Maior e menor diferença entre o valor da intensidade de pixeis (-1-1)")

    # Guardar as imagens para serem usadas como output final (é possivel que a diferença tenha problemas se for muito pequena)
    plt.imsave("FT_original.png",abs(ft))
    plt.imsave("FT_MTF.png",abs(output_ft))
    plt.imsave("MTF.png",abs(MTF))
    plt.imsave("DIF_original_e_Output.png",(abs(output_field - image)))
    plt.imsave("FT_MTF_Final.png",abs(output_field), dpi=300)

def make_DIC(image_path,n):
    # Função para criar a partir do OPD a imagem do DIC
    image_array = png_to_ndarray(image_path)
    data = np.zeros((len(image_array),len(image_array), 3), dtype=np.uint8)
    data[0:len(image_array), 0:len(image_array)] = [255,0,0] # em caso de erro imagem vermelha 


    for i in range(len(image_array)):
        for j in range(len(image_array[i])):
            try:
                cor = ( 0.5 +  0.25 * dif(phase(image_array[i][j]),phase(image_array[i][j-1]))/PI + 0.25 * dif(phase(image_array[i][j]),phase(image_array[i-1][j]))/PI)
                data[i,j] =  [cor *255,cor * 255,cor * 255]
            except:
                pass

    img = Image.fromarray(data, "RGB")

    if n == 0:
        img.save("DIC_original_" + str(lam) + "nm.png")
    if n == 1:
        img.save("DIC_MTF_" + str(lam) + "nm.png")
    img.show()

pygame.init()

# Constantes iniciais
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 800
CANVAS_WIDTH, CANVAS_HEIGHT = N_mask, N_mask
color = (255, 255, 255)
pencil_size = 5

# Criar a window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("DIC miscroscope drawing")
canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))

# Variable to keep track of whether the left mouse button is pressed
drawing = False

# Mais definições de coisas
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# Loop principal
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Desenha
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:  
                drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                drawing = False

        elif event.type == pygame.MOUSEMOTION:
            if drawing:
                # Posicao do rato
                x, y = pygame.mouse.get_pos()

                # escalar a posição para o ecrã
                scaled_x = x * CANVAS_WIDTH // WINDOW_WIDTH
                scaled_y = y * CANVAS_HEIGHT // WINDOW_HEIGHT
                
                # Desenha
                pygame.draw.circle(canvas, color, (scaled_x, scaled_y), pencil_size)

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_s:
                # Apresentar os resultados todos

                pygame.image.save(canvas, "Original.png")

                make_DIC("Original.png",1)

                make_fft("DIC_MTF_" + str(lam) + "nm.png") # Alterar a ordem e o nome dos ficheiros para fazer a FT da imagem original

                #make_DIC("FT_MTF_Final.png",0)  
                
            elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                # Tornar mais escuro
                color = tuple(max(value - 10, 0) for value in color)
            elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                # Tornar mais claro
                color = tuple(min(value + 10, 255) for value in color)

            elif event.key == pygame.K_y:
                # Aumentar o comprimento de onda
                lam += 50
                wavelength = lam*10**(-9)

            elif event.key == pygame.K_t:
                # Diminuir o comprimento de onda
                lam -= 50
                wavelength = lam*10**(-9)

            elif event.key == pygame.K_i:
                # Aumentar o tamanho do pincel
                pencil_size += 1

            elif event.key == pygame.K_u:
                # Diminuir o tamanho do pincel
                pencil_size = max(pencil_size - 1 , 1)

    # Escalar o Ecrã
    scaled_canvas = pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))

    # Dar Reset ao ecrã
    window.fill((0, 0, 0))
    
    # Meter o canvas na window
    window.blit(scaled_canvas, (0, 0))

    # Preview do comprimento de onda
    lam_text = font.render(f"Wavelength: {lam} nm", True, (255, 255, 255))
    window.blit(lam_text, (10, 10))

    # Preview do pincel
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.circle(window, color, mouse_pos, pencil_size / (CANVAS_WIDTH / WINDOW_WIDTH))

    # Update
    pygame.display.flip()
    
    # Framerate
    clock.tick(1000)

# Apagar
pygame.quit()