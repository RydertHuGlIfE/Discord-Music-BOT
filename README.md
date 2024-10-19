# Discord-Music-BOT
This is a Discord Music BOT 
You have to first create a discord bot, get it's secret token and paste it in the bottom of the main code

and using OAuth Authentication, add the bot to the server using administrator Privilages

Discord Music Bot
This Discord bot uses the discord.py and yt-dlp libraries to play music from YouTube URLs in voice channels. It supports commands to play, pause, resume, stop, and vote to skip songs.

Features
Play Music

Command: /play <YouTube URL>

Description: Adds the song to the queue and starts playing if not already playing.

Pause Music

Command: /pause

Description: Pauses the current song.

Resume Music

Command: /resume

Description: Resumes the paused song.

Stop Music

Command: /stop

Description: Stops the current song and disconnects from the voice channel.

Vote to Skip

Command: /voteskip

Description: Starts a vote to skip the current song. If more than half of the users vote to skip, the song is skipped.


Libraries Used
discord.py: For interacting with the Discord API.

yt-dlp: For downloading and extracting audio from YouTube videos.

asyncio: For asynchronous programming.

dotenv: For loading environment variables from a .env file.

here is an image of the bot in action
![image](https://github.com/user-attachments/assets/b0ce3145-b5cb-4361-98bb-94bb14c852e0)

