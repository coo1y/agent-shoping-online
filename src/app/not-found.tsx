
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <h1 className="text-4xl font-black text-[#222] mb-4">404 - Page Not Found</h1>
      <p className="text-muted-foreground text-lg mb-8">
        We couldn&apos;t find the page you were looking for.
      </p>
      <Link 
        href="/"
        className="inline-flex items-center justify-center h-10 px-8 text-sm font-bold text-white transition-colors bg-[#222] hover:bg-[#000] rounded-none uppercase tracking-wide"
      >
        Return Home
      </Link>
    </div>
  )
}
