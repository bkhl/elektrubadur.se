#!/usr/bin/python3

"""
Script to convert content from using Zola/Markdown do using Hugo/Org.
"""

from pathlib import Path
import os
import re
import shutil
import subprocess
import tomllib

def get_files(dir):
    markdown_files = set()
    data_files = set()

    for root, dirs, files in os.walk(dir):
        path = Path(root).relative_to(dir)
        for filename in files:
            filename_path = Path(path / filename)
            filename_extension = filename_path.suffix
            if filename_path.suffix == ".md":
                markdown_files.add(filename_path)
            else:
                data_files.add(filename_path)

    return markdown_files, data_files


def copy_data_files(old_content_dir, new_content_dir, data_files):
    for path in data_files:
        old_path = old_content_dir / path
        new_path = new_content_dir / path
        new_path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        shutil.copyfile(old_path, new_path)


def convert_markdown_file(source_path, destination_path):
    with open(source_path, "r") as source_file:
        content = source_file.read()

    preamble, body = re.match(
        r'^\s*?\+\+\+\s*$\s*(.*)$\s*^\+\+\+\s*$\s*(.*)$',
        content,
        re.MULTILINE | re.DOTALL).groups()

    parsed_preamble = tomllib.loads(preamble)

    pandoc_output = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "org"],
        input=body.encode("utf-8"),
        stdout=subprocess.PIPE)

    new_body = pandoc_output.stdout.decode("utf-8").replace(
        "\n#+begin_html\n  <!-- more -->\n#+end_html\n",
        "\n# more\n",
    ).strip()

    new_body = re.sub(
        r'^#\+caption: (.*)', r'#+ATTR_HTML: :title \1 :alt \1',
        new_body,
        re.MULTILINE)

    new_body = re.sub(
        r'{{\s*download\(filename="(.*)"\)\s*}}',
       r'[[file:\1][Download]]',
        new_body)

    new_body = re.sub(
        r'\n:PROPERTIES:\n:CUSTOM_ID: [\w\.-]+\n:END:\n',
        r'\n',
        new_body)

    title = parsed_preamble.get("title", None)
    date = parsed_preamble.get("date", None)
    path = parsed_preamble.get("path", None)

    taxonomies = parsed_preamble.get("taxonomies", {})
    categories = taxonomies.get("categories", [])
    tags = taxonomies.get("tags", [])

    extra = parsed_preamble.get("extra", {})
    links = extra.get("links", {})
    mastodon_link = links.get("mastodon", None)
    image = extra.get("image", None)

    preamble_lines = []

    if title:
        preamble_lines.append(f"#+TITLE: {title}\n")

    if date:
        preamble_lines.append(f"#+DATE: {date}\n")

    if path:
        preamble_lines.append(f"#+URL: /{path}\n")

    if categories:
        preamble_lines.append(f"#+CATEGORIES[]: {' '.join(categories)}\n")

    if tags:
        preamble_lines.append(f"#+TAGS[]: {' '.join(tags)}\n")

    if mastodon_link:
        preamble_lines.append(f"#+MASTODON_LINK: {mastodon_link}\n")

    with open(destination_path, "w") as destination_file:
        for line in preamble_lines:
            destination_file.write(line)

        if preamble_lines and new_body:
            destination_file.write("\n")

        if new_body:
            destination_file.write(f"{new_body}\n")

    write_config(destination_path.parent / "config.toml", extra)

def write_config(config_path, extra):
    image = extra.get("image", None)
    gallery = extra.get("gallery", None)

    if not (image or gallery):
        return

    output = []

    if image:
        output.append(f"""\
[image]
title = "{image['title']}"
filename = "{image['filename']}"
""")

    if gallery:
        for filename, entry in gallery.items():
            output.append("[[gallery]]")
            if "title" in entry:
                output.append(f"title = \"{entry['title']}\"")
            if "description" in entry:
                output.append(f"description = \"{entry['description']}\"")
            output.append(f"filename = \"{filename}\"")
            if entry.get("featured", False):
                output.append("featured = true")
            output.append("")
    with open(config_path, "w") as config_file:
        config_file.write("\n".join(output))


def convert_markdown_files(old_content_dir, new_content_dir, markdown_files):
    for path in markdown_files:
        source_path = old_content_dir / path
        destination_path = new_content_dir / path.with_suffix(".org")
        convert_markdown_file(source_path, destination_path)


def main():
    project_dir = Path.cwd()
    old_content_dir = project_dir / "content.old"
    new_content_dir = project_dir / "content"
    markdown_files, data_files = get_files(old_content_dir)

    try:
        shutil.rmtree(new_content_dir)
    except FileNotFoundError:
        pass

    copy_data_files(old_content_dir=old_content_dir,
                    new_content_dir=new_content_dir,
                    data_files=data_files)

    convert_markdown_files(old_content_dir=old_content_dir,
                           new_content_dir=new_content_dir,
                           markdown_files=markdown_files)


if __name__ == '__main__':
   main()
