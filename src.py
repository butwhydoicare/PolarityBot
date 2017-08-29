#import shit

from datetime import *
from discord import utils
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio, math, random, os, sys, socket, base64
import urllib.parse
from mods.checks import embed_perms, cmd_prefix_len, find_channel
from mods.r34api import get_pics_from_page 
from mods.nsfw import Nsfw
from mods.members import Members


# define external functions

def encrypt(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decrypt(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)




#define extra classes

if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = '*{0.title}* uploaded by {0.uploader} and requested by {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [length: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)

class VoiceState:
    def __init__(self, client):
        self.current = None
        self.voice = None
        self.client = client
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set() # a set of user_ids that voted
        self.audio_player = self.client.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.client.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.client.send_message(self.current.channel, 'Now playing ' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


#Command Category Classes (Cogs)

class Administrators:
    """ Administrator commands. Only server Admins/Mods can use these """
    def __init__(self, client):
        self.client = client


    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def softban(self, ctx, member:discord.Member):
        """ Softban a Member """
        role = discord.utils.get(ctx.message.server.roles, name="softbanned")
        await self.client.add_roles(member, role)
        await self.client.say("**%s** has been softbanned" % member.name)


    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def unsoftban(self, ctx, member:discord.Member):
        """ Un-Softban a Member """
        role = discord.utils.get(ctx.message.server.roles, name="softbanned")
        await self.client.remove_roles(member, role)
        await self.client.say("**%s** has been unsoftbanned" % member.name)


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, member:discord.Member):
        """ Ban a Member """
        await self.client.ban(member)

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member:discord.Member):
        """ Unban a Banned Member """
        await self.client.unban(ctx.message.server, member)
        await self.client.say("Unbanned **%s** from **%s**!" % (member.name, ctx.message.server.name))


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, member:discord.Member):
        """ Kick a member """
        await self.client.kick(member)

    @commands.command(pass_context=True)
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, limit:int):
        """Purges 500 or less messages from the target channel"""
        def is_me(m):
            return m.author == m.author
                                
        deleted = await self.client.purge_from(ctx.message.channel, limit=limit, check=is_me)
        await self.client.send_message(ctx.message.channel,'Deleted {} Message(s)'.format(len(deleted)))


class Creators:
    """ Creator commands. Only Creators can use these """
    def __init__(self, client):
        self.client = client


    @commands.command(pass_context=True)
    async def destroy(self, ctx):
        """ turn the bot off """
        if ctx.message.author.id == '244531479462412288':
            await self.client.say("**Goodbye!**")
            await self.client.logout()
        else:
            await self.client.say("**Sorry, you must be a Creator to use this command**")


