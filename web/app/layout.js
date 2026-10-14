import "./globals.css";

export const metadata = {
  title: "职汇 | 国企·外企招聘信息聚合",
  description:
    "每日聚合国企与外企公开招聘信息：职位名称、公司、地点、薪资范围、技能要求、发布时间与原文链接，一站浏览。",
};

export default function RootLayout({ children }) {
  return (
    <html lang="zh-CN">
      <body>
        <header className="header">
          <div className="container header-inner">
            <a href="/" className="brand">
              <span className="brand-logo">职</span>
              <span>
                <div className="brand-name">职汇</div>
                <div className="brand-sub">国企 · 外企招聘信息聚合</div>
              </span>
            </a>
            <span className="header-note">数据来自公开渠道 · 每日自动更新</span>
          </div>
        </header>
        {children}
        <footer className="footer">
          <div className="container footer-inner">
            <span>
              数据来源：<a href="https://www.iguopin.com" target="_blank" rel="noreferrer">国聘</a>
              （国资委旗下平台）及各公司官方招聘系统（Greenhouse / Lever / Ashby）
            </span>
            <span>所有职位信息以来源页面为准，本站仅作聚合展示，不参与任何应聘流程。</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
