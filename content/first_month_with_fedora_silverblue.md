+++
title = "First Month with Fedora Silverblue"
date = 2020-02-08

[taxonomies]
categories = ["Software"]

[extra.links]
mastodon = "https://mastodon.sdf.org/@bkhl/103623742796898036"

+++

I decided during my midwinter vacation that I'd try out [Fedora
Silverblue][silverblue] on my desktop, and I liked it, so here I am still
using it on my work laptop.

Silverblue is a version of Fedora using [rpm-ostree][rpm-ostree] to provide a
minimal and immutable base OS, providing a platform for running applications in
containers.

Previously I was using Ubuntu with a lot of Ansible playbooks for installing
things both globally and in my home directory. I used to keep those playbooks
in the same directory as my [dotfiles][dotfiles], but after the switch to
Fedora I removed them. If anyone is curious about what that looked like, [they
are here][workstation-playbooks].

<!-- more -->

The benefits I was hoping for was

* Make my laptop setup more "out of the box", to get away from having a
  big collection of Ansible roles for varied purposes,
  that all have to work together on my laptop.
* Simplifying my base OS by moving development stuff and applications into
  containers.
* Plain Gnome desktop without custom themes.
* RPM-based. This is not an advantage in itself, but makes things a bit easier
  as I mostly deal with RHEL and Centos for work.

## Applications

For applications, I'm using mostly Flatpak. I found after a while that
applications I had installed from the Fedora Flatpak repository was more buggy
than the ones I had from [Flathub][flathub], so at one point I made a switch to
get all my applications from Flathub.

Here's the entire command line to get `rpm-ostree` into the current state of my
laptop:

```bash
rpm-ostree reset

rpm-ostree install \
  fedora-workstation-repositories \
  ffmpeg-libs \
  google-chrome-stable \
  gparted \
  krb5-workstation \
  langpacks-en \
  langpacks-en_GB \
  langpacks-sv \
  langpacks-th \
  libgnome-keyring \
  NetworkManager-fortisslvpn-gnome \
  nextcloud-client \
  qemu \
  thai-arundina-sans-fonts \
  thai-arundina-sans-mono-fonts \
  thai-arundina-serif-fonts \
  vim-enhanced \
  vim-X11 \
  virt-manager \
  wl-clipboard

rpm-ostree install 'https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-31.noarch.rpm'
rpm-ostree install 'https://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-31.noarch.rpm'

rpm-ostree install fuse-exfat exfat-utils
```

As you can see, there's just a few things that has to be added as RPMs. Not a
lot, considering that in the default installation, Silverblue just comes with a
terminal, a file manager, and Firefox, in terms of applications.

## Development environments

The main thing I've done so far to make it convenient for me to use as a
development system is to create container images for use with
[Toolbox][toolbox]. I keep these images [here in GitLab][toolboxes]. I'll write
more about that in a future article.

For now I'll summarize it by saying I've created some Toolbox environments for
various languages, configured to keep caches and such in the container, rather
than my `$HOME`, and it's working quite nicely so far.

## Gnome

I used the default Ubuntu desktop before, so this is not a dramatic change, but
I like the look and feel of the default Gnome desktop. I also get a somewhat
newer version of it, which is nice.

A few weeks after the switch, Tobias Bernard (Gnome developer) posted the
article [Doing Things That Scale][doing-things-that-scale], which resonated
with me. While I've done some hacking to set up my development environments
"just right" as described above, I'm trying to think of how to make that work
more usable for others, maybe by contributing back to the [Toolbox][toolbox]
project, or by making some sort of GUI wrapper to manage a set of development
environment toolboxes.

[silverblue]: https://silverblue.fedoraproject.org/ "Fedora Silverblue"
[dotfiles]: https://gitlab.com/bkhl/dotfiles/ "My dotfiles"
[workstation-playbooks]: https://gitlab.com/bkhl/workstation-playbooks/tree/065ce9ca0547ca4d9c1e574407ba6373fcc99b69 "My old workstation Ansible playbooks"
[toolbox]: https://github.com/containers/toolbox "Toolbox"
[toolboxes]: https://gitlab.com/bkhl/toolboxes "bkhl/toolboxes"
[flathub]: https://flathub.org/ "Flathub"
[rpm-ostree]: https://rpm-ostree.readthedocs.io "rpm-ostree"
[doing-things-that-scale]: https://blogs.gnome.org/tbernard/2020/01/17/doing-things-that-scale/ "Doing Things That Scale"