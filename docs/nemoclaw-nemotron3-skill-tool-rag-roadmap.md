# NemoClaw + Nemotron-3 Skill/Tool/RAG Roadmap

更新日期：2026-06-11

這份文件把目前的 SpecTaskAI / NemoClaw / OpenClaw / Nemotron-3 / OpenProject 方向拆成「先做什麼、為什麼、做到什麼程度算成功」。重點不是一次做完整系統，而是先建立一個最小可展示的閉環：

```text
使用者自然語句
  -> OpenClaw agent
  -> runtime tool
  -> OpenProject 或 spec RAG
  -> Nemotron-3 整理結果
  -> 回答使用者或回寫 OpenProject
```

## 1. 先釐清四個名詞

### NemoClaw 是安全執行環境

NemoClaw 負責建立 sandbox、控管網路、工具、檔案與推理服務。它本身不是你的業務邏輯。

可以把它想成：

```text
NemoClaw = 安全隔離的執行房間
```

你要先確認這個房間可以啟動、可以連模型、可以跑 OpenClaw agent：

```bash
nemoclaw list
nemoclaw my-assistant status
nemoclaw inference get
nemoclaw my-assistant exec -- openclaw agent --agent main -m "hello"
```

### Nemotron-3 是推理模型

Nemotron-3 負責理解文字、推理、摘要、分類、產生回答。它不會自動知道如何打 OpenProject API，也不會自動讀整個 PDF repository。

可以把它想成：

```text
Nemotron-3 = 大腦
```

但大腦要能做事，需要工具。

### Skill 是行為說明與使用方式

Skill 通常包含：

- 什麼情境要使用這個能力。
- 自然語句如何對應到意圖。
- 可執行腳本或操作範例。
- 輸入輸出格式。

可以把它想成：

```text
Skill = 使用說明書 + 操作規則
```

重要觀念：skill 不一定等於 agent 可以直接穩定呼叫的 tool。你之前遇到的狀況就是社群 OpenProject skill CLI 可以跑，但 agent 不一定會自動、穩定地用對 CLI。

### Runtime tool 是 agent 真正可以呼叫的動作

Runtime tool 是給 OpenClaw agent 直接呼叫的函式能力，例如：

```text
openproject_project_list
openproject_work_package_create
openproject_comment_add
spec_search
spec_answer
```

可以把它想成：

```text
Runtime tool = agent 手上的按鈕
```

所以短期最佳策略是：

```text
先做少量高價值 runtime tools
再用 skill 告訴 agent 何時該按哪個按鈕
```

## 2. 最小可行版本應該長什麼樣

不要一開始就做完整 RAG、完整 OpenProject API wrapper、完整多文件分析。第一個版本只需要證明三件事：

```text
1. agent 能聽懂自然語句
2. agent 能呼叫 tool
3. tool 能把結果交給 Nemotron-3 或 OpenProject
```

建議的 MVP 是兩條閉環。

### 閉環 A：OpenProject 任務操作

```text
User:
  請列出 demo-project 最新 5 個 task

OpenClaw agent:
  -> openproject_work_package_list
  -> 回覆 id / subject / status
```

成功標準：

```text
toolSummary.calls >= 1
toolSummary.tools includes openproject_work_package_list
toolSummary.failures = 0
```

### 閉環 B：單份文件問答

```text
User:
  這份 spec 裡 GNSS 的範圍是什麼？

OpenClaw agent:
  -> spec_search
  -> Nemotron-3 根據搜尋片段回答
  -> 回覆答案與來源頁碼/章節
```

第一版不用真正 vector DB，也可以先用關鍵字/全文搜尋。重點是先把 `spec_search` 和 `spec_answer` 的 tool 介面定下來。

## 3. 推薦階段

### Phase 0：確認既有環境

目的：確認 NemoClaw、Nemotron-3、OpenClaw 都能動。

要做：

```bash
nemoclaw list
nemoclaw my-assistant status
nemoclaw inference get
nemoclaw my-assistant exec -- openclaw agent --agent main -m "hello"
```

完成定義：

- sandbox 是 Ready。
- inference 指到 Nemotron-3。
- `hello` 能得到模型回答。

### Phase 1：先做 OpenProject runtime tools

目的：讓 agent 真的能操作 OpenProject。

已經驗證可用的方向：

```text
plugins/openproject-tool
  -> openproject_project_list
  -> openproject_work_package_list
  -> openproject_work_package_create
  -> openproject_comment_add
```

建議先只保留最常用 4 個：

| Tool | 目的 |
|---|---|
| `openproject_project_list` | 確認連線與專案 |
| `openproject_work_package_list` | 查任務 |
| `openproject_work_package_create` | 建任務 |
| `openproject_comment_add` | 回寫 AI 結果 |

完成定義：

- 自然語句可以列專案。
- 自然語句可以列 task。
- 控制情境下可以建立一張測試 task。
- 可以把一段文字加成 comment。

### Phase 2：補一個 openproject-agent skill

目的：教 agent 何時該用哪個 OpenProject tool。

skill 的內容應該是意圖對照，而不是塞一堆 API 細節：

```text
「列 project / 有哪些專案」
  -> openproject_project_list

「列 task / 查工作項目 / show issues」
  -> openproject_work_package_list

「開 task / 建任務 / 新增工作項目」
  -> openproject_work_package_create

「留言 / 加 comment / 回覆到 task」
  -> openproject_comment_add
```

完成定義：

