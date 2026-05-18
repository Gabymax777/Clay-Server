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

bot = commands.Bot(command_prefix=".", intents=intents)
TOKEN_CLAY = os.environ.get("TOKEN_CLAY")

ID_CANAL_SUGERENCIAS = 1505170785772503160  

# 📦 BASE DE DATOS DE PROGRAMAS
PROGRAMAS = {
    "calculadora": {
        "nombre": "GX Calculadora", 
        "enlace": "https://tu-enlace-de-descarga.com",
        "mensaje": "Aquí tienes tu enlace para descargar **GX Calculadora**:"
    },
    "bloc_de_notas": {
        "nombre": "GX Bloc de Notas", 
        "enlace": "https://tu-enlace-de-descarga.com",
        "mensaje": "📝 ¡No olvides ninguna idea! Descarga tu **GX Bloc de Notas** aquí:"
    },
    "aurora_ia": {
        "nombre": "Aurora IA", 
        "enlace": { 
            "AMD": "https://tu-enlace-de-descarga.com",
            "NVIDIA CUDA V12": "https://tu-enlace-de-descarga.com",
            "NVIDIA CUDA V13": "https://tu-enlace-de-descarga.com"
        }, 
        "mensaje": (
            "Antes de descargar este programa, debes verificar si tu tarjeta gráfica es AMD o es NVIDIA. "
            "En caso de ser AMD, pulsa en el enlace de descarga de AMD.\n\n"
            "Para los usuarios de NVIDIA, debéis verificar la versión CUDA de la misma. Para ello, ejecutad el "
            "símbolo del sistema con permisos de administrador y poned el siguiente comando: `nvidia-smi`\n\n"
            "La terminal responderá con una tabla muy grande. Arriba del todo veréis algo así:\n"
            "```\n"
            "+-----------------------------------------------------------------------------------------+\n"
            "| NVIDIA-SMI X                      Driver Version: X              CUDA Version: X        |\n"
            "+-----------------------------------------+------------------------+----------------------+\n"
            "```\n"
            "Si la CUDA version es 12.algo, pulsad en el enlace de **NVIDIA CUDA V12**. Si es 13.0 o superior, "
            "pulsad en el enlace **NVIDIA CUDA V13**. ¡Disfrutad!\n"
        ) 
    }
}

async def programme_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=prog["nombre"], value=id_prog)
        for id_prog, prog in PROGRAMAS.items()
    ]
    return [choice for choice in choices if current.lower() in choice.name.lower()][:25]


async def comprobar_canal_privado(interaction: discord.Interaction) -> bool:
    if not interaction.channel.name.startswith("ticket-"):
        await interaction.response.send_message(
            "❌ Este comando solo se puede usar dentro de tu canal privado de comandos.", 
            ephemeral=True
        )
        return False
    return True


# =========================================================================
# 📥 1. COMANDO: /descargar (Adaptado para enlaces múltiples o simples)
# =========================================================================
@bot.tree.command(name="descargar", description="Obtén el enlace de descarga de un programa")
@app_commands.describe(programa="El nombre del programa que quieres descargar")
@app_commands.autocomplete(programa=programme_autocomplete)
async def descargar(interaction: discord.Interaction, programa: str):
    if not await comprobar_canal_privado(interaction): return

    programa_buscado = programa.lower().strip().replace(" ", "_")

    if programa_buscado in PROGRAMAS:
        datos = PROGRAMAS[programa_buscado]
        mensaje_final = datos['mensaje']
        
        # 🔍 Si "enlace" es un diccionario, recorre las opciones y las añade abajo
        if isinstance(datos['enlace'], dict):
            links_formateados = ""
            for version, url in datos['enlace'].items():
                links_formateados += f"🔗 **{version}**: {url}\n"
            
            await interaction.response.send_message(f"{mensaje_final}\n{links_formateados}", ephemeral=True)
        else:
            # Si es un enlace de texto normal
            await interaction.response.send_message(f"{mensaje_final} {datos['enlace']}", ephemeral=True)
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
    try:
        await bot.tree.sync()
        print("🚀 ¡Éxito! Todos los comandos de Clay se han cargado en el servidor.")
    except Exception as e:
        print(f"Hubo un error al sincronizar: {e}")

if TOKEN_CLAY:
    bot.run(TOKEN_CLAY)
