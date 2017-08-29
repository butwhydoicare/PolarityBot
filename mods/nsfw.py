from r34api import get_pics_from_page
from datetime import *
from discord import utils
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio, math, random, os, sys, socket, base64
import urllib.parse



class Nsfw:
    """ NSFW commands. Works in multiple servers at once."""
    def __init__(self,client):
        self.client = client


    @commands.command(pass_context=True)
    async def r34(self, ctx, keyword:str):
        """ Find a Rule34 image through a keyword """
        if 'nsfw' in ctx.message.channel.name.lower():
            list1 = get_pics_from_page("%s" % keyword, 1)
            em = discord.Embed()
            em.set_image(url="%s" % list1[random.randint(0,len(list1))])
            await self.client.say(embed=em)
        else:
            await self.client.say("Sorry, Try in an nsfw channel")


    @commands.command(pass_context=True)
    async def ass(self, ctx):
        """shows asses"""
        if 'nsfw' in ctx.message.channel.name.lower():
            asslist = ['http://i.imgur.com/VBQexlY.jpg','http://i.imgur.com/lBB6D0E.jpg','http://i.imgur.com/wVfvPzw.jpg','https://fat.gfycat.com/ForcefulVigorousKangaroo.gifv','https://pbs.twimg.com/profile_images/455098214493216769/bS417m6J.jpeg','http://openpornreviews.com/wp-content/uploads/2016/12/latina_lesbian_ass-2.jpg','http://x.imagefapusercontent.com/u/ampletits/3126095/1329462009/wallpaper4.jpg']
            return await self.client.say(random.choice(asslist))
        else:
            await self.client.say("Sorry, Try in an nsfw channel")


    @commands.command(pass_context=True)
    async def boobs(self, ctx):
        """shows boobs"""
        if 'nsfw' in ctx.message.channel.name.lower():
            booblist = ['http://xxxadultphoto.com/xxx/big-firm-tits.jpg','http://wallpapers.skins.be/keeley-hazell/keeley-hazell-1024x768-26903.jpg','https://s-media-cache-ak0.pinimg.com/736x/a2/01/6b/a2016bc41744bbc164f8a0c030514bb2--sexy-women-sexy-girls.jpg','http://www.sexiestpicture.com/upload/Pictures/thumbs/girls-tits-sexy_big.jpg','http://hwcdn.voyeurweb.com/albums/3236132/large/5361829-naughty-redhead-looking-for-a-ride.jpg','http://s19.postimg.org/4dfha55wj/kloe_6.jpg']
            return await self.client.say(random.choice(booblist))
        else:
await self.client.say("Sorry, Try in an nsfw channel")
