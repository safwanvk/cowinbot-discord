import discord
import os
from discord.utils import find
import requests

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
        embedVar.add_field(name="**myInfo**", value="To know your registration details", inline=False)
        embedVar.add_field(name="**vaccine**", value="To know available centers", inline=True)
        embedVar.add_field(name="**register**", value="For registration", inline=True)
        embedVar.add_field(name="**notify**", value="To get notification of the slots", inline=True)
        embedVar.add_field(name="**delete_myInfo**", value="To delete your info", inline=True)
        embedVar.add_field(name="**stop_notify**", value="To stop the notification", inline=True)
        embedVar.set_author(name='Cowin Bot', icon_url='https://images.vexels.com/media/users/3/140503/isolated/lists/24882e71e8111a13f3f1055c1ad53cf3-hand-with-injection.png', url='https://discordpy.readthedocs.io/en/stable/index.html')
        embedVar.set_thumbnail(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        embedVar.set_image(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/photo6147825254626602018.jpg?alt=media&token=38ca1f38-ad75-4ad0-b0fe-5ac4fce18d56')
        embedVar.set_footer(text='Get Vaccinated', icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        await message.channel.send(embed=embedVar)

    if message.content.startswith('vaccine'):
        # message.reply('Hi Choose You State')
        try:
            print("jcvhb")
            url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            res = requests.get(url,headers=headers)
            print(res)
            if res.status_code == 200:
                data = res.json()
                
                state = data.get('states')

                arr_len = len(state)

                num_str = ''
                
                for i in range(0,arr_len):
                    state_data = str(state[i].get('state_name')) + " (" + " Id: " + str(data.get('states')[i].get('state_id')) + ")"
                    
                    num_str += str(state[i].get('state_name')) + " 🆔 == " + "**!" + str(data.get('states')[i].get('state_id')) + "**"
                    
                    if i < (arr_len - 1):
                        num_str += '\n'
                        
                embedVar = discord.Embed(title="Choose Your State", description=num_str, color=15462131)
                embedVar.set_footer(text="Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                await message.channel.send(embed=embedVar)
    
        except requests.ConnectionError as e:
            return print(e)
        
    if message.content.startswith('!'):
        # message.reply('Hi Choose You State')
        if message.content == '!':
            await message.reply('Please enter valid commands')
        else:
            try:
                user_input = message.content.split('!')[1]
                url = 'https://cdn-api.co-vin.in/api/v2/admin/location/districts/' + user_input
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                res = requests.get(url,headers=headers)
                print(res)
                if res.status_code == 200:
                    data = res.json()
                    
                    district = data.get('districts')

                    dis_length = len(district)

                    dist_string = ''
                    
                    for i in range(0,dis_length):
                        dist_data = str(district[i].get('district_name')) + " (" + " Id: " + str(data.get('districts')[i].get('district_id')) + ")"
                        
                        dist_string += str(district[i].get('district_name')) + " 🆔 == " + "#" + str(data.get('districts')[i].get('district_id'))
                        
                        if i < (dis_length - 1):
                            dist_string += '\n'
                            
                    embedVar = discord.Embed(title="Choose Your District", description=dist_string, color=15462131)
                    embedVar.set_footer(text="Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                    await message.channel.send(embed=embedVar)
        
            except requests.ConnectionError as e:
                return print(e)
    
                


client.run(DISCORD_TOKEN)
