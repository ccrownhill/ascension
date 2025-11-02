import { useState } from 'react';
import { CursorShadow } from '@/components/CursorShadow';
import { AmbientGrid } from '@/components/AmbientGrid';
import { Header } from '@/components/Header';
import { UploadCard } from '@/components/UploadCard';
import { AuthModal } from '@/components/AuthModal';
import { useToast } from '@/components/Toast';

const Index = () => {
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const { ToastContainer } = useToast();

  return (
    <>
      <CursorShadow />
      <AmbientGrid />
      
      {/* Background gradients */}
      <div 
        className="fixed inset-0 pointer-events-none"
        style={{
          background: `
            radial-gradient(circle at 20% 20%, hsl(220 60% 12% / 0.4) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, hsl(199 60% 20% / 0.2) 0%, transparent 50%)
          `
        }}
      />

      <div className="relative min-h-screen">
        <Header onLoginClick={() => setAuthModalOpen(true)} />

        <main className="container mx-auto px-6 flex flex-col items-center justify-center min-h-screen">
          <UploadCard />

          <footer className="mt-16 text-center">
            <p className="text-sm text-[hsl(var(--muted))]">
              Automated applications. Human results.
            </p>
          </footer>
        </main>
      </div>

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
      <ToastContainer />
    </>
  );
};

export default Index;
