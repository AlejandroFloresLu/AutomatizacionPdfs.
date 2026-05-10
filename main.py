import os
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# 1. ¡Importamos tu módulo de IA!
from analizador import analizar_reporte_con_ia

load_dotenv()
RUC = os.getenv('SRI_RUC')
PASSWORD = os.getenv('SRI_PASSWORD')

def automatizar_sri_y_analizar():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print(f"🚀 Iniciando Pipeline para el RUC: {RUC}")
        page.goto("https://facturadorsri.sri.gob.ec/portal-facturadorsri-internet/pages/inicio.html")

        # --- FASE DE LOGIN ---
        try:
            page.fill('input[id="loginForm:nombreusuario"]', RUC)
            page.fill('input[id="loginForm:passwordInput"]', PASSWORD)
            page.click("text='Ingresar'")
            print("✅ Login exitoso...")
            page.wait_for_timeout(3000)
            
            # Navegación directa para evitar menús engañosos
            print("🔗 Saltando directamente a la URL de Administración...")
            page.goto("https://facturadorsri.sri.gob.ec/portal-facturadorsri-internet/pages/consultas/consultaComprobantesElectronicos.html")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
        except Exception as e:
            print(f"❌ Error en login o navegación: {e}")
            browser.close()
            return

        # --- FASE DE FECHAS ---
        hoy = datetime.now()
        primer_dia = hoy.replace(day=1).strftime("%d/%m/%Y")
        dia_actual = hoy.strftime("%d/%m/%Y")
        
        print(f"📅 Buscando comprobantes desde {primer_dia} hasta {dia_actual}")

        ruta_final = "" # Variable para guardar la ruta del archivo

        try:
            page.fill('input[id="form:tabView:clnFechaInicio_input"]', primer_dia)
            page.fill('input[id="form:tabView:j_idt32_input"]', dia_actual)
            
            page.click("button:has-text('Buscar')")
            print("🔍 Buscando en la base de datos del SRI...")
            page.wait_for_timeout(3000) 

            # --- FASE DE DESCARGA ---
            print("⬇️ Descargando el archivo...")
            
            with page.expect_download() as download_info:
                page.click("text='Descargar reporte'")
            
            download = download_info.value
            
            # El SRI a veces descarga en .txt o .csv, usamos el nombre original sugerido
            nombre_archivo = f"reporte_sri_{hoy.strftime('%Y%m%d_%H%M%S')}_{download.suggested_filename}"
            ruta_final = os.path.join("descargas", nombre_archivo)
            
            download.save_as(ruta_final)
            print(f"✅ Archivo guardado correctamente en: {ruta_final}")

        except Exception as e:
            print(f"❌ Error al buscar o descargar: {e}")
            browser.close()
            return

        browser.close()
        
        # --- FASE DE INTELIGENCIA ARTIFICIAL ---
        if ruta_final and os.path.exists(ruta_final):
            print("\n⚙️ Iniciando motor de IA Local (Ollama)...")
            
            # Le pasamos EXACTAMENTE el archivo que acabamos de descargar
            reporte_final = analizar_reporte_con_ia(ruta_final)
            
            print("\n" + "█"*50)
            print("📈 INFORME CONTABLE ESTRATÉGICO")
            print("█"*50)
            print(reporte_final)
            print("█"*50)

if __name__ == "__main__":
    # Asegurarnos de que la carpeta descargas exista antes de empezar
    if not os.path.exists("descargas"):
        os.makedirs("descargas")
        
    automatizar_sri_y_analizar()