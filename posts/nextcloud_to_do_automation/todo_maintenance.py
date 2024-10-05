#!/usr/bin/env python3

"""Archive tasks in a todo.txt file kept on a WebDAV server (e.g. Nextcloud)."""

import argparse
import configparser
import re
import sys

import requests

DONE_LINE_RE = re.compile(r"^x\b")
ETAG_RE = re.compile(r'^"(.*)-gzip"$')

SUCCESS = object()
FAILURE = object()


def get_etag(response):
    tag = ETAG_RE.match(response.headers["etag"]).group(1)
    return '"{}"'.format(tag)


def archive_done_tasks(hostname, username, password):
    base_url = "https://{}/remote.php/dav/files/{}/".format(hostname, username)

    session = requests.Session()
    session.auth = (username, password)

    todo_url = "{}/todo.txt".format(base_url)
    done_url = "{}/done.txt".format(base_url)

    todo_put = None
    while (todo_put is None) or not (200 <= todo_put.status_code < 300):
        todo_get = session.get(todo_url)

        # If the first GET fails, just return and wait for next
        # time script is run.
        if not (200 <= todo_get.status_code < 300):
            return SUCCESS

        todo_lines = todo_get.content.decode(encoding="utf8").splitlines(True)

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
    while (done_put is None) or not (200 <= done_put.status_code < 300):
        done_get = session.get(done_url)
        if not (200 <= done_get.status_code < 300):
            continue

        done_lines = done_get.content.decode("UTF-8").splitlines(True)

        done_put = session.put(
            done_url,
            "".join(done_lines + added_done_lines).encode("UTF-8"),
            headers={"If-Match": get_etag(done_get)},
        )

        # Retry this a few times since we updated todo.txt and want
        # to get done.txt into a correct state.
        i += 1
        if i >= 10:
            return SUCCESS


def main():
    # Parse command line arguments
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-c", "--config", help="configuration filename")
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
        sys.stderr.write('Missing configuration in "{}".\n'.format(config_filename))
        return FAILURE

    # Perform maintenance
    return archive_done_tasks(hostname, username, password)


if __name__ == "__main__":
    result = main()

    if result is SUCCESS:
        sys.exit(0)
    elif result is FAILURE:
        sys.exit(1)
