import discord
import lectio
import json
import pytz
from datetime import datetime


fag = { # Ikke brugbart endnu
    "ff": "Fælles faglig",
    "pu": "Produkt udvikling",
    "ke": "Kemi",
    "da": "Dansk",
}

client = discord.Client()

config = json.loads(open("config.json").read())
lectioClient = lectio.sdk(brugernavn=config["brugernavn"], adgangskode=config["adgangskode"], skoleId=config["skole_id"])

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Pollux serveren | !hjælp"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!hjælp'):
        embed = discord.Embed(title="Hjælp",
                              description="""
                              **!hjælp**: Få hjælp til hvordan botten virker
                              **!næste modul**: Få informationer om dit næste modul
                              **!næste time**: Få informationer om dit næste modul
                              """,
                              color=discord.Color.from_rgb(26, 144, 130))
        await message.reply(embed=embed)

    if message.content.startswith('!næste modul') or message.content.startswith('!næste time'):
        successful = False
        skema = lectioClient.skema()
        for modul in skema:
            modulDetailer = modul["data-additionalinfo"].split("\n\n")[0].split("\n")

            tidspunkt = modulDetailer[-4]
            hold = modulDetailer[-3].replace("Hold: ", "")
            lærer = modulDetailer[-2].replace("Lærere: ", "").replace("Lærer: ", "")
            lokale = modulDetailer[-1].replace("Lokale: ", "")

            unixTidspunkt = int(datetime.strptime(tidspunkt.split(" til")[0], "%d/%m-%Y %H:%M").timestamp())
            danskUnixTid = int(datetime.now(pytz.timezone('Europe/Copenhagen')).timestamp())

            tidTilTime = unixTidspunkt - danskUnixTid
            if tidTilTime > 0:
                embed = discord.Embed(title="Næste modul",
                                      description=f"""
                                              **Tidspunkt:** {tidspunkt}
                                              **Hold:** {hold}
                                              **Lærer(e):** {lærer}
                                              **Lokale:** {lokale}
                                              """,
                                      color=discord.Color.from_rgb(26, 144, 130))
                successful = True
                break
        if not successful:
            embed = discord.Embed(title="Næste modul",
                                  description="Der skete en fejl",
                                  color=discord.Color.from_rgb(26, 144, 130))

        await message.reply(embed=embed)

client.run(config["discord_bot_token"])
