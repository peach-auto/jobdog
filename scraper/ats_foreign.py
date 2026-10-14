# -*- coding: utf-8 -*-
"""外企招聘信息采集器。

原理: 外企普遍使用 Greenhouse / Lever / Ashby 等招聘系统(ATS)，
      这些系统提供免登录的公开 JSON 接口，直接请求即可拿到职位数据。

流程: 遍历 companies.py 名单 -> 调对应接口 -> 筛选中国职位
      -> 抽取技能关键词 -> 统一字段 -> 存为 data/foreign_jobs.json

用法: python ats_foreign.py
"""

import html
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import request as urlreq

from companies import COMPANY_LIST

# ---------------------------------------------------------------- 配置区 ----

OUT_FILE = Path(__file__).parent.parent / "data" / "foreign_jobs.json"
REQUEST_INTERVAL = 1.0          # 每次请求间隔(秒)，控制频率、避免给对方造成压力
MAX_JOBS_PER_COMPANY = 50       # 单家公司最多保留的职位数

# 中国相关关键词: 职位地点里出现其一才算"在华职位"
TARGET_CITY_KEYWORDS = [
    "China", "Beijing", "Shanghai", "Shenzhen", "Hangzhou", "Suzhou",
    "Guangzhou", "Chengdu", "Nanjing", "Wuhan", "Xi'an", "Dalian",
    "Qingdao", "Hefei", "Xiamen", "Changsha", "Zhuhai", "Wuxi",
    "Ningbo", "Shenyang", "Dongguan",
    "Hong Kong", "Taipei", "Remote - APAC", "中国", "北京", "上海",
    "深圳", "杭州", "苏州", "广州", "成都", "南京", "武汉", "西安",
    "大连", "香港", "台北",
]

# 技能关键词表: 从职位描述(JD)里做匹配，命中哪些就记录哪些
SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "Golang", "C++", "C#", "Rust",
    "SQL", "MySQL", "PostgreSQL", "Redis", "MongoDB", "Kafka", "Spark",
    "Hadoop", "Flink", "Kubernetes", "Docker", "Linux", "AWS", "Azure", "GCP",
    "React", "Vue", "Angular", "Node.js", "Spring", "GraphQL",
    "Machine Learning", "Deep Learning", "LLM", "NLP", "TensorFlow", "PyTorch",
    "Git", "CI/CD", "Terraform", "SRE", "Data Engineer",
    "微服务", "分布式", "大数据", "机器学习", "深度学习",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
}

# ---------------------------------------------------------------- 工具函数 ----


