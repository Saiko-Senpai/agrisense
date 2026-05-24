import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4">
      <div className="text-8xl mb-6">🌾</div>
      <h1 className="text-4xl font-serif text-green-800 mb-3">Page Not Found</h1>
      <p className="text-green-700/60 mb-8 max-w-md">
        The page you are looking for does not exist. It may have been moved or deleted.
      </p>
      <Link
        href="/"
        className="px-6 py-3 bg-green-600 text-white rounded-full font-semibold hover:bg-green-500 transition-colors"
      >
        ← Back to Home
      </Link>
    </div>
  );
}
