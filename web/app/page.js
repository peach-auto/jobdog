import JobExplorer from "../components/JobExplorer";
import { JOBS, CITIES } from "../lib/jobs";

// 首页整页静态化：数据在构建时读入，访问时零服务端开销
export const dynamic = "force-static";

export default function Home() {
  const soeCount  = JOBS.filter((j) => j.company_type === "国企").length;
  const withSalary = JOBS.filter((j) => j.salary_min).length;
  const zhuanBenke = JOBS.filter((j) => j.eduRank <= 2).length;   // 专科/本科可投
  const latest    = JOBS[0]?.published_at?.slice(0, 10) || "";

  return (
    <>
      <section className="hero">
        <div className="container">
          <h1>国企 · 外企招聘信息聚合</h1>
          <p>公开渠道每日采集，一站浏览职位、薪资、技能要求，直达原文投递</p>
          <div className="hero-stats">
            <span className="stat-chip">在招职位 <b>{JOBS.length}</b></span>
            <span className="stat-chip">国企 <b>{soeCount}</b></span>
            <span className="stat-chip">外企 <b>{JOBS.length - soeCount}</b></span>
            <span className="stat-chip">专科·本科可投 <b>{zhuanBenke}</b></span>
            <span className="stat-chip">含薪资 <b>{withSalary}</b></span>
            {latest && <span className="stat-chip">更新至 <b>{latest}</b></span>}
          </div>
        </div>
      </section>

      <JobExplorer jobs={JOBS} cities={CITIES} />
    </>
  );
}
