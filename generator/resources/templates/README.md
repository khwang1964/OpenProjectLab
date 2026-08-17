# OpenProjectLab Template Pack v1.0

此目錄是 OpenProjectLab 的預設模板根目錄。

## 必要模板

BootstrapGenerator：

- `bootstrap/project/README.md.j2`
- `bootstrap/project/LICENSE.j2`
- `bootstrap/project/CONTRIBUTING.md.j2`
- `bootstrap/project/gitignore.j2`
- `bootstrap/project/course.yaml.j2`

CourseGenerator：

- `course/README.md.j2`

WeekGenerator：

- `week/README.md.j2`

## 模板規則

- 編碼一律使用 UTF-8。
- 模板路徑一律使用相對路徑。
- 禁止使用 `..` 路徑跳脫。
- 模板必須可在 Jinja2 `StrictUndefined` 模式下編譯與渲染。
- 新增或修改模板時，必須同步更新 `manifest.yaml`、測試與文件。
