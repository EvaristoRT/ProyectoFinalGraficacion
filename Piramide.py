import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np
import math
import sys
import random 

# Inicializamos la lista de posiciones de los árboles (estática y global)
STATIC_TREE_POSITIONS = [] 

# ---------- NUBES: POSICIONES Y MOVIMIENTO (CUADRADAS Y GRANDES) ----------
# [x_pos, y_pos (alto), z_pos, ancho (w), profundidad (d)]
CLOUD_POSITIONS = [
    [-40.0, 35.0, -10.0, 30.0, 30.0],  # Nube 1: Ancha y cuadrada
    [20.0, 32.0, -30.0, 25.0, 25.0],   # Nube 2: Ancha y cuadrada
    [-10.0, 38.0, 40.0, 40.0, 40.0],   # Nube 3: La más grande
    [50.0, 30.0, 5.0, 28.0, 28.0],     # Nube 4: Ancha y cuadrada
]
# Offset para el movimiento de las nubes (actualizado en el bucle principal)
cloud_offset_z = 0.0
# -----------------------------------------------------------


# ---------- TEXTURAS ----------
def load_texture(filename):
    # Asegúrate de tener archivos 'piedra.jpg', 'madera.jpg', 'hojas.jpg', 'pasto.jpg', 'pelota.jpg' en la misma carpeta.
    try:
        img = Image.open(filename)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo de textura '{filename}'. Asegúrate de tenerlo en la misma carpeta.")
        # Usar una textura dummy si falla la carga
        dummy_data = np.full((1, 1, 4), [255, 0, 255, 255], dtype=np.uint8).tobytes() # Magenta
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, dummy_data)
        return tex
        
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.convert("RGBA").tobytes()

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                    img.width, img.height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return tex

# ---------- CÁMARA ----------
camera_pos = np.array([0.0, 2.0, 8.0])
camera_front = np.array([0.0, 0.0, -1.0])
camera_up = np.array([0.0, 1.0, 0.0])
movement_speed = 0.3
yaw = -90.0
pitch = 0.0
first_mouse = True
lastX = 400
lastY = 300
mouse_sensitivity = 0.1
keys = {}

def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if key in (glfw.KEY_W, glfw.KEY_A, glfw.KEY_S, glfw.KEY_D):
        keys[key] = action != glfw.RELEASE

def mouse_callback(window, xpos, ypos):
    global first_mouse, lastX, lastY, yaw, pitch, camera_front

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = (xpos - lastX) * mouse_sensitivity
    yoffset = (lastY - ypos) * mouse_sensitivity
    lastX, lastY = xpos, ypos

    yaw += xoffset
    pitch += yoffset
    pitch = max(-89.0, min(89.0, pitch))

    front = np.array([
        math.cos(math.radians(yaw)) * math.cos(math.radians(pitch)),
        math.sin(math.radians(pitch)),
        math.sin(math.radians(yaw)) * math.cos(math.radians(pitch))
    ])

    camera_front[:] = front / np.linalg.norm(front)

def process_input():
    global camera_pos

    if keys.get(glfw.KEY_W):
        camera_pos += movement_speed * camera_front
    if keys.get(glfw.KEY_S):
        camera_pos -= movement_speed * camera_front

    right = np.cross(camera_front, camera_up)
    right /= np.linalg.norm(right)

    if keys.get(glfw.KEY_A):
        camera_pos -= movement_speed * right
    if keys.get(glfw.KEY_D):
        camera_pos += movement_speed * right

# ---------- VENTANA ----------
def init_window(width, height):
    glfw.init()
    window = glfw.create_window(width, height, "Escena Azteca Diurna 3D", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, mouse_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)
    return window

# Coordenadas de la esfera del sol
SUN_LIGHT_POS = [0.0, 80.0, 0.0, 1.0] 

# ---------- ILUMINACIÓN DIURNA (SOL DIRECCIONAL) ----------
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)

    # 1. LUZ PRINCIPAL (Simula el SOL - GL_LIGHT0)
    glEnable(GL_LIGHT0)
    
    # LUZ DIRECCIONAL (w=0.0)
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 1.0, 0.0, 0.0]) 
    
    # Colores brillantes de día
    sun_ambient = [0.3, 0.3, 0.4, 1.0] 
    sun_diffuse = [1.0, 1.0, 1.0, 1.0] 
    sun_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_AMBIENT, sun_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, sun_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, sun_specular)
    
    # 2. Luz de Linterna (GL_LIGHT1) - Desactivada
    glDisable(GL_LIGHT1)


# ---------- ESCENA (Fondo Azul Claro y Transparencia) ----------
def setup_scene(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w/h, 0.1, 400)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    
    # ACTIVAR TRANSPARENCIA Y BLENDING (Necesario para las nubes y sus sombras)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Color de fondo: Azul claro diurno
    glClearColor(0.53, 0.81, 0.98, 1) 

    setup_lighting()

