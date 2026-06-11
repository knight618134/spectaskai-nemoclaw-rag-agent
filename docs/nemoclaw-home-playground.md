# NemoClaw Home Playground

更新日期：2026-06-11

這份筆記是給「在家裡玩 NemoClaw」用的最小安全路線。目標不是一次重建公司 demo，而是先建立一個乾淨、低風險、可重複實驗的 sandbox。

## 1. 家裡先不要做什麼

先不要：

- 放公司 OpenProject API token。
- 連公司內網或公司 VPN。
- 把正式 PDF 規格書丟進去。
- 安裝來源不明的第三方 skill。
- 一開始就開大範圍網路 policy。

先做：

```text
NemoClaw sandbox
  -> OpenClaw agent hello
  -> Nemotron-3 推理測試
  -> 本地 Markdown / toy PDF 查詢
  -> 小型 spec_search demo
```

## 2. 家用 playground 的目標

第一天只要完成三件事：

```text
1. sandbox 能啟動
2. Nemotron-3 能回答
3. agent 能使用一個非常小的本地 tool
```

不要急著接 OpenProject。OpenProject 是第二階段。

## 3. 建議命名

如果你家裡已經有 `my-assistant`，可以繼續用。若要跟公司 demo 分開，建議命名：

```text
home-assistant
```

這樣你之後看指令時比較不會混淆：

```text
my-assistant    = 之前已驗證 demo
home-assistant  = 家裡實驗用
```

## 4. 基礎檢查

先確認 CLI 與 Node 環境：

```bash
source ~/.nvm/nvm.sh
nvm use 22
node --version
nemoclaw --version
```

如果安裝 NemoClaw 最後出現這種錯誤：

```text
npm error code EACCES
npm error syscall symlink
npm error dest /usr/local/lib/node_modules/nemoclaw
```

代表安裝器要把 `nemoclaw` CLI link 到 `/usr/local`，但目前使用者沒有權限。家用環境建議不要直接用 `sudo` 重跑 installer，先改成使用者自己的 npm global prefix：

```bash
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"
```

把 PATH 加到 zsh：

```bash
printf '\nexport PATH="$HOME/.npm-global/bin:$PATH"\n' >> "$HOME/.zshrc"
```

確認：

```bash
npm config get prefix
```

應該看到：

```text
/Users/yanfengzhe/.npm-global
```

然後重新跑 NemoClaw installer。若你使用 nvm，另一個更乾淨的做法是先切到 nvm Node：

```bash
source ~/.nvm/nvm.sh
nvm install 22
nvm use 22
npm config get prefix
```

此時 prefix 應該在 `~/.nvm/versions/node/...`，也不會寫到 `/usr/local`。

確認 sandbox：

```bash
nemoclaw list
nemoclaw home-assistant status
```

如果你還沒有 `home-assistant`，使用你當初建立 `my-assistant` 的 onboard/create 流程建立一個新的 sandbox。因為目前我沒有可靠的官方公開安裝頁可核對，不建議在文件裡硬寫未驗證的新建指令。

## 5. 第一個測試：agent hello

```bash
nemoclaw home-assistant exec -- openclaw agent --agent main -m "hello"
```

完成定義：

- agent 有回應。
- 沒有 gateway pairing error。
- 沒有 inference route error。

如果只是要確認模型路由：

```bash
nemoclaw inference get
```

## 6. 第二個測試：dashboard

```bash
nemoclaw home-assistant dashboard-url --quiet
```

把輸出的 URL 貼到瀏覽器。這個 URL 通常帶 token，不要貼到公開地方。

## 7. 第三個測試：本地文件問答

先不要做 PDF。建立一個玩具 Markdown：

```text
data/home-specs/router-demo.md
```

內容可以像這樣：

```markdown
# Router Demo Spec

## GNSS

GNSS is used as an optional timing source.

## Timing

The system should support PTP as the primary timing source.
```

第一版 RAG 可以先不用 embedding，只做：

```text
讀 Markdown
  -> 依 heading 切段
  -> 搜尋 keyword
  -> 回傳相關段落
  -> 交給 Nemotron-3 回答
```

## 8. 家用 RAG 最小工具設計

先做四個 tool 名稱即可：

| Tool | 家用第一版 |
|---|---|
| `spec_list` | 列出 `data/home-specs/` 裡有哪些文件 |
| `spec_ingest` | 把 Markdown 或 PDF 轉成 JSONL chunks |
| `spec_search` | 用關鍵字搜尋 chunks |
| `spec_answer` | 根據 chunks 請 Nemotron-3 回答 |

第一版資料格式：

```json
{
  "spec_id": "router-demo",
  "title": "Router Demo Spec",
  "section": "GNSS",
  "page": null,
  "chunk_id": "router-demo:gnss:001",
  "text": "GNSS is used as an optional timing source."
}
```

## 9. 第二階段才接 OpenProject

等家用 RAG 能跑，再接一個本地 OpenProject：

```text
OpenProject on home machine
  -> http://localhost:8090
  -> test API token
  -> openproject_* tools
```

如果要讓 sandbox 存取 host 上的 OpenProject，仍然要處理：

```text
sandbox localhost != host localhost
```

家裡也可以用 proxy：

```text
sandbox
  -> host LAN IP:8092
  -> nginx
  -> localhost:8090 OpenProject
```

但家裡第一天不需要做這個。

## 10. 推薦順序

```text
Day 1:
  NemoClaw sandbox + hello + dashboard

Day 2:
  本地 Markdown spec_search

Day 3:
  spec_answer with Nemotron-3

Day 4:
  接 toy OpenProject

Day 5:
  才開始測 PDF ingestion
```

## 11. 安全提醒

- 家用 sandbox 不要使用公司 token。
- 家用測試 PDF 先用公開文件或自己寫的 demo spec。
- 第三方 skill 要先讀 `SKILL.md` 和 scripts，再安裝。
- network policy 只開需要的 host/port。
- 建議每次實驗記錄：sandbox 名稱、policy、安裝的 skill/tool、測試指令、結果。

## 12. 最短路線

如果只想先玩起來：

```bash
source ~/.nvm/nvm.sh
nvm use 22
nemoclaw list
nemoclaw home-assistant status
nemoclaw inference get
nemoclaw home-assistant exec -- openclaw agent --agent main -m "hello"
nemoclaw home-assistant dashboard-url --quiet
```

如果 `home-assistant` 尚未建立，就先用你之前建立 `my-assistant` 的同一套 onboarding 流程建立它。
