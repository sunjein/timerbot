import discord
from discord.commands import Option
from discord.ext import tasks

from datetime import date, datetime, timedelta
import json
import asyncio

from motor import motor_asyncio as motor

bot = discord.Bot()
data = []

data_ready = False

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
    if not data_ready:
        return await ctx.respond(f'申し訳ございません。再起動の処理中です。しばらくお待ちしてからもう一度試してください。', ephemeral=True)

    await ctx.respond(f'{sec}秒後に通知します。', ephemeral=False)
    time = datetime.now() + timedelta(seconds=sec)
    time = time_to_int(time)
    data.append({
        'guild_id': ctx.guild.id,
        'channel_id': ctx.channel.id,
        'author_id': ctx.author.id,
        'datetime': time,
        'message': message,
    })

    await timers_collection.insert_one({
        'guild_id': ctx.guild.id,
        'channel_id': ctx.channel.id,
        'author_id': ctx.author.id,
        'datetime': time,
        'message': message,
    })

@tasks.loop(seconds=1)
async def loop():
    await bot.wait_until_ready()
    for item in data:
        if item['datetime'] <= time_to_int(datetime.now()):
            guild = await bot.fetch_guild(item['guild_id'])
            channel = await bot.fetch_channel(item['channel_id'])
            await channel.send(f'<@{item["author_id"]}> {item["message"]}')
            data.remove(item)
            result = await timers_collection.delete_one({
                'guild_id': item['guild_id'],
                'channel_id': item['channel_id'],
                'author_id': item['author_id'],
                'datetime': item['datetime'],
                'message': item['message'],
            })
            if result.deleted_count == 0:
                print("データが見つかりませんでした。")

@bot.event
async def on_ready():
    global data_ready, data
    data = await timers_collection.find().to_list(length=None)
    data_ready = True

with open("./config.json", 'r', encoding='utf-8') as f:
    config = json.load(f)
    token = config['token']

dbclient = motor.AsyncIOMotorClient(config['mongodb'])
db = dbclient["myFirstDatabase"]
timers_collection = db.timers

loop.start()
bot.run(token)