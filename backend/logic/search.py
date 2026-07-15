# backend/logic/search.py
import json
import os
import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

PORTAL_WEEKLY_REPORT_URL = os.getenv("PORTAL_WEEKLY_REPORT_URL")
REPORT_DIR = "data/report"

CONTEXT_CHARS = 10  # キーワード前後に表示する文字数
DEFAULT_PAGE_SIZE = 5

# 半角/全角スペース・改行(\n, \r)・タブなど、あらゆる空白文字をまとめて拾う
WHITESPACE_PATTERN = re.compile(r"\s+")


# 改行コードやタブ、連続する空白を半角スペース1つに正規化する（単語の区切りは残す）
def normalize_text(text: str) -> str:
    if not text:
        return ""
    normalized = WHITESPACE_PATTERN.sub(" ", text)
    return normalized.strip()


# 正規化済みテキストからキーワード前後 context_chars 文字を prefix/match/suffix に分けて抜き出す
def build_snippet(
    normalized_text: str, keyword: str, context_chars: int = CONTEXT_CHARS
) -> Optional[dict]:
    idx = normalized_text.find(keyword)
    if idx == -1:
        return None

    start = max(0, idx - context_chars)
    end = min(len(normalized_text), idx + len(keyword) + context_chars)

    prefix = normalized_text[start:idx]
    match = normalized_text[idx : idx + len(keyword)]
    suffix = normalized_text[idx + len(keyword) : end]

    return {
        "prefix": ("…" if start > 0 else "") + prefix,
        "match": match,
        "suffix": suffix + ("…" if end < len(normalized_text) else ""),
    }


# 週報をキーワード検索し、ページングされた結果を返す
def search_reports(keyword: str, page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> dict:
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = DEFAULT_PAGE_SIZE

    all_results = []

    for filename in os.listdir(REPORT_DIR):
        if not filename.endswith(".json"):
            continue

        path = os.path.join(REPORT_DIR, filename)

        with open(path, encoding="utf-8") as f:
            report = json.load(f)

        section = None
        report_date = ""
        snippet = None

        # (表示ラベル, 対象テキスト) のリスト
        text_sections = [
            ("直近で学んだこと", report["studying_memo"]),
            ("コメント欄", report["comment"]),
            ("リーダーからの返信", report["replies"]["leader"]),
            ("社長からの返信", report["replies"]["president"]),
            ("その他の返信", report["replies"]["other"]),
        ]

        for label, text in text_sections:
            normalized = normalize_text(text)
            if keyword in normalized:
                section = label
                snippet = build_snippet(normalized, keyword)
                break

        if not section:
            for daily in report["daily_reports"]:
                normalized = normalize_text(daily["content"])
                if keyword in normalized:
                    section = "日報"
                    report_date = daily["date"]
                    snippet = build_snippet(normalized, keyword)
                    break

        if section:
            # 「日報」のときだけ日付をラベルに埋め込む
            section_label = (
                f"{section}（{report_date}）"
                if section == "日報" and report_date
                else section
            )

            all_results.append(
                {
                    "year_month": report["year_month"],
                    "week_num": report["week_num"],
                    "member_no": report["member_no"],
                    "section": section_label,
                    "snippet": snippet,
                    "url": (
                        f"{PORTAL_WEEKLY_REPORT_URL}"
                        f"?member_no={report['member_no']}"
                        f"&weekly_report_year_month={report['year_month']}"
                        f"&weekly_report_week_num={report['week_num']}"
                    ),
                }
            )

    total = len(all_results)
    start = (page - 1) * page_size
    end = start + page_size
    paged_results = all_results[start:end]
    total_pages = (total + page_size - 1) // page_size if page_size else 0

    return {
        "items": paged_results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }