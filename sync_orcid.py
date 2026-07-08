import requests
import json
import os

ORCID_ID = "0000-0001-5447-8008"
BASE_URL = f"https://pub.orcid.org/v3.0/{ORCID_ID}/works"
headers = {"Accept": "application/json"}

def fetch_and_generate():
    print(f"Executing Data Sync Engine... Fetching Node: {ORCID_ID}")
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code != 200:
        return

    data = response.json()
    works = data.get("group", [])
    output_dir = "content/publications"
    os.makedirs(output_dir, exist_ok=True)
    
    for work in works:
        summary = work["work-summary"][0]
        title = summary["title"]["title"]["value"]
        year = summary.get("publication-date", {}).get("year", {}).get("value", "N/A")
        put_code = summary.get("put-code")
        url = summary.get("url", {}).get("value", "")
        
        authors_str = "Ke XU"
        journal_title = "IEEE Transactions / Conference"
        abstract = ""

        if put_code:
            detail_url = f"https://pub.orcid.org/v3.0/{ORCID_ID}/work/{put_code}"
            detail_res = requests.get(detail_url, headers=headers)
            if detail_res.status_code == 200:
                detail_data = detail_res.json()
                journal_node = detail_data.get("journal-title")
                if journal_node:
                    journal_title = journal_node.get("value", journal_title)
                contributors = detail_data.get("contributors", {}).get("contributor", [])
                author_names = [c.get("credit-name", {}).get("value") for c in contributors if c.get("credit-name", {}).get("value")]
                if author_names:
                    authors_str = ", ".join(author_names)
                desc_node = detail_data.get("short-description")
                if desc_node:
                    abstract = " ".join(desc_node.split())

        safe_title = "".join(x for x in title if x.isalnum() or x in " -_").replace(" ", "-").lower()
        
        # 核心改变：Front Matter 内部全部变为纯粹的 K-V 结构化数据
        md_content = f"""---
title: '{title}'
authors: '{authors_str}'
journal: '{journal_title}'
year: '{year}'
paper_url: '{url}'
abstract: '{abstract.replace("'", "''")}'
draft: false
---
"""
        file_path = os.path.join(output_dir, f"{safe_title}.md")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_content)
    print(f"Sync Complete. {len(works)} structural data payloads generated.")

if __name__ == "__main__":
    fetch_and_generate()