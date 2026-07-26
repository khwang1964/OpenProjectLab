class OPLGeneratorError(Exception):
    """OPL Framework 基礎例外。"""


class ValidationError(OPLGeneratorError):
    """輸入資料或執行條件驗證失敗。"""

    pass


class GeneratorNotFoundError(OPLGeneratorError):
    """找不到指定的 Generator。"""

    pass


class ConfigurationError(OPLGeneratorError):
    """設定檔不存在或內容無效。"""

    pass


class TemplateError(OPLGeneratorError):
    """模板載入、驗證或渲染失敗。"""

    pass


class PluginError(OPLGeneratorError):
    """外掛探索或載入失敗。"""

    pass