- 不需要明講 tool 名稱，agent 也會選對工具。
- agent 回答格式穩定。
- 寫入型操作前可以辨識 project、subject、type。

### Phase 3：建立最小 RAG tool

目的：讓 agent 可以查文件，而不是只靠模型記憶。

第一版建議先做 local JSON index，不急著上 vector DB：

```text
PDF
  -> pdfplumber 抽文字
  -> 依頁碼/章節切 chunk
  -> 存成 data/spec_index.jsonl
  -> spec_search 用關鍵字或簡單分數搜尋
  -> spec_answer 把 top chunks 交給 Nemotron-3
```

最小資料格式：

```json
{
  "spec_id": "cobra-oru-sdk-ug",
  "title": "Cobra O-RU SDK User Guide",
  "version": "unknown",
  "page": 12,
  "section": "GNSS",
  "chunk_id": "cobra-oru-sdk-ug:p12:001",
  "text": "..."
}
```

建議先做 4 個 RAG tools：

| Tool | 目的 |
|---|---|
| `spec_list` | 列出已索引文件 |
| `spec_ingest` | 把 PDF 轉成 chunks |
| `spec_search` | 查相關片段 |
| `spec_answer` | 根據片段產生答案 |

完成定義：

- 能 ingest 一份 PDF。
- 能針對問題找出 top 3-5 個片段。
- 回答會附 `spec_id`、page、section。
- 不知道時要說找不到，不要硬編。

### Phase 4：把 RAG 和 OpenProject 串起來

目的：讓文件分析結果可以進入任務管理流程。

示範流程：

```text
User:
  幫我分析 GNSS 相關需求，整理成 task 放到 demo-project。

Agent:
  1. spec_search("GNSS requirements")
  2. spec_answer(...)
  3. openproject_work_package_create(...)
  4. openproject_comment_add(...來源段落...)
```

完成定義：

- 可以從文件查出需求。
- 可以建立 task。
- 可以把來源段落與分析結果寫入 comment。

## 4. RAG 到底在分析什麼

RAG 不是「把 PDF 丟給模型」。RAG 是一個流程：

```text
1. Ingestion：把 PDF 轉成可搜尋資料
2. Chunking：切成段落，每段帶 metadata
3. Retrieval：根據問題找出相關段落
4. Generation：把相關段落交給模型回答
5. Citation：告訴使用者答案來自哪份文件、哪頁、哪章
```

它解決三個問題：

| 問題 | 沒有 RAG | 有 RAG |
|---|---|---|
| 大型 PDF 太長 | 塞不進 prompt | 只取相關 chunks |
| 多份 spec | 模型不知道查哪份 | 先搜尋再回答 |
| 可信度 | 答案沒有來源 | 回答附 page/section |

所以 RAG layer 應該放在 OpenProject 外面：

```text
OpenProject = 任務、留言、流程紀錄
RAG service/tool = 文件解析、搜尋、引用答案
Nemotron-3 = 根據檢索結果推理與生成
```

## 5. 建議的 repo 結構

目前這個 repo 可以先長成這樣：

```text
docs/
  nemoclaw-nemotron3-skill-tool-rag-roadmap.md
  combined-guide.md
  architecture.md

plugins/
  openproject-tool/
    plugin manifest and runtime tools
  spec-rag-tool/
    plugin manifest and runtime tools

openclaw-skills/
  openproject-agent/
    SKILL.md
  spec-rag-agent/
    SKILL.md

src/
  pdf_parser.py
  rag_indexer.py
  rag_search.py
  nemotron_client.py
  openproject_client.py

data/
  specs/
    input PDFs
  indexes/
    spec_index.jsonl
```

## 6. 現在最該先做的三件事

### 第一件：固定 OpenProject tool baseline

不要再糾結 skill CLI 為什麼 agent 不穩。把 OpenProject 操作固定成 runtime tools，skill 只負責意圖對應。

第一個 demo 指令：

```bash
nemoclaw my-assistant exec -- openclaw agent --agent main --json \
  -m "請列出 demo-project 目前最新的工作項目，最多 5 筆，只回覆 id、subject、status。"
```

### 第二件：做最小 spec_search

先不要急著 embedding。先把一份 PDF 變成 `spec_index.jsonl`，讓 agent 可以搜尋。

第一版 `spec_search` 可以只做：

```text
query
  -> lowercase
  -> keyword score
  -> return top 5 chunks
```

### 第三件：做 spec_answer

`spec_answer` 不負責搜尋所有文件，它只拿 `spec_search` 找到的 chunks，請 Nemotron-3 根據來源回答。

回答格式固定：

```text
Answer:
...

Sources:
- cobra-oru-sdk-ug, page 12, section GNSS
- cobra-oru-sdk-ug, page 14, section Timing
```

## 7. 一句話版本

先不要把「NemoClaw + Nemotron-3 + skill + tool + RAG」想成一個大系統。它其實是這樣分工：

```text
NemoClaw：安全地跑 agent
Nemotron-3：負責理解與生成
Skill：告訴 agent 什麼時候該做什麼
Tool：讓 agent 真的能做事
RAG：讓 agent 先查文件，再根據來源回答
OpenProject：保存任務、留言、流程結果
```

第一個真正有價值的版本就是：

```text
自然語句
  -> 查文件
  -> 用 Nemotron-3 產生帶來源答案
  -> 建 OpenProject task
  -> 把答案與來源貼到 comment
```
