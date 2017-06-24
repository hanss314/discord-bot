'''
This whole file is garbage

You have been warned
'''
import asyncio

from discord.ext import commands
import feedparser
import aiohttp
import discord


class YouTube:
    '''
    Youtube related commands
    '''
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.task = self.bot.loop.create_task(self.youtube_feed())

        # Fake context
        try:
            with open('youtube_ids.txt', 'r') as f:
                self.youtube_ids = f.read().splitlines()
        except IOError:
            # File will be created later
            self.youtube_ids = []

    def __unload(self):
        self.task.cancel()
        self.session.close()

        with open('youtube_ids.txt', 'w') as f:
            f.writelines(self.youtube_ids)

    def __global_check(self, ctx):
        return ctx.guild.id == 282219466589208576 if not ctx.bot.debug else True

    @commands.group(aliases=['yt'])
    async def youtube(self, ctx):
        '''Info about how to get the YouTube role'''
        formatted = await ctx.bot.formatter.format_help_for(ctx, ctx.command)

        for page in formatted:
            ctx.send(page)

    @youtube.command()
    async def on(self, ctx):
        '''Add the YouTube role'''
        role = discord.utils.find(lambda r: r.id == 289942717419749377 or r.name == 'YouTube', ctx.guild.roles)
        ctx.author.add_role(role)

    @youtube.command()
    async def off(self, ctx):
        '''Remove the YouTube role'''
        role = discord.utils.find(lambda r: r.id == 289942717419749377 or r.name == 'YouTube', ctx.guild.roles)
        ctx.author.remove_role(role)

    async def youtube_feed(self):
        await self.bot.wait_until_ready()

        channel = discord.utils.find(lambda c: c.id == 282236775215267860 or c.name == 'announcements',
                                     self.bot.get_all_channels())

        if channel is None:
            return

        role = discord.utils.find(lambda r: r.id == 289942717419749377 or r.name == 'YouTube', channel.guild.roles)

        while True:
            async with self.session.get('https://youtube.com/feeds/videos.xml?user=carykh') as resp:
                data = feedparser.parse(await resp.read())
            videos = data['entries']

            for video in videos:
                href = video['link']

                if href not in self.youtube_ids:
                    self.youtube_ids.append(href)
                    await channel.send('{0.mention} {1} {2}'.format(role, video['title'], href))

            await asyncio.sleep(60)


def setup(bot):
    bot.add_cog(YouTube(bot))