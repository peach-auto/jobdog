import { fmtDate, fmtSalary } from "../lib/jobs";

/** 单条职位卡片：点标题进详情页，卡片内提供原文链接 */
export default function JobCard({ job }) {
  const isSoe = job.company_type === "国企";
  return (
    <div className="job-card">
      <div className="job-card-top">
        <a className="job-title" href={`/job/${job.id}`}>{job.title}</a>
        <span className="job-salary">{fmtSalary(job)}</span>
      </div>

      <div className="job-company-row">
        <span className="job-company">{job.company}</span>
        <span className={`badge ${isSoe ? "soe" : "foreign"}`}>{job.company_type}</span>
        {job.recruitment_type && <span className="badge plain">{job.recruitment_type}</span>}
      </div>

      <div className="job-meta">
        {job.location && <span>{job.location}</span>}
        {job.education && <span>{job.education}</span>}
        {job.experience && <span>{job.experience}</span>}
        <span>{fmtDate(job.published_at)} 发布</span>
      </div>

      {job.skills?.length > 0 && (
        <div className="skill-tags">
          {job.skills.slice(0, 6).map((s) => <span key={s} className="skill-tag">{s}</span>)}
        </div>
      )}

      <div className="job-footer">
        <span>来源: {job.source_site}</span>
        <a className="link" href={`/job/${job.id}`}>查看详情 →</a>
      </div>
    </div>
  );
}