class Members:
    """ Member commands. No permissions needed """
    def __init__(self, client):
        self.client = client
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']

    @commands.command(pass_context=True)
    async def info(self, ctx, member:discord.Member):
        """ Shows information about a Member """
        
        if member.game == None:
            memgame = "Nothing"
        em = discord.Embed()
        em.set_thumbnail(url="%s" % member.avatar_url)
        em.add_field(name="Name", value="%s" % member.name)
        em.add_field(name="ID", value=member.id)
        em.add_field(name="Join Date", value=member.joined_at, inline=False)
        em.add_field(name="Status", value=member.status)
        em.add_field(name="Now Playing", value=memgame)
        em.add_field(name="Highest Role", value=member.top_role.name)
        em.add_field(name='Account Created', value=member.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
        await self.client.say(embed=em)


    @commands.command()
    async def ping(self):
        """ Shows how long it takes to reply """
        t1 = datetime.now()
        await self.client.say("**Pong!**")
        t2 = datetime.now()
        t3 = t2 - t1
        await self.client.say("**Replied in %s**" % t3)


    @commands.command(pass_context=True, aliases=['8ball'])
    async def ball8(self, ctx, *, msg: str):
        """Let the 8ball decide your fate. Ex: ;8ball Am I Dead??"""
        answer = random.randint(0, 19)
        if embed_perms(ctx.message):
            if answer < 10:
                color = 0x008000
            elif 10 <= answer < 15:
                color = 0xFFD700
            else:
                color = 0xFF0000
            em = discord.Embed(color=color)
            em.add_field(name='\u2753 Question', value=msg)
            em.add_field(name='\ud83c\udfb1 8ball', value=self.ball[answer], inline=False)
            await self.client.send_message(ctx.message.channel, content=None, embed=em)
            await self.client.delete_message(ctx.message)
        else:
            await self.client.send_message(ctx.message.channel, '\ud83c\udfb1 ``{}``'.format(random.choice(self.ball)))

    @commands.command(description='Choice System')
    async def choose(self, *choices : str):
        """Chooses between multiple choices."""
        await self.client.say(random.choice(choices))


    @commands.command(pass_context=True)
    async def lmg(self, ctx, *, msg: str):
        """Creates a lmgtfy link. Ex: ;lmg how to make a bot."""
        lmgtfy = 'http://lmgtfy.com/?q='
        await self.client.send_message(ctx.message.channel, self.client.client_prefix + lmgtfy + urllib.parse.quote_plus(msg.lower().strip()))
        await self.client.delete_message(ctx.message)


    @commands.command()
    async def say(self, *left: str):
        """say something (I'm giving up on you)"""
        return await self.client.say("%s" % left)

    @commands.command()
    async def harpoonish(self, *left: str):
        """HARPOONISHMENT"""
        async def aaa():
            try:
                e = discord.Embed()
                e.set_image(url="https://raw.githubusercontent.com/active9/harpoon/master/files/default.png")
                e.set_footer(text="%s" % left)
                for x in range(10):
                    return await self.client.say(embed = e)
                    await asyncio.sleep(1)
            except TypeError:
                await self.client.say("Sorry there was a type error.")
        await aaa()


    @commands.command()
    async def pyx(self, *args):
            """Gives a Pretend You're Xzyzzy Link"""
            return await self.client.say('http://pyx-2.pretendyoure.xyz/zy/game.jsp#game=%s' % random.randint(0,50))


    @commands.command()
    async def noods(self):
        """Sends noods"""
        noodlist = ['http://i.imgur.com/8fpiqyX.gifv','http://i.imgur.com/XB4S1cq.jpg','http://i.imgur.com/eH0kX2r.gifv']
        return await self.client.say(random.choice(noodlist))


    @commands.command()
    async def massenc(self, key:str,word:str):
        """Sooper strong encryption"""
        enc1 = encrypt(key,word)
        enc2 = encrypt(key,enc1)
        enc3 = encrypt(key,enc2)
        return await self.client.say(encrypt(key,enc3))

    @commands.command()
    async def massdec(self, key:str,encryptedword:str):
        """Sooper strong decryption"""
        dec1 = decrypt(key,encryptedword)
        dec2 = decrypt(key,dec1)
        dec3 = decrypt(key,dec2)
        return await self.client.say(decrypt(key,dec3))



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

class Music:
    """ Music commands. Works in multiple servers at once. """
    def __init__(self, client):
        self.client = client
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.client)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.client.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.client.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.command(pass_context=True, no_pm=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.client.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.client.say('This is not a voice channel...')
        else:
            await self.client.say('Ready to play audio in ' + channel.name)

    @commands.command(pass_context=True, no_pm=True)
    async def summon(self, ctx):
        """Summons the client to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.client.say('You are not in a voice channel.')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.client.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song : str):
        """Plays a song.
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await self.client.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.client.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx, value : int):
        """Sets the volume of the currently playing song."""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.client.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.client.say('Not playing any music right now...')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.client.say('Requester requested skipping song...')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 3:
                await self.client.say('Skip vote passed, skipping song...')
                state.skip()
            else:
                await self.client.say('Skip vote added, currently at [{}/3]'.format(total_votes))
        else:
            await self.client.say('You have already voted to skip this song.')

    @commands.command(pass_context=True, no_pm=True)
    async def playing(self, ctx):
        """Shows info about the currently played song."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.client.say('Not playing anything.')
        else:
            skip_count = len(state.skip_votes)
            await self.client.say('Now playing {} [skips: {}/3]'.format(state.current, skip_count))






#define globals and add categories

client = Bot(command_prefix=";")

client.add_cog(Music(client))
client.add_cog(Creators(client))
client.add_cog(Administrators(client))
client.add_cog(Members(client))
client.add_cog(Nsfw(client))
sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)



#events

@client.event
async def on_ready():
	print("Ready!")
	await discord.Client.change_presence(client,game=discord.Game(name=";help"))


@client.event
async def on_member_kick(member):
	await client.send_message(":white_check_mark: **%s** has been kicked from **%s**"%(member,member.server.name))


@client.event
async def on_member_ban(member):
	await client.send_message(":white_check_mark: **%s** has been banned from **%s**"%(member,member.server.name))


@client.event
async def on_member_remove(member):
	await client.send_message("**%s** has left **%s**"%(member,member.server.name))


@client.event
async def on_member_join(member):
	await client.send_message("**%s** has joined **%s**"%(member,member.server.name))
        role = discord.utils.get(member.server.roles, name="Member")
        await client.add_roles(member, role)




#run the client

client.run("TOKEN")
