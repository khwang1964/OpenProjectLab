# Generation Manifest

## 目的

Generation Manifest 是 OpenProjectLab 的產物索引。每次 Bootstrap、Course 或 Week Generator 成功產生檔案時，預設同步更新：

```text
<project>/.opl/manifest.yaml
```

## 架構

```text
CLI → Generator → TemplateRenderer / FileSystem
                  └→ GenerationManifest → .opl/manifest.yaml
```

Generator 先完成模板渲染與既有 Manifest 驗證，再寫入產物，最後以原子寫入更新 Manifest。`dry-run` 會完成所有驗證與序列化，但不建立任何檔案。

## 格式

```yaml
schema_version: "1.0"
project:
  slug: modern-java
  name: Modern Java in Action
generated:
  - path: README.md
    generator: course
    template: course/README.md.j2
    metadata:
      weeks: 16
  - path: week-01/README.md
    generator: week
    template: week/README.md.j2
    metadata:
      week: 1
      title: 課程介紹
```

相同 `path` 再次記錄時會更新原項目，不會建立重複資料。

## 路徑安全

- 只允許專案內相對路徑。
- 統一儲存為 `/` 分隔的 POSIX 路徑。
- 拒絕絕對路徑、空路徑及 `..` 跳脫。
- 絕對輸出路徑必須位於 `project_root` 之下。

## CLI

Manifest 預設啟用：

```powershell
opl course modern-java --name "Modern Java in Action"
opl week modern-java --week 1 --title "課程介紹"
```

特殊情況可停用：

```powershell
opl course modern-java --name "Modern Java in Action" --no-manifest
```

## API

```python
manifest = GenerationManifest.load(project_root)
manifest.set_project(slug="modern-java", name="Modern Java in Action")
manifest.record(
    project_root / "week-01" / "README.md",
    generator="week",
    template="week/README.md.j2",
    metadata={"week": 1, "title": "課程介紹"},
)
manifest.save()
```

## 測試

```powershell
python -m pytest tests/core/test_generation_manifest.py `
  tests/integration/test_manifest_integration.py -v --no-cov
python -m pytest -v
```

## Code Review Checklist

- [ ] schema 版本被嚴格驗證
- [ ] YAML 格式錯誤轉換為 GenerationManifestError
- [ ] 所有記錄路徑都是安全相對路徑
- [ ] 相同產物路徑採更新而非重複新增
- [ ] UTF-8 與繁體中文可往返保存
- [ ] dry-run 無檔案系統副作用
- [ ] Generator 預設記錄 Manifest
- [ ] `--no-manifest` 僅供明確停用
- [ ] 產物寫入失敗時不更新 Manifest
- [ ] 單元、整合與完整回歸測試通過
