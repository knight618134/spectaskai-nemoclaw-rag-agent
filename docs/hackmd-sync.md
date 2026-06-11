# HackMD Sync

更新日期：2026-06-11

本專案使用 `scripts/sync_to_hackmd.py` 將本地 Markdown 同步到 HackMD。token 不寫入 repo，請用環境變數提供。

## 1. 建立 HackMD API token

到 HackMD Settings 建立 API token。HackMD API 使用 Bearer authentication：

```text
Authorization: Bearer <token>
```

可先測試 token：

```bash
export HACKMD_API_TOKEN="你的 token"
curl "https://api.hackmd.io/v1/me" \
  -H "Authorization: Bearer $HACKMD_API_TOKEN"
```

## 2. 建立新的 HackMD note

```bash
export HACKMD_API_TOKEN="你的 token"
python scripts/sync_to_hackmd.py \
  docs/nemoclaw-nemotron3-skill-tool-rag-roadmap.md \
  --read-permission owner \
  --write-permission owner
```

成功後會輸出：

```text
Created HackMD note id: ...
Publish link: ...
```

請把 note id 記下來，之後可更新同一篇。

## 3. 更新既有 HackMD note

目前 roadmap 對應的 HackMD note：

```text
note id: jLoQL262Rla1xcneVMvC1Q
publish link: https://hackmd.io/@PGOQ-dmhQB2FiBLxI64sug/SJmVeUdbGg
```

家用 NemoClaw playground 對應的 HackMD note：

```text
note id: 9AWNjpmoT9-3Dq-qRkKKbg
publish link: https://hackmd.io/@PGOQ-dmhQB2FiBLxI64sug/BkarGLd-fg
```

```bash
export HACKMD_API_TOKEN="你的 token"
python scripts/sync_to_hackmd.py \
  docs/nemoclaw-nemotron3-skill-tool-rag-roadmap.md \
  --note-id "jLoQL262Rla1xcneVMvC1Q"
```

## 3.1 同步 O-RAN AI Self-Healing 文件

若要建立新的 HackMD note：

```bash
export HACKMD_API_TOKEN="你的 token"
python scripts/sync_to_hackmd.py \
  docs/product-research-brief.md \
  --read-permission guest \
  --write-permission owner
```

若已經建立 note，請把 note id 記錄在這裡：

```text
product research note id: hJiT66tNQHGiLnJk_1LC3A
publish link: https://hackmd.io/@PGOQ-dmhQB2FiBLxI64sug/ByAWuLuWzg
```

更新既有 note：

```bash
export HACKMD_API_TOKEN="你的 token"
python scripts/sync_to_hackmd.py \
  docs/product-research-brief.md \
  --note-id "hJiT66tNQHGiLnJk_1LC3A"
```

## 4. 權限建議

會議共編時：

```bash
python scripts/sync_to_hackmd.py docs/nemoclaw-nemotron3-skill-tool-rag-roadmap.md \
  --read-permission guest \
  --write-permission signed_in
```

正式內部文件時：

```bash
python scripts/sync_to_hackmd.py docs/nemoclaw-nemotron3-skill-tool-rag-roadmap.md \
  --read-permission owner \
  --write-permission owner
```

## 5. 注意

- HackMD 的 note title 會優先取 Markdown 第一個 H1。
- 若要避免覆蓋線上共編內容，請先從 HackMD 匯出最新 Markdown，再同步本地檔案。
- 不要把 `HACKMD_API_TOKEN` 寫進 `.env` 後提交到 Git。
