# 安裝 OpenProjectLab

本章說明 OpenProjectLab（OPL）的一般 installed-user 安裝流程。

目前 v1.0 文件是在 release stabilization 階段建立。現行 project metadata 將 package 識別為 `openprojectlab`，並要求 Python 3.12 或更新版本。在目前 stabilization baseline 中，package version 為 `0.6.0`；最終 v1.0 release process 將建立正式的 v1.0 artifact/version relationship。

本章不會宣稱 v1.0 package 已經發布到 public package index。

## 1. 系統需求

目前 package metadata 要求：

```text
Python >= 3.12
```

Python runtime dependencies：

```text
Jinja2 >= 3.1
PyYAML >= 6.0
```

package 安裝後提供的 console entry point：

```text
opl
```

environment support claims 屬於後續 v1.0 Support Matrix 工作。上述 Python metadata 是 package requirements，不應解讀成更廣泛的 operating-system support guarantee。

## 2. 建議使用隔離的 Virtual Environment

使用符合需求的 Python interpreter 建立 virtual environment。

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

如果 Python 3.14 不是你要使用的 interpreter，請選擇其他符合 package requirement 的已安裝 Python 版本。

### POSIX shells

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
```

## 3. 安裝 Built Wheel

Step 8.4 已透過使用者實際會安裝的 artifact 驗證 OPL。

假設你已取得本機 wheel：

```text
<distribution-directory>/openprojectlab-<version>-py3-none-any.whl
```

執行：

```console
python -m pip install <wheel-path>
```

例如 Step 8.4 stabilization artifact 為：

```text
openprojectlab-0.6.0-py3-none-any.whl
```

因此本機驗證指令可能是：

```console
python -m pip install ./dist/openprojectlab-0.6.0-py3-none-any.whl
```

實際路徑取決於你取得 artifact 的位置。

不要把上述 stabilization filename 視為最終 v1.0 version number 的承諾。

## 4. 驗證安裝

先確認 Python package 可以 import：

```console
python -c "import generator; print(generator.__file__)"
```

輸出的 path 應指向目前安裝 environment，而不是 OpenProjectLab source checkout。

再驗證 CLI：

```console
opl --help
```

並列出已安裝的 built-in Generators：

```console
opl list
```

目前 built-in list 包含：

```text
assignment
bootstrap
course
lab
quiz
slides
website
week
```

Generator identities 旁可能同時顯示 descriptions。

## 5. 驗證 Package-Owned Runtime Resources

正常 installed use 不應依賴 repository-level `templates/` directory。

內建 runtime templates 透過 `generator.resources` boundary 包裝。

一般使用者不需要直接檢查這個內部 path。真正的 user-facing verification，是在 source repository 外成功執行 built-in Generator。

[快速開始](quick-start.md)會完成這項代表性驗證。

## 6. 選擇 Output Directory

installed-user workflow 建議明確指定 output root。

例如：

```console
opl --output-root ./opl-output list
```

`list` 本身不會生成 output，但此例顯示 global option 的位置。

generation command 可以使用你有寫入權限的位置：

```console
opl --output-root ./opl-output course demo-course --name "Demo Course"
```

onboarding 時明確指定 output root，可以避免依賴 implementation-derived default paths。

## 7. Template Root Override

內建 Generators 正常情況下使用 package-owned templates。

若你確實要改用不同的 template tree，CLI 提供：

```text
--template-root DIR
```

例如：

```console
opl --template-root ./custom-templates --output-root ./opl-output course demo-course --name "Demo Course"
```

custom template root 是 advanced override，會改變 Generator 使用的 templates，因此也可能改變 output content。

一般 v1.0 onboarding path 應使用 package-owned templates。

## 8. Configuration File Override

CLI 提供：

```text
--config FILE
```

使用者提供的 configuration file 可以設定 path-related configuration。

如果 installed environment 中不存在 built-in default configuration file，CLI 會在未載入該 default file 的情況下繼續執行；但明確指定的 configuration file 仍會被載入並驗證。

完整 configuration surface 將由[組態設定](configuration.md)章節說明。

## 9. 不要把 Editable Installation 當作一般使用者安裝方式

以下指令適合 development：

```console
python -m pip install -e .
```

但它**不是**主要的 v1.0 user-installation workflow。

editable installation 可能意外讓 repository files 可被 runtime 使用，因而掩蓋 packaging defects。

v1.0 release-readiness path 驗證的是：

```text
build artifact
    ↓
install wheel in a clean environment
    ↓
import installed package
    ↓
resolve package resources
    ↓
run installed opl command
    ↓
generate representative artifact
```

## 10. Developer Installation

如果你是在開發 OPL 本身，development installation 可能是合理選擇。該流程屬於 contributor/development documentation，而不是一般 installed-user Quick Start。

專案的 development extras 包含 `build`、`pytest`、`pytest-cov`、`ruff`、`pre-commit`、`mypy`、`twine` 等工具。

不要從 development-only dependencies 推導一般使用者 requirements。

## 11. 安裝驗證 Checklist

安裝後請確認：

```text
[ ] Python environment 符合 package requirement。
[ ] openprojectlab wheel 安裝成功。
[ ] 在 repository 外執行 import generator 成功。
[ ] opl --help 成功。
[ ] opl list 成功。
[ ] 有可寫入的 output directory。
[ ] Quick Start 的代表性 generation 成功。
```

## 12. 本章不承諾的事項

本章不定義：

- 最終 v1.0 publication location；
- 最終 v1.0 release filename；
- operating-system support guarantees；
- long-term compatibility/deprecation policy；
- release signing policy；
- 未來版本之間的 upgrade guarantees。

這些項目屬於後續 Milestone 8 release-readiness gates。

## 下一步

請繼續[快速開始](quick-start.md)。
