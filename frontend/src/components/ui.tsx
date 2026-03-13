export function Spinner({ text = "Cargando…" }: { text?: string }) {
  return (
    <div className="flex items-center gap-3 py-8 justify-center text-gray-500">
      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
      </svg>
      <span className="text-sm">{text}</span>
    </div>
  );
}

export function ErrorBox({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
      <span className="text-red-500 text-lg leading-none">⚠</span>
      <div className="flex-1">
        <p className="text-sm text-red-700">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Reintentar
          </button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({
  icon = "📭",
  title,
  description,
}: {
  icon?: string;
  title: string;
  description?: string;
}) {
  return (
    <div className="text-center py-12">
      <span className="text-4xl block mb-3">{icon}</span>
      <p className="text-gray-600 font-medium">{title}</p>
      {description && <p className="text-sm text-gray-400 mt-1">{description}</p>}
    </div>
  );
}

export function SectionCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      {children}
    </div>
  );
}

export function InfoBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="p-3 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-lg mb-4">
      {children}
    </div>
  );
}
