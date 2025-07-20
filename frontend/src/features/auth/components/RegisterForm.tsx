import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { registerSchema } from '../schemas/registerSchema';
import type { RegisterFormData } from '../schemas/registerSchema';
import { Input } from '@components/ui/Input';
import { Button } from '@components/ui/Button';
import { Checkbox } from '@components/ui/Checkbox';

interface RegisterFormProps {
  onSubmit: (data: RegisterFormData) => Promise<void>;
  isLoading?: boolean;
  error?: string | null;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSubmit, isLoading, error }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      acceptTerms: false
    }
  });

  const password = watch('password');

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                {error}
              </h3>
            </div>
          </div>
        </div>
      )}
      <div className="space-y-4">
        <Input
          {...register('fullName')}
          type="text"
          label="Full Name"
          placeholder="John Doe"
          error={errors.fullName?.message}
          autoComplete="name"
        />

        <Input
          {...register('email')}
          type="email"
          label="Email Address"
          placeholder="john@example.com"
          error={errors.email?.message}
          autoComplete="email"
        />

        <Input
          {...register('organizationName')}
          type="text"
          label="Organization Name"
          placeholder="Acme Inc."
          error={errors.organizationName?.message}
          autoComplete="organization"
        />

        <Input
          {...register('password')}
          type="password"
          label="Password"
          placeholder="Enter a strong password"
          error={errors.password?.message}
          autoComplete="new-password"
          helperText="Must be at least 8 characters with uppercase, lowercase, number, and special character"
        />

        <Input
          {...register('confirmPassword')}
          type="password"
          label="Confirm Password"
          placeholder="Confirm your password"
          error={errors.confirmPassword?.message}
          autoComplete="new-password"
        />

        <div className="space-y-2">
          <Checkbox
            {...register('acceptTerms')}
            id="accept-terms"
            label={
              <span className="text-sm text-gray-600">
                I agree to the{' '}
                <Link to="/terms" className="text-primary-600 hover:text-primary-500">
                  Terms of Service
                </Link>{' '}
                and{' '}
                <Link to="/privacy" className="text-primary-600 hover:text-primary-500">
                  Privacy Policy
                </Link>
              </span>
            }
          />
          {errors.acceptTerms && (
            <p className="text-sm text-red-600">{errors.acceptTerms.message}</p>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <Button
          type="submit"
          loading={isLoading}
          disabled={isLoading}
          className="w-full"
        >
          Create Account
        </Button>

        <p className="text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500">
            Sign in
          </Link>
        </p>
      </div>

      {/* Password strength indicator */}
      {password && (
        <div className="mt-2">
          <div className="text-xs text-gray-600 mb-1">Password strength:</div>
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((level) => (
              <div
                key={level}
                className={`h-1 flex-1 rounded-full ${
                  getPasswordStrength(password) >= level
                    ? level <= 2
                      ? 'bg-red-500'
                      : level === 3
                      ? 'bg-yellow-500'
                      : 'bg-green-500'
                    : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
        </div>
      )}
    </form>
  );
};

function getPasswordStrength(password: string): number {
  let strength = 0;
  if (password.length >= 8) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  return Math.min(4, strength);
}