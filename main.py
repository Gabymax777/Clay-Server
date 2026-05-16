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
# 📦 BASE DE DATOS DE PROGRAMAS
# =========================================================================
PROGRAMAS = {
    "calculadora": {
        "nombre": "Calculadora Pro", 
        "enlace": "https://tu-enlace-de-descarga.com"
    },
    "bloc_de_notas": {
        "nombre": "Bloc de Notas Avanzado", 
        "enlace": "https://tu-enlace-de-descarga.com"
    },
    "aurora_ia": {
        "nombre": "Aurora IA", 
        "enlace": "https://tu-enlace-de-descarga.com"
    }
}
# =========================================================================

# ✨ FUNCIÓN DE AUTOCOMPLETADO (Muestra la lista al usuario mientras escribe)
async def programa_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=prog["nombre"], value=id_prog)
        for id_prog, prog in PROGRAMAS.items()
    ]
    # Filtra las opciones según lo que va escribiendo el usuario
    return [
        choice for choice in choices if current.lower() in choice.name.lower()
    ][:25]


# --- FUNCIÓN DE CLAY MEJORADA ---
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
@app_commands.autocomplete(programa=programa_autocomplete) # <-- Conectamos el autocompletado
async def descargar(interaction: discord.Interaction, programa: str):
    
    # 1. Filtro de seguridad por canal
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return

    # 2. Normalizamos la entrada (reemplazamos espacios por guiones bajos)
    programa_buscado = programa.lower().strip().replace(" ", "_")

    # 3. Búsqueda directa
    if programa_buscado in PROGRAMAS:
        datos = PROGRAMAS[programa_buscado]
        await interaction.response.send_message(
            f"Aquí tienes tu enlace para descargar **{datos['nombre']}**: {datos['enlace']}", 
            ephemeral=True
        )
    else:
        # Copia de seguridad por si escriben algo que no está en la lista
        lista_visibles = ", ".join([f"`{p['nombre']}`" for p in PROGRAMAS.values()])
        await interaction.response.send_message(
            f"❌ No encontré el programa '{programa}'.\n"
            f"📋 **Programas en el sistema:** {lista_visibles}", 
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
