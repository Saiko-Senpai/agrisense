interface SectionHeaderProps {
  badge: string;
  title: string;
  subtitle?: string;
  center?: boolean;
}

export default function SectionHeader({
  badge,
  title,
  subtitle,
  center = true,
}: SectionHeaderProps) {
  return (
    <div className={`mb-10 ${center ? "text-center" : ""}`}>
      <span className="inline-flex items-center gap-2 bg-amber-50 text-amber-800 border border-amber-200 px-4 py-1.5 rounded-full text-sm font-semibold mb-4">
        {badge}
      </span>
      <h2 className="text-3xl md:text-4xl font-serif text-green-800 mb-3 leading-tight">
        {title}
      </h2>
      {subtitle && (
        <p className="text-green-700/60 text-base md:text-lg max-w-2xl mx-auto">
          {subtitle}
        </p>
      )}
    </div>
  );
}
