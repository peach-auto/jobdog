# -*- coding: utf-8 -*-
"""数据合并与清洗：把外企、国企两份数据统一、去重，输出 JSON + SQLite。

流程:
    1. 读取 data/foreign_jobs.json + data/soe_jobs.json
    2. 按 source_url 指纹去重
    3. 轻度清洗(裁剪空白、统一时间格式)
    4. 输出 data/jobs.json (给前端静态渲染用)
       输出 data/jobs.db   (SQLite 数据库，可查询/统计)

用法: python merge_jobs.py
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE    = Path(__file__).parent.parent / "data"
SOURCES = [BASE / "foreign_jobs.json", BASE / "soe_jobs.json"]
OUT_JSON = BASE / "jobs.json"
OUT_DB   = BASE / "jobs.db"
WEB_JSON = BASE.parent / "web" / "data" / "jobs.json"   # 前端构建用的副本

# 建表字段: 与 JSON 的统一字段一一对应
COLUMNS = [
    "title", "company", "company_type", "location",
    "salary_raw", "salary_min", "salary_max",
    "skills", "education", "experience", "recruitment_type",
    "description", "published_at", "source_site", "source_url", "fetched_at",
]


def clean_text(value) -> str:
    """去掉首尾空白和多余空格。"""
    if not isinstance(value, str):
        return value
    return " ".join(value.split()).strip()


def clean_job(job: dict) -> dict:
    """对单条职位做轻度清洗。"""
    job = dict(job)
    for key in ("title", "company", "location", "salary_raw"):
        job[key] = clean_text(job.get(key) or "")
    # 统一发布时间为 ISO 格式(国聘是 "2026-10-14 20:06:25"，外企已带时区)
    pub = job.get("published_at")
    if pub and " " in pub and "T" not in pub:
        pub = pub.replace(" ", "T") + "+08:00"       # 国聘时间是北京时间
    job["published_at"] = pub
    return job


def main() -> None:
    merged, seen_urls = [], set()

    for src in SOURCES:
        if not src.exists():
            print(f"[警告] 找不到 {src}，跳过")
            continue
        rows = json.loads(src.read_text(encoding="utf-8"))
        for job in rows:
            job = clean_job(job)
            url = job.get("source_url") or ""
            if not url or url in seen_urls:          # 指纹去重
                continue
            seen_urls.add(url)
            merged.append(job)

    # ---- 输出 JSON(按发布时间倒序，新的在前) ----
    merged.sort(key=lambda j: j.get("published_at") or "", reverse=True)
    payload = json.dumps(merged, ensure_ascii=False, indent=2)
    OUT_JSON.write_text(payload, encoding="utf-8")
    # 同步一份给前端构建用（Next.js 从 web/data/jobs.json 读取）
    WEB_JSON.parent.mkdir(parents=True, exist_ok=True)
    WEB_JSON.write_text(payload, encoding="utf-8")

    # ---- 输出 SQLite ----
    if OUT_DB.exists():
        OUT_DB.unlink()                              # 每次全量重建，逻辑最简单
    conn = sqlite3.connect(OUT_DB)
    cols_sql = ",\n    ".join(f"{c} TEXT" for c in COLUMNS)
    conn.execute(f"CREATE TABLE jobs (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    {cols_sql}\n)")
    conn.executemany(
        f"INSERT INTO jobs ({', '.join(COLUMNS)}) "
        f"VALUES ({', '.join('?' for _ in COLUMNS)})",
        [tuple(json.dumps(j[c], ensure_ascii=False) if isinstance(j.get(c), list) else j.get(c) for c in COLUMNS)
         for j in merged],
    )
    conn.commit()

    # ---- 统计报告 ----
    by_type = {}
    for j in merged:
        by_type[j["company_type"]] = by_type.get(j["company_type"], 0) + 1
    print("========== 合并报告 ==========")
    print(f"总计 {len(merged)} 条 (去重后)")
    for t, n in by_type.items():
        print(f"  {t}: {n} 条")
    print(f"JSON -> {OUT_JSON}")
    print(f"DB   -> {OUT_DB}")
    conn.close()


if __name__ == "__main__":
    main()
