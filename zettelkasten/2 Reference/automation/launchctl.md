---
title: Apple Launchctl
created: 2025-02-21T10:27:00Z
updated: 2025-02-21T10:27:00Z
tags: [launchctl, automation, scripting]
---

# Apple Launchctl

I tried to get cron running on my Macbook Pro M4 this week, only to learn that Apple has pretty much deprecated cron in favor of their launchctl tool. Launchctl expects Apple plist format that looks a lot like XML...well, it is XML.

plist file example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.chris.zksync</string> <!--name of your file-->
    <key>ProgramArguments</key>
    <array>
      <string>/Users/chris/.local/bin/zk_sync</string> <!--where your script is located--></-->
    </array>
    <key>StartInterval</key>
    <integer>1800</integer> <!-- time to wait between runs (in seconds)-->
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/chris/Library/Logs/zksync.log</string> <!-- log destination -->
    <key>StandardErrorPath</key>
    <string>/Users/chris/Library/Logs/zksync.error.log</string> <!-- error logs -->
</dict>
</plist>
```

Put this file in `~/Library/LaunchAgents/`

Activate it: `launchctl load $HOME/Library/LaunchAgents/<plist file name>`

Deactivate it `launchctl unload $HOME/Library/LaunchAgents/<plist file name>`

Check that it's running: `launchctl list | grep <label defined in the xml file>`, using our example above: `launchctl list | grep com.chris.zksync`

View the logs: `tail -f ~/Library/Logs/zksync.log` (tip, add `-n` to select the number of previous lines you want to view)

Not covered here, but you can also script this whole process.

Links: [[launchctl]] [[automation]] [[scripting]]

202502211027
