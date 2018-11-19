#!/usr/bin/env python3

import os

from plumbum import cli, local
from plumbum.cmd import tidy, xmlstarlet, zola


class Builder(cli.Application):
    local_prefix = cli.Flag(["l", "local"], help="Build for local viewing")

    def build(self):
        zola("build")

    def public_files_by_extension(self, *extensions):
        extensions_with_dot = ["." + e for e in extensions]
        for root, _, files in os.walk("public"):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension in extensions_with_dot:
                    yield os.path.join(root, file)

    def replace_prefix(self):
        for file in self.public_files_by_extension("html", "xml", "txt"):
            with open(file) as file_object:
                s = file_object.read().replace("__PREFIX__", self.prefix)
            with open(file, "w") as file_object:
                file_object.write(s)

    def clean_html(self):
        files = list(self.public_files_by_extension("html"))
        tidy("-config", "tidy.conf", *files, retcode=(0, 1))

    def clean_xml(self):
        for file in self.public_files_by_extension("xml"):
            xml = xmlstarlet(
                "fo", "--noindent", "--nocdata", "--nsclean", "--encode", "utf-8", file
            )
            with open(file, "w") as file_object:
                file_object.write(xml)

    def main(self):
        if self.local_prefix:
            self.prefix = "file://" + str(local.cwd / "public")
        else:
            self.prefix = "http://elektrubadur.se"

        self.build()
        self.replace_prefix()
        self.clean_html()
        self.clean_xml()


if __name__ == "__main__":
    Builder.run()
