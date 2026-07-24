# Framework v0.6 設計

## 目標

v0.6 將 OPL 從「可執行的 Generator 框架」推進為「可診斷、可描述、可擴充的框架」。

## 架構

```text
CLI
├── list
├── doctor ──> Core Doctor Checks
└── generators ──> Registry ──> Generator SDK

Generator Manifest (YAML)
└── name / version / description / entrypoint
```

## 關鍵決策

1. `opl doctor` 僅做唯讀檢查，不修改專案。
2. Doctor 回傳結構化 `DoctorCheck`，CLI 只負責顯示與 exit code。
3. Manifest 由獨立 Domain Model 驗證，避免把外掛描述資料耦合到 CLI。
4. 所有新增能力維持 Python 3.12+，不增加第三方相依套件。

## 相容性

- 保留 `opl list` 與 legacy `opl --list`。
- Bootstrap、Course、Week Generator 介面不變。
