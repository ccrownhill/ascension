import { useState, useRef, DragEvent } from 'react';
import { Upload, X, FileText } from 'lucide-react';
import { Button } from './Button';
import { FormHint } from './FormHint';

interface UploadedFile {
  name: string;
  size: number;
}

interface UploadCardProps {
  onFileSelect?: (file: File) => void;
}

export function UploadCard({ onFileSelect }: UploadCardProps) {
  const [file, setFile] = useState<UploadedFile | null>(null);
  const [error, setError] = useState<string>('');
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedTypes.includes(file.type)) {
      return 'Invalid file type';
    }

    if (file.size > maxSize) {
      return 'File too large';
    }

    return null;
  };

  const handleFile = (file: File) => {
    setError('');
    const validationError = validateFile(file);

    if (validationError) {
      setError(validationError);
      return;
    }

    setFile({
      name: file.name,
      size: file.size
    });

    onFileSelect?.(file);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleRemove = () => {
    setFile(null);
    setError('');
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div className="panel p-8 w-full max-w-[720px]">
      <h2 className="text-2xl font-semibold text-[hsl(var(--text))] mb-6">
        Upload your CV
      </h2>

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          relative border-2 border-dashed rounded-xl p-12 transition-colors duration-220
          ${isDragging ? 'border-[hsl(var(--accent))] bg-[hsl(var(--accent))]/5' : 'border-[hsl(var(--stroke))]'}
          ${file ? 'bg-[hsl(var(--panel))]' : ''}
        `}
      >
        {!file ? (
          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-[hsl(var(--panel))] flex items-center justify-center">
              <Upload size={28} className="text-[hsl(var(--muted))]" />
            </div>
            
            <div className="text-center">
              <Button
                variant="primary"
                onClick={() => inputRef.current?.click()}
                className="mb-2"
              >
                Browse files
              </Button>
              <p className="text-sm text-[hsl(var(--muted))]">or drag and drop here</p>
            </div>

            <input
              ref={inputRef}
              type="file"
              accept=".pdf,.docx"
              onChange={handleInputChange}
              className="hidden"
              aria-describedby="file-hint"
            />
          </div>
        ) : (
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-[hsl(var(--accent))]/10 flex items-center justify-center flex-shrink-0">
              <FileText size={24} className="text-[hsl(var(--accent))]" />
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-[hsl(var(--text))] font-medium truncate">
                {file.name}
              </p>
              <p className="text-sm text-[hsl(var(--muted))]">
                {formatFileSize(file.size)}
              </p>
            </div>

            <button
              onClick={handleRemove}
              className="text-[hsl(var(--muted))] hover:text-[hsl(var(--destructive))] transition-colors focus-ring rounded p-2"
              aria-label="Remove file"
            >
              <X size={20} />
            </button>
          </div>
        )}
      </div>

      <FormHint 
        id="file-hint" 
        error={!!error}
        className="mt-2 text-center"
      >
        {error || 'Accepted: PDF or DOCX, up to 10 MB'}
      </FormHint>
    </div>
  );
}
