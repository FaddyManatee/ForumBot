# ForumBot
A discord.py bot for [shadowkingdom.org](https://shadowkingdom.org) that periodically 
retrieves new Xenforo forum threads (staff applications, punishment appeals) via RSS 
feed and reports details related to them.

## Dependencies
+ ffmpeg and ffprobe binaries are required in the root folder. [Install them here](https://ffbinaries.com/downloads).

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
