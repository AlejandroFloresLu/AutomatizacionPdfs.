🤖 Pipeline Contable SRI + IA Local (Llama 3)
Este proyecto es una herramienta de automatización (RPA) que ingresa al portal del SRI, descarga los comprobantes electrónicos del mes actual y utiliza un modelo de Inteligencia Artificial local para generar un dashboard financiero interactivo.

⚙️ Arquitectura del Proyecto
Scraping/RPA: Playwright (Python)

Procesamiento de Datos: Pandas

Motor IA: Ollama (Modelo Llama 3)

Vista: HTML dinámico + Tailwind CSS

🚀 Guía de Instalación Rápida
Sigue estos pasos para levantar el proyecto en tu máquina local:

1. Clonar el repositorio y crear el entorno virtual

python -m venv venv IMPORTANTE

2. Activar el entorno virtual
Windows: .\venv\Scripts\activate

Mac/Linux: source venv/bin/activate

3. Instalar dependencias y el navegador fantasma
Bash
pip install -r requirements.txt
playwright install chromium
4. Configurar Ollama (IA Local)
Asegúrate de tener Ollama instalado y abierto en tu computadora. Luego, descarga el modelo Llama 3 ejecutando en una terminal aparte:

Bash
ollama run llama3
5. Configurar Credenciales
Copia el archivo .env.example y renómbralo a .env.

Abre el nuevo archivo .env y coloca tu RUC y contraseña del SRI reales. (Nota: El archivo .env está ignorado por Git por seguridad).

🏃‍♂️ Cómo ejecutar el Pipeline
Con el entorno virtual activado y Ollama corriendo en segundo plano, simplemente ejecuta el orquestador:

Bash
python main.py
¿Qué hará el bot?

Abrirá el navegador e iniciará sesión en el SRI.

Descargará el reporte de comprobantes en formato .csv.

Analizará los montos y calculará estimaciones de base imponible e IVA (15%).

Generará un Dashboard en HTML con un análisis de la IA y lo abrirá automáticamente en tu navegador.