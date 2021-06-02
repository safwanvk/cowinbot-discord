import discord
import os
from discord.utils import find

from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    
@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hey\nType **help** to know the bot')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')
        
    if message.content.startswith('!help'):
        embedVar = discord.Embed(title="Type the following to perform the steps", description="Thanks For Choosing ME", color=0xFFFFFF,
                                 url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae',
                                 )
        embedVar.add_field(name="!myInfo", value="To know your registration details", inline=False)
        embedVar.add_field(name="!vaccine", value="To know available centers", inline=True)
        embedVar.add_field(name="!register", value="For registration", inline=True)
        embedVar.add_field(name="!notify", value="To get notification of the slots", inline=True)
        embedVar.add_field(name="!delete_myInfo", value="To delete your info", inline=True)
        embedVar.add_field(name="!stop_notify", value="To stop the notification", inline=True)
        embedVar.set_author(name='Cowin Bot', icon_url='https://images.vexels.com/media/users/3/140503/isolated/lists/24882e71e8111a13f3f1055c1ad53cf3-hand-with-injection.png', url='https://discordpy.readthedocs.io/en/stable/index.html')
        embedVar.set_thumbnail(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        embedVar.set_image(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/photo6147825254626602018.jpg?alt=media&token=38ca1f38-ad75-4ad0-b0fe-5ac4fce18d56')
        embedVar.set_footer(text='Get Vaccinated', icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        await message.channel.send(embed=embedVar)

client.run(DISCORD_TOKEN)
