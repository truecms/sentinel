import toast from 'react-hot-toast';

// Success toast
export const showSuccess = (message: string, options?: any) => {
  return toast.success(message, options);
};

// Error toast
export const showError = (message: string, options?: any) => {
  return toast.error(message, options);
};

// Info toast (using custom)
export const showInfo = (message: string, options?: any) => {
  return toast(message, {
    icon: '📢',
    ...options,
  });
};

// Warning toast
export const showWarning = (message: string, options?: any) => {
  return toast(message, {
    icon: '⚠️',
    style: {
      background: '#fbbf24',
      color: '#000',
    },
    ...options,
  });
};

// Loading toast
export const showLoading = (message: string, options?: any) => {
  return toast.loading(message, options);
};

// Promise toast
export const showPromise = <T>(
  promise: Promise<T>,
  messages: {
    loading: string;
    success: string | ((data: T) => string);
    error: string | ((err: unknown) => string);
  }
) => {
  return toast.promise(promise, messages);
};

// Dismiss toast
export const dismissToast = (toastId?: string) => {
  if (toastId) {
    toast.dismiss(toastId);
  } else {
    toast.dismiss();
  }
};