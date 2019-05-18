+++
title = "Simple Nextcloud To-Do List Automation with Python and WebDAV"
date = 2019-05-05

[taxonomies]
categories = ["Programming"]
+++

I keep a task list in a [todo.txt][todo.txt] format in
[Nextcloud][Nextcloud]. They are simply kept as two text files, `todo.txt`
and `done.txt` in the root of my Nextcloud user directory.

Some clients already have the option to move tasks from `todo.txt` to
`done.txt` when you mark a task as done. However, I would prefer they stick
around in the `todo.txt` for a while, in case I change my mind.

At first I thought I'd just write a script to run as a cronjob on the server
hosting Nextcloud, but that won't work with syncrhonization, as it won't let
Nextcloud know the files have changed. I then thought there must be an API to
read/write files to Nextcloud, and then quickly realized that this API is
[WebDAV][webdav]. So, I should be able to make a Python script to do this,
using [requests][requests]. A more full-featured WebDAV library would be
overkill for this.

<!-- more -->

# Outline

Here's what the script will do.

1. Get the `todo.txt` file.
1. If there are any completed tasks in there, get the `done.txt` file.
1. Strip the completed tasks from `todo.txt`.
1. Append the completed tasks to the content from `done.txt`.
1. Update `todo.txt`.
1. If there was no problem updating `todo.txt`, update `done.txt`. This step
  has to be retried in case of a conflict, because now the only copy of those
  done tasks is in the script's memory.

This still leaves room for some issues if the script crashes in the middle of
running, but I figured if it happens I'd get a mail from cron, and there's a
file history in Nextcloud so I can sort it out then. After running this a few
months now it still hasn't happened.

# Implementation

Starting with imports and stuff of course:

```python
#!/usr/bin/env python3

import argparse
import configparser
import re
import sys

import requests
```

In [todo.txt][todo.txt], tasks are marked as done by prepending the token `x`
at the start of the line. For this purpose, that's really all we need to do,
so I just create regexp to match these lines:

```python
DONE_LINE_RE = re.compile(r"^x\b")
```

That's it for the parsing.

Now, as this script will update two files, and I don't want to lose any
tasks, I need to worry about race conditions. In other words, I'll need to
use [ETags][etag].

For the structure of the script, I at first wrote it using the [Plumbum CLI
application][plumbum-cli], but later found that it was adding so little
benefit I didn't want that dependency. Instead I'll use `configparser` and
`argparse` for the same thing. For error handling, I'll have functions return
one of these values, and translate them to return codes at the end.

```python
SUCCESS = object()
FAILURE = object()
```

It's time for the `main` function.

```python
def main():
    # Parse command line arguments
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "-c", "--config", help="configuration filename"
    )
    arguments = argument_parser.parse_args()
    config_filename = arguments.config

    # Parse configuration
    config_parser = configparser.ConfigParser()
    config_parser.read(config_filename)
    try:
        username = config_parser.get("Connection", "username")
        password = config_parser.get("Connection", "password")
        hostname = config_parser.get("Connection", "hostname")
    except configparser.Error:
        sys.stderr.write(
            'Missing configuration in "{}".\n'.format(
                config_filename
            )
        )
        return FAILURE

    # Perform maintenance
    return archive_done_tasks(hostname, username, password)
```

This allows you to pass a command line argument pointing you to a configfile
containing something like this:

```ini
[Connection]
hostname = your.nextcloud.instance.net
username = your_user_name
password = v3ris3curep4ssworð
```

Now, the function that's the meat of the script, which actually gets and
updates the files, and moves the completed tasks over.

The first loop will get the `todo.txt`, then put it back after filtering out
the completed tasks.

If the initial GET fails, it will return successfully, since that probably
means the server is unavailable, and we are better off just waiting for the
next time cron triggers the script.

The next loop will retry up to ten times, because at that point `todo.txt`
has been updated, so we should try a bit harder to get `done.txt` into a
correct state.

This function is a bit long and would benefit from refactoring. (Pull
requests accepted.)

```python
def archive_done_tasks(hostname, username, password):
    base_url = "https://{}/remote.php/dav/files/{}/".format(
        hostname, username
    )

    session = requests.Session()
    session.auth = (username, password)

    todo_url = "{}/todo.txt".format(base_url)
    done_url = "{}/done.txt".format(base_url)

    todo_put = None
    while (todo_put is None) or not (
        200 <= todo_put.status_code < 300
    ):
        todo_get = session.get(todo_url)

        # If the first GET fails, just return and wait for next
        # time script is run.
        if not (200 <= todo_get.status_code < 300):
            return SUCCESS

        todo_lines = todo_get.content.decode(
            encoding="utf8"
        ).splitlines(True)

        updated_todo_lines = []
        added_done_lines = []

        for line in todo_lines:
            if DONE_LINE_RE.match(line):
                added_done_lines.append(line)
            else:
                updated_todo_lines.append(line)

        if not added_done_lines:
            # Nothing to do.
            return SUCCESS

        todo_put = session.put(
            todo_url,
            "".join(updated_todo_lines).encode("UTF-8"),
            headers={"If-Match": get_etag(todo_get)},
        )

    done_put = None
    i = 0
    while (done_put is None) or not (
        200 <= done_put.status_code < 300
    ):
        done_get = session.get(done_url)
        if not (200 <= done_get.status_code < 300):
            continue

        done_lines = done_get.content.decode("UTF-8").splitlines(
            True
        )

        done_put = session.put(
            done_url,
            "".join(done_lines + added_done_lines).encode(
                "UTF-8"
            ),
            headers={"If-Match": get_etag(done_get)},
        )

        # Retry this a few times since we updated todo.txt
        #  and want to get done.txt into a correct state.
        i += 1
        if i >= 10:
            return SUCCESS
```

Here's the helper function to get the etag from a `requests.Response` object.
I found that the ETags from Nextcloud has a content type suffix, so had to
make another regexp to remove that :

```python
ETAG_RE = re.compile(r'^"(.*)-gzip"$')

def get_etag(response):
    tag = ETAG_RE.match(response.headers["etag"]).group(1)
    return '"{}"'.format(tag)
```

Finally, we call the main function like this. The `SUCCESS`/`FAILURE` objects
are converted into status codes and the script exits accordingly.


```python
if __name__ == "__main__":
    result = main()

    if result is SUCCESS:
        sys.exit(0)
    elif result is FAILURE:
        sys.exit(1)
```

The entire script is in this [GitLab project][gitlab-project].

This is just a start, if you want more advanced automation, handy things that
could be added include (again, pull requests accepted):

* Parse tags indicating repeating tasks. When those are completed, move the
  current one to `done.txt`, but create a new task for the next occurance at
  the same time.
* Change it to keep completed tasks in `done.txt` for a certain numer of days
  after the completion date.

[todo.txt]: http://todotxt.org/
[Nextcloud]: https://nextcloud.com/
[todo_maintenance]: https://gitlab.com/bkhl/todo_maintenance
[webdav]: https://tools.ietf.org/html/rfc2518
[requests]: https://pypi.org/project/requests/
[etag]: https://tools.ietf.org/html/rfc7232
[plumbum-cli]: https://plumbum.readthedocs.io/en/latest/cli.html
[gitlab-project]: https://gitlab.com/bkhl/todo_maintenance
