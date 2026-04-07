#!/usr/bin/env python3
"""
Download all talks from a General Conference session.

Usage:
    python scrape_conference.py <year> <april|october>

Examples:
    python scrape_conference.py 2025 october
    python scrape_conference.py 2020 april
"""

import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.churchofjesuschrist.org"
MONTH_MAP = {"april": "04", "october": "10"}


def sanitize_filename(name: str) -> str:
    """Remove characters that are invalid in filenames."""
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', "", name)
    name = re.sub(r"\s+", " ", name)
    return name


def get_talk_links(year: int, month_num: str) -> list[str]:
    """Fetch the session index page and return all unique talk URLs."""
    index_url = f"{BASE_URL}/study/general-conference/{year}/{month_num}?lang=eng"
    print(f"Fetching index: {index_url}")

    resp = requests.get(index_url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    prefix = f"/study/general-conference/{year}/{month_num}/"

    seen = set()
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        # Strip query string for dedup, but keep it for fetching
        path = href.split("?")[0]
        if path.startswith(prefix) and path != prefix.rstrip("/"):
            full_url = BASE_URL + path + "?lang=eng"
            if full_url not in seen:
                seen.add(full_url)
                links.append(full_url)

    return links


def fetch_talk(url: str) -> tuple[str, str, str] | None:
    """
    Fetch a talk page and return (title, speaker, body_text).
    Returns None if the page doesn't look like a talk.
    """
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    h1 = soup.find("h1")
    if not h1:
        return None
    title = h1.get_text(strip=True)

    author_tag = soup.find(class_="author-name")
    if not author_tag:
        return None
    speaker = author_tag.get_text(strip=True)

    body_block = soup.find(class_="body-block")
    if not body_block:
        return None

    paragraphs = []
    for p in body_block.find_all("p"):
        text = p.get_text(separator=" ", strip=True)
        if text:
            paragraphs.append(text)

    body = "\n\n".join(paragraphs)
    return title, speaker, body


def main():
    if len(sys.argv) != 3:
        print("Usage: python scrape_conference.py <year> <april|october>")
        sys.exit(1)

    year_str, month_str = sys.argv[1], sys.argv[2].lower()

    if not year_str.isdigit():
        print(f"Error: '{year_str}' is not a valid year.")
        sys.exit(1)

    if month_str not in MONTH_MAP:
        print(f"Error: month must be 'april' or 'october', got '{month_str}'.")
        sys.exit(1)

    year = int(year_str)
    month_num = MONTH_MAP[month_str]
    month_label = month_str.capitalize()
    output_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "sessions", f"{month_label} {year}"
    )

    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}/")

    talk_links = get_talk_links(year, month_num)
    if not talk_links:
        print("No talk links found. The page structure may have changed.")
        sys.exit(1)

    print(f"Found {len(talk_links)} talk(s). Downloading...\n")

    success = 0
    for i, url in enumerate(talk_links, 1):
        print(f"[{i}/{len(talk_links)}] {url}")
        try:
            result = fetch_talk(url)
            if result is None:
                print("  Skipped (missing title, speaker, or body).")
                continue

            title, speaker, body = result
            filename = sanitize_filename(f"{title} - {speaker}") + ".txt"
            filepath = os.path.join(output_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"{title}\n")
                f.write(f"By {speaker}\n")
                f.write("=" * 60 + "\n\n")
                f.write(body)
                f.write("\n")

            print(f"  Saved: {filename}")
            success += 1
        except Exception as e:
            print(f"  Error: {e}")

        time.sleep(0.5)

    print(f"\nDone. {success}/{len(talk_links)} talks saved to '{output_dir}/'.")


if __name__ == "__main__":
    main()
