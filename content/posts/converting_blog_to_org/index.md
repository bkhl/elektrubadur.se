+++
title = "Converting Sources of This Blog to Org format"
author = "Björn Lindström"
date = 2023-05-28
tags = ["WWW", "Markdown", "Org", "Hugo", "Python", "Emacs"]
categories = ["Programming"]
draft = false
aliases = ["/converting_blog_to_org"]
+++

It looks a bit bad that the last entry here was three years ago and was about how the site generation works, and here is another one on the same topic. However, it's in the interest of making it more enjoyable for me to write more that I've switched from [Zola](https://www.getzola.org/) to [Hugo](https://gohugo.io/) in order to be able to keep the sources in Org format.

Here I'll just share [the script](<{{< file "convert.py" >}}>) I made to do the format conversion, in case it's useful for anyone else. Actually, half the reason I'm even writing this entry is that I will need to later on repeat this process for another page I manage, and this way I have the script and some notes for then.

At the same time I've moved the sources from [GitLab](https://gitlab.com/) to [Sourcehut](https://sr.ht/) [Update 2024-11-05: I have since moved them to [GitHub](https://github.com/)].

I won't delve deeper into the reasons for that, but I thought I'd post the Python script I used for the conversion in case it's useful for anyone else. It's not particularly pretty and has special casing for various things that were particular to my Zola theme, so if anyone else were to use it, they would in all likelyhood need to do some changes. I made a few manual fixes in the Org source after the conversion, of things that occurred to rarely to mke it worth automating.

The script does the following:

- Clears out the target content directory. That's the `content/` directory under your current working directory.
- Copy any non-Markdown files into the same location from the old content directory, assumed to be `content.old/` in your current working directory.
- Extract TOML front matter from the old source files and convert into Org front matter.
- Run the remainder of the Markdown file through [Pandoc](https://pandoc.org/) to convert it from Markdown to Org.
- Apply various substitutions to the body to fix some things Pandoc doesn't handle, or just according to my preferences.
- Write some metadata that can not be nicely encoded as Org front matter and put it in a `config.toml` file next to the Org file instead.

Then I just needed to go ahead and write a Hugo templates that works with this new content directory. Getting the same general structure of the page as in Zola isn't difficult, as Zola is inspired by Hugo and uses a lot of the same conventions. I didn't have to do much to be able to preserve mostly the same hierarchy of the source files for equivalent output.

If you are curious about the Hugo templates used to render this page, they are in [the repository with the sources for this page](https://github.com/bkhl/elektrubadur.se/).

Finally, if you want to use the script I've been talking about, you can download it here: [convert.py](<{{< file "convert.py" >}}>)
