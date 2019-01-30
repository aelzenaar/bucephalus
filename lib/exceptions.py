""" This module contains the basic exception classes for bucephawiki. """

class BucephalusException(Exception):
    """ Basic exception for errors raised by bucephalus. """

class UnimplementedError(BucephalusException):
    """ The functionality is unimplemented. """

    def __init__(self, wat, msg=msg):
        if msg is None:
            # Set some default useful error message
            msg = "Unimplemented: " + str(wat)
        super(NoMetadataError, self).__init__(msg)
        self.wat = wat
