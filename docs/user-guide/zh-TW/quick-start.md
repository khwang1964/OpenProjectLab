# 快速開始：OpenProjectLab 的 First 15 Minutes

本 Quick Start 提供一個小型但具代表性的 installed-user workflow。

目標是驗證完整路徑：

```text
installed OPL
    ↓
working CLI
    ↓
package-owned runtime templates
    ↓
Course Generator
    ↓
generated README.md
```

此流程刻意避免 editable installation、`PYTHONPATH` 與 repository-only templates。

## 開始之前

請先完成[安裝](installation.md)。

你應該已經具備：

- 一個已安裝 `openprojectlab` distribution 的 active Python environment；
- 可執行的 `opl` command；
- 可寫入的 working directory。

以下範例使用：

```text
opl-quick-start/
```

作為暫時 working location。

## 1. 建立乾淨的 Working Directory

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force opl-quick-start | Out-Null
Set-Location opl-quick-start
```

### POSIX shells

```bash
mkdir -p opl-quick-start
cd opl-quick-start
```

這個 directory 不需要 OpenProjectLab source checkout。

## 2. 驗證 CLI

執行：

```console
opl --help
```

你應該會看到 OpenProjectLab command-line help。

接著查看 built-in Generators：

```console
opl list
```

目前 built-in identities：

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

command 會在這些名稱旁顯示 descriptions。

## 3. 使用 Dry Run 預覽 Course Generation

明確指定 output root：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en --dry-run
```

這個 request 表示：

- `./output` 是 generation output root；
- `course` 選擇 Course Generator；
- `demo-course` 是 project slug；
- `--name "Demo Course"` 提供 course name；
- `--weeks 4` 提供 course length metadata；
- `--language en` 提供 authored language value；
- `--dry-run` 要求執行 validation/planning，但不持久化正常 output。

dry run 完成後，正常生成的 course README 不應被持久化於：

```text
output/demo-course/README.md
```

## 4. 生成 Course

執行相同 request，但移除 `--dry-run`：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

Course Generator 的 target：

```text
output/demo-course/
```

並生成代表性 artifact：

```text
output/demo-course/README.md
```

預設情況下，generation 也會參與既有 manifest behavior，除非提供 `--no-manifest`。

## 5. 查看 Generated Artifact

### Windows PowerShell

```powershell
Get-Content .\output\demo-course\README.md
```

### POSIX shells

```bash
cat ./output/demo-course/README.md
```

你應該會看到由 installed package-owned Course template，以及 CLI request 中提供的 values 所 render 出來的 course README。

實際 Markdown 內容屬於 template contract，未來可以在適用的 compatibility rules 下演進。Quick Start 的關鍵保證，是 installed Course Generator 能解析 packaged template，並產生預期 artifact path。

## 6. 查看 Generated Tree

### Windows PowerShell

```powershell
Get-ChildItem .\output\demo-course -Recurse
```

### POSIX shells

```bash
find ./output/demo-course -maxdepth 3 -type f -print
```

代表性 Course artifact 至少應包含：

```text
output/
└── demo-course/
    └── README.md
```

由於此 command 預設啟用 manifest recording，也可能存在 OPL-owned manifest metadata。

## 7. 選用：不記錄 Manifest

如果你刻意不希望 command 更新 generation manifest，可以使用：

```console
opl --output-root ./output course no-manifest-course --name "No Manifest Course" --weeks 4 --language en --no-manifest
```

這會改變 manifest behavior，但不會改變 Course Generator identity 或 canonical lifecycle。

## 8. 選用：測試 Overwrite Protection

再次執行相同的正常 generation command：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

由於 target artifact 已存在，既有 write policy 可能拒絕操作，而不是默默覆蓋使用者內容。

如果你確實要 overwrite，CLI 提供 `--force`：

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en --force
```

overwrite 應該是明確決定。不要把 `--force` 當成處理 user-authored content 的預設習慣。

## 9. 你剛剛驗證了什麼

這個小型 workflow 驗證了多個重要 v1.0 concepts：

```text
installed console entry point
        ↓
opl list
        ↓
global output-root resolution
        ↓
Course Generator request
        ↓
validation and planning
        ↓
package-owned template resolution
        ↓
filesystem write
        ↓
README.md artifact
```

它同時證明一般 onboarding path 不需要：

```text
source checkout
editable install
PYTHONPATH
repository-level templates
```

## 10. 常見問題

### 找不到 `opl`

確認安裝 OPL 的 environment 已啟用。

也可以執行：

```console
python -m pip show openprojectlab
```

如果 package 安裝在其他 environment，請啟用該 environment 後再試。

### `python -c "import generator"` 失敗

先檢查 package：

```console
python -m pip show openprojectlab
```

再確認 Python executable 與 `pip` 屬於同一個 environment：

```console
python -c "import sys; print(sys.executable)"
python -m pip --version
```

### Output directory 無法寫入

改用你的 user account 可寫入的 output root：

```console
opl --output-root <writable-directory> course demo-course --name "Demo Course"
```

### Target file 已存在

可以使用另一個 project slug；或在確認內容後移除／搬移既有 output；如果 overwrite 確實合理，也可以明確使用 `--force`。

## 11. 清除 Tutorial Output

不再需要 Quick Start files 時，請使用一般 filesystem tools 移除 `opl-quick-start` working directory。

不要自動刪除與本教學無關的 paths。

## 12. 下一步

完成 First 15 Minutes workflow 後，可以繼續閱讀：

- [組態設定](configuration.md)
- [CLI](cli.md)
- [Generators](generators.md)
- [Courseware](courseware.md)

如果你計畫擴充 OPL，之後再閱讀 [Plugins](plugins.md)。

## Automation Note

v1.0 documentation contract 要求此代表性 onboarding path 最終成為 executable documentation smoke test。

因此本章刻意使用可以在 CI 中 deterministic verification 的 commands 與 artifact expectations 撰寫，而不是只提供無法驗證的敘述性範例。
