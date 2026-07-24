class OPLGeneratorError(Exception):
    """OPL Framework 基礎例外。"""


class ValidationError(OPLGeneratorError):
    pass


class GeneratorNotFoundError(OPLGeneratorError):
    pass


class ConfigurationError(OPLGeneratorError):
    pass


class TemplateError(OPLGeneratorError):
    pass


class PluginError(OPLGeneratorError):
    pass