def fetch_json(url: str, timeout: int = 25) -> dict | list:
    """请求一个 URL 并把返回内容解析成 JSON。"""
    req = urlreq.Request(url, headers=HEADERS)
    with urlreq.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def strip_html(raw: str) -> str:
    """清洗 HTML 文本。注意顺序: Greenhouse 返回的是"转义过的HTML"，
    必须先还原实体(&lt;p&gt; -> <p>)，再去标签，否则标签会残留。"""
    text = html.unescape(raw or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return html.unescape(text)


def extract_skills(jd_text: str) -> list[str]:
    """在职位描述里匹配技能关键词，返回命中列表(保持词表顺序)。"""
    found = []
    for skill in SKILL_KEYWORDS:
        # \b 保证按整词匹配，避免 "Java" 命中 "JavaScript"
        pattern = re.escape(skill).replace(r"\ ", r"\s+")
        if re.search(rf"(?i)(?<![A-Za-z]){pattern}(?![A-Za-z])", jd_text):
            found.append(skill)
    return found


def is_china_job(location: str) -> bool:
    """判断职位地点是否属于中国(含港台)。"""
    return any(kw.lower() in (location or "").lower() for kw in TARGET_CITY_KEYWORDS)


def make_job(company: str, title: str, location: str, jd_text: str,
             published_at: str | None, url: str, source_site: str) -> dict:
    """把各家接口的原始数据整理成统一字段的职位记录。"""
    # 外企接口一般不公布中国区薪资，如实标注"面议"
    return {
        "title":        title.strip(),
        "company":      company,
        "company_type": "外企",
        "location":     location.strip(),
        "salary_raw":   "面议",
        "salary_min":   None,
        "salary_max":   None,
        "skills":       extract_skills(jd_text),
        "education":    None,
        "experience":   None,
        "description":  jd_text[:4000],              # 职位描述，截断到 4000 字符
        "published_at": published_at,
        "source_site":  source_site,
        "source_url":   url,
        "fetched_at":   datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

# ---------------------------------------------------------------- 三种接口 ----


def fetch_greenhouse(company: str, token: str) -> list[dict]:
    """Greenhouse 公开接口: 一次返回该公司全部职位。"""
    data = fetch_json(
        f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    )
    jobs = []
    for j in data.get("jobs", []):
        location = (j.get("location") or {}).get("name", "")
        if not is_china_job(location):
            continue
        jd_text = strip_html(j.get("content", ""))
        jobs.append(make_job(
            company=company,
            title=j.get("title", ""),
            location=location,
            jd_text=jd_text,
            published_at=j.get("updated_at"),      # Greenhouse 只有更新时间
            url=j.get("absolute_url", ""),
            source_site="Greenhouse",
        ))
    return jobs[:MAX_JOBS_PER_COMPANY]


def fetch_lever(company: str, token: str) -> list[dict]:
    """Lever 公开接口: mode=json 返回纯文本描述。"""
    data = fetch_json(f"https://api.lever.co/v0/postings/{token}?mode=json")
    jobs = []
    for j in data:
        location = (j.get("categories") or {}).get("location", "")
        if not is_china_job(location):
            continue
        created_ms = j.get("createdAt")
        published = (
            datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).isoformat(timespec="seconds")
            if created_ms else None
        )
        jobs.append(make_job(
            company=company,
            title=j.get("text", ""),
            location=location,
            jd_text=j.get("descriptionPlain", "") or "",
            published_at=published,
            url=j.get("hostedUrl", ""),
            source_site="Lever",
        ))
    return jobs[:MAX_JOBS_PER_COMPANY]


def fetch_ashby(company: str, token: str) -> list[dict]:
    """Ashby 公开接口: posting-api/job-board/{token}。"""
    data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{token}")
    jobs = []
    for j in data.get("jobs", []):
        location = j.get("location") or ""
        if not is_china_job(location):
            continue
        jobs.append(make_job(
            company=company,
            title=j.get("title", ""),
            location=location,
            jd_text=j.get("descriptionPlain", "") or strip_html(j.get("description", "")),
            published_at=j.get("publishedAt"),
            url=j.get("jobUrl", ""),
            source_site="Ashby",
        ))
    return jobs[:MAX_JOBS_PER_COMPANY]


FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever":      fetch_lever,
    "ashby":      fetch_ashby,
}

# ---------------------------------------------------------------- 主流程 ----


def log(msg: str) -> None:
    """带即时刷新的打印，避免后台运行时日志被缓冲看不到进度。"""
    print(msg, flush=True)


def main() -> None:
    all_jobs: list[dict] = []
    ok, empty, fail = [], [], []          # 三类结果: 有中国职位 / 接口正常但无 / 失败

    for name, ats, token in COMPANY_LIST:
        fetch = FETCHERS.get(ats)
        if fetch is None:
            log(f"[跳过] {name}: 未知 ATS 类型 {ats}")
            continue
        try:
            jobs = fetch(name, token)
            if jobs:
                ok.append((name, len(jobs)))
                all_jobs.extend(jobs)
                log(f"[OK  ] {name}: 抓到 {len(jobs)} 个中国职位")
            else:
                empty.append(name)
                log(f"[--  ] {name}: 接口正常，暂无中国职位")
        except Exception as exc:
            fail.append((name, str(exc)[:60]))
            log(f"[失败] {name}: {exc}")
        time.sleep(REQUEST_INTERVAL)       # 控制频率，做礼貌的采集者

    # ---- 输出统计与结果文件 ----
    log("\n========== 采集报告 ==========")
    log(f"名单公司数: {len(COMPANY_LIST)}")
    log(f"有中国职位: {len(ok)} 家, 共 {len(all_jobs)} 条")
    log(f"无中国职位: {len(empty)} 家;  失败: {len(fail)} 家")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(all_jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log(f"已保存 -> {OUT_FILE}")


if __name__ == "__main__":
    main()
