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

# 📌 RECUERDA CAMBIAR ESTA ID POR LA DE TU CANAL DE TEXTO DONDE QUIERES QUE TE LLEGUEN LAS SUGERENCIAS
ID_CANAL_SUGERENCIAS = 1505170785772503160  

# 📦 BASE DE DATOS DE PROGRAMAS
PROGRAMAS = {
    "calculadora": {"nombre": "GX Calculadora", "enlace": "https://tu-enlace-de-descarga.com"},
    "bloc_de_notas": {"nombre": "GX Bloc de Notas", "enlace": "https://tu-enlace-de-descarga.com"},
    "aurora_ia": {"nombre": "Aurora IA", "enlace": "https://tu-enlace-de-descarga.com"}
}

async def programme_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=prog["nombre"], value=id_prog)
        for id_prog, prog in PROGRAMAS.items()
    ]
    return [choice for choice in choices if current.lower() in choice.name.lower()][:25]


# =========================================================================
# 🛡️ FUNCIÓN DE COMPROBACIÓN DE CANAL (Para evitar repetir código)
# =========================================================================
async def comprobar_canal_privado(interaction: discord.Interaction) -> bool:
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return False
    return True


# =========================================================================
# 📥 1. COMANDO: /descargar
# =========================================================================
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
@app_commands.autocomplete(programa=programme_autocomplete)
async def descargar(interaction: discord.Interaction, programa: str):
    if not await comprobar_canal_privado(interaction): return

    programa_buscado = programa.lower().strip().replace(" ", "_")

    if programa_buscado in PROGRAMAS:
        datos = PROGRAMAS[programa_buscado]
        await interaction.response.send_message(f"Aquí tienes tu enlace para descargar **{datos['nombre']}**: {datos['enlace']}", ephemeral=True)
    else:
        lista_visibles = ", ".join([f"`{p['nombre']}`" for p in PROGRAMAS.values()])
        await interaction.response.send_message(f"❌ No encontré el programa '{programa}'.\n📋 **Programas:** {lista_visibles}", ephemeral=True)


# =========================================================================
# 📥 2. COMANDO: /sugerencia
# =========================================================================
@bot.tree.command(name="sugerencia", description="Propón un nuevo programa para añadir a la base de datos")
@app_commands.describe(propuesta="Escribe detalladamente qué programa o mejora te gustaría pedir")
async def sugerencia(interaction: discord.Interaction, propuesta: str):
    if not await comprobar_canal_privado(interaction): return

    canal_destino = bot.get_channel(ID_CANAL_SUGERENCIAS)
    if not canal_destino:
        await interaction.response.send_message("❌ Error: El canal de sugerencias no está bien configurado por la administración.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📥 ¡Nueva Sugerencia Recibida!",
        description=propuesta,
        color=discord.Color.from_rgb(255, 165, 0)
    )
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
    embed.set_footer(text=f"Enviado por ID: {interaction.user.id}")

    await canal_destino.send(embed=embed)
    await interaction.response.send_message("✅ ¡Tu sugerencia ha sido enviada con éxito! La administración la revisará pronto.", ephemeral=True)


# =========================================================================
# 📥 3. COMANDO: /info
# =========================================================================
@bot.tree.command(name="info", description="Muestra los enlaces oficiales y redes de la comunidad")
async def info(interaction: discord.Interaction):
    if not await comprobar_canal_privado(interaction): return
        
    embed = discord.Embed(
        title="🌐 Enlaces Oficiales de la Comunidad",
        description="Aquí tienes acceso directo a todos nuestros sitios oficiales:",
        color=discord.Color.from_rgb(58, 110, 165)
    )
    # Cambia los enlaces de ejemplo de abajo por tus links reales
    embed.add_field(name="📜 Normas del Server", value="[Ver Normas](https://tu-link.com)", inline=True)
    embed.add_field(name="📱 Redes Sociales", value="[Nuestro TikTok](https://tiktok.com)", inline=True)
    embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================================================================
# 📥 4. COMANDO: /help
# =========================================================================
@bot.tree.command(name="help", description="Muestra la lista de comandos disponibles y cómo usarlos")
async def help_command(interaction: discord.Interaction):
    if not await comprobar_canal_privado(interaction): return

    embed = discord.Embed(
        title="🤖 Guía de Comandos de Clay",
        description="Hola, soy tu asistente privado. Aquí tienes los comandos que puedes usar en este chat:",
        color=discord.Color.from_rgb(46, 204, 113)
    )
    embed.add_field(name="📥 `/descargar`", value="Te proporciona el enlace directo de un programa de la base de datos.", inline=False)
    embed.add_field(name="💡 `/sugerencia`", value="Envía una propuesta de programa a la administración para que la añadamos.", inline=False)
    embed.add_field(name="🌐 `/info`", value="Muestra los enlaces esenciales y redes sociales de la comunidad.", inline=False)
    embed.add_field(name="❓ `/help`", value="Muestra este menú de ayuda en tu pantalla.", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# =========================================================================
# 🚀 ENTRADA EN VIGOR Y SINCRONIZACIÓN
# =========================================================================
@bot.event
async def on_ready():
    id_mi_servidor = 1479175423764987914 
    try:
        bot.tree.copy_global_to(guild=discord.Object(id=id_mi_servidor))
        await bot.tree.sync(guild=discord.Object(id=id_mi_servidor))
        print(f"🚀 ¡Éxito! Todos los comandos de Clay se han cargado en el servidor {id_mi_servidor}.")
    except Exception as e:
        print(f"Hubo un error al sincronizar: {e}")

if TOKEN_CLAY:
    bot.run(TOKEN_CLAY)
