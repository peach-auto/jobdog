// 职位数据加载与工具函数
// 数据来自 Python 采集器合并后的 data/jobs.json（构建时静态读入，无运行时开销）

import rawData from "../data/jobs.json";

/** 给每条职位生成稳定短 ID（对来源链接做 djb2 哈希），用于详情页路由 */
function shortId(url) {
  let h = 5381;
  for (let i = 0; i < url.length; i++) {
    h = ((h << 5) + h + url.charCodeAt(i)) >>> 0;
  }
  return h.toString(36);
}

/* 城市归一化: 外企职位的地点常是 "Beijing; Shanghai" 这类原文串，
   用关键词表映射成统一城市名，筛选项才干净 */
const CITY_RULES = [
  ["北京", ["beijing", "北京"]],
  ["上海", ["shanghai", "上海"]],
  ["深圳", ["shenzhen", "深圳"]],
  ["广州", ["guangzhou", "广州"]],
  ["杭州", ["hangzhou", "杭州"]],
  ["成都", ["chengdu", "成都"]],
  ["苏州", ["suzhou", "苏州"]],
  ["南京", ["nanjing", "南京"]],
  ["武汉", ["wuhan", "武汉"]],
  ["西安", ["xi'an", "西安"]],
  ["大连", ["dalian", "大连"]],
  ["厦门", ["xiamen", "厦门"]],
  ["合肥", ["hefei", "合肥"]],
  ["香港", ["hong kong", "香港"]],
  ["台北", ["taipei", "台北"]],
];

function normalizeCity(location) {
  if (!location) return "";
  const lower = location.toLowerCase();
  for (const [city, keys] of CITY_RULES) {
    if (keys.some((k) => lower.includes(k))) return city;
  }
  // 中文地点(如 "宜宾市-翠屏区")取 "-" 前段并去掉"市"字
  const first = location.split(/[-/·,;]/)[0].trim();
  if (/[\u4e00-\u9fa5]/.test(first)) return first.replace(/市$/, "");
  return "其他";                                   // "Home based" 等无法识别的归为一类
}

/* 学历分级: 数字越小门槛越低。未注明的一律视为"可投"(rank 0) */
const EDU_RANK = {
  "无学历要求": 0, "学历不限": 0,
  "高中": 1, "中专/中技": 1, "大专": 1, "专科": 1,
  "本科": 2, "硕士": 3, "博士": 4,
};

function eduRankOf(job) {
  const e = job.education;
  if (!e) return 0;                        // 未注明 -> 默认可投
  return EDU_RANK[e] ?? 0;
}

/** 统一数据结构：补上 id、规范时间显示 */
export const JOBS = rawData.map((j) => ({
  ...j,
  id: shortId(j.source_url || j.title + j.company),
  city: normalizeCity(j.location),
  eduRank: eduRankOf(j),
})).sort((a, b) => (b.published_at || "").localeCompare(a.published_at || ""));

/** 城市列表（归一化后） */
export const CITIES = [...new Set(JOBS.map((j) => j.city).filter(Boolean))]
  .sort((a, b) => a.localeCompare(b, "zh"));

export function getJobById(id) {
  return JOBS.find((j) => j.id === id) || null;
}

/** 格式化发布时间为 YYYY-MM-DD */
export function fmtDate(iso) {
  if (!iso) return "—";
  return iso.slice(0, 10);
}

/** 薪资显示：有范围用范围，否则显示原文（面议） */
export function fmtSalary(job) {
  return job.salary_raw || "面议";
}
