# Instalación de dependencias en Colab
!apt-get install -q libspatialindex-dev
!pip install -q osmnx networkx folium geopy matplotlib plotly

import osmnx as ox
import networkx as nx
import folium
from IPython.display import display, HTML
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import math
import numpy as np
import heapq
from collections import defaultdict

# Configuración para Colab
ox.settings.log_console = True
ox.settings.use_cache = True
ox.settings.timeout = 300

def dijkstra_manual(grafo, inicio, fin):
    """
    Implementación manual del algoritmo de Dijkstra
    """
    print("🔍 Ejecutando algoritmo de Dijkstra manual...")
    
    # Inicializar estructuras
    distancias = {nodo: float('inf') for nodo in grafo.nodes()}
    predecesores = {nodo: None for nodo in grafo.nodes()}
    visitados = set()
    
    # La distancia al nodo inicial es 0
    distancias[inicio] = 0
    
    # Cola de prioridad: (distancia, nodo)
    cola_prioridad = [(0, inicio)]
    
    iteraciones = 0
    nodos_visitados = 0
    
    while cola_prioridad:
        # Extraer el nodo con menor distancia
        distancia_actual, nodo_actual = heapq.heappop(cola_prioridad)
        
        # Si ya visitamos este nodo con una distancia menor, saltar
        if distancia_actual > distancias[nodo_actual]:
            continue
            
        visitados.add(nodo_actual)
        nodos_visitados += 1
        iteraciones += 1
        
        # Si llegamos al destino, terminar
        if nodo_actual == fin:
            print(f"✅ Dijkstra completado: {iteraciones} iteraciones, {nodos_visitados} nodos visitados")
            break
        
        # Explorar vecinos
        for vecino in grafo.neighbors(nodo_actual):
            if vecino in visitados:
                continue
                
            # Obtener el peso de la arista (tiempo de viaje)
            edge_data = grafo.get_edge_data(nodo_actual, vecino)
            if not edge_data:
                continue
                
            # Tomar la primera arista disponible
            first_key = list(edge_data.keys())[0]
            peso = edge_data[first_key].get('tiempo_viaje', float('inf'))
            
            if peso == float('inf'):
                continue
                
            nueva_distancia = distancia_actual + peso
            
            # Si encontramos un camino más corto, actualizar
            if nueva_distancia < distancias[vecino]:
                distancias[vecino] = nueva_distancia
                predecesores[vecino] = nodo_actual
                heapq.heappush(cola_prioridad, (nueva_distancia, vecino))
    
    # Reconstruir el camino
    if distancias[fin] == float('inf'):
        print("❌ No se encontró camino al destino")
        return None
    
    camino = []
    nodo_actual = fin
    while nodo_actual is not None:
        camino.append(nodo_actual)
        nodo_actual = predecesores[nodo_actual]
    
    camino.reverse()
    
    print(f"📏 Camino reconstruido: {len(camino)} nodos")
    return camino, distancias[fin]

def descargar_mapa():
    print("🗺️ Descargando mapa de la zona metropolitana de Oaxaca...")

    try:
        north, south, east, west = 17.15, 16.90, -96.60, -96.90
        G = ox.graph_from_bbox(north, south, east, west, network_type='drive')
        print(f"✅ Mapa descargado exitosamente. Nodos: {len(G.nodes())}, Aristas: {len(G.edges())}")
        return G

    except Exception as e:
        print(f"❌ Error con bbox: {e}")
        print("🔄 Intentando con lugares específicos...")

        try:
            lugares = ["Oaxaca de Juárez, Oaxaca, México", "Santa Cruz Xoxocotlán, Oaxaca, México"]
            G = ox.graph_from_place(lugares, network_type='drive')
            print(f"✅ Mapa descargado. Nodos: {len(G.nodes())}, Aristas: {len(G.edges())}")
            return G
        except Exception as e2:
            print(f"❌ Error crítico: {e2}")
            return None

