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

# cog for the help & hello command.
class Help(ext.Cog):

    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        
    async def add_brief_command_info(self, ctx, embed, command):
        name_string = f"{self.emojis[command.extras['emoji']]}  {command.name}"
        for argument in command.extras["args"].keys():
            name_string += f" <{argument}>"

        embed.add_field(name=name_string,value=f"```{command.brief}```\u200b\n", inline=False)
        return embed

    async def add_big_command_info(self, ctx, embed, command):

        me = self.client.user
        mention="/"
        cmd = f"/{command.name}"
        try:
            mention = me.mention
            cmd = f"{me.mention} {command.name}"
        except:
            pass
        
        name_string = cmd
        for argument in command.extras["args"].keys():
            arg = f"<{argument}>"
            info = command.extras['args'][argument]
            
            if "(Optional)" in info:
                info = info.replace("(Optional)","")
                arg = f"(Optional) {arg}"
                
            name_string += f"\n{arg} : {info}\n"

        embed_desc = f"\n\u200b\n**{name_string}**\n\u200b\n{command.description}\n\u200b".replace("<@mention_me>",f"{mention}")
        embed.description=embed_desc
        embed = await stw.add_requested_footer(ctx,embed)
        return embed

    async def add_default_page(self, ctx, embed, embed_colour):
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"), description=f"\u200b\n**To use a command mention the bot, then type the name and arguments after e.g:** {await stw.mention_string(self.client, 'reward 7')}\n\u200b\n\u200b")
        
        embed = await stw.add_requested_footer(ctx,embed)


        for command in self.client.commands:
            embed = await self.add_brief_command_info(ctx, embed, command)
        return embed

    async def help_embed(self, ctx, command):
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "Help", "info"), description="\u200b")
        names = map(lambda command: command.name, self.client.commands)

        if command not in names:
            embed = await self.add_default_page(ctx, embed, embed_colour)
        else:
            for command_retrieved in self.client.commands:
                if command_retrieved.name == command:
                    embed = await self.add_big_command_info(ctx, embed, command_retrieved)
        
        return embed

    async def select_options_commands(self):
        options = []
        
        for command in self.client.commands:
            options.append(
                discord.SelectOption(label=command.name,value=command.name,description=command.brief,emoji=self.emojis[command.extras['emoji']],default=False)
            )

        return options

    async def help_command(self, ctx, command, slash = False):
        embed = await self.help_embed(ctx, command)
        help_options = [discord.SelectOption(label="all",value="main_menu",description="Display a brief amount of info about every command",emoji=self.emojis['blueinfo'], default= False)]
        help_options += await self.select_options_commands()

        class HelpView(discord.ui.View):
            def __init__(self, author):
                super().__init__()
                self.author = author
                
            async def interaction_check(self, interaction):
                return self.author == interaction.user
    
            @discord.ui.select(
                placeholder="Select a help page here",
                min_values=1,
                max_values=1,
                options=help_options,
                )
            async def selected_option(self, select,interaction):
                embed=await self.help.help_embed(ctx, select.values[0])
                await interaction.response.edit_message(embed=embed, view=self)

        help_view = HelpView(author=ctx.author)
        help_view.help = self
        
        await stw.slash_send_embed(ctx, slash, embed, help_view)




    @ext.command(name='help',
                aliases=['halp', 'holp', 'how', 'hel', 'h', '?', 'helpp', 'huh'],
                extras={'emoji':"info", 'args':{'command': "A command to display a more detailed information guide of (Optional)"}},
                brief="Displays commands info, only the author may use the select",
                description="A command which displays information about all other commands, helpful to understand the usage of each command and their purpose.")
    async def help(self, ctx, command = None):
        await self.help_command(ctx, command)

    @ext.command(name="rlcg",
                 aliases=[],
                extras={'emoji':"info", 'args':{'command': "A command to display a more detailed information guide of (Optional)"}},
                brief="Displays commands info",
                description="A command which displays information about all other commands, helpful to understand the usage of each command and their purpose.")
    async def reload_cog(self, ctx, cog):
        self.client.reload_extension(f'ext.{cog}')

    @ext.command(name="lcg",
                 aliases=[],
                extras={'emoji':"info", 'args':{'command': "A command to display a more detailed information guide of (Optional)"}},
                brief="Displays commands info",
                description="A command which displays information about all other commands, helpful to understand the usage of each command and their purpose.")
    async def load_cog(self, ctx, cog):
        self.client.load_extension(f'ext.{cog}')                  

    @slash_command(name='help',      
             description='Displays information about other commands',
                   guild_ids=stw.guild_ids)
    async def slashhelp(
            self,
            ctx: discord.ApplicationContext,
            command: Option(str, "Choose a command to view help of", choices=["help","kill","auth","daily","info","reward"]) = None):

        await self.help_command(ctx, command, True)



    #hello command
       
    async def hello_command(self, ctx):
        embed_colour = self.client.colours["generic_blue"]
        embed = discord.Embed(colour=embed_colour, title=await stw.add_emoji_title(self.client, "STW Daily", "calendar"),
                              description=f"""\u200b\nHello! I'm Save The World Daily, A bot which collects your Fortnite: Save The World daily rewards via Discord. [If you have any questions or issues join us here]({self.client.config["support_url"]}), [If you want to invite the bot press here!](https://tinyurl.com/stwdailyinvite)\n\u200b""")

        embed = await stw.add_requested_footer(ctx,embed)
    
        embed.add_field(name="To check out my commands use:",value=await stw.mention_string(self.client, "help") + "\n\u200b\n[**To view the privacy policy and terms of use click here**](https://sites.google.com/view/stwdaily/legal-info)\n\u200b")
        embed.add_field(name="Disclaimer:",value="Portions of the materials used are trademarks and/or copyrighted works of Epic Games, Inc. All rights reserved by Epic. This material is not official and is not endorsed by Epic.\n\u200b", inline=False)
        embed = await stw.set_thumbnail(self.client, embed, "calendar") 
        await ctx.channel.send(embed=embed)
    
    # the harder you climb the harder you fall
    @ext.Cog.listener()
    async def on_message(self, message):
        self_id = self.client.user.id

        # simple checker to see if the hello command should be triggered or not
        if self_id in message.raw_mentions:
            stripped_message = await stw.strip_string(message.content)

            if len(stripped_message) == len(str(self_id)):
                await self.hello_command(message)
                return


def setup(client):
    client.add_cog(Help(client))
