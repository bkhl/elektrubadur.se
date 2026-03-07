+++
title = "How This Blog Works"
author = "Björn Lindström"
date = 2020-05-03
tags = ["WWW", "HCoop", "Git", "Automation"]
categories = ["Software"]
draft = false
aliases = ["/how_this_blog_works"]
+++

This blog is created using the [Zola static site engine](https://www.getzola.org/). I use a combination of [GitLab CI](https://docs.gitlab.com/ci/) and `cron` to automatically upload it to my web server whenever I merge a change to the [Git](https://git-scm.com/) `master` branch of the home page.

The `elektrubadur.se` source code is kept _here in GitLab_ _[Update 2024-11-05: [elektrubadur.se source code since moved to GitHub](https://github.com/bkhl/elektrubadur.se/)]_. While writing a post I just run `zola serve` on my computer and can look at a dynamically updated website on a local web server.

Once ready, I commit on a branch and push it to GitLab, and then make a merge request. This might seem a bit silly for a one-man project, but this way I can disable pushes to the `master` branch entirely, which can help prevent an accident.

The repository includes the separate repository [web-build](https://gitlab.com/bkhl/web-build) as a submodule. It contains some scripts used to build and publish the web site.

My website is hosted at [HCoop](https://hcoop.net/), a hosting cooperative. Because it uses AFS, passwordless login requires the use of Kerberos, so I can't just push the page using a deploy key.

So, rather than pushing the website there, I'm pulling. I've put the script `fetch_website.py` from [web-build](https://gitlab.com/bkhl/web-build) on the target host, and makes it run it as a cron job:

```crontab
*/5 * * * * k5start -qtUf "/etc/keytabs/user.daemon/$USER" -- "$HOME/scripts/fetch_website.py" "https://gitlab.com/bkhl/elektrubadur.se/-/jobs/artifacts/master/download?job=build" "$HOME/www/elektrubadur.se"
```

The `k5start` thing is another thing needed because of the use of AFS and Kerberos. The point here is that you give the script a URL to a GitLab artifact, and a target directory, and it will deploy it if there's been any change.

[The entire script](https://gitlab.com/bkhl/web-build/-/blob/f76df73fd337b43452e7cb934347357b5c9aafa7/fetch_website.py) is a bit long to post here, but it basically checks if there is a new artifact in GitLab for the website, built from the `master` branch, and if there is downloads and deploys it. It saves the ETag in a file, so that it can compare to that and skip downloading unless there has been a change.

Credits for tools used making this page, inspirations for the design &amp;c. are also on [About This Page](/about_page/).
