# Claude 點子驗證 Skill

[English](README.md) · **繁體中文**

一個 Claude Code skill：用 5、12 或 16 輪有結構的辯論挑戰你的點子，最後留下結論與可列印的報告。

**專案介紹頁：** https://ted-h-com.github.io/claude-idea-review-skill/?lang=zh-TW

這是 **個人 IP 陪跑計畫** 與 **「自由工坊」Discord 社群** 的開源 Claude Code skill，授權：MIT。

當你有一個產品、內容、創業、功能、個人品牌、社群或商業模式的點子，想在投入大量時間之前先好好檢驗一次，就可以用它。

## 它會做什麼

這個 skill 在 Claude Code 裡跑 5、12 或 16 輪的 review（預設 5 輪）。第一輪開始前，它會先：

1. 檢查哪些選配的 provider CLI 已經安裝、而且能回應：Codex CLI、Antigravity（`agy`）或 Gemini CLI，以及 Grok CLI。
2. 工具允許的話，先上網查資料：競品、價格、需求、技術與平台限制，以及法規或通路上的限制。

接著由四種思考個性一輪一輪辯論。第 1 輪各自表態，中間幾輪互相攻防，最後一輪每個個性都要在「做、先驗證、轉向、停止」之中選一個。最後產出附停止條件的結論，存成可以列印的本機檔案。

review 的內容是 Claude 依照 `SKILL.md` 寫出來的。三個 Python scripts 只負責檢查 provider、建立 review 資料夾與產生報告。

## 四種思考個性

這四個是思考個性，不是部門或職務，也不代表真的有四個模型：

- `Optimist`：把點子最強的版本展開。
- `Skeptic`：攻擊弱假設、隱藏成本與可能失敗的原因。
- `Pragmatist`：把討論變成測試、MVP 形狀、限制與取捨。
- `Synthesizer`：整合分歧，追蹤什麼證據會改變結論。

第 1 輪之後，每個個性都至少要回應一個其他個性先前的論點。

## Provider 偵測與備援

`scripts/check_providers.py --smoke` 會在 `PATH` 上找各家 CLI，並對每個找到的 CLI 送出一句很短的提示：`Reply OK only.`

| Provider | 找的 CLI | 測試方式 | 會回報的 key 變數 |
|---|---|---|---|
| Codex | `codex` | `codex exec`，提示從 stdin 送入 | `OPENAI_API_KEY` |
| Gemini | 先找 `agy`（Antigravity），沒有再找 `gemini` | `-p "Reply OK only."` | `GEMINI_API_KEY`、`GOOGLE_API_KEY` |
| Grok | `grok` | `grok -p "Reply OK only."` | `XAI_API_KEY`、`GROK_API_KEY` |

它也會回報有沒有設定 `OPENROUTER_API_KEY`。只列出變數名稱，不會印出值。CLI 在 45 秒內以結束碼 0 結束、而且有輸出，測試就算通過。

`SKILL.md` 要求 Claude 這樣處理檢查結果：

- CLI 裝了卻無法回應，就對該 provider 回報「測不到帳號」。
- 缺少的 provider，Claude 只問一次你有沒有 API key，以及想用原廠 API 還是 OpenRouter。
- 不會一直等 key。沒有 key，就由 Claude 模擬該 provider 的風格並標示出來，例如「Claude 模擬 Grok」。
- 模擬的風格：Codex 嚴謹、有系統；Grok 直接、務實優先；Gemini 視野廣，會權衡整體的取捨。

script 本身還註明了兩件事。`agy -p` 在沒有接終端機時，可能以結束碼 0 結束卻沒有任何輸出，所以 Antigravity 測試失敗不一定代表帳號不能用。找到 `gemini` CLI 卻沒有回應時，script 會附上提示：Google 在 2026 年把免費、Pro、Ultra 等消費者方案移到 Antigravity，Gemini CLI 仍可搭配付費的 `GEMINI_API_KEY`，或 Enterprise、Code Assist 授權使用。

## 審查標準與評估量表

陪跑小組會根據 5 個核心標準來評估你的點子：**問題解決契合度** (Problem-Solution Fit)、**市場需求** (Market Demand)、**執行力** (Execution)、**差異化** (Differentiation) 以及 **商業模式** (Business Model)。

最終的信心分數對應明確的結論：

- **80-100 (`worth_building`)：** 所有標準都顯示強烈訊號。有明確的 MVP 與獲得第一筆收入的路徑。
- **60-79 (`validate_first`)：** 潛力不錯，但依賴高風險假設。在投入開發前，需要先進行低成本的驗證。
- **40-59 (`pivot`)：** 核心問題存在，但解決方案或市場區隔有缺陷。需要大幅調整。
- **0-39 (`not_worth_building`)：** 在需求、可行性或單位經濟學上有致命缺陷。最好直接放棄這個點子。

## 輸出

每次執行都會在 review 執行目錄底下的 `.idea-review/` 建立一個資料夾：

```text
.idea-review/<YYYYMMDD-HHMMSS>-<slug>/
├── input.md          你的點子，接著是研究摘要
├── rounds/
│   ├── round-01.md   每個個性各一段
│   └── ...
├── final.md          結論
├── report.md         先放 final.md，再放 input.md，最後是每一輪
└── report.html       同樣內容的可列印網頁
```

slug 取自點子的前八個字詞，中文字會保留。`report.html` 是靜態檔案：用瀏覽器打開，按 **Print / Save PDF** 就能列印或存成 PDF。列印時會隱藏按鈕列，每個部分都從新的一頁開始。

