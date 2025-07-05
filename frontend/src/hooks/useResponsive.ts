import { useState, useEffect } from 'react';

interface Breakpoints {
  xs: boolean;
  sm: boolean;
  md: boolean;
  lg: boolean;
  xl: boolean;
  '2xl': boolean;
  '3xl': boolean;
  '4k': boolean;
}

const breakpointValues = {
  xs: 480,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1440,
  '3xl': 1920,
  '4k': 2560,
};

export const useResponsive = (): Breakpoints => {
  const [breakpoints, setBreakpoints] = useState<Breakpoints>(() => {
    const width = window.innerWidth;
    return {
      xs: width >= breakpointValues.xs,
      sm: width >= breakpointValues.sm,
      md: width >= breakpointValues.md,
      lg: width >= breakpointValues.lg,
      xl: width >= breakpointValues.xl,
      '2xl': width >= breakpointValues['2xl'],
      '3xl': width >= breakpointValues['3xl'],
      '4k': width >= breakpointValues['4k'],
    };
  });

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      setBreakpoints({
        xs: width >= breakpointValues.xs,
        sm: width >= breakpointValues.sm,
        md: width >= breakpointValues.md,
        lg: width >= breakpointValues.lg,
        xl: width >= breakpointValues.xl,
        '2xl': width >= breakpointValues['2xl'],
        '3xl': width >= breakpointValues['3xl'],
        '4k': width >= breakpointValues['4k'],
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return breakpoints;
};

// Hook to check if screen is at least a certain size
export const useMinWidth = (breakpoint: keyof typeof breakpointValues): boolean => {
  const [isMinWidth, setIsMinWidth] = useState(() => {
    return window.innerWidth >= breakpointValues[breakpoint];
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMinWidth(window.innerWidth >= breakpointValues[breakpoint]);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return isMinWidth;
};

// Hook to check if screen is at most a certain size
export const useMaxWidth = (breakpoint: keyof typeof breakpointValues): boolean => {
  const [isMaxWidth, setIsMaxWidth] = useState(() => {
    return window.innerWidth < breakpointValues[breakpoint];
  });

  useEffect(() => {
    const handleResize = () => {
      setIsMaxWidth(window.innerWidth < breakpointValues[breakpoint]);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [breakpoint]);

  return isMaxWidth;
};