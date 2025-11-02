import { Link } from 'react-router-dom';
import { useSession } from '@/contexts/SessionContext';
import { Button } from './Button';
import { useState, useEffect } from 'react';
import { LogOut } from 'lucide-react';

interface HeaderProps {
  onLoginClick: () => void;
}

export function Header({ onLoginClick }: HeaderProps) {
  const { isAuthed, signOut } = useSession();
  const [scrolled, setScrolled] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 24);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      className="fixed top-0 left-0 right-0 z-40 transition-all duration-260"
      style={{
        background: scrolled 
          ? 'linear-gradient(to bottom, hsl(var(--bg)) 0%, hsl(var(--bg) / 0.95) 100%)'
          : 'transparent',
        boxShadow: scrolled ? '0 1px 0 hsl(var(--stroke))' : 'none'
      }}
    >
      <div className="container mx-auto px-6 py-6 flex items-center justify-between">
        <Link
          to="/"
          className="font-display font-bold text-xl tracking-[0.02em] text-[hsl(var(--text))] hover:text-[hsl(var(--accent))] transition-colors focus-ring rounded"
        >
          FASTTRACK
        </Link>

        {!isAuthed ? (
          <Button variant="text" onClick={onLoginClick}>
            Login
          </Button>
        ) : (
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="w-10 h-10 rounded-full bg-[hsl(var(--accent))] text-[hsl(var(--bg))] font-medium flex items-center justify-center focus-ring"
              aria-label="User menu"
            >
              U
            </button>

            {showMenu && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowMenu(false)}
                />
                <div className="absolute right-0 top-full mt-2 w-48 panel p-2 z-50">
                  <Link
                    to="/dashboard"
                    className="block px-4 py-2 text-sm text-[hsl(var(--text))] hover:bg-[hsl(var(--panel))] rounded-lg transition-colors"
                    onClick={() => setShowMenu(false)}
                  >
                    Dashboard
                  </Link>
                  <button
                    onClick={() => {
                      signOut();
                      setShowMenu(false);
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2 text-sm text-[hsl(var(--text))] hover:bg-[hsl(var(--panel))] rounded-lg transition-colors"
                  >
                    <LogOut size={16} />
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
