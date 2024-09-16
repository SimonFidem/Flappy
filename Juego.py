import pygame
from pygame.locals import *
import random

# Inicializamos Pygame
pygame.init() 

# Se crea una instancia de Clock para controlar la velocidad de fotogramas
reloj = pygame.time.Clock()

# Aca se define la velocidad de fotogramas
fps = 60

# Estas variables son para las dimensiones de la pantalla
ancho_pantalla = 864
alto_pantalla = 720

# Y aquí hacemos su superficie.
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))

# Aquí configuramos el nombre de la ventana.
pygame.display.set_caption("Flappy Bird")

# Se define la fuente de texto para la puntuación
fuente = pygame.font.SysFont('Bauhaus 93', 60)

# Definimos el color blanco, lo usaremos para el texto.
blanco = (255, 255, 255)

# --- Variables del juego ---

# Desplazamiento inicial del suelo
desplazamiento_suelo = 0

# Velocidad de desplazamiento del suelo
velocidad_desplazamiento = 3

# Estado de vuelo de la paloma (inicialmente False: no volando)
volar = False

# Estado del juego (inicialmente False: juego en curso)
fin_juego = False

# Espacio entre las tuberías superior e inferior
pipe_gap = 150

# Frecuencia de aparición de las tuberías (en milisegundos)
pipe_frequency = 1500

# Tiempo de la última tubería generada (inicializado para que aparezca una al principio)
last_pipe = pygame.time.get_ticks() - pipe_frequency

# Puntuación actual del jugador
score = 0

# Variable para controlar si la paloma ha pasado una tubería
pass_pipe = False

# --- Carga de imágenes ---

# Cargar la imagen de fondo
fondo = pygame.image.load('img/bg.png')

# Cargar la imagen del suelo
suelo = pygame.image.load('img/ground.png')

# Cargar la imagen del botón de reiniciar
imagen_reiniciar = pygame.image.load('img/restart.png')

# Cargar la imagen del botón de salir
imagen_salir = pygame.image.load('img/quit.png')

# --- Funciones del juego ---

# Función para renderizar y mostrar texto en la pantalla
def implementar_texto(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    pantalla.blit(img, (x,y))

# Función para reiniciar el estado del juego
def reiniciar_juego():
    # Eliminar todas las tuberías existentes
    grupo_tuberia.empty()

    # Reiniciar la posición del pájaro
    flappy.rect.x = 100
    flappy.rect.y = int(alto_pantalla / 2)

    # Reiniciar la puntuación
    score = 0
    return score 

# --- Clases del juego ---

# Clase para representar la paloma
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        # Inicializar la clase base Sprite
        pygame.sprite.Sprite.__init__(self)

        # Lista para almacenar las imágenes de animación de la paloma
        self.images = []

        # Índice de la imagen actual en la animación
        self.index = 0

        # Contador para controlar la velocidad de la animación
        self.counter = 0

        # Cargar las imágenes de animación de la paloma
        for num in range (1,4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)

        # Establecer la imagen inicial del palomón
        self.image = self.images[self.index]

        # Obtener el rectángulo que define su posición y el tamaño
        self.rect = self.image.get_rect()

        # Establecer su posición inicial
        self.rect.center = [x,y]

        # Esta es la velocidad vertical
        self.vel = 0

        # Estado de clic del mouse (para controlar el salto)
        self.clicked = False 

    # Función para actualizar el estado de la paloma en cada fotograma
    def update(self):
        # Aplicar gravedad si la paloma está volando
        if volar == True: 
            self.vel += 0.5

            # Limitar la velocidad de caída
            if self.vel > 8:
                self.vel = 8

            # Empujar la paloma al sueli (a menos que lo toque)
            if self.rect.bottom < 552:  # 552 es la posición y del suelo
                self.rect.y += int(self.vel)

        # Solo procesar el salto y la animación si el juego está en curso
        if fin_juego == False:

            # Detectar clic del mouse para hacer saltar la paloma
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: 
                self.clicked = True
                self.vel = -10  # Aquí la impulsamos hacia arriba

            # Reiniciamos el estado del click cuando se suelta el botón
            if pygame.mouse.get_pressed()[0] == 0 : 
                self.clicked = False
                
            # --- Control de animación de la paloma ---

            self.counter +=1
            flap_cooldown = 5  # Tiempo de espera entre cambios de imagen

            # Cambiar la imagen de animación después del tiempo de espera
            if self.counter > flap_cooldown:
                self.counter = 0
                self.index +=1

                # Volver a la primera imagen de animación si se llega al final
                if self.index >= len(self.images):
                    self.index = 0
            
            # Actualizar la imagen de la paloma con la actual
            self.image = self.images[self.index]

            # Rotar la imagen según la velocidad vertical
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)

        # La rotamos hacia abajo si el juego ha terminado
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