# Función auxiliar para actualizar la posición y dirección de la linterna (No usada en modo día)
def update_torch_light():
    pass

# ---------- BLOQUE ----------
def draw_block(x, y, z, w, h, d):
    # Dibuja un cubo centrado en (x,y,z) con dimensiones w, h, d
    w/=2; h/=2; d/=2
    glBegin(GL_QUADS)
    faces = [
        [(x-w,y-h,z+d),(x+w,y-h,z+d),(x+w,y+h,z+d),(x-w,y+h,z+d)], # Frente
        [(x-w,y-h,z-d),(x+w,y-h,z-d),(x+w,y+h,z-d),(x-w,y+h,z-d)], # Atrás
        [(x-w,y-h,z-d),(x-w,y-h,z+d),(x-w,y+h,z+d),(x-w,y+h,z-d)], # Izquierda
        [(x+w,y-h,z-d),(x+w,y-h,z+d),(x+w,y+h,z+d),(x+w,y+h,z-d)], # Derecha
        [(x-w,y+h,z-d),(x+w,y+h,z-d),(x+w,y+h,z+d),(x-w,y+h,z+d)], # Arriba
        [(x-w,y-h,z-d),(x+w,y-h,z-d),(x+w,y-h,z+d),(x-w,y-h,z+d)] # Abajo
    ]
    
    # Texturas y vértices
    for face in faces:
        glTexCoord2f(0,0); glVertex3f(*face[0])
        glTexCoord2f(1,0); glVertex3f(*face[1])
        glTexCoord2f(1,1); glVertex3f(*face[2])
        glTexCoord2f(0,1); glVertex3f(*face[3])
    glEnd()

# ---------- SUELO ----------
def draw_ground(pasto):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, pasto)
    glBegin(GL_QUADS)
    glTexCoord2f(0,0); glVertex3f(-120,0,-120)
    glTexCoord2f(25,0); glVertex3f(120,0,-120)
    glTexCoord2f(25,25); glVertex3f(120,0,120)
    glTexCoord2f(0,25); glVertex3f(-120,0,120)
    glEnd()

# ---------- PIRÁMIDE (GRANDE) ----------
def draw_pyramid(tex):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex)
    w = 10; d = 10; h = 0.6; y = h/2
    for _ in range(10):
        draw_block(0,y,0,w,h,d)
        y += h; w -= 0.9; d -= 0.9

# ---------- ESFERA DEL SOL (Color Naranja y Sin Textura) ----------
def draw_sun_sphere():
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    
    # Color Naranja
    glColor3f(1.0, 0.6, 0.0) 

    glPushMatrix()
    glTranslatef(SUN_LIGHT_POS[0], SUN_LIGHT_POS[1], SUN_LIGHT_POS[2])
    
    quad = gluNewQuadric()
    gluSphere(quad, 4.0, 32, 32) 
    gluDeleteQuadric(quad)
    
    glPopMatrix()
    
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0) 

# ---------- ÁRBOLES ----------
def draw_tree(x,z,madera,hojas):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, madera)
    draw_block(x,0.5,z,0.4,1,0.4)
    glBindTexture(GL_TEXTURE_2D, hojas)
    draw_block(x,1.4,z,1.2,1,1.2)

def draw_trees(m,h):
    for x,z in STATIC_TREE_POSITIONS:
        draw_tree(x,z,m,h)

# ---------- DONA ----------
def draw_torus(inner_radius, outer_radius, sides=20, rings=30):
    for i in range(rings):
        theta = 2.0 * math.pi * i / rings
        next_theta = 2.0 * math.pi * (i + 1) / rings

        glBegin(GL_QUAD_STRIP)
        for j in range(sides + 1):
            phi = 2.0 * math.pi * j / sides

            x1 = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
            y1 = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
            z1 = inner_radius * math.sin(phi)

            x2 = (outer_radius + inner_radius * math.cos(phi)) * math.cos(next_theta)
            y2 = (outer_radius + inner_radius * math.cos(phi)) * math.sin(next_theta)
            z2 = z1

            glVertex3f(x1, y1, z1)
            glVertex3f(x2, y2, z2)
        glEnd()