def calcular_tiempo_viaje(G):
    print("🕒 Calculando tiempos de viaje...")

    # Velocidad estándar para las calles sin información (20 km/h en m/s)
    velocidad_estandar_ms = 20 * 1000 / 3600

    for u, v, k, data in G.edges(keys=True, data=True):
        longitud = data.get('length', 0)
        if longitud is None or longitud == 0:
            longitud = 1

        maxspeed = data.get('maxspeed', None)
        velocidad_ms = velocidad_estandar_ms

        if maxspeed is not None:
            if isinstance(maxspeed, list):
                maxspeed = maxspeed[0] if maxspeed else velocidad_estandar_ms

            if isinstance(maxspeed, str):
                if 'km/h' in maxspeed.lower():
                    try:
                        velocidad_kmh = float(maxspeed.replace('km/h', '').strip())
                        velocidad_ms = velocidad_kmh * 1000 / 3600
                    except:
                        pass
                else:
                    try:
                        velocidad_kmh = float(maxspeed)
                        velocidad_ms = velocidad_kmh * 1000 / 3600
                    except:
                        pass
            elif isinstance(maxspeed, (int, float)):
                velocidad_ms = maxspeed * 1000 / 3600

        tiempo_viaje = longitud / velocidad_ms if velocidad_ms > 0 else float('inf')

        G[u][v][k]['tiempo_viaje'] = tiempo_viaje
        G[u][v][k]['velocidad_utilizada_ms'] = velocidad_ms

    print("✅ Tiempos de viaje calculados y asignados")
    return G

def obtener_seleccion_usuario():
    print("\n📍 SELECCIÓN INTERACTIVA DE PUNTOS")
    print("=" * 50)

    puntos_disponibles = {
        1: {"nombre": "Oaxaca de Juárez (Zócalo)", "coords": (17.0614, -96.7250)},
        2: {"nombre": "Xoxocotlán (Centro)", "coords": (17.0292, -96.7356)},
        3: {"nombre": "San Raymundo Jalpan (Centro)", "coords": (16.9667, -96.7667)},
        4: {"nombre": "Central de Abastos", "coords": (17.058180699139797, -96.73396139714094)},
        5: {"nombre": "Parque del Amor", "coords": (17.049926116453296, -96.72903950405214)},
    }

    print("\n🏁 PUNTOS DISPONIBLES:")
    print("-" * 40)
    for key, punto in puntos_disponibles.items():
        print(f"{key}. {punto['nombre']}")
    print("-" * 40)

    def seleccionar_punto(tipo_punto):
        while True:
            try:
                seleccion = int(input(f"\nSeleccione el número para el {tipo_punto} (1-{len(puntos_disponibles)}): "))
                
                if seleccion in puntos_disponibles:
                    punto_seleccionado = puntos_disponibles[seleccion]
                    print(f"✅ {tipo_punto.capitalize()}: {punto_seleccionado['nombre']}")
                    return punto_seleccionado
                else:
                    print(f"❌ Error: Seleccione un número entre 1 y {len(puntos_disponibles)}")
            except ValueError:
                print("❌ Error: Ingrese un número válido")
            except KeyboardInterrupt:
                print("\n👋 Programa interrumpido por el usuario")
                exit()

    print("\n📍 SELECCIÓN DE ORIGEN:")
    origen = seleccionar_punto("origen")

    print("\n🎯 SELECCIÓN DE DESTINO:")
    destino = seleccionar_punto("destino")

    if origen['nombre'] == destino['nombre']:
        print("\n⚠️ Advertencia: Origen y destino son el mismo lugar.")

    return origen, destino

def configurar_puntos_ruta(G, origen, destino):
    print(f"📍 ORIGEN: {origen['nombre']}")
    print(f"🎯 DESTINO: {destino['nombre']}")

    origen_nodo = ox.distance.nearest_nodes(G, origen['coords'][1], origen['coords'][0])
    destino_nodo = ox.distance.nearest_nodes(G, destino['coords'][1], destino['coords'][0])

    puntos_nodos = {
        "ORIGEN": origen_nodo,
        "DESTINO": destino_nodo
    }

    puntos_coords = {
        "ORIGEN": origen['coords'],
        "DESTINO": destino['coords']
    }

    nombres = {
        "ORIGEN": origen['nombre'],
        "DESTINO": destino['nombre']
    }

    print(f"🔍 Nodos encontrados: Origen[{origen_nodo}], Destino[{destino_nodo}]")

    return puntos_nodos, puntos_coords, nombres

