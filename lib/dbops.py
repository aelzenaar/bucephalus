""" This module contains the database access functions for bucephawiki. """

# Standard library
from enum import Enum
import magic
import re

# Libraries
from tinydb import TinyDB, where

# Bucephalus imports
import config
from exceptions import *


#
# Metadata database management
#

class NoMetadataError(BucephalusException):
    """ A path has no metadata associated to it. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "No metadata for: " + str(path)
        super(NoMetadataError, self).__init__(msg)
        self.path = path


class TooManyMetadataError(BucephalusException):
    """ A path has more than one metadata entry associated to it. """
    def __init__(self, path, docids, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Too many metadata entries for: " + str(path) + "\n[Internal] Document ID's: " + str(docids)
        super(TooManyMetadataError, self).__init__(msg)
        self.path = path
        self.docids = docids


def get_database_object():
    """ Open the correct TinyDB. """

    return TinyDB(config.get_metadata_file_path(), indent=2)


def read_path_metadata(path):
    """ Return the metadata associated with our path as a dict. """

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

class InvalidPagePathError(BucephalusException):
    """ An invalid (i.e. non-conforming formtat) page path was chucked our way by someone nasty. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Invalid page path: " + str(path)
        super(InvalidPagePathError, self).__init__(msg)
        self.path = path


class NonexistentPagePathError(BucephalusException):
    """ A non-existent (i.e. may be valid but does not physically exist) page path was chucked our way by someone nasty. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Non-existent page path: " + str(path)
        super(NonexistentPagePathError, self).__init__(msg)
        self.path = path


# Compile our regular expression first, so we don't do it every time we need it.
_valid_path_re = re.compile(r"(\b/[A-Z][a-z]+(/[A-Z]\w)+\b)")


def valid_path(path):
    """ Decide whether path is a valid path for a page that might or might not exist. """
    return False if _valid_page_path_re.fullmatch(path) is None else True


def path_exists(path):
    """ Actually check whether the given path exists in the database. """

    if not valid_page_path(path):
        raise InvalidPagePathError(path)

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

class FileIsDirectoryError(BucephalusException):
    """ Expected a file, got a directory. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Unexpectedly a directory: " + str(path)
        super(FileIsDirectoryError, self).__init__(msg)
        self.path = path


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
