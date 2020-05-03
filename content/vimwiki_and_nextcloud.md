+++
title = "Vimwiki + Nextcloud Notes"
date = 2020-05-02

[taxonomies]
categories = ["Software"]
tags = ["Vim", "Vimwiki", "Nextcloud", "notes"]

[extra.links]
mastodon = "https://mastodon.sdf.org/@bkhl/104099207807530812"

+++

I've been using [Vimwiki] for a while, which lets me keep interlinked plain
text notes on my computer with minimal hassle.

For a while I've also kept these synced to my phone via the [Nextcloud Notes]
application. I have a self-hosted [Nextcloud] instance, and simply point
Vimwiki on my computer to the same directory in the directory that I have
synchronized with Nextcloud.

The Nextcloud Notes app uses Markdown, so I have to configure Vimwiki to use
that syntax, which is fine with me. One quirk of the Nextcloud Notes app is
that rather than letting you name files independently, it will change filenames
to whatever the first line of your note is. Until today that meant I had to
keep making sure in Vimwiki to add those headers, but I've now finally
automated that.

<!-- more -->

To start with, I added the function `SetWikiHeader` to
[my `~/.vim/plugin/config/vim.wiki`](https://gitlab.com/bkhl/dotfiles/-/blob/0ab54ef439d570e09aae61fe18c8c0538fa90a0d/.vim/plugin/config/vimwiki.vim):

```vim
if &runtimepath !~? "vimwiki"
  finish
endif

" My main wiki.
let g:vimwiki_list = [{
            \"path": "~/Documents/Notes/",
            \"syntax": "markdown", "ext": ".md"
            \}]

" Disable creation of temporary wikis.
let g:vimwiki_global_ext = 0

" Function to set header of current file to match filename.
"
" This helps interoparability with Nextcloud Notes, which assumes that
" the first line of the file matches the filename.
function SetWikiHeader()
    let first_line = getline(1)
    let filename = expand("%:t:r")

    if "# " . filename == first_line
        " First line is already correct.
        :
    elseif first_line =~ '^#*\s*\V' . escape(filename, '\') . '\m\s*$'
        " First line matches filename but has wrong header format.
        " Reformat to have proper format.
        call setline(1, "# " . filename)
    else
        " First line not matching filename at all. Prepend lines with
        " filename as a header.
        if first_line != ""
            call append(0, "")
        endif
        call append(0, "# " . filename)
    endif
endfunction
```

Vim script is pretty weird, had to search in documentation for how to do most
things in there. Props to people who write entire programs in it, like let's
say [those people that wrote Vimwiki](https://github.com/orgs/vimwiki/people).

Now, to make this run whenever I open a Vimwiki file, or before saving it, I
put this in [my
`~/.vim/ftplugin/vimwiki.vim`](https://gitlab.com/bkhl/dotfiles/-/blob/0ab54ef439d570e09aae61fe18c8c0538fa90a0d/.vim/ftplugin/vimwiki.vim):

```vim
" Set header to match filename when opening or saving file, for
" interoperability with Nextcloud Notes.
call SetWikiHeader()
autocmd BufWritePre <buffer> call SetWikiHeader()
```

The end result is pretty nice. The only big catch is that I can't rename files in
Nextcloud Notes if they have a lot of links to them, since those links only get
updated if I use the rename function in Vimwiki, but then that's not something
I do very often.

[vimwiki]: http://vimwiki.github.io/ "Vimwiki"
[nextcloud notes]: https://apps.nextcloud.com/apps/notes/ "Nextcloud Notes"
[nextcloud]: https://nextcloud.com/