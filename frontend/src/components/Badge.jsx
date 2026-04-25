import { FaBriefcase, FaCheckCircle, FaFire, FaGlobe, FaInfoCircle, FaTimesCircle } from 'react-icons/fa';
import '../styles/Badge.css';

export const Badge = ({ label, variant = 'default', size = 'md', icon: Icon, className = '', ...props }) => (
  <span className={`badge badge-${variant} badge-${size} ${className}`} {...props}>
    {Icon && <Icon className="badge-icon" />}
    {label}
  </span>
);

export const PriorityBadge = ({ priority = 'Medium', className = '' }) => {
  const map = {
    High:   { variant: 'danger',  icon: FaFire },
    Medium: { variant: 'warning', icon: FaInfoCircle },
    Low:    { variant: 'info',    icon: null },
  };
  const { variant, icon } = map[priority] ?? map.Medium;
  return <Badge label={priority} variant={variant} icon={icon} size="sm" className={`priority-badge ${className}`} />;
};

export const StatusBadge = ({ status = 'pending', className = '' }) => {
  const map = {
    analyzed:   { label: 'Analyzed',   variant: 'success',   icon: FaCheckCircle },
    unanalyzed: { label: 'Pending',    variant: 'secondary', icon: null },
    pending:    { label: 'Pending',    variant: 'warning',   icon: null },
    error:      { label: 'Error',      variant: 'danger',    icon: FaTimesCircle },
    processing: { label: 'Processing', variant: 'info',      icon: null },
  };
  const { label, variant, icon } = map[status] ?? map.pending;
  return <Badge label={label} variant={variant} icon={icon} size="sm" className={`status-badge ${className}`} />;
};

const SOURCE_CONFIG = {
  'Impactpool':    { color: '#6366F1', icon: FaBriefcase },
  'World Bank':    { color: '#3B82F6', icon: FaGlobe },
  'DevelopmentAid':{ color: '#8B5CF6', icon: FaGlobe },
  'Devex':         { color: '#EC4899', icon: FaBriefcase },
  'UNDP':          { color: '#06B6D4', icon: FaGlobe },
  'Mock Data':     { color: '#6B7280', icon: null },
};

export const SourceBadge = ({ source = 'Unknown', className = '' }) => {
  const { color, icon: Icon } = SOURCE_CONFIG[source] ?? { color: '#9CA3AF', icon: FaGlobe };
  return (
    <span className={`source-badge ${className}`} style={{ '--source-color': color }}>
      {Icon && <Icon className="source-badge-icon" />}
      {source}
    </span>
  );
};

export const Tag = ({ label, onRemove, variant = 'default', className = '' }) => (
  <span className={`tag tag-${variant} ${className}`}>
    <span className="tag-label">{label}</span>
    {onRemove && (
      <button className="tag-remove" onClick={onRemove} aria-label={`Remove ${label}`} type="button">×</button>
    )}
  </span>
);

export default Badge;
