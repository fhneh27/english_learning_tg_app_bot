type PageHeaderProps = {
  title: string;
  description?: string;
  eyebrow?: string;
  meta?: string[];
};

function PageHeader({ title, description, eyebrow, meta = [] }: PageHeaderProps) {
  return (
    <header className="page-header">
      {eyebrow ? <p className="page-eyebrow">{eyebrow}</p> : null}
      <div className="page-header-top">
        <h1>{title}</h1>
      </div>
      {description ? <p className="page-description">{description}</p> : null}
      {meta.length > 0 ? (
        <div className="page-meta">
          {meta.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      ) : null}
    </header>
  );
}

export default PageHeader;
