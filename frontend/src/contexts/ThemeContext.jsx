import { createContext, useContext, useEffect, useState } from 'react';

const lightTheme = {
  name: 'light',
  '--primary':         '#8C98C6',
  '--primary-light':   '#AEB3CB',
  '--primary-dark':    '#63687D',
  '--accent':          '#6366F1',
  '--accent-light':    '#EEF2FF',
  '--bg-primary':      '#F8F9FC',
  '--bg-secondary':    '#EDEEF7',
  '--bg-tertiary':     '#E2E4F0',
  '--bg-card':         '#FFFFFF',
  '--bg-hover':        'rgba(99,102,241,0.05)',
  '--input-bg':        '#FFFFFF',
  '--text-primary':    '#1A1D2E',
  '--text-secondary':  '#5B5F72',
  '--text-tertiary':   '#8B8FAD',
  '--text-inverse':    '#FFFFFF',
  '--border':          '#D8DAE8',
  '--border-light':    '#EDEEF7',
  '--border-dark':     '#AEB3CB',
  '--success':         '#10B981',
  '--success-light':   '#D1FAE5',
  '--warning':         '#F59E0B',
  '--warning-light':   '#FEF3C7',
  '--danger':          '#EF4444',
  '--danger-light':    '#FEE2E2',
  '--info':            '#3B82F6',
  '--info-light':      '#DBEAFE',
  '--shadow-sm':       '0 1px 3px rgba(0,0,0,0.06)',
  '--shadow-md':       '0 4px 12px rgba(0,0,0,0.08)',
  '--shadow-lg':       '0 8px 24px rgba(0,0,0,0.10)',
  '--shadow-xl':       '0 16px 40px rgba(0,0,0,0.12)',
};

const darkTheme = {
  name: 'dark',
  '--primary':         '#8C98C6',
  '--primary-light':   '#AEB3CB',
  '--primary-dark':    '#63687D',
  '--accent':          '#818CF8',
  '--accent-light':    '#1E2251',
  '--bg-primary':      '#0D0F1A',
  '--bg-secondary':    '#141627',
  '--bg-tertiary':     '#1A1D2E',
  '--bg-card':         '#1A1D2E',
  '--bg-hover':        'rgba(129,140,248,0.08)',
  '--input-bg':        '#141627',
  '--text-primary':    '#E8EAF4',
  '--text-secondary':  '#8B8FAD',
  '--text-tertiary':   '#5B5F72',
  '--text-inverse':    '#0D0F1A',
  '--border':          '#252A40',
  '--border-light':    '#1A1D2E',
  '--border-dark':     '#2E3450',
  '--success':         '#10B981',
  '--success-light':   '#064E3B',
  '--warning':         '#F59E0B',
  '--warning-light':   '#78350F',
  '--danger':          '#EF4444',
  '--danger-light':    '#7F1D1D',
  '--info':            '#60A5FA',
  '--info-light':      '#1E3A8A',
  '--shadow-sm':       '0 1px 3px rgba(0,0,0,0.3)',
  '--shadow-md':       '0 4px 12px rgba(0,0,0,0.4)',
  '--shadow-lg':       '0 8px 24px rgba(0,0,0,0.5)',
  '--shadow-xl':       '0 16px 40px rgba(0,0,0,0.6)',
};

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme');
    if (saved) return saved === 'dark';
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    const theme = isDark ? darkTheme : lightTheme;
    const root = document.documentElement;
    Object.entries(theme).forEach(([key, val]) => {
      if (key !== 'name') root.style.setProperty(key, val);
    });
    root.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => setIsDark((d) => !d);

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, theme: isDark ? darkTheme : lightTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export const useTheme = () => {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
};
