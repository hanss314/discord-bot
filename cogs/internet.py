import urllib.parse
import time
import os

from discord.ext import commands
import aiohttp
import discord
import random

XKCD_ENDPOINT = 'https://xkcd.com/{}/info.0.json'


class Internet:
    def __init__(self, bot):
        self.session = aiohttp.ClientSession(loop=bot.loop)

    def __unload(self):
        self.session.close()

    @commands.command(aliases=['adam', 'slice', 'jake'])
    async def dog(self, ctx):
        '''Sends a picture of a random dog'''
        async with self.session.get('http://random.dog/woof.json') as resp:
            json = await resp.json()
            await ctx.send(json['url'])

    @commands.command(aliases=['b1nzy'])
    async def cat(self, ctx):
        '''Sends a picture of a random cat'''
        async with self.session.get('http://random.cat/meow') as resp:
            json = await resp.json()
            await ctx.send(json['file'])

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, query: str):
        '''Google for a query'''
        op = urllib.parse.urlencode({'q': query})
        await ctx.send('https://google.com/search?{}&safe=active'.format(op))

    @commands.command(aliases=['wa', 'alpha', 'wolfram_alpha'])
    async def wolfram(self, ctx, *, query: str):
        '''Search Wolfram|Alpha for a query'''
        op = urllib.parse.urlencode({'i': query})
        await ctx.send('https://www.wolframalpha.com/input/?{}'.format(op))

    @commands.command()
    async def lucky(self, ctx, *, query: str):
        '''I'm feeling lucky. Are you?'''
        op = urllib.parse.urlencode({'q': query})
        async with self.session.get('https://google.com/search?{}&safe=active&&btnI'.format(op)) as resp:
            await ctx.send(resp.url)

    @commands.command(aliases=['haste', 'paste'])
    async def hastebin(self, ctx, *, data: str):
        '''Upload data to https://hastebin.com and return the URL'''
        async with self.session.post('https://hastebin.com/documents', data=data.encode(), headers={'content-type': 'application/json'}) as resp:
            await ctx.send('{0.mention} https://hastebin.com/{}'.format(ctx.author, (await resp.json())["key"]))
            await ctx.message.delete()

    async def post_comic(self, ctx: commands.Context, metadata: 'Dict[str, Any]', comic_number: int):
        embed = discord.Embed(title='#{}'.format(metadata['num']), description=metadata['safe_title'],
                              url='https://xkcd.com/{}/'.format(metadata['num']), colour=0xFFFFFF)
        embed.set_image(url=metadata['img'])
        embed.set_footer(text=metadata['alt'])

        await ctx.send(embed=embed)

    async def fetch_comic_data(self, number=None, *, latest=False):
        async with self.session.get(XKCD_ENDPOINT.format(number if not latest else '')) as resp:
            return await resp.json()

    @commands.group(invoke_without_command=True)
    async def xkcd(self, ctx, *, comic_number: int):
        ''' Shows an XKCD comic by comic number. '''
        latest = await self.fetch_comic_data(latest=True)

        if comic_number > latest['num']:
            await ctx.send('Woah! Steady there tiger! There are only {} comics available. :cry:'.format(latest['num']))
            return
        elif comic_number < 1:
            await ctx.send('"Get strip number {}," they said, "It\'ll be easy."'.format(comic_number))
            return

        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @xkcd.command()
    async def latest(self, ctx):
        ''' Shows the latest XKCD comic. '''
        latest = await self.fetch_comic_data(latest=True)
        await self.post_comic(ctx, latest, latest['num'])

    @xkcd.command()
    async def random(self, ctx):
        ''' Shows a random XKCD comic. '''
        latest = await self.fetch_comic_data(latest=True)
        comic_number = random.randint(1, latest['num'])
        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        '''Views websocket and message send latency.'''
        # Websocket latency
        results = []
        for shard in ctx.bot.shards.values():
            ws_before = time.monotonic()
            await (await shard.ws.ping())
            ws_after = time.monotonic()
            results.append(round((ws_after - ws_before) * 1000))

        # Message send latency
        rtt_before = time.monotonic()
        message = await ctx.send('Ping...')
        rtt_after = time.monotonic()

        rtt_latency = round((rtt_after - rtt_before) * 1000)

        await message.edit(content='WS: **{0} ms**\nRTT: **{1} ms**'.format(', '.join(map(str, results)), rtt_latency))


def setup(bot):
    bot.add_cog(Internet(bot))
