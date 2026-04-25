import { createPortal } from 'react-dom';
import { FaCheckCircle, FaTimesCircle, FaInfoCircle, FaExclamationTriangle, FaTimes } from 'react-icons/fa';
import '../styles/Notification.css';

const ICONS = {
  success: <FaCheckCircle />,
  error:   <FaTimesCircle />,
  info:    <FaInfoCircle />,
  warning: <FaExclamationTriangle />,
};

export default function Notification({ toasts, onDismiss }) {
  if (!toasts.length) return null;

  return createPortal(
    <div className="toast-container" role="region" aria-label="Notifications" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          <span className="toast-icon">{ICONS[toast.type]}</span>
          <span className="toast-message">{toast.message}</span>
          <button
            className="toast-dismiss"
            onClick={() => onDismiss(toast.id)}
            aria-label="Dismiss notification"
          >
            <FaTimes />
          </button>
        </div>
      ))}
    </div>,
    document.body
  );
}
