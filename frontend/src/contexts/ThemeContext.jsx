import React, { createContext, useContext, useState, useEffect } from 'react';

// Define color schemes
const lightTheme = {
  // Name and identifier
  name: 'light',
  
  // Primary Colors
  '--primary': '#8C98C6',
  '--primary-light': '#AEB3CB',
  '--primary-dark': '#63687D',

  // Backgrounds
  '--bg-primary': '#FFFFFF',
  '--bg-secondary': '#F1F3FA',
  '--bg-tertiary': '#AEB3CB',

  // Text
  '--text-primary': '#1D1F29',
  '--text-secondary': '#63687D',
  '--text-tertiary': '#848BAB',
  '--text-inverse': '#FFFFFF',

  // Borders
  '--border': '#AEB3CB',
  '--border-light': '#F1F3FA',
  '--border-dark': '#848BAB',

  // Status Colors
  '--success': '#10b981',
  '--success-light': '#d1fae5',
  '--warning': '#f59e0b',
  '--warning-light': '#fef3c7',
  '--danger': '#ef4444',
  '--danger-light': '#fee2e2',
  '--info': '#3b82f6',
  '--info-light': '#dbeafe',
};

const darkTheme = {
  // Name and identifier
  name: 'dark',
  
  // Primary Colors
  '--primary': '#8C98C6',
  '--primary-light': '#AEB3CB',
  '--primary-dark': '#63687D',

  // Backgrounds
  '--bg-primary': '#1D1F29',
  '--bg-secondary': '#252B42',
  '--bg-tertiary': '#20222F',

  // Text
  '--text-primary': '#FFFFFF',
  '--text-secondary': '#AEB3CB',
  '--text-tertiary': '#848BAB',
  '--text-inverse': '#1D1F29',

  // Borders
  '--border': '#333A55',
  '--border-light': '#252B42',
  '--border-dark': '#463D60',

  // Status Colors
  '--success': '#10b981',
  '--success-light': '#064e3b',
  '--warning': '#f59e0b',
  '--warning-light': '#78350f',
  '--danger': '#ef4444',
  '--danger-light': '#7f1d1d',
  '--info': '#3b82f6',
  '--info-light': '#1e3a8a',
};

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved preference
    const saved = localStorage.getItem('theme');
    if (saved) {
      return saved === 'dark';
    }
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Apply theme to document
  useEffect(() => {
    const theme = isDark ? darkTheme : lightTheme;
    Object.entries(theme).forEach(([key, value]) => {
      if (key !== 'name') {
        document.documentElement.style.setProperty(key, value);
      }
    });
    // Save preference
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    // Update HTML attribute for potential CSS hooks
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const value = {
    isDark,
    toggleTheme,
    theme: isDark ? darkTheme : lightTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
