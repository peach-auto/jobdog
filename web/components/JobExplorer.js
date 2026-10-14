"use client";

import { useMemo, useState, useEffect } from "react";
import JobCard from "./JobCard";

const PAGE_SIZE = 20;
const TYPES = [
  { key: "all", label: "全部" },
  { key: "国企", label: "国企" },
  { key: "外企", label: "外企" },
];

export default function JobExplorer({ jobs, cities }) {
  const [keyword, setKeyword] = useState("");        // 输入框实时值
  const [query, setQuery] = useState("");            // 防抖后真正参与搜索的值
  const [type, setType] = useState("all");
  const [city, setCity] = useState("all");
  const [edu, setEdu] = useState("all");
  const [hasSalary, setHasSalary] = useState(false);
  const [page, setPage] = useState(1);

  // 搜索防抖: 输入停顿 250ms 后才触发过滤，避免每敲一个字就重算整张表
  useEffect(() => {
    const t = setTimeout(() => { setQuery(keyword.trim()); setPage(1); }, 250);
    return () => clearTimeout(t);
  }, [keyword]);

  const filtered = useMemo(() => {
    const q = query.toLowerCase();
    return jobs.filter((j) => {
      if (type !== "all" && j.company_type !== type) return false;
      if (city !== "all" && j.city !== city) return false;
      if (hasSalary && !j.salary_min) return false;
      if (edu === "zhuanke" && j.eduRank > 1) return false;   // 专科可投(含未注明)
      if (edu === "benke" && j.eduRank > 2) return false;     // 本科可投(含专科及未注明)
      if (edu === "shuoshi" && j.eduRank < 3) return false;   // 硕士及以上
      if (q) {
        const hay = `${j.title}${j.company}${j.location}${(j.skills || []).join()}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [jobs, query, type, city, hasSalary, edu]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageJobs = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  // 分页页码: 最多显示 7 个，超出时当前页居中
  const pageItems = useMemo(() => {
    const items = [];
    const span = 2;
    for (let p = 1; p <= totalPages; p++) {
      if (p === 1 || p === totalPages || Math.abs(p - page) <= span) items.push(p);
      else if (items[items.length - 1] !== "…") items.push("…");
    }
    return items;
  }, [totalPages, page]);

  return (
    <>
      <div className="container search-area">
        <div className="search-box">
          <input
            className="search-input"
            placeholder="搜索职位名 / 公司 / 技能，如: Python、北京、东方电气"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
          />
          <button className="search-btn" onClick={() => setQuery(keyword.trim())}>搜索</button>
        </div>
      </div>

      <div className="filter-bar">
        <div className="container filter-inner">
          <div className="segmented">
            {TYPES.map((t) => (
              <button key={t.key} className={type === t.key ? "on" : ""}
                      onClick={() => { setType(t.key); setPage(1); }}>
                {t.label}
              </button>
            ))}
          </div>

          <select className="filter-select" value={city}
                  onChange={(e) => { setCity(e.target.value); setPage(1); }}>
            <option value="all">全部城市</option>
            {cities.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>

          <select className="filter-select" value={edu}
                  onChange={(e) => { setEdu(e.target.value); setPage(1); }}>
            <option value="all">不限学历</option>
            <option value="zhuanke">专科可投</option>
            <option value="benke">本科可投</option>
            <option value="shuoshi">硕士及以上</option>
          </select>

          <select className="filter-select" value={hasSalary ? "1" : "0"}
                  onChange={(e) => { setHasSalary(e.target.value === "1"); setPage(1); }}>
            <option value="0">不限薪资</option>
            <option value="1">仅看有薪资</option>
          </select>

          <span className="result-count">
            {filtered.length === jobs.length
              ? `共 ${jobs.length} 个职位`
              : `筛选出 ${filtered.length} / ${jobs.length} 个职位`}
          </span>
        </div>
      </div>

      <div className="container">
        {pageJobs.length === 0 ? (
          <div className="empty">
            <div className="icon">🔍</div>
            <p>没有找到匹配的职位，换个关键词或放宽筛选条件试试</p>
          </div>
        ) : (
          <div className="job-list">
            {pageJobs.map((j) => <JobCard key={j.id} job={j} />)}
          </div>
        )}

        {totalPages > 1 && (
          <div className="pager">
            <button disabled={page === 1} onClick={() => setPage(page - 1)}>‹</button>
            {pageItems.map((p, i) =>
              p === "…" ? (
                <span key={`g${i}`} className="gap">…</span>
              ) : (
                <button key={p} className={p === page ? "on" : ""} onClick={() => setPage(p)}>
                  {p}
                </button>
              ),
            )}
            <button disabled={page === totalPages} onClick={() => setPage(page + 1)}>›</button>
          </div>
        )}
      </div>
    </>
  );
}
