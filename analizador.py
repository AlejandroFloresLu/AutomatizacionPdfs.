import pandas as pd
import ollama
import os
import webbrowser

def analizar_reporte_con_ia(ruta_archivo):
    print(f"📊 Analizando datos de: {ruta_archivo}")
    
    try:
        df = pd.read_csv(ruta_archivo, sep=None, engine='python', encoding='latin-1')
    except Exception as e:
        print(f"❌ Error al leer el archivo: {e}")
        return None

    df.columns = df.columns.str.strip()

    # --- CÁLCULOS CONTABLES ---
    total_facturado = 0
    if 'VALOR_TOTAL' in df.columns:
        df['VALOR_TOTAL'] = pd.to_numeric(df['VALOR_TOTAL'], errors='coerce')
        total_facturado = df['VALOR_TOTAL'].sum()
        
    num_facturas = len(df)
    
    if 'RAZON_SOCIAL' in df.columns:
        top_proveedores = df.groupby('RAZON_SOCIAL')['VALOR_TOTAL'].sum().nlargest(3).to_dict()
        top_nombres = ", ".join([f"{k} (${v:.2f})" for k, v in top_proveedores.items()])
    else:
        top_nombres = "No detectados"

    # Cálculos de IVA (Asumiendo tarifa 15% estándar en Ecuador actualmente)
    # Matemáticamente: Total = Base + (Base * 0.15) -> Base = Total / 1.15
    base_imponible = total_facturado / 1.15
    iva_calculado = total_facturado - base_imponible

    # --- CONSULTA A LA IA ---
    contexto_contable = f"""
    Eres un auditor financiero en Ecuador. Aquí están los datos del mes:
    - Total Gastos/Compras: ${total_facturado:.2f}
    - Base Imponible estimada: ${base_imponible:.2f}
    - IVA (15%) estimado: ${iva_calculado:.2f}
    - Top Proveedores: {top_nombres}
    
    Escribe un reporte de 3 párrafos en formato HTML (usa solo etiquetas <p>, <ul>, <li> y <strong>).
    Párrafo 1: Análisis breve de en qué se está gastando el dinero.
    Párrafo 2: Instrucciones exactas para la declaración del IVA (menciona el Formulario 104 y el Crédito Tributario).
    Párrafo 3: Una recomendación administrativa para optimizar estos gastos.
    """

    print("🤖 Generando análisis contable e instrucciones de IVA...")
    
    try:
        response = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': contexto_contable}])
        analisis_ia = response['message']['content']
    except Exception as e:
        analisis_ia = f"<p class='text-red-500'>❌ Error al conectar con Ollama: {e}</p>"

    # --- GENERACIÓN DEL DASHBOARD HTML (LA VISTA) ---
    print("🎨 Construyendo Dashboard Visual...")
    
    # Extraemos las primeras filas para mostrarlas en la tabla del dashboard
    tabla_html = df[['FECHA_EMISION', 'RAZON_SOCIAL', 'VALOR_TOTAL']].head(10).to_html(classes='min-w-full bg-white border border-gray-200', index=False)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Contable - Automatización SRI</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 text-gray-800 font-sans p-8">
        <div class="max-w-6xl mx-auto">
            <h1 class="text-3xl font-bold text-blue-800 mb-6 border-b pb-2">📊 Reporte Ejecutivo Mensual SRI</h1>
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <div class="bg-white p-6 rounded-lg shadow border-l-4 border-blue-500">
                    <h3 class="text-gray-500 text-sm">Comprobantes</h3>
                    <p class="text-2xl font-bold">{num_facturas}</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
                    <h3 class="text-gray-500 text-sm">Total Procesado</h3>
                    <p class="text-2xl font-bold">${total_facturado:.2f}</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow border-l-4 border-yellow-500">
                    <h3 class="text-gray-500 text-sm">Base Imponible (Est.)</h3>
                    <p class="text-2xl font-bold">${base_imponible:.2f}</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow border-l-4 border-red-500">
                    <h3 class="text-gray-500 text-sm">Crédito Tributario IVA (15%)</h3>
                    <p class="text-2xl font-bold">${iva_calculado:.2f}</p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                <div class="lg:col-span-1 bg-white p-6 rounded-lg shadow">
                    <h2 class="text-xl font-semibold text-gray-700 mb-4 flex items-center">
                        <span class="text-2xl mr-2">🤖</span> Recomendación IA y Guía IVA
                    </h2>
                    <div class="prose text-gray-600 text-sm leading-relaxed">
                        {analisis_ia}
                    </div>
                </div>

                <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow overflow-hidden">
                    <h2 class="text-xl font-semibold text-gray-700 mb-4">📑 Últimos Comprobantes (Top 10)</h2>
                    <div class="overflow-x-auto text-sm">
                        {tabla_html}
                    </div>
                </div>
            </div>
            
            <p class="text-center text-xs text-gray-400 mt-8">Generado automáticamente por Bot SRI + Llama 3</p>
        </div>
    </body>
    </html>
    """

    # Guardar el HTML
    ruta_html = os.path.join("descargas", "dashboard_reporte.html")
    with open(ruta_html, "w", encoding="utf-8") as file:
        file.write(html_content)

    print(f"✨ Dashboard creado en: {ruta_html}")
    
    # ¡La magia final! Abrir en el navegador automáticamente
    webbrowser.open('file://' + os.path.realpath(ruta_html))
    
    return "Dashboard web generado y abierto con éxito."

if __name__ == "__main__":
    carpeta = "descargas"
    archivos = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith('.csv') or f.endswith('.txt')]
    if archivos:
        ultimo_archivo = max(archivos, key=os.path.getctime)
        analizar_reporte_con_ia(ultimo_archivo)
    else:
        print("❌ No se encontró ningún archivo.")