# ---------- CANCHA ----------
def draw_court(piedra, pelota_tex):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, piedra)
    draw_block(30,0.05,0,16,0.1,8)

    draw_block(30,1.5,4.15,2,3,0.3)
    draw_block(30,1.5,-4.15,2,3,0.3)

    glDisable(GL_TEXTURE_2D)
    glColor3f(0.8,0.8,0.8)

    glPushMatrix()
    glTranslatef(30, 2.2, 3.5)
    glRotatef(90, 0, 1, 0)
    draw_torus(0.1, 0.6)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(30, 2.2, -3.5)
    glRotatef(90, 0, 1, 0)
    draw_torus(0.1, 0.6)
    glPopMatrix()

    glEnable(GL_TEXTURE_2D)
    glColor3f(1,1,1)

    glBindTexture(GL_TEXTURE_2D, pelota_tex)
    quad = gluNewQuadric()
    gluQuadricTexture(quad, GL_TRUE)

    glPushMatrix()
    glTranslatef(30,0.4,0)
    gluSphere(quad, 0.35, 32, 32)
    glPopMatrix()

    gluDeleteQuadric(quad)
    
# ---------- DIBUJAR NUBES Y SOMBRAS ----------
def draw_clouds(offset_z):
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)

    # Los elementos en CLOUD_POSITIONS son [x, y, z, w, d]
    for x_start, y, z_start, w, d in CLOUD_POSITIONS:
        
        # 1. NUBE BLANCA (Cielo)
        
        # Coordenada Z animada y cíclica
        z_cloud = (z_start + offset_z) % 120.0 
        if z_cloud > 60.0: 
            z_cloud -= 120.0
            
        # Color: Blanco semi-transparente
        glColor4f(1.0, 1.0, 1.0, 0.6) 

        glPushMatrix()
        glTranslatef(x_start, y, z_cloud)
        # Escala: w y d grandes (cuadradas), altura muy pequeña (0.01)
        glScalef(w, 0.01, d) 
        
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(-0.5, 0, 0.5)
        glEnd()
        glPopMatrix()
        
        # -----------------------------------------------
        
        # 2. SOMBRA PROYECTADA (Simulación de Sombra en el Suelo)
        
        z_shadow = z_cloud
        
        # Color: Gris oscuro semi-transparente (Sombra)
        glColor4f(0.0, 0.0, 0.0, 0.3) 

        glPushMatrix()
        # Posición: En el suelo (y=0.01)
        glTranslatef(x_start, 0.01, z_shadow) 
        # La sombra se hace más grande y difusa (w * 1.5, d * 1.5)
        glScalef(w * 1, 0.01, d * 1) 
        
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0, -0.5)
        glVertex3f(0.5, 0, -0.5)
        glVertex3f(0.5, 0, 0.5)
        glVertex3f(-0.5, 0, 0.5)
        glEnd()
        glPopMatrix()

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_LIGHTING)
    glColor4f(1.0, 1.0, 1.0, 1.0) # Restablecer color y alfa
    

# ---------- MAIN ----------
def main():
    global STATIC_TREE_POSITIONS, cloud_offset_z
    
    window = init_window(1280,720)
    setup_scene(1280,720)

    # --- GENERACIÓN DE POSICIONES ESTÁTICAS DE ÁRBOLES ---
    num_trees = 150 
    area_limit = 60.0 
    safe_zone_radius = 10.0 
    court_pos_x = 30.0
    court_safe_radius = 10.0 

    while len(STATIC_TREE_POSITIONS) < num_trees:
        x = random.uniform(-area_limit, area_limit)
        z = random.uniform(-area_limit, area_limit)
        
        distance_to_center = math.sqrt(x**2 + z**2)
        distance_to_court = math.sqrt((x - court_pos_x)**2 + z**2)

        if distance_to_center > safe_zone_radius and distance_to_court > court_safe_radius:
                STATIC_TREE_POSITIONS.append((x, z))
    # -----------------------------------------------------------

    piedra = load_texture("imagenes/piedra.jpg")
    madera = load_texture("imagenes/madera.jpg")
    hojas = load_texture("imagenes/hojas.jpg")
    pasto = load_texture("imagenes/pasto.jpg")
    pelota = load_texture("imagenes/pelota.jpg")
    
    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        # Cálculo del tiempo delta para el movimiento
        current_time = glfw.get_time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # --- MOVIMIENTO DE NUBES ---
        cloud_offset_z += 5.0 * delta_time 
        if cloud_offset_z > 120.0:
            cloud_offset_z -= 120.0 
        # ---------------------------

        process_input()
        glfw.poll_events()
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        center = camera_pos + camera_front
        gluLookAt(*camera_pos, *center, *camera_up)
        
        # Orden de dibujo: Las sombras deben dibujarse antes de los objetos 3D.
        draw_ground(pasto) 
        draw_clouds(cloud_offset_z) 
        
        draw_pyramid(piedra)
        draw_trees(madera, hojas) 
        draw_court(piedra, pelota)
        
        draw_sun_sphere() 

        glfw.swap_buffers(window)

    glfw.terminate()

if __name__ == "__main__":
    main()