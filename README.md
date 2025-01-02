# ForumBot

**ForumBot** is a Discord bot built with `discord.py` for the community at [shadowkingdom.org](https://shadowkingdom.org). It periodically monitors the forums for new threads and posts related to staff applications, appeals, and reports, and notifies staff of relevant updates.

## Features

### New Forum Thread Notifications
ForumBot will send a notification whenever new threads are created concerning staff applications, appeals, or reports.

![New Thread Notification](<image_url_placeholder>)

### New Post Notifications
The bot also sends a notification when new posts are added to existing threads.

![New Post Notification](<image_url_placeholder>)

### Weekly Open Thread Reminders
ForumBot sends out weekly reminders about open threads to keep users informed.

![Open Thread Reminder](<image_url_placeholder>)

### Command: `/viewthreads [type=<appeal|application|report>]`
Lists the currently open threads. Optionally, you can specify a type to filter the results:
- `appeal` — Show appeal threads.
- `application` — Show application threads.
- `report` — Show report threads.

Example: `/viewthreads type=appeal` will list only open appeal threads.

![View Threads](<image_url_placeholder>)