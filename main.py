import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "Clay está vivo y respondiendo comandos 24/7"

def run():
    puerto = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=puerto)

threading.Thread(target=run, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="/", intents=intents)
TOKEN_CLAY = os.environ.get("TOKEN_CLAY")

# 1. LA BASE DE DATOS DEBE ESTAR ARRIBA DEL COMANDO
PROGRAMAS = {
    "calculadora": {"nombre": "Calculadora Pro", "enlace": "https://tu-enlace-de-descarga.com"},
    "bloc_de_notas": {"nombre": "Bloc de Notas Avanzado", "enlace": "https://tu-enlace-de-descarga.com"},
    "aurora_ia": {"nombre": "Aurora IA", "enlace": "https://tu-enlace-de-descarga.com"}
}

# 2. LA FUNCIÓN DE AUTOCOMPLETADO
async def programa_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=prog["nombre"], value=id_prog)
        for id_prog, prog in PROGRAMAS.items()
    ]
    return [choice for choice in choices if current.lower() in choice.name.lower()][:25]

# --- EL COMANDO CORREGIDO CON EL MISMO NOMBRE DE PARÁMETRO ---
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar") # <-- Aquí dice 'programa'
@app_commands.autocomplete(programa=programa_autocomplete)
async def descargar(interaction: discord.Interaction, programa: str): # <-- ¡AQUÍ YA DICE 'programa'!
    
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return

    # Limpiamos el texto que llegue
    programa_buscado = programa.lower().strip().replace(" ", "_")

    if programa_buscado in PROGRAMAS:
        datos = PROGRAMAS[programa_buscado]
        await interaction.response.send_message(
            f"Aquí tienes tu enlace para descargar **{datos['nombre']}**: {datos['enlace']}", 
            ephemeral=True
        )
    else:
        lista_visibles = ", ".join([f"`{p['nombre']}`" for p in PROGRAMAS.values()])
        await interaction.response.send_message(
            f"❌ No encontré el programa '{programa}'.\n📋 **Programas:** {lista_visibles}", 
            ephemeral=True
        )

@bot.event
async def on_ready():
    id_mi_servidor = 1479175423764987914 
    try:
        # Volvemos a limpiar e inyectar el árbol de comandos completo en tu servidor
        bot.tree.copy_global_to(guild=discord.Object(id=id_mi_servidor))
        await bot.tree.sync(guild=discord.Object(id=id_mi_servidor))
        print(f"🚀 ¡Éxito! Comandos con autocompletado cargados en el servidor {id_mi_servidor}.")
    except Exception as e:
        print(f"Hubo un error al sincronizar: {e}")

if TOKEN_CLAY:
    bot.run(TOKEN_CLAY)
