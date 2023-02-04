# ForumBot
A discord.py bot for [shadowkingdom.org](https://shadowkingdom.org) that periodically 
retrieves new Xenforo forum threads (staff applications, punishment appeals) via RSS 
feed and reports details related to them.

## Dependencies
+ ffmpeg and ffprobe binaries are required in the root folder. [Install them here](https://ffbinaries.com/downloads).
+ For embed navigaton to function, install [embed-pagination](https://github.com/FaddyManatee/embed-pagination).
 


## Preview
### New forum threads found
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061707111479922830/image.png"><br/>

### Weekly open thread reminder
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061710985968238763/image.png"><br/>

### /viewthreads appeal
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061708918868414515/image.png"><br/>

### /viewthreads application
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061707976253132881/image.png"><br/>

## NBS music player
Play note block songs from .nbs files! Add your own .nbs songs into the `nbs` directory.

### /play `songname`
Plays `songname` in your current voice channel.

### /shuffle
Continues to play random songs from the playlist in your current voice channel.

### /songs
Lists the names of all playable songs from the `nbs` directory.

### /stop
Stops the currently playing song or shuffled playlist.

### /leave
Disconnects the bot from its voice channel.
