import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading

# --- SERVIDOR WEB FALSO PARA RENDER (CLAY) ---
app = Flask('')

@app.route('/')
def home():
    return "Clay está vivo y respondiendo comandos 24/7"

def run():
    puerto = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=puerto)

threading.Thread(target=run, daemon=True).start()
# ----------------------------------------------

intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="/", intents=intents)
TOKEN_CLAY = os.environ.get("TOKEN_CLAY")

# =========================================================================
# 📦 BASE DE DATOS DE PROGRAMAS (Añade aquí todos los que quieras fácilmente)
# =========================================================================
# Clave: siempre escríbela en MINÚSCULAS.
# Valor: Un diccionario con el Nombre real y el Enlace de descarga.
PROGRAMAS = {
    "aurora_ia": {
        "nombre": "Aurora IA", 
        "enlace": "https://tu-enlace-de-descarga.com"
    },
    "calculadora": {
        "nombre": "GX Calculadora", 
        "enlace": "https://tu-enlace-de-descarga.com"
    },
    "bloc_de_notas": {
        "nombre": "GX Bloc de Notas", 
        "enlace": "https://tu-enlace-de-descarga.com"
    },
    # 💡 Para añadir uno nuevo en el futuro, solo copia y pega esta línea:
    # "nombre_comando": {"nombre": "Nombre Visible", "enlace": "https://link.com"},
}
# =========================================================================


# --- FUNCIÓN DE CLAY ULTRA AMPLIABLE ---
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
async def descargar(interaction: discord.Interaction, programa: str):
    
    # 1. Filtro de seguridad por canal
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return

    # 2. Convertimos lo que escribe el usuario a minúsculas y limpiamos espacios o guiones comunes
    programa_buscado = programa.lower().strip().replace(" ", "_")

    # 3. Buscamos de golpe en nuestro diccionario ultra ampliable
    if programa_buscado in PROGRAMAS:
        datos = PROGRAMAS[programa_buscado]
        nombre_real = datos["nombre"]
        enlace_real = datos["enlace"]
        
        await interaction.response.send_message(
            f"Aquí tienes tu enlace para descargar **{nombre_real}**: {enlace_real}", 
            ephemeral=True
        )
    else:
        # Si no lo encuentra, le listamos automáticamente los programas que sí existen
        lista_disponibles = ", ".join([f"`{p['nombre']}`" for p in PROGRAMAS.values()])
        await interaction.response.send_message(
            f"Lo siento, no tengo el programa '{programa}' en mi base de datos.\n"
            f"📋 **Programas disponibles:** {lista_disponibles}", 
            ephemeral=True
        )


@bot.event
async def on_ready():
    id_mi_servidor = 1479175423764987914 

    try:
        bot.tree.copy_global_to(guild=discord.Object(id=id_mi_servidor))
        await bot.tree.sync(guild=discord.Object(id=id_mi_servidor))
        print(f"🚀 ¡Éxito! Comandos de Clay sincronizados al instante en el servidor {id_mi_servidor}.")
    except Exception as e:
        print(f"Hubo un error al sincronizar: {e}")

if TOKEN_CLAY:
    bot.run(TOKEN_CLAY)
else:
    print("Error crítico: No se encontró la variable TOKEN_CLAY.")
