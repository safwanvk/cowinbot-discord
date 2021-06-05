from logging import exception
import discord
import os
from discord.message import Message
from discord.utils import find
import asyncio
import http.client, json, sys
from utils import *
import mysql.connector
from apscheduler.schedulers.blocking import BlockingScheduler
import moment

from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PASSWORD = os.getenv("PASSWORD")

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password= PASSWORD,
  database="CowinBot"
)

cursor = db.cursor()


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
    
    async def fetch_next_7Days():
        dates = []
        today = moment.now()
        for i in range(0,7):
            date_string = today.now().format("DD-MM-YYYY")
            dates.append(date_string)
            today.add(1,'day')
        return dates
            
    
    async def checkAvailability(district,age,userid):
        date_array = await fetch_next_7Days()
        for i in date_array:
            conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
            url = f'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=" + {district} + "&date=" + {i}'

            conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
            conn.request("GET",url)
            res = conn.getresponse()
            print(res)
            if res.status == 200:
                d = res.read()
                data = json.loads(d)
                
                session = data.get('sessions')
                validate_slots = filter(lambda x: x.get('min_age_limit') <= age and x.get('available_capacity') > 0, session)
                if len(validate_slots) > 0:
                    data = json.dumps(validate_slots, separators=(None, '\t'))
                    sessions = json.loads(str(data))
                    
                    s_str = ''

                    s_len = len(sessions)

                    abc = []
                    
                    for i in range(0,s_len):
                        s_str = " :hospital:" + "\n" + "**Center Id: ** " + str(sessions[i].get('center_id')) + "\n" +"**Center Name: ** " + str(sessions[i].get('name')) + "\n" + "**Block: **" + str(sessions[i].get('block_name')) + " \n" +"**PIN: **" + str(sessions[i].get('pincode')) + "\n" +"**Fees: **" + str(sessions[i].get('fee_type')) + " \n" + "**Slot Avaliable For Dose 1: **" + str(sessions[i].get('available_capacity_dose1')) + " \n"+ "**Slot Avaliable For Dose 2: **" + str(sessions[i].get('available_capacity_dose2')) + " \n" + "**Slot Avaliable- **" + str(sessions[i].get('available_capacity')) + " \n"+ "**Age: **" + str(sessions[i].get('min_age_limit')) + "+" + " \n" + ":syringe:**Vaccine: **" + str(sessions[i].get('vaccine')) + " \n" +":stopwatch:**Session Timings**:stopwatch:" + "\n" + str(sessions[i].get('slots')) + "\n" + "\n"
                        abc.push(s_str)
                    user = await client.fetch_user(userid)
                    embedVar = discord.Embed(title="Vaccine Avaliable Slots", description=s_str, color=15462131)
                    embedVar.set_footer(text="Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                    await user.send(embed=embedVar)
                else:
                    user = await client.fetch_user(userid)
                    await user.send("No Vaccine Avaliable Slots")
    
    def job():
        sql = ("SELECT district,age,user_id FROM notify where status = 0")
        cursor.execute(sql)
        res = cursor.fetchall()
        print("cbvh")
        for i in range(0,len(res)):
            checkAvailability(res[i].district, res[i].age, res[i].userid)
    def app():      
        try:
            scheduler = BlockingScheduler()
            scheduler.add_job(job, 'interval', hours=1)
            scheduler.start()
        except Exception as e:
            print(e)

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')
        app()
        
    def check(m):
        return m.author == message.author
    


    if message.content.startswith('help'):
        embedVar = discord.Embed(title="Type the following to perform the steps", description="Thanks For Choosing ME", color=0xFFFFFF,
                                 url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae',
                                 )
        embedVar.add_field(name="**myInfo**", value="To know your registration details", inline=False)
        embedVar.add_field(name="**vaccine**", value="To know available centers", inline=True)
        embedVar.add_field(name="**register**", value="For registration", inline=True)
        embedVar.add_field(name="**notify**", value="To get notification of the slots", inline=True)
        embedVar.add_field(name="**deleteMyInfo**", value="To delete your info", inline=True)
        embedVar.add_field(name="**stopNotify**", value="To stop the notification", inline=True)
        embedVar.set_author(name='Cowin Bot', icon_url='https://images.vexels.com/media/users/3/140503/isolated/lists/24882e71e8111a13f3f1055c1ad53cf3-hand-with-injection.png', url='https://discordpy.readthedocs.io/en/stable/index.html')
        embedVar.set_thumbnail(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        embedVar.set_image(url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/photo6147825254626602018.jpg?alt=media&token=38ca1f38-ad75-4ad0-b0fe-5ac4fce18d56')
        embedVar.set_footer(text='Get Vaccinated', icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
        await message.channel.send(embed=embedVar)

    if message.content.startswith('vaccine'):
        print("jcvhb")
        conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
        url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'

        conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
        conn.request("GET",url)
        res = conn.getresponse()
        print(res)
        if res.status == 200:
            await message.channel.send('Hi Choose You State')
            d = res.read()
            data = json.loads(d)
            
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
    
        
    if message.content.startswith('!'):
        if message.content == '!':
            await message.reply('Please enter valid commands')
        else:
            user_input = message.content.split('!')[1]
            url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/" + user_input

            conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
            conn.request("GET",url)
            res = conn.getresponse()
            print(res)
            if res.status == 200:
                await message.channel.send('Hi Choose You District')
                d = res.read()
                data = json.loads(d)
                
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
        

            
    if message.content.startswith('#'):
        if message.content == '#':
            await message.reply('Please enter valid commands')
        else:


            user_input = message.content.split('#')[1]
            
            await message.channel.send("\n" + "Please Enter Your Preferred Date in this format ** 01-05-2021 **")
            
            print("dcbv")
            
            try:
                date = await client.wait_for('message', check=check, timeout=60000)
                print(date.content)
            except asyncio.TimeoutError:
                return await message.channel.send(f'Sorry, you took too long.')
                
        
            conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
            url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict?district_id=" + user_input + "&date=" + date.content
            conn.request("GET",url)
            res = conn.getresponse()
            print(res.status)
            if res.status == 200:
                d = res.read()
                data = json.loads(d)
                
                session = data.get('sessions')

                s_len = len(session)

                s_str = ''
                
                abc = []
                
                
                if s_len < 1:
                    await message.reply("Sorry, there is no Centers Avaliable on " + date.content +"\n"+ "Please enter district id and try again! ")
                
                for i in range(0,s_len):
                    session_data = str(session[i].get('center_id')) + " (" + str(data.get('sessions')[i].get('name')) + ")" + " (" + str(data.get('sessions')[i].get('block_name')) + ")" + " (" + str(data.get('sessions')[i].get('pincode')) + ")" + " (" + str(data.get('sessions')[i].get('from')) + ")" + " (" + str(data.get('sessions')[i].get('to')) + ")" + " (" + str(data.get('sessions')[i].get('lat')) + ")" + " (" + str(data.get('sessions')[i].get('long')) + ")" + " (" + str(data.get('sessions')[i].get('slots')) + ")"
                    
                    s_str = ":hospital:" + "\n" + "**Center Id: ** " + str(data.get('sessions')[i].get('center_id')) + "\n" + "**Center Name: ** " + str(data.get('sessions')[i].get('name')) + "\n" + "**Block: **" + str(data.get('sessions')[i].get('block_name')) + "\n" +"**PIN: **" + str(data.get('sessions')[i].get('pincode')) + "\n" +"**Fees: **" + str(data.get('sessions')[i].get('fee_type')) + "\n" + "**Slot Avaliable For Dose 1: **" + str(data.get('sessions')[i].get('available_capacity_dose1')) + "\n" + "**Slot Avaliable For Dose 2: **" + str(data.get('sessions')[i].get('available_capacity_dose2')) + "\n" + "**Slot Avaliable- **" + str(data.get('sessions')[i].get('available_capacity')) + "\n" + "**Age: **" + str(data.get('sessions')[i].get('min_age_limit')) + "+" + "\n" + ":syringe:**Vaccine: **" + str(data.get('sessions')[i].get('vaccine')) + "\n" +":stopwatch:**Session Timings**:stopwatch:" + "\n" + str(data.get('sessions')[i].get('slots')) + "\n" + "\n"
                
                    abc.append(s_str)
                    
                await message.channel.send("\n" + "** Center Details **")
                    
                # def fun(x):
                #     embedVar = discord.Embed(title="Session Details", description=x, color=3447003)
                #     embedVar.set_footer(text=f"Total Parts {len(abc)}",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                #     message.channel.send(embed=embedVar)
                    
                # await asyncio.wait(map(fun, abc))
                
                for i in abc:
                    embedVar = discord.Embed(title="Session Details", description=i, color=3447003)
                    embedVar.set_footer(text=f"Total Parts {len(abc)}",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                    await message.channel.send(embed=embedVar)
                    
            else:
                print(res.status)
                await message.channel.send("Sorry, There is no available slots on ")
        
            
    if message.content.startswith('register'):
        await message.channel.send("I'm Concernd About Your privacy, so I have directly send you the details 🔒")
        await message.author.send("Enter your Phone number with your contry code (91-India) 📞")   
        
        
    if message.content.startswith('91'):
        phone = message.content.split('91')[1]
        
        sql = ("SELECT id FROM users where userId = %s and status = 0")
        val = (message.author.id,)
        cursor.execute(sql, val)
        res = cursor.fetchone()
        
        if res:
            pass
        else:
            sql = "INSERT INTO users (id, userId, phoneNo) VALUES (default,%s, %s)"
            val = (message.author.id,phone)
            cursor.execute(sql, val)

            db.commit()
        
        conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
        url = "https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP"

        payload = json.dumps({
        "secret": "U2FsdGVkX18NuNa/jso3AJbIkh1Rf6DDBC58kOBELnGJA58OH/R5EKIz6hrONnCg2kTB8ktbqt0gyJ9aCKyWFw==",
        "mobile": phone,
        })

        headers = {
        'authority': 'cdn-api.co-vin.in',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'accept': 'application/json, text/plain, */*',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'content-type': 'application/json',
        'origin': 'https://selfregistration.cowin.gov.in',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://selfregistration.cowin.gov.in/',
        'accept-language': 'en-IN,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,en-GB;q=0.6,en-US;q=0.5'
        }

        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        if res.status == 200:
            d = res.read()
            data = json.loads(d)

            
            sql = "UPDATE users SET txnId = %s WHERE userId = %s"
            val = (data['txnId'],message.author.id)
            cursor.execute(sql, val)

            db.commit()
            
            #otp verification
            await message.author.send("Enter OTP ")
            
            try:
                otp = await client.wait_for('message', check=check, timeout=60000)
                print(otp.content)
            except asyncio.TimeoutError:
                return await message.channel.send(f'Sorry, you took too long.')
            
            encoded_otp = encrypt_string(otp.content)
            
            
            payload = json.dumps({
            "otp": encoded_otp,
            "txnId": data["txnId"]
            })

            headers = {
            'authority': 'cdn-api.co-vin.in',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'content-type': 'application/json',
            'origin': 'https://selfregistration.cowin.gov.in',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://selfregistration.cowin.gov.in/',
            'accept-language': 'en-IN,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,en-GB;q=0.6,en-US;q=0.5'
            }

            conn.request("POST", "/api/v2/auth/validateMobileOtp", payload, headers)
            res = conn.getresponse()
            
            if res.status == 200:
                d = res.read()
                data = json.loads(d)

                # token = data["token"]

                
                sql = "UPDATE users SET token = %s WHERE userId = %s"
                val = (data["token"],message.author.id)
                cursor.execute(sql, val)

                db.commit()
                
                await message.author.send("OTP Verification Successfull 👍")
                
                ## Taking user details
                await message.author.send("Enter your Full Name")
        
                try:
                    name = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET name = %s WHERE userId = %s"
                    val = (name.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                await message.author.send("Enter your District")
                
                try:
                    district = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET district = %s WHERE userId = %s"
                    val = (district.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                await message.author.send("Enter your Address")
                
                try:
                    address = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET address = %s WHERE userId = %s"
                    val = (address.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                await message.author.send("Enter your age")
                
                try:
                    age = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET age = %s WHERE userId = %s"
                    val = (age.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                await message.author.send("Enter your ID Type (adhaar, election id, pan card...)")
                
                try:
                    idType = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET idType = %s WHERE userId = %s"
                    val = (idType.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                await message.author.send("Enter your ID Number")
                
                try:
                    idNo = await client.wait_for('message', check=check, timeout=60000)

                    sql = "UPDATE users SET idNo = %s WHERE userId = %s"
                    val = (idNo.content,message.author.id)
                    cursor.execute(sql, val)

                    db.commit()
                    await message.author.send("✅ Done!!" + "\n" + "Enter 'myInfo' to know your details.");
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
            else:
                await message.author.send("Sorry, OTP is incorrect 👎")
                await message.author.send("You can still store your data for future use \n Enter **'storeInfo'**")

    if message.content.startswith('myInfo'):
        await message.channel.send("Checking....⌛")
        
        sql = ("SELECT name,district,address,age,idType,idNo,phoneNo FROM users where userId = %s")
        val = (message.author.id,)
        cursor.execute(sql, val)
        res = cursor.fetchone()
        
        if res:
            await  message.channel.send("I'm Concernd About Your privacy so I'm sending it directly to you 🔒")
            embedVar = discord.Embed(title=res[0], description="**District: **" + res[1] + "\n" + "**Address: **" + res[2] + "\n" + "**Age: **" + str(res[3]) + "\n" + "**Personal ID: **" + res[4] + "\n" + "**ID Card no.: **" + str(res[5]) + "\n" + "**Phone no.: **" + str(res[6]) + "\n" + "\n"
                  + "Go to the server to use me Again ", color=3447003)
            embedVar.set_footer(text=f"Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
            await message.author.send(embed=embedVar)
        else:
            await message.channel.send("Sorry You Are Not Registered 😞" + "\n" + "Enter 'register' for registration")
    
    if message.content.startswith('notify'):
        
        conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
        url = 'https://cdn-api.co-vin.in/api/v2/admin/location/states'

        conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
        conn.request("GET",url)
        res = conn.getresponse()
        print(res)
        if res.status == 200:
            await message.channel.send('Hi Choose You State')
            d = res.read()
            data = json.loads(d)
            
            state = data.get('states')

            arr_len = len(state)

            num_str = ''
            
            for i in range(0,arr_len):
                state_data = str(state[i].get('state_name')) + " (" + " Id: " + str(data.get('states')[i].get('state_id')) + ")"
                
                num_str += str(state[i].get('state_name')) + " 🆔 == " + "**" + str(data.get('states')[i].get('state_id')) + "**"
                
                if i < (arr_len - 1):
                    num_str += '\n'
                    
            embedVar = discord.Embed(title="Choose Your State", description=num_str, color=15462131)
            embedVar.set_footer(text="Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
            await message.channel.send(embed=embedVar)
            
            try:
                state_id = await client.wait_for('message', check=check, timeout=60000)

            except asyncio.TimeoutError:
                return await message.channel.send(f'Sorry, you took too long.')
            
            url = "https://cdn-api.co-vin.in/api/v2/admin/location/districts/" + state_id.content

            conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
            conn.request("GET",url)
            res = conn.getresponse()
            print(res)
            if res.status == 200:
                await message.channel.send('Hi Choose You District')
                d = res.read()
                data = json.loads(d)
                
                district = data.get('districts')

                dis_length = len(district)

                dist_string = ''
                
                for i in range(0,dis_length):
                    dist_data = str(district[i].get('district_name')) + " (" + " Id: " + str(data.get('districts')[i].get('district_id')) + ")"
                    
                    dist_string += str(district[i].get('district_name')) + " 🆔 == " + "**" + str(data.get('districts')[i].get('district_id'))
                    
                    if i < (dis_length - 1):
                        dist_string += '\n'
                        
                embedVar = discord.Embed(title="Choose Your District", description=dist_string, color=15462131)
                embedVar.set_footer(text="Get Vaccinated",icon_url='https://firebasestorage.googleapis.com/v0/b/bot-discord-f0d02.appspot.com/o/bot.png?alt=media&token=edbbf198-5a38-4434-a0c0-c12a885de0ae')
                await message.channel.send(embed=embedVar)
                
                try:
                    district_id = await client.wait_for('message', check=check, timeout=60000)

                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')

                
                sql = ("SELECT id FROM notify where user_id = %s and status = 0")
                val = (message.author.id,)
                cursor.execute(sql, val)
                res = cursor.fetchone()
                
                if res:
                    pass
                else:
                    sql = "INSERT INTO users (id, user_id, district) VALUES (default,%s, %s)"
                    val = (message.author.id,district_id.content)
                    cursor.execute(sql, val)

                    db.commit()
                    
                await message.channel.send('Enter Your Age')
                
                try:
                    age = await client.wait_for('message', check=check, timeout=60000)
                    
                except asyncio.TimeoutError:
                    return await message.channel.send(f'Sorry, you took too long.')
                
                sql = "UPDATE notify SET age = %s WHERE userId = %s"
                val = (age.content,message.author.id)
                cursor.execute(sql, val)

                db.commit()
                
                await message.channel.send("**✅ Done!!** You are subscribed to get notification. You will get notification every hour when slots are available \n If you want to unsubscribe notification, then Just Enter '**stopNotify**'")
                await message.author.send("✅ Done!! You are Subscribed To Get Notification")

    if message.content.startswith('stopNotify'):
        sql = "DELETE FROM notify WHERE userId = %s"
        val = (message.author.id)
        cursor.execute(sql, val)

        db.commit()
        await message.channel.send("❌ You have successfully unsubscribed ")
        
    if message.content.startswith('deleteMyInfo'):
        sql = "DELETE FROM users WHERE userId = %s"
        val = (message.author.id)
        cursor.execute(sql, val)

        db.commit()
        await message.channel.send("❌ You have successfully deleted your information")
        
    if message.content.startswith('storeInfo'):
        ## Taking user details
        await message.author.send("Enter your Full Name")

        try:
            name = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET name = %s WHERE userId = %s"
            val = (name.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
        await message.author.send("Enter your District")
        
        try:
            district = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET district = %s WHERE userId = %s"
            val = (district.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
        await message.author.send("Enter your Address")
        
        try:
            address = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET address = %s WHERE userId = %s"
            val = (address.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
        await message.author.send("Enter your age")
        
        try:
            age = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET age = %s WHERE userId = %s"
            val = (age.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
        await message.author.send("Enter your ID Type (adhaar, election id, pan card...)")
        
        try:
            idType = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET idType = %s WHERE userId = %s"
            val = (idType.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
        await message.author.send("Enter your ID Number")
        
        try:
            idNo = await client.wait_for('message', check=check, timeout=60000)

            sql = "UPDATE users SET idNo = %s WHERE userId = %s"
            val = (idNo.content,message.author.id)
            cursor.execute(sql, val)

            db.commit()
            await message.author.send("✅ Done!!" + "\n" + "Enter 'myInfo' to know your details.");
        except asyncio.TimeoutError:
            return await message.channel.send(f'Sorry, you took too long.')
        
client.run(DISCORD_TOKEN)
