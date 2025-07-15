import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from 'react-router-dom';
import { loginSchema, LoginFormData } from '../schemas/loginSchema';
import { Input } from '@components/ui/Input';
import { Button } from '@components/ui/Button';
import { Checkbox } from '@components/ui/Checkbox';

interface LoginFormProps {
  onSubmit: (data: LoginFormData) => Promise<void>;
  isLoading?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSubmit, isLoading }) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      remember: false,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700">
          Email address
        </label>
        <div className="mt-1">
          <Input
            id="email"
            type="email"
            autoComplete="email"
            {...register('email')}
            error={errors.email?.message}
            placeholder="Enter your email"
            disabled={isLoading}
          />
        </div>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700">
          Password
        </label>
        <div className="mt-1">
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            {...register('password')}
            error={errors.password?.message}
            placeholder="Enter your password"
            disabled={isLoading}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <Checkbox
            id="remember"
            {...register('remember')}
            disabled={isLoading}
          />
          <label htmlFor="remember" className="ml-2 block text-sm text-gray-900">
            Remember me
          </label>
        </div>

        <div className="text-sm">
          <Link
            to="/forgot-password"
            className="font-medium text-primary-600 hover:text-primary-500"
          >
            Forgot your password?
          </Link>
        </div>
      </div>

      <div>
        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="w-full"
          disabled={isLoading}
          loading={isLoading}
        >
          Sign in
        </Button>
      </div>

      <div className="text-center text-sm">
        <span className="text-gray-600">Don't have an account?</span>{' '}
        <Link
          to="/register"
          className="font-medium text-primary-600 hover:text-primary-500"
        >
          Sign up
        </Link>
      </div>
    </form>
  );
};