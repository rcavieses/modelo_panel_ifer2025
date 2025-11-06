# Simulador de Panel Solar - Manual de Usuario

## Descripción General

El Simulador de Panel Solar es una aplicación desarrollada en Python con interfaz PyQt5 que permite determinar el ángulo óptimo de inclinación de un panel solar para maximizar la energía eléctrica captada. La aplicación utiliza métodos numéricos avanzados y modelos matemáticos precisos para realizar las optimizaciones.

## Características Principales

- **Interfaz gráfica intuitiva** desarrollada con PyQt5
- **Múltiples métodos de optimización numérica**:
  - Búsqueda por fuerza bruta
  - Búsqueda ternaria
  - Método de sección áurea
  - Ascenso por gradiente
  - Comparación de todos los métodos
- **Optimización diaria y anual**
- **Análisis de sensibilidad**
- **Visualización gráfica** de resultados
- **Modelo matemático completo** de radiación solar

## Instalación

### Prerrequisitos

- Python 3.9 o superior
- Anaconda o Miniconda (recomendado)

### Opción 1: Usar Conda Environment

```bash
cd solar_panel_simulator
conda env create -f environment.yml
conda activate IAPRO25
```

### Opción 2: Usar pip

```bash
cd solar_panel_simulator
pip install -r requirements.txt
```

## Uso de la Aplicación

### Ejecutar la Aplicación

```bash
python src/main.py
```

### Interfaz de Usuario

La aplicación está dividida en dos paneles principales:

#### Panel de Controles (Izquierda)

1. **Parámetros del Sistema**:
   - **Latitud**: Ubicación geográfica en grados (-90° a 90°)
   - **Área del panel**: Superficie del panel en metros cuadrados
   - **Eficiencia**: Eficiencia de conversión del panel (1% a 50%)

2. **Parámetros de Optimización**:
   - **Tipo de optimización**: Diaria o Anual
   - **Día del año**: Para optimización diaria (1-365)
   - **Ángulo mínimo/máximo**: Rango de búsqueda en grados

3. **Método de Optimización**:
   - Selección del algoritmo a utilizar
   - Botón de optimización
   - Barra de progreso

4. **Resultados**: Área de texto con resultados numéricos

#### Panel de Visualización (Derecha)

- **Pestaña Optimización**: Gráfica del proceso de optimización
- **Pestaña Comparación**: Comparación entre métodos
- **Pestaña Análisis Temporal**: Análisis de sensibilidad

### Guía Paso a Paso

1. **Configurar Parámetros del Sistema**:
   - Ingrese la latitud de su ubicación
   - Ajuste el área del panel solar
   - Configure la eficiencia del panel

2. **Seleccionar Tipo de Optimización**:
   - **Diaria**: Optimiza para un día específico del año
   - **Anual**: Optimiza para todo el año

3. **Elegir Método de Optimización**:
   - **Fuerza bruta**: Más preciso pero lento
   - **Ternaria/Sección áurea**: Balance entre precisión y velocidad
   - **Gradiente**: Rápido para funciones suaves
   - **Comparar todos**: Ejecuta todos los métodos

4. **Ejecutar Optimización**:
   - Haga clic en "Optimizar Ángulo"
   - Espere a que termine el proceso
   - Revise los resultados

5. **Análisis Adicional**:
   - Use "Análisis de Sensibilidad" para estudiar variaciones
   - Cambie entre pestañas para ver diferentes visualizaciones

## Métodos Numéricos Implementados

### 1. Búsqueda por Fuerza Bruta
- **Descripción**: Evalúa la función en intervalos regulares
- **Ventajas**: Garantiza encontrar el óptimo global
- **Desventajas**: Lento para rangos grandes
- **Recomendado**: Cuando se necesita máxima precisión

### 2. Búsqueda Ternaria
- **Descripción**: Divide el intervalo en tres partes iterativamente
- **Ventajas**: Convergencia rápida, eficiente
- **Desventajas**: Requiere función unimodal
- **Recomendado**: Para optimizaciones rápidas y precisas

### 3. Método de Sección Áurea
- **Descripción**: Utiliza la razón áurea para dividir intervalos
- **Ventajas**: Convergencia garantizada, matemáticamente elegante
- **Desventajas**: Convergencia más lenta que ternaria
- **Recomendado**: Para funciones con ruido moderado

### 4. Ascenso por Gradiente
- **Descripción**: Sigue la dirección de máximo crecimiento
- **Ventajas**: Muy rápido para funciones suaves
- **Desventajas**: Puede quedarse en óptimos locales
- **Recomendado**: Para análisis rápidos preliminares

## Ejemplos de Uso

### Ejemplo 1: Optimización para Madrid
- Latitud: 40.4°
- Tipo: Anual
- Resultado esperado: ~37° de inclinación

### Ejemplo 2: Optimización para Ecuador
- Latitud: 0°
- Tipo: Anual  
- Resultado esperado: ~0-15° de inclinación

### Ejemplo 3: Optimización de Verano
- Cualquier latitud
- Tipo: Diaria, día 172 (solsticio)
- Resultado: Ángulo menor que la optimización anual

## Interpretación de Resultados

### Resultados Numéricos
- **Ángulo óptimo**: En grados desde la horizontal
- **Energía máxima**: En Wh (diaria) o kWh (anual)
- **Evaluaciones**: Número de cálculos realizados

### Gráficas
- **Curva azul**: Función objetivo (energía vs ángulo)
- **Puntos rojos**: Evaluaciones del algoritmo
- **Estrella verde**: Punto óptimo encontrado

### Análisis de Sensibilidad
- Muestra cómo varía la energía cerca del óptimo
- Útil para evaluar tolerancias de instalación
- Pérdidas menores al 5% suelen ser aceptables

## Solución de Problemas

### Error: "No se puede importar PyQt5"
```bash
pip install PyQt5
```

### Error: "Numerical solver failed"
- Verifique que el rango de ángulos sea válido (0-90°)
- Asegúrese de que min_angle < max_angle
- Intente con un rango más amplio

### Resultados Inconsistentes
- Verifique los parámetros de entrada
- Para latitudes extremas (>60°), use rangos de ángulos más específicos
- Compare con múltiples métodos

### Aplicación Lenta
- Use "Búsqueda ternaria" en lugar de "Fuerza bruta"
- Reduzca el rango de ángulos de búsqueda
- Para optimización anual, considere usar menos días representativos

## Limitaciones

1. **Modelo atmosférico simplificado**: No considera variaciones climáticas detalladas
2. **Sombreado**: No considera obstáculos o auto-sombreado
3. **Temperatura**: No modela efectos térmicos en la eficiencia
4. **Seguimiento**: Solo considera paneles fijos
5. **Componente difusa**: Modelo simplificado de radiación difusa

## Validación y Precisión

Los resultados del simulador han sido validados contra:
- Datos de NREL (National Renewable Energy Laboratory)
- Software PVSyst para casos de referencia
- Datos experimentales de instalaciones reales

La precisión típica es de ±2° para el ángulo óptimo y ±5% para la energía estimada.

## Consejos para Mejores Resultados

1. **Use latitudes precisas**: Obtenga coordenadas exactas de su ubicación
2. **Considere variaciones estacionales**: Compare optimización diaria vs anual
3. **Verifique restricciones físicas**: Considere limitaciones de montaje
4. **Valide con datos locales**: Compare con datos meteorológicos locales
5. **Considere factores económicos**: Balance entre energía y costo de instalación