def calcular_ruta_dijkstra_manual(G, puntos_nodos):
    print("\n🧮 CALCULANDO RUTA ÓPTIMA CON DIJKSTRA MANUAL...")

    try:
        origen_nodo = puntos_nodos["ORIGEN"]
        destino_nodo = puntos_nodos["DESTINO"]

        # Usar nuestra implementación manual de Dijkstra
        resultado_dijkstra = dijkstra_manual(G, origen_nodo, destino_nodo)
        
        if resultado_dijkstra is None:
            return None
            
        ruta_nodos, tiempo_total = resultado_dijkstra

        # Calcular métricas de la ruta
        distancia_total = 0
        segmentos = []

        for i in range(len(ruta_nodos) - 1):
            u = ruta_nodos[i]
            v = ruta_nodos[i + 1]

            edge_data = G.get_edge_data(u, v)
            if edge_data:
                first_key = list(edge_data.keys())[0]
                data = edge_data[first_key]

                segment_length = data.get('length', 0)
                segment_time = data.get('tiempo_viaje', 0)
                velocidad_kmh = data.get('velocidad_utilizada_ms', 0) * 3.6

                distancia_total += segment_length
                segmentos.append({
                    'distancia': segment_length,
                    'tiempo': segment_time,
                    'velocidad': velocidad_kmh
                })

        print("✅ Ruta calculada exitosamente con Dijkstra manual")
        return {
            'ruta_nodos': ruta_nodos,
            'distancia_total': distancia_total,
            'tiempo_total': tiempo_total,
            'segmentos': segmentos
        }

    except Exception as e:
        print(f"❌ Error al calcular la ruta con Dijkstra manual: {e}")
        return None

def mostrar_resumen_ruta(resultados_ruta, nombres):
    print("\n" + "="*70)
    print("📊 RESUMEN DETALLADO DEL RECORRIDO")
    print("="*70)

    print(f"📍 ORIGEN: {nombres['ORIGEN']}")
    print(f"🎯 DESTINO: {nombres['DESTINO']}")
    print("-" * 70)

    # Métricas principales
    print(f"📏 DISTANCIA FÍSICA TOTAL: {resultados_ruta['distancia_total']:.2f} m | {resultados_ruta['distancia_total']/1000:.2f} km")
    print(f"⏰ TIEMPO ESTIMADO TOTAL: {resultados_ruta['tiempo_total']:.0f} seg | {resultados_ruta['tiempo_total']/60:.1f} minutos")
    print(f"🛣️ SEGMENTOS DE CARRETERA: {len(resultados_ruta['segmentos'])} segmentos")

    # Velocidad promedio
    if resultados_ruta['tiempo_total'] > 0:
        velocidad_promedio = (resultados_ruta['distancia_total'] / 1000) / (resultados_ruta['tiempo_total'] / 3600)
        print(f"🚀 VELOCIDAD PROMEDIO: {velocidad_promedio:.1f} km/h")

    # Información de segmentos
    if resultados_ruta['segmentos']:
        print("\n📈 ESTADÍSTICAS DE SEGMENTOS:")
        distancias = [s['distancia'] for s in resultados_ruta['segmentos']]
        tiempos = [s['tiempo'] for s in resultados_ruta['segmentos']]
        velocidades = [s['velocidad'] for s in resultados_ruta['segmentos']]

        print(f"   • Segmento más corto: {min(distancias):.0f} m")
        print(f"   • Segmento más largo: {max(distancias):.0f} m")
        print(f"   • Velocidad mínima: {min(velocidades):.0f} km/h")
        print(f"   • Velocidad máxima: {max(velocidades):.0f} km/h")

    print("-" * 70)

