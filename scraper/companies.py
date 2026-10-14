# -*- coding: utf-8 -*-
"""外企公司名单：每家公司对应一个招聘系统(ATS)的公开接口标识。

ats 取值说明:
    greenhouse  -> boards-api.greenhouse.io 公开接口
    lever       -> api.lever.co 公开接口
    ashby       -> api.ashbyhq.com 公开接口

维护说明: 404 的公司(token 失效)直接删除；抓到中国职位的保留。
"""

COMPANY_LIST = [
    # ---- 第一批: 已验证能抓到中国职位的 ----
    ("Stripe",         "greenhouse", "stripe"),
    ("Airbnb",         "greenhouse", "airbnb"),
    ("Databricks",     "greenhouse", "databricks"),
    ("MongoDB",        "greenhouse", "mongodb"),
    ("Canonical",      "greenhouse", "canonical"),
    ("Akuna Capital",  "greenhouse", "akunacapital"),
    ("Elastic",        "greenhouse", "elastic"),
    ("Cloudflare",     "greenhouse", "cloudflare"),

    # ---- 第二批: 在华有办公室的外企(设计/游戏/广告/硬件) ----
    ("Canva",          "greenhouse", "canva"),
    ("Unity",          "greenhouse", "unity"),
    ("Roblox",         "greenhouse", "roblox"),
    ("Duolingo",       "greenhouse", "duolingo"),
    ("AppLovin",       "greenhouse", "applovin"),
    ("Liftoff",        "greenhouse", "liftoff"),
    ("Moloco",         "greenhouse", "moloco"),
    ("AppsFlyer",      "greenhouse", "appsflyer"),
    ("Criteo",         "greenhouse", "criteo"),
    ("The Trade Desk", "greenhouse", "thetradedesk"),
    ("PubMatic",       "greenhouse", "pubmatic"),
    ("DoubleVerify",   "greenhouse", "doubleverify"),
    ("FreeWheel",      "greenhouse", "freewheel"),
    ("Mobileye",       "greenhouse", "mobileye"),
    ("Logitech",       "greenhouse", "logitech"),
    ("GoPro",          "greenhouse", "gopro"),
    ("Razer",          "greenhouse", "razer"),
    ("Shopee",         "greenhouse", "shopee"),
    ("Grab",           "greenhouse", "grab"),

    # ---- 第二批: 开发者工具/基础设施(在华有研发或远程岗) ----
    ("Kong",           "greenhouse", "kong"),
    ("Tetrate",        "greenhouse", "tetrate"),
    ("Redis",          "greenhouse", "redis"),
    ("InfluxData",     "greenhouse", "influxdata"),
    ("Cloudera",       "greenhouse", "cloudera"),
    ("Grafana Labs",   "greenhouse", "grafana"),

    # ---- 第二批: 安全/网络(在华有办公室) ----
    ("Zscaler",        "greenhouse", "zscaler"),
    ("Palo Alto Networks", "greenhouse", "paloaltonetworks"),
    ("Trend Micro",    "greenhouse", "trendmicro"),
    ("Netskope",       "greenhouse", "netskope"),
    ("Thoughtworks",   "greenhouse", "thoughtworks"),

    # ---- 第二批: 量化金融(上海/深圳办公室) ----
    ("Two Sigma",      "greenhouse", "twosigma"),
    ("Squarepoint",    "greenhouse", "squarepoint"),
    ("Jump Trading",   "greenhouse", "jumptrading"),
    ("IMC Trading",    "greenhouse", "imctrading"),
    ("Flow Traders",   "greenhouse", "flowtraders"),

    # ---- 第二批: 其他 ATS ----
    ("Deel",           "ashby",      "Deel"),
]
