#!/usr/bin/env python3
import csv
import time
import argparse
from pathlib import Path

import requests

API_KEY: str = Path(".apikey").read_text().strip()

SEARCH_QUERY: str = 'page.title:("Most Popular Online Crypto Casino Based on Blockchain" OR "Play at the best online casino based on Blockchain")'
DEFAULT_VALUE: str = "N/A"


def search(search_after: str | None = None) -> list:
    time.sleep(2)
    
    headers = {"API-Key": API_KEY, "Content-Type": "application/json"}
    params = {"q": SEARCH_QUERY, "size": 100}

    if search_after:
        params["search_after"] = search_after

    try:
        resp = requests.get(
            "https://urlscan.io/api/v1/search/",
            headers=headers,
            params=params,
        )
        return resp.json().get("results", [])
    except:
        print("Error: Failed to connect to urlscan.io API.")
        return []


def process(max_search_count: int, output_file: str):
    search_after = None
    output = []
    ctr = 0

    while ctr < max_search_count:
        print("=" * 20, f"#{ctr + 1}", "=" * 20)
        ctr += 1
        results = search(search_after)
        if len(results) == 0:
            break
    
        for r in results:
            urlscan_id = r["_id"]
            urlscan_sort = r["sort"]

            ip_addr = r["page"].get("ip", DEFAULT_VALUE)
            country = r["page"].get("country", DEFAULT_VALUE)
            url = r["page"].get("url", DEFAULT_VALUE)
            domain = r["page"].get("domain", DEFAULT_VALUE)
            http_title = r["page"].get("title", DEFAULT_VALUE)

            asn = r["page"].get("asn", DEFAULT_VALUE)
            asn_name = r["page"].get("asnname", DEFAULT_VALUE)
            tls_issuer = r["page"].get("tlsIssuer", DEFAULT_VALUE)
            tls_age = r["page"].get("tlsAgeDays", DEFAULT_VALUE)

            output.append(
                {
                    "scan_id": urlscan_id,
                    "ip": ip_addr,
                    "country": country,
                    "domain": domain,
                    "url": url,
                    "title": http_title,
                    "asn": asn,
                    "asn_name": asn_name,
                    "tls_issuer": tls_issuer,
                    "tls_age_days": tls_age,
                }
            )

            search_after = ",".join(map(str, urlscan_sort))

    keys = [
        "scan_id",
        "ip",
        "country",
        "domain",
        "url",
        "title",
        "asn",
        "asn_name",
        "tls_issuer",
        "tls_age_days",
    ]
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(output)


def main():
    parser = argparse.ArgumentParser(
        description="Search and output results to CSV file."
    )
    parser.add_argument(
        "-m",
        "--max-search-count",
        type=int,
        default=10,
        help="Maximum number of search pages to fetch.",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        default="casino_hunt_results.csv",
        help="Output CSV file name.",
    )

    args = parser.parse_args()
    max_search_count = args.max_search_count
    output_file = args.output_file

    process(max_search_count, output_file)
    print(f"Results successfully written to {output_file}")


if __name__ == "__main__":
    main()
