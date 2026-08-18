# AI Integration

OpenProjectLab 提供 provider-independent AI contracts，用於 AI-assisted courseware workflows。Provider invocation 刻意與 OPL domain validation、Generator execution 分離。

## Core contracts

AI core 提供：

```text
AIRequest
AIResponse
AIProvider
```

`AIRequest` 是 immutable value，包含 `task`、`instructions`、`context` 與 optional `response_contract`。

`AIResponse` 包含彈性的 `content` 與 provider `metadata`。

`AIProvider` 是 runtime-checkable protocol：

```python
def generate(request: AIRequest) -> AIResponse:
    ...
```

如此 downstream OPL code 不必綁定 vendor SDK。

## Provider boundary

provider adapter 負責轉換：

```text
OPL AIRequest / AIResponse
        ↕
provider-specific API
```

credentials、HTTP behavior、retries、model names 與 vendor exceptions 應留在 courseware domain model 之外。

## Course generation

`AICourseGenerationService` 執行：

```text
AIRequest
→ AIProvider.generate()
→ AIResponse
→ validated course mapping
→ Course
```

結果使用與 non-AI courseware 相同的 `Course` domain model。

AI-generated content 在 mapping/validation 成功前都是 untrusted structured input：

```text
AI output ≠ validated OPL domain object
```

## 其他 AI-assisted services

repository 包含 courseware assistance、documentation、review、template completion 等 AI-oriented services。它們共用 provider-independent boundary，但可以有不同 response contracts。

這些 services 的存在不代表每個 capability 都是 stable end-user CLI command。

## CLI 與 configuration boundaries

documented v1.0 CLI 沒有 general `ai` command，因此本手冊不會自行發明 `opl ai ...`。

同樣地，不應假設 generic OPL YAML configuration 會設定所有 providers。API keys、endpoints、model identifiers、timeouts、retry policies 應由 chosen adapter/deployment 管理，除非另有明確 OPL contract。provider secrets 不應 commit 到 repository。

## Testing

一般 contract tests 應使用 deterministic test providers，而不是 live network services。如此 request、mapping、failure、orchestration tests 可在沒有 external credentials 的 CI 中執行。

若有 live provider tests，應維持為獨立受控 integration boundary。

## AI 與 Generators

責任保持分離：

```text
AI service   → propose/produce structured content
Generator    → validate request → plan artifacts → execute writes
```

provider adapter 不應繞過 Generator validation，也不應成為 hidden filesystem writer。

### Checklist

- provider boundary 使用 `AIRequest` / `AIResponse`。
- 實作 `AIProvider`，不要讓 domain code 綁定 vendor SDK。
- 建立 OPL domain value 前驗證 AI output。
- provider metadata 與 courseware state 分離。
- writes 不繞過 Generator planning。
- secrets 不進 repository/examples。
- normal CI 優先使用 deterministic test providers。
- 不假設 `opl ai` 存在。

## 下一步

繼續閱讀 [Marketplace](marketplace.md)。
