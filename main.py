import discord
from discord.commands import Option
from discord.ext import tasks

from datetime import date, datetime, timedelta
import json
import asyncio

from motor import motor_asyncio as motor

bot = discord.Bot()

data = []

def time_to_int(dt):
    basetime = datetime(2000,1,1,hour=0,second=0,microsecond=0,tzinfo=None)
    diff = dt - basetime
    return int(diff.total_seconds())

@bot.slash_command(guild_ids=[929200570093424660], name="set")
async def set_command(
    ctx,
    sec: Option(int, '通知する秒数'),
    message: Option(str, '通知するときのコマンドを入力', required=False, default='メッセージなし'),
):
    await ctx.respond(f'{sec}秒後に通知します。', ephemeral=False)
    time = datetime.now() + timedelta(seconds=sec)
    data.append({
        'guild_id': ctx.guild.id,
        'channel_id': ctx.channel.id,
        'author_id': ctx.author.id,
        'datetime': time_to_int(time),
        'message': message,
    })
    print(data)

    #await ctx.channel.send(f'{ctx.author.mention} {sec}秒経過しました。')

@tasks.loop(seconds=1)
async def loop():
    await bot.wait_until_ready()
    for item in data:
        if item['datetime'] <= time_to_int(datetime.now()):
            guild = await bot.fetch_guild(item['guild_id'])
            channel = await bot.fetch_channel(item['channel_id'])
            await channel.send(f'<@{item["author_id"]}> {item["message"]}')
            data.remove(item)


with open("./config.json", 'r', encoding='utf-8') as f:
    config = json.load(f)
    token = config['token']

dbclient = motor.AsyncIOMotorClient(config['mongodb'])
db = dbclient["myFirstDatabase"]
profiles_collection = db.profiles

loop.start()
bot.run(token)
