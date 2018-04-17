+++
title = "Using i3 in Xubuntu"
date = 2017-10-22
+++

Here are the steps I've taken to set up the [i3](https://i3wm.org/) window manager in my [Xubuntu](https://xubuntu.org/) desktop environment, based on [XFCE](https://xfce.org/).

I have used this with Xubuntu 17.04 and 17.10.

![Xubuntu i3 desktop](/images/using_i3_in_xubuntu/xubuntu_i3.png)

<!-- more -->

# Step 1: Install i3

```
# apt install i3-wm i3status</pre>
```

# Step 2: Set window manager

In the XFCE *Whisker* menu, open up *Settings/Session and Startup*, and select the Session tab. Set Restart style for *xfwm4*, *xfce4-panel* and *xfdesktop* to *Never*.

![Xubuntu i3 session settings](/images/using_i3_in_xubuntu/xubuntu_i3_session_settings.png)

Don't forget to click *Save Session*>.

You could leave the panel enabled to use it along with i3, but I prefer to just use the i3 bar.

Then go to the *Application Autostart* tab, and click the *Add* button. Create a startup entry for i3 with the command `/usr/bin/i3`.

![Xubuntu i3 autostart settings](/images/using_i3_in_xubuntu/xubuntu_i3_autostart_settings.png)

# Step 3: Log in again

Log out and then log in again. Unless you have an i3 configuration already, the i3 configuration wizard will be started

# Next

As my application launcher I use [Rofi](https://davedavenport.github.io/rofi/), which understands `.desktop` files.

For my entire i3 configuration, see my [configuration repository on GitHub](https://github.com/bkhl/config).
