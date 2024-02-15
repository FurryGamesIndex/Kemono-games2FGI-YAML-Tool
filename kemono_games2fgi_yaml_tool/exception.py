class ConverterError(Exception):
    pass


class FolderStructureError(ConverterError):
    pass


class InvalidYAMLDataError(ConverterError):
    pass


class UnsupportedTagList(ConverterError):
    pass


class InvalidHTTPStatusCodeError(ConverterError):
    pass