def visualizar_ruta_interactiva(G, resultados_ruta, puntos_coords, nombres):
    print("\n🗺️ GENERANDO MAPA INTERACTIVO...")

    # Crea un mapa centrado en los puntos de origen y destino
    centro_lat = (puntos_coords["ORIGEN"][0] + puntos_coords["DESTINO"][0]) / 2
    centro_lon = (puntos_coords["ORIGEN"][1] + puntos_coords["DESTINO"][1]) / 2

    mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=13)

    # Agrega marcadores de origen y destino
    folium.Marker(
        puntos_coords["ORIGEN"],
        popup=f"ORIGEN: {nombres['ORIGEN']}",
        tooltip="PUNTO DE ORIGEN",
        icon=folium.Icon(color='green', icon='play', prefix='fa')
    ).add_to(mapa)

    folium.Marker(
        puntos_coords["DESTINO"],
        popup=f"DESTINO: {nombres['DESTINO']}",
        tooltip="PUNTO DE DESTINO",
        icon=folium.Icon(color='red', icon='stop', prefix='fa')
    ).add_to(mapa)

    # Obtener coordenadas de los puntos que conforman la ruta
    ruta_coords = []
    for nodo in resultados_ruta['ruta_nodos']:
        lat = G.nodes[nodo]['y']
        lon = G.nodes[nodo]['x']
        ruta_coords.append([lat, lon])

    # Agrega la ruta al mapa
    folium.PolyLine(
        ruta_coords,
        weight=6,
        color='blue',
        opacity=0.8,
        popup=f"Ruta Óptima: {resultados_ruta['distancia_total']/1000:.2f} km, {resultados_ruta['tiempo_total']/60:.1f} min",
        tooltip="RUTA MÁS RÁPIDA - Algoritmo de Dijkstra (Implementación Manual)"
    ).add_to(mapa)

    # Panel de información flotante dentro del mapa
    info_html = f"""
    <div style="position: fixed;
                top: 10px;
                left: 10px;
                width: 350px;
                height: auto;
                background-color: white;
                border: 3px solid #007cbf;
                border-radius: 10px;
                z-index: 9999;
                padding: 15px;
                font-family: Arial, sans-serif;
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        <h3 style="color: #007cbf; margin-top: 0; text-align: center;">
            🧮 DIJKSTRA MANUAL - RUTA ÓPTIMA
        </h3>

        <div style="background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <p style="margin: 3px 0; font-size: 12px;"><b>📍 Origen:</b><br>{nombres['ORIGEN']}</p>
            <p style="margin: 3px 0; font-size: 12px;"><b>🎯 Destino:</b><br>{nombres['DESTINO']}</p>
        </div>

        <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <p style="margin: 3px 0; font-size: 12px; color: #2e7d32;">
                <b>📏 Distancia total:</b> {resultados_ruta['distancia_total']/1000:.2f} km
            </p>
            <p style="margin: 3px 0; font-size: 12px; color: #d32f2f;">
                <b>⏰ Tiempo estimado:</b> {resultados_ruta['tiempo_total']/60:.1f} minutos
            </p>
        </div>

        <div style="margin: 5px 0;">
            <p style="margin: 2px 0; font-size: 11px;">
                <b>🛣️ Segmentos:</b> {len(resultados_ruta['segmentos'])} calles
            </p>
        </div>

        <p style="text-align: center; font-size: 10px; color: #666; margin: 5px 0 0 0;">
            Algoritmo de Dijkstra - Implementación Manual
        </p>
    </div>
    """

    mapa.get_root().html.add_child(folium.Element(info_html))
    display(mapa)

    return mapa

def main():
    print("🧮 ALGORITMO DE DIJKSTRA MANUAL - RUTA ÓPTIMA EN OAXACA")
    print("📍 Selección interactiva de origen y destino")
    print("="*70)

    # Descarga el mapa
    G = descargar_mapa()
    if G is None:
        return

    # Calcula tiempos de viaje
    G = calcular_tiempo_viaje(G)

    # Selección del usuario sobre el origen y el destino
    origen, destino = obtener_seleccion_usuario()
    puntos_nodos, puntos_coords, nombres = configurar_puntos_ruta(G, origen, destino)

    # Cálculo de la ruta óptima con Dijkstra manual
    resultados_ruta = calcular_ruta_dijkstra_manual(G, puntos_nodos)

    if resultados_ruta:
        # Muestra el resumen
        mostrar_resumen_ruta(resultados_ruta, nombres)
        visualizar_ruta_interactiva(G, resultados_ruta, puntos_coords, nombres)

        # Gráfico
        print("\n📊 Generando gráfico de la ruta...")
        try:
            fig, ax = ox.plot_graph_route(G, resultados_ruta['ruta_nodos'],
                                        route_linewidth=6,
                                        node_size=0,
                                        bgcolor='white',
                                        edge_color='gray',
                                        edge_linewidth=0.5,
                                        show=False,
                                        close=False)
            ax.set_title(f'Ruta Dijkstra Manual: {nombres["ORIGEN"]} → {nombres["DESTINO"]}\n'
                        f'{resultados_ruta["distancia_total"]/1000:.2f} km, {resultados_ruta["tiempo_total"]/60:.1f} min',
                       fontsize=12, fontweight='bold')
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"⚠️ No se pudo generar el gráfico: {e}")

        print("\n✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
        print(f"🎯 Ruta calculada con Dijkstra manual: {nombres['ORIGEN']} → {nombres['DESTINO']}")

    else:
        print("\n❌ No se pudo calcular una ruta entre los puntos seleccionados")

# Ejecutar el programa
if __name__ == "__main__":
    main()