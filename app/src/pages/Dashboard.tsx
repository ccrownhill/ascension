import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CursorShadow } from '@/components/CursorShadow';
import { AmbientGrid } from '@/components/AmbientGrid';
import { Header } from '@/components/Header';
import { UploadCard } from '@/components/UploadCard';
import { RecentUploads } from '@/components/RecentUploads';
import { AuthModal } from '@/components/AuthModal';
import { Button } from '@/components/Button';
import { useSession } from '@/contexts/SessionContext';
import { useToast } from '@/components/Toast';

interface Upload {
  name: string;
  size: number;
}

interface FileUpload extends Upload {
  file: File;
}

const Dashboard = () => {
  const { isAuthed } = useSession();
  const navigate = useNavigate();
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [fileUploads, setFileUploads] = useState<FileUpload[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const { showToast, ToastContainer } = useToast();


  useEffect(() => {
    if (!isAuthed) {
      navigate('/');
    }
  }, [isAuthed, navigate]);

  const handleFileSelect = (file: File) => {
    setUploads(prev => [{ name: file.name, size: file.size }, ...prev]);
    setFileUploads(prev => [{ name: file.name, size: file.size, file }, ...prev]);
  };

  const handleApply = async () => {
    if (fileUploads.length === 0) {
      showToast('Please upload a file first');
      return;
    }

    setIsUploading(true);
    const fileUpload = fileUploads[0]; // Get the most recent upload

    try {
      const formData = new FormData();
      formData.append('file', fileUpload.file);

      const response = await fetch('http://localhost:8080/api/upload-cv', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        showToast('File uploaded and script triggered successfully');
      } else {
        showToast('Failed to upload file');
      }
    } catch (error) {
      console.error('Upload error:', error);
      showToast('Error uploading file');
    } finally {
      setIsUploading(false);
    }
  };

  if (!isAuthed) return null;

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

        <main className="container mx-auto px-6 py-32 flex flex-col items-center">
          <UploadCard onFileSelect={handleFileSelect} />
          
          <RecentUploads uploads={uploads} />

          <Button
            variant="primary"
            size="lg"
            onClick={handleApply}
            disabled={isUploading || uploads.length === 0}
            className="mt-8"
          >
            {isUploading ? 'Uploading...' : 'Apply'}
          </Button>
        </main>
      </div>

      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
      <ToastContainer />
    </>
  );
};

export default Dashboard;
