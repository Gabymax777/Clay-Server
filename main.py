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
    # Render asignará un puerto automático para Clay
    puerto = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=puerto)

# Arranca la web en un hilo separado
threading.Thread(target=run, daemon=True).start()
# ----------------------------------------------

# Configuración de los permisos de Clay
intents = discord.Intents.default()
intents.message_content = True  # Obligatorio para leer lo que se escribe

bot = commands.Bot(command_prefix="/", intents=intents)

# Obtenemos el token de Clay desde las variables de entorno de su propio servidor
TOKEN_CLAY = os.environ.get("TOKEN_CLAY")

# --- ÚNICA FUNCIÓN DE CLAY: COMANDO /DESCARGAR ---
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
async def descargar(interaction: discord.Interaction, programa: str):
    # Pasamos el nombre a minúsculas para evitar fallos por mayúsculas
    if programa.lower() == "calculadora":
        enlace = "https://tu-enlace-de-descarga.com" # <-- Cambia esto por tu link real
        # 'ephemeral=True' hace que solo el usuario que ejecutó el comando vea la respuesta
        await interaction.response.send_message(f"Aquí tienes tu enlace para descargar **Calculadora**: {enlace}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Lo siento, no tengo el programa '{programa}' en mi base de datos.", ephemeral=True)

@bot.event
async def on_ready():
    # Sincroniza el comando /descargar con Discord al encenderse
    await bot.tree.sync()
    print(f"🤖 Clay conectado 24/7. Listo para comandos en los canales privados.")

if TOKEN_CLAY:
    bot.run(TOKEN_CLAY)
else:
    print("Error crítico: No se encontró la variable TOKEN_CLAY.")
