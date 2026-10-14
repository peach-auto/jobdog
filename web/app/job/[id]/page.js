import { JOBS, getJobById, fmtDate, fmtSalary } from "../../../lib/jobs";

// 详情页静态化: 构建时为每个职位生成一个页面
export const dynamic = "force-static";

export function generateStaticParams() {
  return JOBS.map((j) => ({ id: j.id }));
}

export async function generateMetadata({ params }) {
  const { id } = await params;
  const job = getJobById(id);
  if (!job) return { title: "职位不存在" };
  return {
    title: `${job.title} - ${job.company} | 职汇`,
    description: (job.description || "").slice(0, 80),
  };
}

export default async function JobDetail({ params }) {
  const { id } = await params;
  const job = getJobById(id);
  if (!job) {
    return (
      <div className="container detail-wrap">
        <div className="empty">
          <div className="icon">🫥</div>
          <p>职位不存在或已下线，<a href="/" style={{ color: "var(--primary)" }}>返回首页</a></p>
        </div>
      </div>
    );
  }

  const isSoe = job.company_type === "国企";
  const infos = [
    { k: "工作地点", v: job.location || "—" },
    { k: "薪资",     v: fmtSalary(job) },
    { k: "学历要求", v: job.education || "—" },
    { k: "经验要求", v: job.experience || "—" },
    { k: "招聘类型", v: job.recruitment_type || "—" },
    { k: "发布时间", v: fmtDate(job.published_at) },
    { k: "信息来源", v: job.source_site },
    { k: "职位类别", v: job.company_type },
  ];

  return (
    <div className="container detail-wrap">
      <a className="back-link" href="/">← 返回职位列表</a>

      <article className="detail-card">
        <div className="detail-head">
          <h1 className="detail-title">{job.title}</h1>
          <span className="detail-salary">{fmtSalary(job)}</span>
        </div>

        <div className="detail-company">
          <span className="job-company">{job.company}</span>
          <span className={`badge ${isSoe ? "soe" : "foreign"}`}>{job.company_type}</span>
          {job.recruitment_type && <span className="badge plain">{job.recruitment_type}</span>}
        </div>

        <div className="info-grid">
          {infos.map((it) => (
            <div className="info-item" key={it.k}>
              <div className="k">{it.k}</div>
              <div className="v">{it.v}</div>
            </div>
          ))}
        </div>

        {job.skills?.length > 0 && (
          <div className="skill-tags" style={{ marginTop: 18 }}>
            {job.skills.map((s) => <span key={s} className="skill-tag">{s}</span>)}
          </div>
        )}

        {job.description && (
          <div className="detail-desc">
            <h3>职位描述</h3>
            <div className="jd">{job.description}</div>
          </div>
        )}

        <a className="apply-btn" href={job.source_url} target="_blank" rel="noreferrer">
          前往原文查看 / 投递 ↗
        </a>
      </article>
    </div>
  );
}