# Clase para representar las tuberías
class Tuberia(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        # Inicializar la clase base Sprite
        pygame.sprite.Sprite.__init__(self)

        # Cargamos la imagen de la tubería
        self.image = pygame.image.load('img/pipe.png')

        # Obtener el rectángulo que define la posición y el tamaño de la tubería
        self.rect = self.image.get_rect()

        # --- Posicionamiento de la tubería ---
        # position 1: tubería superior, position -1: tubería inferior

        # Si la tubería es superior, voltearla verticalmente
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2 )]
        # Si la tubería es inferior, posicionarla debajo de la superior
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    # Función para actualizar la posición de la tubería en cada fotograma
    def update(self):
        self.rect.x -= velocidad_desplazamiento

        # Eliminar la tubería si sale de la pantalla por la izquierda
        if self.rect.right < 0:
            self.kill()

# --- Grupos de sprites ---
# Creamos un grupo de sprites para la paloma
grupo_paloma = pygame.sprite.Group()
# Y un grupo de sprites para las tuberías
grupo_tuberia = pygame.sprite.Group()

# --- Clase para representar los botones ---
class Boton():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    # Método para mostrar el botón en pantalla y detectar clics
    def verBoton(self):
        # Variable para indicar si se ha hecho clic en el botón
        accion = False

        # Obtener la posición actual del mouse
        pos = pygame.mouse.get_pos()

        # Detectar si el mouse está sobre el botón
        if self.rect.collidepoint(pos):
            # Detectar clic del mouse izquierdo
            if pygame.mouse.get_pressed()[0] == 1:
                accion = True

        # Mostrar el botón en la pantalla
        pantalla.blit(self.image, (self.rect.x, self.rect.y))

        # Devolver True si se ha hecho clic en el botón, False en caso contrario
        return accion

# --- Creación de instancias del juego ---

# Aquí se crea una instancia de la paloma
flappy = Bird(100, int(alto_pantalla / 2))

# Y se añade al grupo de sprites
grupo_paloma.add(flappy)

# --- Creación de instancias de botones ---

