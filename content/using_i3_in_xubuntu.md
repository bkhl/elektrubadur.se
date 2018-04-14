+++
title = "Using i3 in Xubuntu"
date = 2017-10-22
+++

Here are the steps I've taken to set up the [i3](https://i3wm.org/) window manager in my [Xubuntu](https://xubuntu.org/) desktop environment, based on [XFCE](https://xfce.org/).

I have used this with Xubuntu 17.04 and 17.10.

![Xubuntu i3 desktop]({filename}/images/xubuntu_i3.png)

<!--more-->

<h1>Step 1: Install i3</h1>

<pre># apt install i3-wm i3status</pre>

<h1>Step 2: Set window manager</h1>

In the XFCE <em>Whisker</em> menu, open up <em>Settings/Session and Startup</em>, and select the Session tab. Set Restart style for <em>xfwm4</em>, <em>xfce4-panel</em> and <em>xfdesktop</em> to <em>Never</em>.

<a href="https://elektrubadur.se/wp-content/uploads/2017/10/xubuntu_i3_session_settings.png"><img src="https://elektrubadur.se/wp-content/uploads/2017/10/xubuntu_i3_session_settings.png" alt="" width="800" height="600" class="alignnone size-full wp-image-570" /></a>

Don't forget to click <em>Save Session</em>.

You could leave the panel enabled to use it along with i3, but I prefer to just use the i3 bar.

Then go to the <em>Application Autostart</em> tab, and click the <em>Add</em> button. Create a startup entry for i3 with the command <code>/usr/bin/i3</code>.

<a href="https://elektrubadur.se/wp-content/uploads/2017/10/xubuntu_i3_autostart_settings.png"><img src="https://elektrubadur.se/wp-content/uploads/2017/10/xubuntu_i3_autostart_settings.png" alt="" width="800" height="600" class="alignnone size-full wp-image-565" /></a>

<h1>Step 3: Log in again</h1>

Log out and then log in again. Unless you have an i3 configuration already, the i3 configuration wizard will be started
I contributed a theme to <a href="https://github.com/acrisci/i3-style">i3-style</a>&nbsp;called mate, to match the default theme of Ubuntu MATE.

<h1>Next</h1>

As my application launcher I use <a href="https://davedavenport.github.io/rofi/">Rofi</a>, which understands <code>.desktop</code> files.

For my entire i3 configuration, see my <a href="https://github.com/bkhl/config">configuration repository on GitHub</a>.
