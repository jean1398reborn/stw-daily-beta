import asyncio
import aiohttp

import math
import random
import json
import re
import os
import sys
import psutil
import datetime
import time
import stwutil as stw
import items

import discord
import discord.ext.commands as ext
from discord import Option
from discord.commands import (  # Importing the decorator that makes slash commands.
    slash_command,
)

# cog for the info related commands.
class Information(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]


    async def info_command(self, ctx, slash = False):
        try:
            osgetlogin = os.getlogin()
        except:
            osgetlogin = 'Not Available'

        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(title=await stw.add_emoji_title(self.client, "Information", "blueinfo"), description="\u200b", colour=embed_colour)
        embed.add_field(name='Host statistics:', value=f'```OS name: {os.name}\nCPU count: {os.cpu_count()}\n'
                                                       f'Working dir: {os.getcwd()}\nLogin: {osgetlogin}\n'
                                                       f'CPU usage: {psutil.cpu_percent()}%\n'
                                                       f'CPU Freq: {int(psutil.cpu_freq().current)}mhz\nRAM Usage:\nTotal: '
                                                       f'{psutil.virtual_memory().total // 1000000}mb\nUsed: '
                                                       f'{psutil.virtual_memory().used // 1000000}mb\nFree: '
                                                       f'{psutil.virtual_memory().free // 1000000}mb\nUtilisation: '
                                                       f'{psutil.virtual_memory().percent}%```\u200b', inline=False)

        shard_ping = "Not Available"
        shard_name = "Not Available"
        shard_id = "Not Available"
        shard_count = "Not Available"
        try:
            shards = str(len(self.client.shards))
            shard_id = ctx.guild.shard_id
            shard_name = await stw.retrieve_shard(self.client, shard_id)
            shard_info = self.client.get_shard(shard_id)
            shard_ping = '{0}'.format(int(shard_info.latency * 100)) + ' ms'
            shard_id = str(shard_info.id + 1)
        except:
            pass
        

        embed.add_field(name='Bot statistics:', value=f'```'
                        f'Shard: {shard_name}\n'
                        f'Shard Id: {shard_id}\n'
                        f'Total Shards: {shards}\n'
                        f'Guild Count: {len(self.client.guilds)}```\u200b')


        websocket_ping = '{0}'.format(int(self.client.latency * 100)) + ' ms'
        embed.add_field(name='Latency Information:', value=f'```Websocket: {websocket_ping}\n'
                    f'Shard: {shard_ping}\n'
                    f'Actual: ...```\u200b', inline=False)
        embed = await stw.add_requested_footer(ctx,embed)
        embed = await stw.set_thumbnail(self.client, embed, "info") 

        before = time.monotonic()
        msg = await stw.slash_send_embed(ctx,slash,embed)
        ping = (time.monotonic() - before) * 1000
        embed.set_field_at(-1, name='Latency Information:', value=f'```Websocket: {websocket_ping}\n'
                    f'Shard: {shard_ping}\n'
                    f'Actual: {int(ping)}ms```\u200b', inline=False)

        await asyncio.sleep(4)
        await stw.slash_edit_original(msg, slash, embed)

    @ext.command(name='info',
                aliases=['inf', 'ifno', 'inof','nifo','information','le_bot_stuf','blinding-lights'],
                extras={'emoji':"hard_drive", "args":{}},
                brief="Get information about the bot and this shard",
                description="This command displays information both about the shard and information about the bots hosting service along with latency. not really useful for the end user.")
    async def info(self, ctx):
        await self.info_command(ctx)

    @slash_command(name='info',
             description="Get information about the bots latency and hosting service for this shard.",
             guild_ids=stw.guild_ids)
    async def slashinfo(self, ctx):
        await self.info_command(ctx, True)
    
def setup(client):
    client.add_cog(Information(client))
