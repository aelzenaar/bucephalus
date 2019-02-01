""" This module contains the database access functions for bucephawiki. """

# Standard library
from datetime import datetime
from enum import Enum
import magic
import os
import re

# Libraries
from tinydb import TinyDB, where

# Bucephalus imports
import config
from exceptions import *


#
# Metadata database management
#

def get_database_object():
    """ Open the correct TinyDB. """

    return TinyDB(config.get_metadata_file_path(), indent=2)


def read_path_metadata(path, db=None):
    """ Return the metadata associated with our path as a dict. """

    if db == None:
        db = get_database_object()

    entries = db.search(where('path') == path)
    if len(entries) < 1:
        raise NoMetadataError(path)

    if len(entries) > 1:
        raise TooManyMetadataError(path, [entry.doc_id for entry in entries])

    return entries[0]


#
# These functions decide whether things are valid or exist.
#

# Compile our regular expression first, so we don't do it every time we need it.
valid_path_re = re.compile(r"(\b(/\w)+\b)")


def valid_path(path):
    """ Decide whether path is a valid path for a page that might or might not exist. """
    return False if valid_page_path_re.fullmatch(path) is None else True


def path_exists(path):
    """ Actually check whether the given path exists in the database. """

    if not valid_page_path(path):
        raise InvalidPathError(path)

    return path_internal(path).exists()


def path_internal(path):
    """ Take a path and give us where it is, physically. """
    return config.get_wiki_dir() / path


class PathType(Enum):
    """ Coarse path types (when we care about editable or not and nothing more). """
    INVALID = -1
    TEXT = 0
    BLOB = 1
    DIRECTORY = 2


def path_type(path):
    """ Get the type of the given path. """

    if not path_exists(path):
        return PathType.INVALID

    real_path = path_internal(path)
    if real_path.is_dir():
        return PathType.DIRECTORY

    mime = magic.Magic(mime=True).from_file(str(real_path))
    if "text/" in mime:
        return PathType.TEXT

    return PathType.BLOB


#
# Methods for reading and writing files.
#

def read_path_content(path):
    """ Return the full contents of the given non-directory path as a byte-string (for blobs) or utf-string (for text). """

    if path_type(path) == PathType.DIRECTORY:
        raise FileIsDirectoryError(path)

    if path_type(path) == PathType.TEXT:
        o = 'r'
    else:
        o = 'rb'

    with path_internal(path).open(o) as f:
      return f.read()

def write_path_text(path, content, metadata):
    """ Overwrite (or create) the given path with new content. Textual content only. """

    if path_type(path) == PathType.DIRECTORY:
        raise FileIsDirectoryError(path)

    # Make the parent directories of this new path exist in a hacky way.
    if not path_exists(path):
        real_path = path_internal(path)
        real_path.mkdir(parents = True)
        real_path.rmdir()

    # TODO: decide whether we throw an error here, or whether we silently replace metadata["path"] with path.
    if metadata["path"] != path:
        raise MetadataMismatchError(path, metadata)

    metadata["timestamp_modify"] = datetime.utcnow().strftime(config.timestamp_format())

    # If we have already got some metadata on this page, bring across any of the old
    # tags we need to and then update the old metadata.
    db = get_database_object()
    try:
        old_metadata = read_path_metadata(path, db=db)
        metadata["timestamp_create"] = old_metadata["timestamp_create"]
        db.update(metadata, doc_ids=[old_metadata.doc_id])

    except NoMetadataError:
        metadata["timestamp_create"] = metadata["timestamp_modify"]
        dbid = db.insert(metadata)

    # Write file after metadata.
    with path_internal(path).open('w') as f:
        f.write(text)

    vcs.commit("dbops: write_path_text: " + str(path))


def delete_path(path):
    """ Delete the path from the database. If the path represents a directory, that directory must be empty. """

    if not path_exists(path):
        raise NonexistentPathError(path)

    if path_type(path) == PathType.directory():
        path_internal().rmdir()
    else:
        path_internal().unlink()

    db = get_database_object()
    db.remove(doc_ids=[read_path_metadata(path, db=db).doc_id])

    vcs.commit("dbops: delete_path(): " + str(path))

def rename_path(path, destination):
    """ Move the data at the given path to the destination. """

    raise UnimplementedError("Please just copy the file data manually and then delete the old thingy.")

def directory_contents(path):
    """ Return a list containing the items in the directory. """

    if path_type(path) != PathType.directory():
        raise FileNotDirectoryError(path)

    return os.listdir(str(path))
