import { FileText } from 'lucide-react';

interface Upload {
  name: string;
  size: number;
}

interface RecentUploadsProps {
  uploads: Upload[];
}

export function RecentUploads({ uploads }: RecentUploadsProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (uploads.length === 0) return null;

  return (
    <div className="w-full max-w-[720px] mt-8">
      <h3 className="text-lg font-semibold text-[hsl(var(--text))] mb-4">
        Recent uploads
      </h3>
      
      <div className="space-y-2">
        {uploads.slice(0, 3).map((upload, index) => (
          <div
            key={index}
            className="panel p-4 flex items-center gap-3 hover:bg-[hsl(var(--panel))]/80 transition-colors"
          >
            <div className="w-10 h-10 rounded-lg bg-[hsl(var(--accent))]/10 flex items-center justify-center flex-shrink-0">
              <FileText size={20} className="text-[hsl(var(--accent))]" />
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-[hsl(var(--text))] font-medium truncate">
                {upload.name}
              </p>
              <p className="text-sm text-[hsl(var(--muted))]">
                {formatFileSize(upload.size)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
