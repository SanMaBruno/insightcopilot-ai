import { Link, Outlet, useLocation } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Home" },
  { to: "/datasets", label: "Datasets" },
] as const;

export default function AppLayout() {
  const { pathname } = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-gray-900 hover:text-blue-600 transition">
          InsightCopilot AI
        </Link>
        <nav className="flex gap-4">
          {NAV_ITEMS.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`text-sm font-medium transition ${
                (to === "/" ? pathname === "/" : pathname.startsWith(to))
                  ? "text-blue-600"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 px-6 py-4 text-center text-xs text-gray-400">
        InsightCopilot AI — Portfolio Project
      </footer>
    </div>
  );
}
