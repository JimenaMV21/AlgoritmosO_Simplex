import numpy as np

def leer_problema():
    print("Maximizar Z")
    func = input("Función objetivo: ").replace(" ", "").lower()
    
    if "x1" in func:
        idx = func.find("x1")
        coef_str = func[:idx]
        if coef_str in ["", "+"]:
            a = 1.0
        elif coef_str == "-":
            a = -1.0
        else:
            a = float(coef_str)
    else:
        a = 0.0
    
    if "x2" in func:
        after_x1 = func[func.find("x1")+2:] if "x1" in func else func
        idx_x2 = after_x1.find("x2")
        if idx_x2 >= 0:
            coef_str = after_x1[:idx_x2]
            if coef_str in ["", "+"]:
                b = 1.0
            elif coef_str == "-":
                b = -1.0
            else:
                b = float(coef_str)
        else:
            b = 0.0
    else:
        b = 0.0
    
    n = int(input("Número de restricciones: "))
    restricciones = []
    
    for i in range(n):
        print(f"Restricción {i+1}:")
        restr = input().replace(" ", "").lower()
        
        if "<=" in restr:
            tipo = "<="
            partes = restr.split("<=")
        elif ">=" in restr:
            tipo = ">="
            partes = restr.split(">=")
        else:
            tipo = "="
            partes = restr.split("=")
        
        lado_izq = partes[0]
        valor = float(partes[1])
        
        if "x1" in lado_izq:
            idx_x1 = lado_izq.find("x1")
            coef_str = ""
            j = idx_x1 - 1
            while j >= 0 and (lado_izq[j].isdigit() or lado_izq[j] in ['.', '+', '-']):
                coef_str = lado_izq[j] + coef_str
                j -= 1
            if coef_str in ["", "+"]:
                a_restr = 1.0
            elif coef_str == "-":
                a_restr = -1.0
            else:
                a_restr = float(coef_str)
        else:
            a_restr = 0.0
        
        if "x2" in lado_izq:
            idx_x2 = lado_izq.find("x2")
            start_idx = idx_x1 + 2 if "x1" in lado_izq else 0
            coef_str = lado_izq[start_idx:idx_x2]
            if coef_str in ["", "+"]:
                b_restr = 1.0
            elif coef_str == "-":
                b_restr = -1.0
            else:
                b_restr = float(coef_str)
        else:
            b_restr = 0.0
        
        restricciones.append(([a_restr, b_restr], tipo, valor))
    
    return [a, b], restricciones

def crear_tableS(func_obj, restricciones):
    n_vars = 2
    n_restr = len(restricciones)
    
    n_holgura = sum(1 for _, tipo, _ in restricciones if tipo == "<=")
    
    tableS = np.zeros((n_restr + 1, n_vars + n_holgura + 2))
    
    tableS[0, 0] = 1
    tableS[0, 1] = -func_obj[0]
    tableS[0, 2] = -func_obj[1]
    
    holgura_count = 0
    for i in range(n_restr):
        coefs, tipo, valor = restricciones[i]
        fila = i + 1
        
        tableS[fila, 1] = coefs[0]
        tableS[fila, 2] = coefs[1]
        
        if tipo == "<=":
            tableS[fila, 3 + holgura_count] = 1
            holgura_count += 1
        
        tableS[fila, -1] = valor
    
    return tableS

def simplex(tableS):
    print("\n--- ITERACIONES ---")
    itera = 0
    max_itera = 10
    
    while itera < max_itera:
        print(f"\nItera {itera}:")
        print("Z\tx1\tx2\t", end="")
        for i in range(3, tableS.shape[1] - 1):
            print(f"s{i-2}\t", end="")
        print("SOLU")
        
        for i in range(tableS.shape[0]):
            for j in range(tableS.shape[1]):
                print(f"{tableS[i,j]:.1f}\t", end="")
            print()
        
        if all(tableS[0, 1:-1] >= -1e-10):
            print("Solución óptima:")
            break
        
        col_pivote = np.argmin(tableS[0, 1:-1]) + 1
        print(f"Columna pivote: {col_pivote}")
        
        ratios = []
        for i in range(1, tableS.shape[0]):
            if tableS[i, col_pivote] > 1e-10:
                ratio = tableS[i, -1] / tableS[i, col_pivote]
                ratios.append(ratio)
            else:
                ratios.append(float('inf'))
        
        if all(r == float('inf') for r in ratios):
            print("Problema no acotado")
            break
            
        fila_pivote = np.argmin(ratios) + 1
        print(f"Fila pivote: {fila_pivote}")
        
        pivote = tableS[fila_pivote, col_pivote]
        print(f"Elemento pivote: {pivote}")
        
        tableS[fila_pivote] = tableS[fila_pivote] / pivote
        
        for i in range(tableS.shape[0]):
            if i != fila_pivote:
                factor = tableS[i, col_pivote]
                tableS[i] = tableS[i] - factor * tableS[fila_pivote]
        
        itera += 1
    
    return tableS

def mostrar_solucion(tableS, func_obj):
    print("\n--- SOLUCIÓN FINAL ---")
    
    x1, x2 = 0, 0
    
    for col in [1, 2]:
        basic_row = -1
        is_basic = True
        
        for i in range(1, tableS.shape[0]):
            if abs(tableS[i, col] - 1) < 1e-10:
                if basic_row == -1:
                    basic_row = i
                else:
                    is_basic = False
                    break
            elif abs(tableS[i, col]) > 1e-10:
                is_basic = False
                break
        
        if is_basic and basic_row != -1:
            if col == 1:
                x1 = tableS[basic_row, -1]
            else:
                x2 = tableS[basic_row, -1]
    
    z_optimo = func_obj[0] * x1 + func_obj[1] * x2
    
    print(f"Z = {z_optimo:.2f}")
    print(f"x1 = {x1:.2f}")
    print(f"x2 = {x2:.2f}")

print("=== SIMPLEX ===")
func_obj, restricciones = leer_problema()

print(f"\nProblema:")
print(f"Max Z = {func_obj[0]}x1 + {func_obj[1]}x2")
print("Restricciones:")
for i, (coefs, tipo, valor) in enumerate(restricciones):
    print(f"{coefs[0]}x1 + {coefs[1]}x2 {tipo} {valor}")
print("x1, x2 >= 0")

tableS = crear_tableS(func_obj, restricciones)
tableS_final = simplex(tableS)
mostrar_solucion(tableS_final, func_obj)