from pathlib import Path


YAML_PATH = Path(r"c:\Users\gabri\OneDrive\Desktop\Aecon\power-apps-ai-skills\PRTrack\src\Src\PR Detail.pa.yaml")


def remove_block(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"start marker not found: {start_marker!r}")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"end marker not found: {end_marker!r}")
    return text[:start] + text[end:]


def main() -> None:
    text = YAML_PATH.read_text(encoding="utf-8")
    orig = text

    # 1) Request Details tab: delete PR-level attachment strip
    text = remove_block(
        text,
        start_marker="                                    - pd_req_attach:\n",
        end_marker="                  - pd_lines_panel:\n",
    )

    # 2) Remove extra approve-all button (prevents duplicate DOA approve actions)
    text = remove_block(
        text,
        start_marker="                        - pd_approve_all:\n",
        end_marker="                  - pd_request_panel:\n",
    )

    if text == orig:
        raise SystemExit("No changes made (unexpected).")

    YAML_PATH.write_text(text, encoding="utf-8")
    print("Removed pd_req_attach block and pd_approve_all block.")
    print("pd_req_attach present?", "pd_req_attach" in text)
    print("pd_approve_all present?", "pd_approve_all" in text)


if __name__ == "__main__":
    main()

