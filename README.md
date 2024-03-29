# ForumBot
A discord.py bot for [shadowkingdom.org](https://shadowkingdom.org) that periodically 
retrieves new Xenforo forum threads (staff applications, punishment appeals) via RSS 
feed and reports details related to them.

## Dependencies
+ ffmpeg and ffprobe binaries are required in the root folder. [Install them here](https://ffbinaries.com/downloads).
+ For embed navigaton to function, install [embed-pagination](https://github.com/FaddyManatee/embed-pagination).

## Preview
### Notifies when new forum threads are found
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061707111479922830/image.png"><br/>

### Sends weekly open thread reminders
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061710985968238763/image.png"><br/>

### /viewthreads `new`
Lists all newly found threads.

### /viewthreads `all`
Lists all open threads.

### /viewthreads `appeal`
Lists all open ban or mute appeals.<br/>
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061708918868414515/image.png"><br/>

### /viewthreads `staffapp`
Lists all open staff applications.<br/>
<img src="https://cdn.discordapp.com/attachments/1058799534408478801/1061707976253132881/image.png"><br/>

## NBS music player
Play note block songs from .nbs files via [nbsplayer](https://github.com/FaddyManatee/nbsplayer)! Add your own 
.nbs songs into the `nbs` directory.

### /nbsongs
Lists the names of all playable songs from the `nbs` directory.

### /nbplay `songname`
Plays `songname` in your current voice channel.

### /nbleave
Disconnects the bot from its voice channel.

### /nbstop
Stops the currently playing song or shuffled playlist.

### /nbloop
Loops the currently playing song until stop is called.

### /nbshuffle
Continues to play random songs from the playlist in your current voice channel.

### /nbskip
Skips to the next song when shuffling.
