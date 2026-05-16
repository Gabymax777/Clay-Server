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

# --- FUNCIÓN DE CLAY PROTEGIDA POR CANAL ---
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
async def descargar(interaction: discord.Interaction, programa: str):
    # CLAVE: Comprobamos si el canal actual empieza por "ticket-"
    # (Si le cambiaste el nombre en la web de Ticket Tool a "comandos-", pon "comandos-" abajo)
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return

    # Si está en un ticket, el bot sigue con su funcionamiento normal:
    if programa.lower() == "calculadora":
        enlace = "https://tu-enlace-de-descarga.com"
        await interaction.response.send_message(f"Aquí tienes tu enlace para descargar **Calculadora**: {enlace}", ephemeral=True)
    else:
        await interaction.response.send_message(f"Lo siento, no tengo el programa '{programa}' en mi base de datos.", ephemeral=True)


@bot.event
async def on_ready():
    # CLAVE: Haz clic derecho en el icono de tu servidor en Discord y dale a "Copiar ID"
    # Reemplaza el número de abajo por la ID real de tu servidor
    id_mi_servidor = 1479175423764987914 

    try:
        # Esto inyecta el comando /descargar directamente en tu servidor de golpe
        bot.tree.copy_global_to(guild=discord.Object(id=id_mi_servidor))
        await bot.tree.sync(guild=discord.Object(id=id_mi_servidor))
        print(f"🚀 ¡Éxito! Comandos de Clay sincronizados al instante en el servidor {id_mi_servidor}.")
    except Exception as e:
        print(f"Hubo un error al sincronizar: {e}")
