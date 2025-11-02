import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X } from 'lucide-react';
import { Button } from './Button';
import { Input } from './Input';
import { FormHint } from './FormHint';
import { useSession } from '@/contexts/SessionContext';
import { useToast } from './Toast';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [tab, setTab] = useState<'login' | 'signup'>('login');
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { signIn } = useSession();
  const navigate = useNavigate();
  const { showToast } = useToast();

  if (!isOpen) return null;

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (tab === 'signup' && !formData.fullName.trim()) {
      newErrors.fullName = 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    if (tab === 'signup') {
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password';
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    // Simulate authentication
    signIn();
    onClose();
    navigate('/dashboard');
  };

  const handleForgotPassword = () => {
    showToast('Not implemented');
  };

  const handleClose = () => {
    setFormData({
      fullName: '',
      email: '',
      password: '',
      confirmPassword: ''
    });
    setErrors({});
    onClose();
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-[hsl(var(--bg))]/80 backdrop-blur-sm z-50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="auth-modal-title"
        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-md"
      >
        <div className="panel p-8 relative">
          <button
            onClick={handleClose}
            className="absolute top-4 right-4 text-[hsl(var(--muted))] hover:text-[hsl(var(--text))] transition-colors focus-ring rounded"
            aria-label="Close dialog"
          >
            <X size={20} />
          </button>

          <h2 
            id="auth-modal-title" 
            className="text-2xl font-semibold text-[hsl(var(--text))] mb-6"
          >
            {tab === 'login' ? 'Login' : 'Sign up'}
          </h2>

          {/* Tabs */}
          <div className="flex gap-1 p-1 bg-[hsl(var(--panel))] rounded-lg mb-6">
            <button
              onClick={() => setTab('login')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors focus-ring ${
                tab === 'login'
                  ? 'bg-[hsl(var(--text))] text-[hsl(var(--bg))]'
                  : 'text-[hsl(var(--muted))] hover:text-[hsl(var(--text))]'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setTab('signup')}
              className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors focus-ring ${
                tab === 'signup'
                  ? 'bg-[hsl(var(--text))] text-[hsl(var(--bg))]'
                  : 'text-[hsl(var(--muted))] hover:text-[hsl(var(--text))]'
              }`}
            >
              Sign up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {tab === 'signup' && (
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-[hsl(var(--text))] mb-2">
                  Full name
                </label>
                <Input
                  id="fullName"
                  type="text"
                  value={formData.fullName}
                  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                  error={!!errors.fullName}
                  aria-describedby={errors.fullName ? 'fullName-error' : undefined}
                />
                {errors.fullName && (
                  <FormHint id="fullName-error" error className="mt-1">
                    {errors.fullName}
                  </FormHint>
                )}
              </div>
            )}

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[hsl(var(--text))] mb-2">
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                error={!!errors.email}
                aria-describedby={errors.email ? 'email-error' : undefined}
              />
              {errors.email && (
                <FormHint id="email-error" error className="mt-1">
                  {errors.email}
                </FormHint>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[hsl(var(--text))] mb-2">
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                error={!!errors.password}
                aria-describedby={errors.password ? 'password-error' : undefined}
              />
              {errors.password && (
                <FormHint id="password-error" error className="mt-1">
                  {errors.password}
                </FormHint>
              )}
            </div>

            {tab === 'signup' && (
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-[hsl(var(--text))] mb-2">
                  Confirm password
                </label>
                <Input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  error={!!errors.confirmPassword}
                  aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
                />
                {errors.confirmPassword && (
                  <FormHint id="confirmPassword-error" error className="mt-1">
                    {errors.confirmPassword}
                  </FormHint>
                )}
              </div>
            )}

            {tab === 'login' && (
              <div className="text-right">
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-sm text-[hsl(var(--muted))] hover:text-[hsl(var(--accent))] transition-colors focus-ring rounded"
                >
                  Forgot password?
                </button>
              </div>
            )}

            <Button type="submit" variant="primary" className="w-full mt-6">
              Continue
            </Button>
          </form>
        </div>
      </div>
    </>
  );
}
