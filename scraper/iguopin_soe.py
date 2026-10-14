# -*- coding: utf-8 -*-
"""国企招聘信息采集器（数据源: 国聘 iguopin.com，国资委旗下官方平台）。

接口要点:
    POST https://gp-api.iguopin.com/api/jobs/v3/list
    请求体: {"search": {"page": 页码, "page_size": 每页条数, "keyword": "", "with_offline": true}}
    需要签名头 Sign / T / Nonce（算法从官网前端 JS 中分析还原）。

签名算法（两层 HMAC-SHA256）:
    时间窗 window = 时间戳 // 180
    中间密钥 k    = HMAC_SHA256(密钥, "YYYYMMDD:时间窗")
    签名 sign     = HMAC_SHA256(k, "时间戳|随机数|POST|接口路径|pc")

用法: python iguopin_soe.py
"""

import hashlib
import hmac
import json
import random
import re
import string
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request as urlreq

from ats_foreign import extract_skills      # 复用外企采集器的技能抽取

# ---------------------------------------------------------------- 配置区 ----

API_HOST  = "https://gp-api.iguopin.com"
LIST_PATH = "/api/jobs/v3/list"
SIGN_KEY  = "cu4&dYe*feF8t$E9m"     # 官网前端内置的签名密钥(公开信息)
SUB_KEY   = 180                      # 时间窗除数(3 分钟一个窗口)

OUT_FILE      = Path(__file__).parent.parent / "data" / "soe_jobs.json"
MAX_PAGES     = 2                    # 匿名访问最多翻 2 页(再多要求登录)
PAGE_SIZE     = 50                   # 每页条数
REQUEST_INTERVAL = 1.5               # 请求间隔(秒)

HEADERS = {
    "User-Agent":   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0",
    "Content-Type": "application/json",
    "Origin":       "https://www.iguopin.com",
    "Referer":      "https://www.iguopin.com/job",
    "Device":       "pc",
    "Version":      "5.2.300",
    "Subsite":      "iguopin",
}

# ---------------------------------------------------------------- 签名与请求 ----


def make_sign_headers(method: str, path: str) -> dict:
    """按官网前端的规则生成 Sign / T / Nonce 三个请求头。"""
    ts    = int(time.time())
    nonce = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    window = ts // SUB_KEY
    day    = time.strftime("%Y%m%d", time.localtime(ts))

    # 第一层: 生成"日期:时间窗"的中间密钥
    k = hmac.new(SIGN_KEY.encode(), f"{day}:{window}".encode(),
                 hashlib.sha256).hexdigest()
    # 第二层: 对"时间戳|随机数|方法|路径|pc"签名
    msg = f"{ts}|{nonce}|{method.upper()}|{path}|pc"
    sign = hmac.new(k.encode(), msg.encode(), hashlib.sha256).hexdigest()

    return {"Sign": sign, "T": str(ts), "Nonce": nonce}


def post_job_list(page: int, page_size: int) -> dict:
    """请求一页职位列表，返回 data 字段(含 total/list)。"""
    headers = dict(HEADERS)
    headers.update(make_sign_headers("POST", LIST_PATH))
    body = json.dumps({"search": {
        "page": page, "page_size": page_size,
        "keyword": "", "with_offline": True,
    }}).encode()
    req = urlreq.Request(f"{API_HOST}{LIST_PATH}", data=body,
                         headers=headers, method="POST")
    with urlreq.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode("utf-8", "replace"))
    if result.get("code") != 200:
        raise RuntimeError(f"接口返回异常: {result.get('msg')}")
    return result.get("data") or {}

# ---------------------------------------------------------------- 字段整理 ----


def fmt_salary(item: dict) -> tuple[str, int | None, int | None]:
    """把接口里的薪资字段整理成 (原文, 最低, 最高)。"""
    if item.get("is_negotiable") or not item.get("min_wage") and not item.get("max_wage"):
        return "面议", None, None
    lo, hi = item.get("min_wage") or 0, item.get("max_wage") or 0
    unit   = item.get("wage_unit_cn") or "元/月"
    months = item.get("months")
    raw = f"{lo}~{hi}{unit}"
    if months and months != 12:
        raw += f"·{months}薪"
    return raw, lo or None, hi or None


def make_job(item: dict) -> dict:
    """把接口返回的一条职位转成统一字段结构。"""
    locations = " / ".join(
        d.get("area_cn", "") for d in item.get("district_list") or []
    )
    salary_raw, s_min, s_max = fmt_salary(item)
    job_id = item.get("job_id", "")
    return {
        "title":        (item.get("job_name") or "").strip(),
        "company":      (item.get("company_name") or "").strip(),
        "company_type": "国企",
        "location":     locations,
        "salary_raw":   salary_raw,
        "salary_min":   s_min,
        "salary_max":   s_max,
        "skills":       extract_skills(item.get("contents") or ""),
        "education":    item.get("education_cn"),
        "experience":   item.get("experience_cn"),
        "description":  (item.get("contents") or "")[:4000],   # 职位描述，截断到 4000 字符
        "recruitment_type": item.get("recruitment_type_cn"),   # 校园招聘/社会招聘
        "published_at": item.get("start_time"),
        "source_site":  "国聘",
        "source_url":   f"https://www.iguopin.com/job/detail?id={job_id}" if job_id else "",
        "fetched_at":   datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

# ---------------------------------------------------------------- 主流程 ----


def log(msg: str) -> None:
    print(msg, flush=True)


def main() -> None:
    all_jobs, seen_ids = [], set()

    for page in range(1, MAX_PAGES + 1):
        try:
            data = post_job_list(page, PAGE_SIZE)
        except RuntimeError as exc:
            # 典型情况: 翻页超过匿名上限提示"登录后查看更多岗位"，用已有数据收工
            log(f"[提示] 第 {page} 页受限: {exc}，改用已采集数据")
            break
        rows  = data.get("list") or []
        total = data.get("total", "?")
        log(f"第 {page} 页: 拿到 {len(rows)} 条 (平台共 {total} 条在招)")

        for item in rows:
            jid = item.get("job_id")
            if not jid or jid in seen_ids:
                continue
            seen_ids.add(jid)
            all_jobs.append(make_job(item))

        if len(rows) < PAGE_SIZE:
            break
        time.sleep(REQUEST_INTERVAL)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(all_jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # ---- 简单统计 ----
    with_salary = sum(1 for j in all_jobs if j["salary_min"])
    campus     = sum(1 for j in all_jobs if "校" in (j["recruitment_type"] or ""))
    log("\n========== 采集报告 ==========")
    log(f"共采集 {len(all_jobs)} 条国企职位")
    log(f"有薪资范围: {with_salary} 条; 校招: {campus} 条")
    log(f"已保存 -> {OUT_FILE}")


if __name__ == "__main__":
    main()