# Se crean instancias de los botones de reiniciar y salir
reiniciar = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 - 100, imagen_reiniciar)
salir = Boton(ancho_pantalla // 2 - 50, alto_pantalla // 2 + 100, imagen_salir )

# --- Bucle principal del juego ---
ejecutar = True 
while ejecutar:
    # Controlamos la velocidad de fotogramas
    reloj.tick(fps)

    # Se dibuja el fondo en la pantalla
    pantalla.blit(fondo, (0,0))

    # --- Actualización y dibujo de sprites ---

    # Se dibuja la paloma
    grupo_paloma.draw(pantalla)
    # Se actualiza su estado
    grupo_paloma.update()
    # Y dibujamos las tuberías
    grupo_tuberia.draw(pantalla)

    # --- Control de puntuación ---
    # Solo se comprueba la puntuación si hay tuberías en pantalla
    if len(grupo_tuberia) > 0:
        # Detectamos si el pájaro ha pasado completamente la tubería
        if grupo_paloma.sprites()[0].rect.left > grupo_tuberia.sprites()[0].rect.left\
            and grupo_paloma.sprites()[0].rect.right < grupo_tuberia.sprites()[0].rect.right\
            and pass_pipe == False:
            pass_pipe = True

        # Se incrementa la puntuación cuando el pájaro pasa la tubería
        if pass_pipe == True:
            if grupo_paloma.sprites()[0].rect.left > grupo_tuberia.sprites()[0].rect.right:
                score +=1
                pass_pipe = False
    
    # Acá mostramos la puntuación en pantalla
    implementar_texto(str(score), fuente, blanco, int(ancho_pantalla / 2), 20)

    # Con esto dibujamos el suelo en pantalla
    pantalla.blit(suelo, (desplazamiento_suelo,552))

    # --- Detección de colisiones ---

    # Detectar colisión entre la paloma y las tuberías, o si la paloma toca el techo
    if pygame.sprite.groupcollide(grupo_paloma, grupo_tuberia, False, False) or flappy.rect.top < 0:
        fin_juego = True

    # Detectamos si la paloma toca el suelo
    if flappy.rect.bottom >= 552:
        fin_juego = True
        volar = False

    # --- Generación de tuberías y movimiento del suelo ---
    # Solo generar tuberías y mover el suelo si el juego está en curso y la paloma vuela
    if fin_juego == False and volar == True :
        # Generar nuevas tuberías a intervalos regulares
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            # Calculamos una altura aleatoria para la tubería
            altura_pipe = random.randint(-100, 100)

            # Se crean las tuberías superior e inferior
            btm_tubo = Tuberia(ancho_pantalla, int(alto_pantalla / 2) + altura_pipe, -1)
            top_tubo = Tuberia(ancho_pantalla, int(alto_pantalla / 2)+ altura_pipe, 1)

            # Añadimos las tuberías al grupo de sprites
            grupo_tuberia.add(btm_tubo)
            grupo_tuberia.add(top_tubo)

            # Y actualizamos el tiempo de la última tubería generada
            last_pipe = time_now
        
        # Con esto vamos moviendo el suelo a la izquierda
        desplazamiento_suelo -= velocidad_desplazamiento

        # Reiniciamos la posición del suelo cuando sale de la pantalla
        if abs(desplazamiento_suelo) > 35:
            desplazamiento_suelo = 0

        # Y actualizamos la posición de las tuberías
        grupo_tuberia.update()

    # --- Pantalla de fin de juego ---
    # Mostrar la pantalla de fin de juego si el juego ha terminado
    if fin_juego == True:
        # Con este bloque podemos obtener un efecto de desenfoque en el fondo
        imagen_pequeña = pygame.transform.smoothscale(fondo, (fondo.get_width() // 10, fondo.get_height() // 10))
        imagen_desenfocada = pygame.transform.smoothscale(imagen_pequeña, (fondo.get_width(), fondo.get_height()))
        pantalla.blit(imagen_desenfocada, (0,0))

        # Ajustamos las condicionantes para mostrar los botones
        if reiniciar.verBoton() == True:
            fin_juego = False
            score = reiniciar_juego()
        if salir.verBoton() == True:
            ejecutar = False  # Salir del bucle principal del juego

    # --- Manejo de eventos ---

    # Procesar eventos de Pygame
    for event in pygame.event.get():
        # Salir del juego si se cierra la ventana
        if event.type == pygame.QUIT:
            ejecutar = False 
        # Iniciar el vuelo de la paloma al hacer clic con el mouse, 
        # solo si el juego no ha terminado la paloma no está volando
        if event.type == pygame.MOUSEBUTTONDOWN and volar == False:
            volar = True

    # Actualizar la pantalla
    pygame.display.update()

# Se sale del juego
pygame.quit()