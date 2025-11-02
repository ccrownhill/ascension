import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[hsl(var(--bg))]">
      <div className="text-center">
        <h1 className="mb-4 text-6xl font-bold text-[hsl(var(--text))]">404</h1>
        <p className="mb-6 text-xl text-[hsl(var(--muted))]">Page not found</p>
        <Link 
          to="/" 
          className="text-[hsl(var(--accent))] hover:underline focus-ring rounded px-2 py-1"
        >
          Return to Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
