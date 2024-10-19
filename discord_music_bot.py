import discord
import os
import asyncio
import yt_dlp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    queues = {}
    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -filter:a "volume=0.25"'
    }

    async def play_next_song(guild_id):
        if guild_id in queues and queues[guild_id]:
            url = queues[guild_id].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            if guild_id in voice_clients:
                voice_clients[guild_id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(guild_id), bot.loop))
                text_channel = discord.utils.get(bot.get_all_channels(), id=voice_clients[guild_id].channel.id)
                if text_channel:
                    await text_channel.send(f"Now playing: {data['title']}")
        else:
            if guild_id in voice_clients:
                await voice_clients[guild_id].disconnect()
                del voice_clients[guild_id]
            text_channel = discord.utils.get(bot.get_all_channels(), id=voice_clients[guild_id].channel.id)
            if text_channel:
                await text_channel.send("Queue is empty.")

    @bot.event
    async def on_ready():
        print(f'{bot.user} is now jamming')
        try:
            synced = await bot.tree.sync()  # Syncing commands globally
            print(f"Synced {len(synced)} commands globally")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    @bot.tree.command(name="play", description="Play a song from a YouTube URL")
    async def play(interaction: discord.Interaction, url: str):
        guild_id = interaction.guild.id
        if interaction.user.voice:
            channel = interaction.user.voice.channel

            if guild_id not in queues:
                queues[guild_id] = []
            queues[guild_id].append(url)

            if guild_id not in voice_clients or not voice_clients[guild_id].is_connected():
                voice_client = await channel.connect()
                voice_clients[guild_id] = voice_client

            if not voice_clients[guild_id].is_playing():
                await play_next_song(guild_id)

            try:
                await interaction.response.send_message(f"Added to queue: {url}")
            except discord.HTTPException as e:
                print(f"Failed to send message: {e}")

        else:
            await interaction.response.send_message("You need to be in a voice channel to play a song.")

    @bot.tree.command(name="pause", description="Pause the current song")
    async def pause(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            voice_clients[guild_id].pause()
            await interaction.response.send_message("Playback paused.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    @bot.tree.command(name="resume", description="Resume the current song")
    async def resume(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_paused():
            voice_clients[guild_id].resume()
            await interaction.response.send_message("Playback resumed.")
        else:
            await interaction.response.send_message("Playback is not paused.")

    @bot.tree.command(name="stop", description="Stop the current song and disconnect")
    async def stop(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in voice_clients:
            voice_clients[guild_id].stop()
            await voice_clients[guild_id].disconnect()
            if guild_id in queues:
                queues[guild_id] = []
            del voice_clients[guild_id]
            await interaction.response.send_message("Playback stopped and disconnected.")
        else:
            await interaction.response.send_message("No song is currently playing.")

    vote_counts = {}

    @bot.tree.command(name="voteskip", description="Vote to Skip")
    async def voteskip(interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in voice_clients and voice_clients[guild_id].is_playing():
            song_url = queues[guild_id][0].voteskip()

            if interaction.user.id in vote_counts.get(song_url, []):
                await interaction.response.send_message("You've Already Voted to skip the song")
                return

            vote_counts.setdefault(song_url, []).append(interaction.user.id)

            if len(vote_counts[song_url]) >= len(interaction.channel.members) / 2:
                voice_clients[guild_id].stop()
                await play_next_song(guild_id)
                await interaction.response.send_message(f"Song skipped due to majority vote.")
                del vote_counts[song_url]  
            else:
                needed_votes = int(len(interaction.channel.members) / 2) + 1
                current_votes = len(vote_counts[song_url])
                await interaction.response.send_message(f"{current_votes} out of {needed_votes} votes needed to skip.")
        else:
            await interaction.response.send_message("No song is currently playing")

    bot.run("enter ur discord token here")

# Run the bot
run_bot()
