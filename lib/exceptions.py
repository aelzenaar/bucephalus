""" This module contains the basic exception classes for bucephawiki. """

class BucephalusException(Exception):
    """ Basic exception for errors raised by bucephalus. """

class UnimplementedError(BucephalusException):
    """ The functionality is unimplemented. """

    def __init__(self, wat, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Unimplemented: " + str(wat)
        super(NoMetadataError, self).__init__(msg)
        self.wat = wat

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


class MetadataMismatchError(BucephalusException):
    """ A path and its associated metadata don't match in some way. """
    def __init__(self, path, metadata, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Mismatched metadata for: " + str(path) + "\nMetadata:" + str(metadata)
        super(MetadataMismatchError, self).__init__(msg)
        self.path = path
        self.metadata = metadata

class InvalidPathError(BucephalusException):
    """ An invalid (i.e. non-conforming formtat) page path was chucked our way by someone nasty. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Invalid page path: " + str(path)
        super(InvalidPathError, self).__init__(msg)
        self.path = path


class NonexistentPathError(BucephalusException):
    """ A non-existent (i.e. may be valid but does not physically exist) page path was chucked our way by someone nasty. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Non-existent page path: " + str(path)
        super(NonexistentPathError, self).__init__(msg)
        self.path = path

class WrongPathTypeError(BucephalusException):
    """ Different file type to expected. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Not correct path type: " + str(path)
        super(FileNotDirectoryError, self).__init__(msg)
        self.path = path

class FileIsDirectoryError(WrongPathTypeError):
    """ Expected a file, got a directory. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Unexpectedly a directory: " + str(path)
        super(FileIsDirectoryError, self).__init__(path,msg)

class FileNotDirectoryError(WrongPathTypeError):
    """ Expected a directory, but didn't get one. """
    def __init__(self, path, msg=None):
        if msg is None:
            # Set some default useful error message
            msg = "Not a directory: " + str(path)
        super(FileNotDirectoryError, self).__init__(path,msg)
