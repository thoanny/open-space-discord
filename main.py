import os
import discord
import json
import requests
from dotenv import dotenv_values
from discord.ext import commands


config = {
    **dotenv_values(".env"),
    **os.environ,
}

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
MESSAGE_DELETE_AFTER: int = 5


@bot.command(name='sync')
async def twitch_sync(ctx, arg):
    certifie = discord.utils.get(ctx.message.guild.roles, name="Certifié")
    approuve = discord.utils.get(ctx.message.guild.roles, name="Approuvé")
    user = ctx.message.author

    if certifie not in user.roles:
        sync = requests.get(config['SYNC_API'] + arg)
        data = json.loads(sync.text)

        if 'error' in data:
            await ctx.message.channel.send('[Erreur] '+data['error'], delete_after=MESSAGE_DELETE_AFTER*2)
        else:
            await user.add_roles(certifie)
            await user.remove_roles(approuve)
            await user.edit(nick=data['success'])
            await ctx.message.channel.send('Bravo, tu es certifié·e !', delete_after=MESSAGE_DELETE_AFTER)

    else:
        await ctx.message.channel.send('Tu as déjà le rôle certifié !', delete_after=MESSAGE_DELETE_AFTER)

    await ctx.message.delete()


@twitch_sync.error
async def on_twitch_sync_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        message = 'La commande est `!sync [token]` en remplaçant [token] par ton jeton d\'identification.'
    else:
        message = f'[Erreur] {error}'

    await ctx.send(message, delete_after=MESSAGE_DELETE_AFTER*2)
    await ctx.message.delete()


@bot.event
async def on_ready():
    print('L\'agent d\'accueil est opérationnel !')


bot.run(config['DISCORD_BOT_TOKEN'])