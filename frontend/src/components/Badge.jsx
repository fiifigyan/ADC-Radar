/**
 * Badge Components - Reusable status and label indicators
 * Professional, accessible, and consistent throughout the app
 */

import React from 'react';
import {
  SuccessIcon,
  WarningIcon,
  ErrorIcon,
  InfoIcon,
  BriefcaseIcon,
  SourceIcon,
  FireIcon as LowIcon,
} from '../utils/icons';
import '../styles/Badge.css';

/**
 * Generic Badge Component
 */
export const Badge = ({
  label,
  variant = 'default',
  size = 'md',
  icon: IconComponent,
  className = '',
  ...props
}) => {
  const variantClass = `badge-${variant}`;
  const sizeClass = `badge-${size}`;

  return (
    <span className={`badge ${variantClass} ${sizeClass} ${className}`} {...props}>
      {IconComponent && <IconComponent className="badge-icon" />}
      {label}
    </span>
  );
};

/**
 * Priority Badge
 */
export const PriorityBadge = ({ priority = 'Medium', className = '' }) => {
  const priorityMap = {
    High: { variant: 'danger', icon: FireIcon },
    Medium: { variant: 'warning', icon: InfoIcon },
    Low: { variant: 'info', icon: null },
  };

  const config = priorityMap[priority] || priorityMap.Medium;

  return (
    <Badge
      label={priority}
      variant={config.variant}
      icon={config.icon}
      size="sm"
      className={`priority-badge ${className}`}
    />
  );
};

/**
 * Status Badge
 */
export const StatusBadge = ({ status = 'pending', className = '' }) => {
  const statusMap = {
    analyzed: { label: 'Analyzed', variant: 'success', icon: SuccessIcon },
    unanalyzed: { label: 'Unanalyzed', variant: 'secondary', icon: null },
    pending: { label: 'Pending', variant: 'warning', icon: null },
    error: { label: 'Error', variant: 'danger', icon: ErrorIcon },
    processing: { label: 'Processing', variant: 'info', icon: null },
  };

  const config = statusMap[status] || statusMap.pending;

  return (
    <Badge
      label={config.label}
      variant={config.variant}
      icon={config.icon}
      size="sm"
      className={`status-badge ${className}`}
    />
  );
};

/**
 * Source Platform Badge
 */
export const SourceBadge = ({ source = 'Unknown', className = '' }) => {
  const sourceMap = {
    Impactpool: { color: '#6366f1', icon: BriefcaseIcon },
    'World Bank': { color: '#3b82f6', icon: SourceIcon },
    DevelopmentAid: { color: '#8b5cf6', icon: SourceIcon },
    Devex: { color: '#ec4899', icon: BriefcaseIcon },
    UNDP: { color: '#06b6d4', icon: SourceIcon },
    'Mock Data': { color: '#6b7280', icon: null },
  };

  const config = sourceMap[source] || { color: '#9ca3af', icon: SourceIcon };

  return (
    <span
      className={`source-badge ${className}`}
      style={{
        '--source-color': config.color,
      }}
    >
      {config.icon && <config.icon className="source-badge-icon" />}
      {source}
    </span>
  );
};

/**
 * Tag Component - Similar to badge but for categorization
 */
export const Tag = ({ label, onRemove, variant = 'default', className = '' }) => {
  return (
    <span className={`tag tag-${variant} ${className}`}>
      <span className="tag-label">{label}</span>
      {onRemove && (
        <button
          className="tag-remove"
          onClick={onRemove}
          aria-label={`Remove ${label}`}
          type="button"
        >
          ×
        </button>
      )}
    </span>
  );
};

// Alias for FireIcon
const FireIcon = ({ className = '' }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="currentColor"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path d="M13.5.67s.02 2.385.142 3.817c.328 3.864-1.736 5.762-3.733 7.023-2.694 1.635-4.41 3.218-4.41 5.393 0 3.026 2.687 5.1 6.101 5.1 3.414 0 6.1-2.074 6.1-5.1 0-1.673-.64-3.236-1.855-4.376-.434-.407-1.026-.825-1.676-1.28l-.04-.03c-.784-.599-1.218-.934-1.437-1.446-.206-.467-.206-1.122-.03-2.205.176-1.082.527-2.564.806-4.346.279-1.782.528-3.357.528-3.357L13.5.67Z" />
  </svg>
);

export default Badge;
