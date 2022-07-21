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

# cog for the research related commands.
class Research(ext.Cog):
    
    def __init__(self, client):
        self.client = client
        self.emojis = client.config["emojis"]
        self.token_guid_research = "Token_collectionresource_nodegatetoken01"
        self.item_templateid_research = "Token:collectionresource_nodegatetoken01"
    def check_for_research_points_item(self, query_json):

        items = query_json['profileChanges'][0]['profile']['items']
        
        for key, item in items.items():
            try:
                if item['templateId'] == f"{self.item_templateid_research}":
                    return item
            except: pass

        return None
    
    def check_for_research_guid_key(self, query_json):

        items = query_json['profileChanges'][0]['profile']['items']
        for key, item in items.items():
            try:
                if item['templateId'] == f"CollectedResource:{self.token_guid_research}":
                    return key
            except: pass

        return None
        
    async def research_command(self, ctx, slash, authcode, auth_opt_out):
        error_colour = self.client.colours["error_red"]
        succ_colour = self.client.colours["success_green"]
        yellow = self.client.colours["warning_yellow"]
        
        auth_info = await stw.get_or_create_auth_session(self.client, ctx, "daily", authcode, slash, auth_opt_out, True)
        if auth_info[0] == False:
            return

        final_embeds = []

        ainfo3 = ""
        try: ainfo3 = auth_info[3]
        except: pass


        # what is this black magic???????? i totally forgot what any of this is and how is there a third value to the auth_info??
        # okay i discovered what it is, its basically the "welcome whoever" embed that is edited
        if ainfo3 != "logged_in_processing" and auth_info[2] != []:
            final_embeds = auth_info[2]

        # CRS stands for "current_research_statistics"
        current_research_statistics_request = await stw.profile_request(self.client, "query", auth_info[1])
        json_response = await current_research_statistics_request.json()

        try:
            error_code = json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            current_levels = json_response['profileChanges'][0]['profile']['stats']['attributes']['research_levels']

            # Find research guid to post too required for ClaimCollectedResources json
            research_guid_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_guid_key, json_response))
            print(research_guid_check)
            if research_guid_check[0] == None:
                error_code = "errors.stwdaily.failed_guid_research"
                support_url = self.client.config["support_url"]
                acc_name = auth_info[1]["account_name"]
                embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
                final_embeds.append(embed)
                await stw.slash_edit_original(auth_info[0], slash, final_embeds)
                return

            research_guid = research_guid_check[0]
            pass

        current_research_statistics_request = await stw.profile_request(self.client, "resources", auth_info[1], json={ "collectorsToClaim": [research_guid]  })
        json_response = await current_research_statistics_request.json()

        try:
            error_code = json_response["errorCode"]
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            print(json_response)
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
        except:
            pass

        # Get total points
        total_points_check = await asyncio.gather(asyncio.to_thread(self.check_for_research_points_item, json_response))
        print(total_points_check)
        if total_points_check[0] == None:
            error_code = "errors.stwdaily.failed_total_points"
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return

        total_points = total_points_check[0]
            
        # Get CollectedResourceResult feedback
        research_feedback, check = json_response["notifications"], False
        
        for notification in research_feedback:
            if notification["type"] == "collectedResourceResult":
                research_feedback, check =notification, True
                break
            
        if not check:
            error_code = "errors.stwdaily.failed_get_collected_resource_type"
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return
            
        available_research_items, check = research_feedback["loot"]["items"], False
        for research_item in available_research_items:
            try:
                if research_item["itemType"] == self.item_templateid_research:
                    research_item, check = research_item, True
                    break
            except:
                pass

        if not check:
            error_code = "errors.stwdaily.failed_get_collected_resource_item"
            support_url = self.client.config["support_url"]
            acc_name = auth_info[1]["account_name"]
            embed = await stw.post_error_possibilities(ctx, self.client, "research", acc_name, error_code, support_url)
            final_embeds.append(embed)
            await stw.slash_edit_original(auth_info[0], slash, final_embeds)
            return
        
        await ctx.send(f"{research_item} {total_points} {current_levels}")
        
    @ext.command(name='research',
                aliases=['res', 'rsearch', 'reach','rese','rse','reasearch','resaesaer'],
                extras={'emoji':"research_point", "args":{'authcode':'The authcode to start an authentication session with if one does not exist, if an auth session already exists this argument is optional (Optional)', 'opt-out':'Any value inputted into this field will opt you out of the authentication session system when you enter the authcode for this command (Optional)'}},
            brief="Allows you to distribute and claim your research points (auth req.)",
            description="""This command allows you to claim your Fortnite: Save The World research points for the FORT (Fortification, Offence, Resistance, Tech) stats, You can view how many currently available research points you have and then distribute them to your choosing through the interface provided by the embed.
                """)
    async def research(self, ctx, authcode='', optout = None):

        if optout != None:
            optout = True
        else:
            optout = False
        
        await self.research_command(ctx, False, authcode, not optout)

    @slash_command(name='research',
             description="Allows you to distribute and claim your research points (auth req.)",
             guild_ids=stw.guild_ids)
    async def slashresearch(self, ctx: discord.ApplicationContext,
                            token: Option(str, "The authcode to start an authentication session with if one does not exist, else this is optional")="",
                             auth_opt_out: Option(bool, "Opt Out of Authentication session")=True,):
        await self.research_command(ctx, True, token, not auth_opt_out)
    
def setup(client):
    client.add_cog(Research(client))
