import psycopg2
import os
import discord
from discord.ext import commands
from time import sleep
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
client = discord.Client()


@client.event
async def on_message(message):
    if message.guild:
        if not str('954448309576155167') in str(message.author.id) and str(message.channel.id) == '796211184684236860':
            if message.content == '!!help':
                await message.channel.send(getHelpMessage())
            elif message.content == '!!info':
                await message.channel.send(getInfoMessage())
            elif message.content == '!!check':
                result = readDatabase('check', message.author.id, message.content, message.author.name)
                if len(result) > 0:
                    await message.channel.send('Your address is set: ' + str(result[0][0]))
                    sleep(10)
                    await message.channel.purge(limit=1000000)
                    await message.channel.send(getHelpMessage())
                else:
                    await message.channel.send('No address set yet.')
            elif str('!!set') in message.content:
                result = readDatabase('check', message.author.id, message.content, message.author.name)
                token = message.content.replace('!!set ', '')
                if len(result) == 1:
                    await message.channel.send('Sorry! There is already set an address for this user.')
                    sleep(10)
                    await message.channel.purge(limit=1000000)
                    await message.channel.send(getHelpMessage())
                else:
                    if len(token) > 25:
                        await message.channel.purge(limit=1)
                        readDatabase('set', message.author.id, token, message.author.name)
                        await message.channel.send('Address is set! Use **!!check** to verify!')
                        sleep(7)
                        await message.channel.purge(limit=1000000)
                        await message.channel.send(getHelpMessage())
                    else:
                        await message.channel.send('Not a valid token address!')
            elif str('!!update') in message.content:
                result = readDatabase('check', message.author.id, message.content, message.author.name)
                token = message.content.replace('!!update ', '')
                if len(result) == 0:
                    await message.channel.send('Sorry! There is no address for this account yet.')
                else:
                    if len(token) > 25:
                        readDatabase('update', message.author.id, token, message.author.name)
                        await message.channel.send('Address is updated! Use **>>check** to verify!')
                        sleep(5)
                        await message.channel.purge(limit=1000000)
                        await message.channel.send(getHelpMessage())
                    else:
                        await message.channel.send('Not a valid token address!')


def getHelpMessage():
    welcomeMessage = f"\nWelcome to the Whitelist bot!\n" \
                     "Example: !!set 0xCD90d9bA0060937c442C5560055a785Ed428E1F9\n" \
                     "**Commands**\n" \
                     "```!!info                  : why is this BOT here?\n" \
                     "!!check                 : will return the current address saved for your current discord ID\n" \
                     "!!set <address>         : will set your adress\n" \
                     "!!update <address>      : will update your address\n```"

    return welcomeMessage


def getInfoMessage():
    infoMessage = f"```This bot is made to set all whitelist addresses so you can get access to our presale of the Vananessiea NFT collection.\n" \
                  "If you don't set a valid address, you will not be able to mint NFT's in our presale.```"
    return infoMessage


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


def readDatabase(type, value, value2,value3):
    global connection
    try:
        connection = psycopg2.connect(user=os.getenv('USER'),
                                      password=os.getenv('PASSWORD'),
                                      host=os.getenv('HOST'),
                                      port=5432,
                                      database=os.getenv('DATABASE'),
                                      sslmode='require',
                                      )
        cursor = connection.cursor()

        result = ''

        if type == 'check':
            query = 'SELECT address, name FROM public.whitelists w where name = \'' + str(value) + '\''
            cursor.execute(query)
            result = cursor.fetchall()

        if type == 'set':
            postgres_insert_query = """ INSERT INTO public.whitelists(address, name, nickname) VALUES (%s, %s, %s)"""
            record_to_insert = (value2, value ,value3)
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            result = cursor.rowcount
        if type == 'update':
            postgres_insert_query = """ UPDATE public.whitelists SET address=(%s), name=(%s) WHERE name = (%s);"""
            record_to_insert = (value2, value, str(value))
            cursor.execute(postgres_insert_query, record_to_insert)
            connection.commit()
            result = cursor.rowcount

        print('res', result)
        return result


    except (Exception, psycopg2.Error) as error:
        print(error)
        return str(error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()


client.run(TOKEN)