如果在 Git repo 裡跑 review，除非你想把 review 一起 commit，否則記得把 `.idea-review/` 加進那個 repo 的 `.gitignore`。

## 需求

- **Claude Code**：review 在它裡面進行。
- **Python 3.8 以上**，要在 `PATH` 上。只有輔助 scripts 會用到，而且只用標準函式庫。
- **選配：** Codex CLI、Antigravity（`agy`）或 Gemini CLI，以及 Grok CLI，用來做原生的交叉檢查。都不是必要的；缺少的 provider 會由 Claude 模擬。

## 安裝

clone 到個人的 skills 資料夾：

```bash
# macOS / Linux
git clone https://github.com/TED-H-com/claude-idea-review-skill.git \
  ~/.claude/skills/idea-review-panel
```

```powershell
# Windows (PowerShell)
git clone https://github.com/TED-H-com/claude-idea-review-skill.git `
  "$env:USERPROFILE\.claude\skills\idea-review-panel"
```

正在執行的 Claude Code session 會自動載入新的 skill，不必重開。如果 session 開始時還沒有 `~/.claude/skills/` 這個資料夾，就執行一次 `/reload-skills`。

只想在某個專案裡使用的話，改 clone 到該專案的 `.claude/skills/idea-review-panel/`。

之後更新：

```bash
git -C ~/.claude/skills/idea-review-panel pull
```

> **Windows 提醒：** 輔助 scripts 是用 `python3` 呼叫，但 Windows 上的指令通常是 `python`。如果輸入 `python` 會跳出 Microsoft Store，那只是佔位用的捷徑，不是真的 Python。請從 [python.org](https://www.python.org/downloads/) 安裝，或執行 `winget install Python.Python.3.12`，然後重開終端機。

## 怎麼用

直接請 Claude Code 驗證點子，skill 會依描述自動觸發：

```text
幫我驗證這個點子：<你的 idea>
```

用英文問也行，例如 `Validate this idea: <your idea>`。另外也可以用 `/idea-review-panel` 直接呼叫。

預設 5 輪；想更深入可以要求 12 或 16 輪。用中文提問時，預設以繁體中文進行；其他語言則跟著你的語言。完成後，Claude 會回覆結論摘要與檔案路徑。

## 使用範例

你可以提供一句話的點子，或是詳細的背景資訊。以下是一些範例：

- **軟體 / SaaS：** "Validate this idea: A Notion-like workspace specifically for lawyers, focusing on secure document management and case linking."
- **內容 / 創作者：** "幫我驗證這個點子：一個專門教非工程師用 AI 工具自動化日常工作的 YouTube 頻道，一開始先做 Notion 和 Zapier 教學。"
- **社群 / 商業：** "Validate this idea: A paid Discord community for indie hackers building micro-SaaS, offering weekly teardowns and accountability groups."

## 輔助 scripts

skill 會自動執行這些 scripts。想手動執行的話，請用安裝後的路徑，並在你希望 `.idea-review/` 出現的資料夾裡執行（Windows 上把 `python3` 換成 `python`）：

```bash
SKILL=~/.claude/skills/idea-review-panel

# 哪些 provider 已安裝、能回應（會對每個找到的 CLI 送出一句提示）
python3 "$SKILL/scripts/check_providers.py" --smoke

# 建立 review 資料夾：--rounds 只接受 5、12、16；--out 可以改上層資料夾
python3 "$SKILL/scripts/init_review.py" --idea "你的點子" --rounds 5

# 從 review 資料夾產生 report.md 與 report.html
python3 "$SKILL/scripts/render_report.py" .idea-review/<資料夾名稱>
```

不加 `--smoke` 時，`check_providers.py` 只回報有哪些 CLI 與 key 變數，不會送出任何提示。

## 最終結論格式

`final.md` 包含：

- `Verdict`：`worth_building`、`validate_first`、`pivot` 或 `not_worth_building`
- `Confidence`：0 到 100
- 一句話結論
- 最強理由
- 最強反論點
- 兩週驗證計畫
- 成功門檻
- 停止條件
- 下一步三件事

## 限制

- review 由 `SKILL.md` 裡的指示驅動，不是程式碼。回合結構、研究與備援方式，都取決於 Claude 有沒有照做，每次的結果也會不同。
- repo 裡沒有 API 用戶端程式。你提供 key 之後要怎麼呼叫 API，由當下 session 裡的 Claude 決定。
- `agy` 測試失敗，不代表帳號一定不能用（見上方說明）。
- `render_report.py` 支援標題、清單、段落，以及行內的程式碼、粗體、斜體與連結；不支援表格與程式碼區塊。產生的 HTML 一律標示為 `lang="zh-Hant"`，英文 review 也一樣。
- 目前沒有測試、CI 或 release；請從 `main` 分支安裝。

## 相關專案

[ai-brainstorming](https://github.com/TED-H-com/ai-brainstorming)（[專案介紹頁](https://ted-h-com.github.io/ai-brainstorming/?lang=zh-TW)）是同一個想法的網頁版：一樣是 5、12、16 輪，一樣走研究立論、互相攻防、漸進收斂的流程，但它透過 OpenRouter 呼叫五個模型席位，有設定 SMTP 時還能用 email 寄出完整紀錄。這個 skill 則在你自己的 Claude Code session 裡執行，用四種思考個性取代模型席位。

## 授權

MIT，見 [LICENSE](LICENSE)。
