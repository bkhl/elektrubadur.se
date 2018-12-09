#!/usr/bin/env python3

import os
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from plumbum import cli, local
from plumbum.cmd import tidy, xmlstarlet, zola

PORT = 8000


class Builder(cli.Application):
    serve_locally = cli.Flag(
        ["l", "serve locally"], help="Build and serve page locally"
    )

    TCPServer.allow_reuse_address = True

    def serve(self):
        with TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
            with local.cwd(local.cwd / "public"):
                httpd.serve_forever()

    def public_files_by_extension(self, *extensions):
        extensions_with_dot = ["." + e for e in extensions]
        for root, _, files in os.walk("public"):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension in extensions_with_dot:
                    yield os.path.join(root, file)

    def replace_prefix(self):
        if self.serve_locally:
            prefix = f"http://localhost:{PORT}"
        else:
            prefix = "http://elektrubadur.se"

        for file in self.public_files_by_extension("html", "xml", "txt"):
            with open(file) as file_object:
                s = file_object.read().replace("__PREFIX__", prefix)
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
        zola("build")
        self.replace_prefix()
        self.clean_html()
        self.clean_xml()

        if self.serve_locally:
            self.serve()


if __name__ == "__main__":
    Builder.run()
