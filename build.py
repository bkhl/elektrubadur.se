#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plumbum import cli, local
from plumbum.cmd import tidy, xmlstarlet, zola


class Builder(cli.Application):
    def public_files_by_extension(self, *extensions):
        for filepath in (local.cwd / "public").walk(
            filter=lambda f: f.is_file() and f.suffix in ("." + e for e in extensions)
        ):
            yield filepath

    def clean_html(self):
        files = list(self.public_files_by_extension("html"))
        tidy("-config", "tidy.conf", *files, retcode=(0, 1))

    def clean_xml(self):
        for filepath in self.public_files_by_extension("xml"):
            xml = xmlstarlet(
                "fo",
                "--noindent",
                "--nocdata",
                "--nsclean",
                "--encode",
                "utf-8",
                filepath,
            )
            with filepath.open("w") as file_object:
                file_object.write(xml)

    def main(self):
        zola("build")
        self.clean_html()
        self.clean_xml()


if __name__ == "__main__":
    Builder.run()
