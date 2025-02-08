import discord
from discord.ext import commands

from dotenv import load_dotenv
import os

load_dotenv()  # Загружает переменные из .env

TOKEN = os.getenv('DISCORD_TOKEN')  # Читает значение переменной DISCORD_TOKEN
print(TOKEN)  # Для проверки

# Укажи ID каналов
SUGGESTION_CHANNEL_ID = 1337846810806456431  # #предложить-пост
MODERATION_CHANNEL_ID = 1337846888673841276  # #ожидание-одобрения
APPROVED_CHANNEL_ID = 1337846989093601280  # #одобренные-посты

# Настрой бота
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Отключаем стандартную команду help
bot.remove_command("help")


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")


@bot.event
async def on_message(message):
    # Игнорируем сообщения от бота
    if message.author.bot:
        return

    # Проверяем, что сообщение в канале предложений
    if message.channel.id == SUGGESTION_CHANNEL_ID:
        await message.delete()  # Удаляем сообщение из общего доступа

        # Отправляем в канал модерации
        mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
        sent_message = await mod_channel.send(
            f"📩 Новое предложение от {message.author.mention}:\n\n{message.content}"
        )

        # Добавляем реакции для модераторов
        await sent_message.add_reaction("✅")  # Одобрить
        await sent_message.add_reaction("❌")  # Отклонить


@bot.event
async def on_raw_reaction_add(payload):
    """ Обработчик реакции модератора (✅ или ❌) """
    if payload.user_id == bot.user.id:
        return  # Бот не реагирует сам на себя

    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id)

    # Получаем канал модерации
    mod_channel = bot.get_channel(MODERATION_CHANNEL_ID)
    approved_channel = bot.get_channel(APPROVED_CHANNEL_ID)

    if not mod_channel or not approved_channel:
        return

    message = await mod_channel.fetch_message(payload.message_id)
    if not message:
        return

    # Проверяем, что реакция от модератора
    if str(payload.emoji) == "✅":
        # Отправляем сообщение в одобренные посты
        await approved_channel.send(f"✅ **Одобрено!**\n{message.content}")
        await message.delete()  # Удаляем из канала модерации

    elif str(payload.emoji) == "❌":
        # Удаляем из модерации, ничего не публикуя
        await message.delete()


bot.run(TOKEN)