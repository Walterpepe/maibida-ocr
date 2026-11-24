"""Apply the contact form accessibility and local-development hardening.

The generated contact pages are intentionally kept as deployable static HTML,
so this migration makes the existing pages match the current generator while
preserving their localized copy and later per-market additions. It is idempotent.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SUBMITTING = {
    "zh-CN": "正在提交…",
    "en-US": "Sending…",
    "en-SG": "Sending…",
    "es-MX": "Enviando…",
    "es-ES": "Enviando…",
    "id-ID": "Mengirim…",
    "th-TH": "กำลังส่ง…",
    "vi-VN": "Đang gửi…",
    "ko-KR": "전송 중…",
    "ja-JP": "送信中…",
    "ms-MY": "Menghantar…",
    "ru-RU": "Отправка…",
}

AUTOCOMPLETE = {
    "name": "name",
    "email": "email",
    "phone": "tel",
    "company": "organization",
    "country": "country-name",
}


def add_attribute(tag: str, name: str, value: str) -> str:
    if re.search(rf"\b{re.escape(name)}\s*=", tag, re.I):
        return tag
    if tag.endswith("/>"):
        return tag[:-2] + f' {name}="{value}"/>'
    return tag[:-1] + f' {name}="{value}">'


def patch_page(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lang_match = re.search(r'<html\b[^>]*\blang="([^"]+)"', text, re.I)
    lang = lang_match.group(1) if lang_match else "zh-CN"
    original = text

    text = re.sub(
        r"<h1(?![^>]*\bid=)[^>]*>",
        '<h1 id="cf-form-heading">',
        text,
        count=1,
        flags=re.I,
    )

    def patch_form(match: re.Match[str]) -> str:
        attrs = match.group(1)
        attrs = re.sub(
            r'\saction="(?:https://www\.maibida\.com)?/api/messages"',
            ' action="/api/messages"',
            attrs,
            flags=re.I,
        )
        if not re.search(r'\baction\s*=\s*"/api/messages"', attrs, re.I):
            attrs += ' action="/api/messages"'
        if not re.search(r"\baria-labelledby\s*=", attrs, re.I):
            attrs += ' aria-labelledby="cf-form-heading"'
        if not re.search(r"\baria-busy\s*=", attrs, re.I):
            attrs += ' aria-busy="false"'
        return f"<form{attrs}>"

    text = re.sub(
        r"<form\b([^>]*\bid=\"message-form\"[^>]*)>",
        patch_form,
        text,
        count=1,
        flags=re.I,
    )

    def patch_input(match: re.Match[str]) -> str:
        tag = match.group(0)
        name_match = re.search(r'\bname="([^"]+)"', tag, re.I)
        name = name_match.group(1) if name_match else ""
        if name in AUTOCOMPLETE:
            tag = add_attribute(tag, "autocomplete", AUTOCOMPLETE[name])
        if name in {"name", "email", "message", "consent"}:
            tag = add_attribute(tag, "aria-describedby", "form-status")
        return tag

    text = re.sub(r"<input\b[^>]*>", patch_input, text, flags=re.I)

    def patch_textarea(match: re.Match[str]) -> str:
        return add_attribute(match.group(0), "aria-describedby", "form-status")

    text = re.sub(r"<textarea\b[^>]*>", patch_textarea, text, flags=re.I)

    def patch_script(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "cn/js/contact.js" not in tag:
            return tag
        return add_attribute(tag, "data-submitting", SUBMITTING.get(lang, "Sending…"))

    text = re.sub(
        r'<script\b[^>]*\bsrc="[^"]*cn/js/contact\.js[^"]*"[^>]*>',
        patch_script,
        text,
        flags=re.I,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
    return text != original


def main() -> None:
    changed = []
    for path in sorted(ROOT.glob("contact*.html")):
        if patch_page(path):
            changed.append(path.name)
    print(f"updated {len(changed)} contact pages: {', '.join(changed)}")


if __name__ == "__main__":
    main()
