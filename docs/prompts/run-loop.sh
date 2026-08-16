#!/usr/bin/env bash
# Plimsoll — RD/QA/PM/PO 自動化驗收迴圈
#
# 用 Claude Code headless mode（claude -p）真正串接四個角色，不需要人工手動開新視窗貼 prompt。
# 每個角色結束時都會 commit，本腳本靠讀取「最新一次 commit 訊息」的「結果：」欄位判斷通過/失敗，
# 靠讀取 dev-report.md 判斷目前切片與失敗次數（見 qa-guardrail-workflow.md 對各 prompt 的調整）。
#
# 使用前提：
#   1. 已安裝並登入 Claude Code（`claude auth` 或設定 ANTHROPIC_API_KEY / apiKeyHelper）
#   2. repo 根目錄含：workflow.md, qa-guardrail-workflow.md, dev-report.md, error-log.md,
#      ui-mockup-v3.2.html, ui-spec.md, architecture-decisions-A-B.md
#   3. 目前分支為 codex/260815
#
# 用法：
#   ./run-loop.sh
#
# 中斷後（連續 3 次失敗，PO_claude 彙整完畢）腳本會自動結束，不會再繼續跑，
# 需要人工看過 PO_claude 的彙整報告、決定下一步後，重新編修對應 prompt 再重跑本腳本。

set -euo pipefail

REPO_DIR="$(pwd)"
MAX_FAILS=3
LOG_DIR="$REPO_DIR/.loop-logs"
mkdir -p "$LOG_DIR"

# ── 四個角色的 prompt 檔（從 qa-guardrail-workflow.md 對應章節各自抽出存成獨立檔案，
#    第一次使用請把 §4.1–§4.5 的 prompt 內文分別存成下列檔名）───────────────────────
RD_PROMPT_FILE="prompts/rd_claude.md"
QA_PROMPT_FILE="prompts/qa_claude.md"
PM_PROMPT_FILE="prompts/pm_claude.md"
RD_FIX_PROMPT_FILE="prompts/rd_claude_fix.md"
PO_PROMPT_FILE="prompts/po_claude.md"

# 允許的工具與權限模式：只給讀檔/改檔/跑指令的權限，不做網路存取以外的危險操作。
# acceptEdits 會自動接受檔案編輯，但仍建議在獨立分支/容器內跑，避免誤動 main。
CLAUDE_FLAGS=(--allowedTools "Bash,Read,Edit,Write" --permission-mode acceptEdits --output-format json)

timestamp() { date +"%Y%m%d-%H%M%S"; }

# 呼叫一個角色，回傳這次呼叫是否成功執行（不代表驗收結果，只代表 claude 有沒有跑完）
run_role() {
  local role="$1" prompt_file="$2"
  local ts; ts="$(timestamp)"
  local out_file="$LOG_DIR/${role}-${ts}.json"

  echo ">>> [${role}] 開始（log: ${out_file}）"
  if ! claude -p "$(cat "$prompt_file")" "${CLAUDE_FLAGS[@]}" > "$out_file" 2> "$LOG_DIR/${role}-${ts}.err"; then
    echo "!!! [${role}] claude 執行失敗，看 ${LOG_DIR}/${role}-${ts}.err"
    exit 1
  fi
  echo "<<< [${role}] 結束"
}

# 讀「最新一次 git commit 訊息」的「結果：」欄位，回傳 通過 / 失敗 / 已中斷
latest_commit_result() {
  git -C "$REPO_DIR" log -1 --pretty=%B | grep -oP '結果：\K[^\n（]+' | head -1 | tr -d ' '
}

# 讀「最新一次 git commit 訊息」的作者標籤（RD_claude/QA_claude/PM_claude/PO_claude）
latest_commit_role() {
  git -C "$REPO_DIR" log -1 --pretty=%B | grep -oP '^\[\K[A-Z_]+claude' | head -1
}

echo "════════════════════════════════════════"
echo " Plimsoll RD/QA/PM 自動化驗收迴圈"
echo "════════════════════════════════════════"

fail_count=0

while true; do
  # 1) RD_claude 開發（或修復）
  if [ "$fail_count" -eq 0 ]; then
    run_role "RD_claude" "$RD_PROMPT_FILE"
  else
    run_role "RD_claude_fix" "$RD_FIX_PROMPT_FILE"
  fi
  rd_result="$(latest_commit_result)"
  echo "    RD_claude commit 結果：${rd_result}"

  # 2) QA_claude 撰寫並執行測試
  run_role "QA_claude" "$QA_PROMPT_FILE"
  qa_result="$(latest_commit_result)"
  echo "    QA_claude commit 結果：${qa_result}"

  if [ "$qa_result" == "失敗" ]; then
    fail_count=$((fail_count + 1))
    echo "    ⚠ QA 判定失敗，本切片連續失敗次數：${fail_count}/${MAX_FAILS}"
  else
    # 3) PM_claude 功能驗收
    run_role "PM_claude" "$PM_PROMPT_FILE"
    pm_result="$(latest_commit_result)"
    echo "    PM_claude commit 結果：${pm_result}"

    if [ "$pm_result" == "失敗" ]; then
      fail_count=$((fail_count + 1))
      echo "    ⚠ PM 判定失敗，本切片連續失敗次數：${fail_count}/${MAX_FAILS}"
    else
      echo "    ✅ 本切片通過（QA 與 PM 皆通過），失敗計數歸零，進入下一切片"
      fail_count=0
      # 檢查 dev-report.md 是否所有階段皆已完成，是的話結束迴圈
      if ! grep -q "⬜ 未開始" "$REPO_DIR/dev-report.md"; then
        echo "════════════════════════════════════════"
        echo " 所有切片皆已通過，P0–P4 完成，迴圈結束。"
        echo "════════════════════════════════════════"
        break
      fi
      continue
    fi
  fi

  # 連續失敗達上限 → 呼叫 PO_claude 並中止，不再自動重試
  if [ "$fail_count" -ge "$MAX_FAILS" ]; then
    echo "════════════════════════════════════════"
    echo " 連續失敗達 ${MAX_FAILS} 次，呼叫 PO_claude 彙整後中止。"
    echo "════════════════════════════════════════"
    run_role "PO_claude" "$PO_PROMPT_FILE"
    po_result="$(latest_commit_result)"
    echo "    PO_claude commit 結果：${po_result}"
    echo ""
    echo " >>> 流程已中斷，請人工閱讀 dev-report.md 的中斷紀錄與 PO_claude 彙整報告，"
    echo " >>> 決定下一步後修改 ${RD_PROMPT_FILE}（或另開新切片範圍），再重新執行本腳本。"
    exit 2
  fi
  # 否則回到迴圈頂端，下一輪會走 RD_claude_fix
done
