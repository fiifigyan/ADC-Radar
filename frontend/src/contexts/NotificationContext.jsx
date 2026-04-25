import { createContext, useCallback, useContext, useState } from 'react';
import Notification from '../components/Notification';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const notify = useCallback(
    (message, type = 'info', duration = 4000) => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, message, type }]);
      if (duration > 0) setTimeout(() => dismiss(id), duration);
      return id;
    },
    [dismiss]
  );

  const success = useCallback((msg, duration) => notify(msg, 'success', duration), [notify]);
  const error   = useCallback((msg, duration) => notify(msg, 'error',   duration), [notify]);
  const info    = useCallback((msg, duration) => notify(msg, 'info',    duration), [notify]);
  const warning = useCallback((msg, duration) => notify(msg, 'warning', duration), [notify]);

  return (
    <NotificationContext.Provider value={{ notify, success, error, info, warning, dismiss }}>
      {children}
      <Notification toasts={toasts} onDismiss={dismiss} />
    </NotificationContext.Provider>
  );
}

export const useNotification = () => {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error('useNotification must be used within NotificationProvider');
  return ctx;
};
