========================================================================
PROYECTO DE GRAFICACIÓN: ESCENA AZTECA DIURNA 3D
AUTOR: EVARISTO ROMERO
INSTITUCIÓN: ITVER
========================================================================

DESCRIPCIÓN
-----------
Este proyecto consiste en una simulación 3D de una escena de estilo azteca
desarrollada en Python utilizando OpenGL. La escena incluye una pirámide,
árboles generados aleatoriamente, una cancha con aros y pelota, nubes en
movimiento con sombras proyectadas, iluminación solar y un terreno
texturizado. La cámara es completamente interactiva en primera persona.

ESTRUCTURA DEL PROYECTO
-----------------------
/ProyectoFinalGraficacion
  |-- Piramide.py          # Archivo principal del proyecto
  |-- README.txt           # Este archivo
  |-- /imagenes            # Carpeta de texturas
      |-- piedra.jpg       # Textura de la pirámide y la cancha
      |-- madera.jpg       # Textura del tronco de los árboles
      |-- hojas.jpg        # Textura de las hojas de los árboles
      |-- pasto.jpg        # Textura del suelo
      |-- pelota.jpg       # Textura de la pelota

REQUERIMIENTOS TÉCNICOS
-----------------------
Para ejecutar este proyecto necesitas tener instalado:

1. Python 3.8 o superior
2. GLFW
3. PyOpenGL
4. Pillow
5. Numpy

INSTALACIÓN DE DEPENDENCIAS
---------------------------
Abre tu terminal o línea de comandos y ejecuta el siguiente comando:

pip install glfw PyOpenGL Pillow numpy

EJECUCIÓN DEL PROYECTO
----------------------
Desde la carpeta donde se encuentra el archivo Piramide.py, ejecutar:

python Piramide.py

Al ejecutarse, se abrirá una ventana con el título:
"Escena Azteca Diurna 3D"

CONTROLES
---------
- W : Mover la cámara hacia adelante
- S : Mover la cámara hacia atrás
- A : Mover la cámara hacia la izquierda
- D : Mover la cámara hacia la derecha
- Mouse : Girar la vista de la cámara
- ESC : Cerrar la aplicación

CARACTERÍSTICAS PRINCIPALES
---------------------------
- Pirámide 3D construida por bloques
- Árboles generados de forma aleatoria
- Cancha con aros tipo dona
- Pelota con textura
- Nubes en movimiento con sombras proyectadas
- Iluminación diurna simulando el sol
- Esfera visible representando el sol
- Suelo con textura de pasto
- Cámara en primera persona

NOTAS FINALES
-------------
- El proyecto utiliza OpenGL clásico con GLU y GLFW.
- La escena es completamente interactiva en tiempo real.
- Si alguna textura no se encuentra, el sistema usa una textura de respaldo.
- Este proyecto fue desarrollado como práctica de la materia de
  Graficación por Computadora.
