import numpy as np
import matplotlib.pyplot as plt

# Entrada de restricciones
n = int(input("Número de restricciones: "))

restricciones = []
for i in range(n):
    expr = input(f"Restricción {i+1} (ej: 2x+3y<=100): ").replace(" ", "").lower()
    if "<=" in expr: 
        partes = expr.split("<=")
        tipo = "<="
    elif ">=" in expr: 
        partes = expr.split(">=")
        tipo = ">="
    else: 
        partes = expr.split("=")
        tipo = "="
    
    # Extraer coeficientes
    lado_izq = partes[0]
    valor = float(partes[1])
    
    coef_x = 0.0
    coef_y = 0.0
    
    if 'x' in lado_izq:
        idx_x = lado_izq.find('x')
        coef_str = lado_izq[:idx_x]
        coef_x = 1.0 if coef_str in ['', '+'] else -1.0 if coef_str == '-' else float(coef_str)
    
    if 'y' in lado_izq:
        idx_y = lado_izq.find('y')
        # Tomar lo que está entre x y y, o desde inicio si no hay x
        start_idx = idx_x + 1 if 'x' in lado_izq else 0
        coef_str = lado_izq[start_idx:idx_y]
        coef_y = 1.0 if coef_str in ['', '+'] else -1.0 if coef_str == '-' else float(coef_str)
    
    restricciones.append((coef_x, coef_y, tipo, valor))

# Agregar restricciones de no negatividad
restricciones.append((1, 0, ">=", 0))  # x >= 0
restricciones.append((0, 1, ">=", 0))  # y >= 0

# Graficar
plt.figure(figsize=(10, 8))
x_vals = np.linspace(0, 100, 400)

for coef_x, coef_y, tipo, valor in restricciones:
    if coef_y != 0:  # Si la restricción involucra a y
        y_vals = (valor - coef_x * x_vals) / coef_y
        label = f"{coef_x}x + {coef_y}y {tipo} {valor}"
        plt.plot(x_vals, y_vals, label=label, linewidth=2)
        
        # Sombrear región factible
        if tipo == "<=":
            plt.fill_between(x_vals, y_vals, 0, alpha=0.1, color='blue')
        elif tipo == ">=":
            plt.fill_between(x_vals, y_vals, 100, alpha=0.1, color='red')

plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xlabel('x')
plt.ylabel('y')
plt.title('Región Factible - Restricciones')
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()