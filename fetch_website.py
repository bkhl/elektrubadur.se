#!/usr/bin/env python3

import argparse
import io
import os
import tempfile
import zipfile

import requests


class ArtifactNotFoundException(Exception):
    pass


class CurrentEtagNotFoundException(Exception):
    pass


class InvalidArtifactException(Exception):
    pass


ARTIFACT_DIRECTORY_PREFIX = "public/"


def remove_artifact_prefix(s: str):
    return s[len(ARTIFACT_DIRECTORY_PREFIX) :]


def is_ok_response(response: requests.Response):
    """
    Verify that HEAD/GET response looks valid.
    """

    return (
        response.status_code == 200
        and "ETag" in response.headers
        and response.headers.get("Content-Type", None) == "application/zip"
    )


def is_ok_archive(archive: zipfile.ZipFile):
    """
    Verify that archive (ZipFile object) looks valid.
    """

    return all(
        name.startswith(ARTIFACT_DIRECTORY_PREFIX) for name in archive.namelist()
    )


def get_remote_etag(session: requests.Session, artifact_url: str):
    """
    Get ETag of remote artifact, using a HEAD request, also checking that it
    looks like an artifact is currently available.
    """

    response = session.head(artifact_url, allow_redirects=True)

    if is_ok_response(response):
        return response.headers["ETag"]
    else:
        raise ArtifactNotFoundException


def get_current_etag(etag_filename: str):
    """
    Get ETag stored with currently deployed website.
    """

    if os.path.isfile(etag_filename):
        with open(etag_filename) as f:
            return f.read().rstrip()
    else:
        raise CurrentEtagNotFoundException


def fetch_website(
    session: requests.Session, artifact_url, destination_dir: str, etag_filename: str
):
    """
    Fetch and deploy the website.
    """

    response = session.get(artifact_url, allow_redirects=True)

    if not is_ok_response(response):
        raise ArtifactNotFoundException

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        if not is_ok_archive(archive):
            raise InvalidArtifactException

        extract_files(archive=archive, destination_dir=destination_dir)
        delete_files(archive=archive, destination_dir=destination_dir)
        save_etag(etag_filename=etag_filename, etag=response.headers["ETag"])


def extract_files(archive: zipfile.ZipFile, destination_dir: str):
    """
    Extract files to target directory.
    """

    for info in archive.infolist():
        target_path = f"{destination_dir}/{remove_artifact_prefix(info.filename)}"
        if info.is_dir():
            if os.path.exists(target_path):
                if not os.path.isdir(target_path):
                    os.remove(target_path)
                    os.mkdir(target_path)
            else:
                os.mkdir(target_path)
        else:
            with archive.open(info) as source_file, open(
                target_path, "wb"
            ) as destination_file:
                destination_file.write(source_file.read())


def delete_files(archive: zipfile.ZipFile, destination_dir: str):
    """
    Delete any files and directories that was not included in the artifact.
    """

    keep_files = set(
        f"{destination_dir}/{remove_artifact_prefix(name)}".rstrip(os.path.sep)
        for name in archive.namelist()
    )

    for path, directory_names, file_names in os.walk(destination_dir, topdown=False):
        for file_name in file_names:
            file_path = os.path.join(path, file_name)
            if file_path not in keep_files:
                os.remove(file_path)

        for directory_name in directory_names:
            directory_path = os.path.join(path, directory_name)
            if directory_path not in keep_files:
                os.rmdir(directory_path)


def save_etag(etag_filename: str, etag: str):
    """
    Save ETag to a ".etag" file in the destination directory, for comparison
    to the artifact ETag in the next iteration.
    """

    with open(etag_filename, "w") as f:
        f.write(f"{etag}\n")


def parse_args():
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_url", help="HTTP URL to artifact")
    parser.add_argument(
        "destination_dir", help="path of directory to deploy website into"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    artifact_url = args.artifact_url
    destination_dir = args.destination_dir

    etag_filename = f"{destination_dir}/.etag"

    session = requests.Session()

    try:
        remote_etag = get_remote_etag(session, artifact_url)
    except ArtifactNotFoundException:
        return

    try:
        current_etag = get_current_etag(etag_filename)
    except CurrentEtagNotFoundException:
        pass
    else:
        if remote_etag == current_etag:
            return

    try:
        fetch_website(
            session=session,
            artifact_url=artifact_url,
            destination_dir=destination_dir,
            etag_filename=etag_filename,
        )
    except ArtifactNotFoundException:
        return


if __name__ == "__main__":
    main()
