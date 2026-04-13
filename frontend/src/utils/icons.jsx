/**
 * Icon Library - Centralized icon usage throughout the application
 * Uses Font Awesome via react-icons for consistent, maintainable icons
 */

import React from 'react';
import {
  FaSearch,
  FaFilter,
  FaEye,
  FaExternalLinkAlt,
  FaCheck,
  FaTimes,
  FaBars,
  FaTwitter,
  FaLinkedin,
  FaGithub,
  FaChartBar,
  FaCode,
  FaBriefcase,
  FaArrowRight,
  FaCalendarAlt,
  FaBuilding,
  FaGlobe,
  FaSave,
  FaDownload,
  FaSync,
  FaChevronDown,
  FaStar,
  FaFire,
  FaLock,
  FaUnlock,
  FaCopy,
  FaShare,
  FaBookmark,
  FaRegBookmark,
  FaLink,
  FaExclamationTriangle,
  FaInfoCircle,
  FaCheckCircle,
  FaTimesCircle,
  FaSpinner,
  FaClipboardList,
  FaList,
  FaSort,
  FaSortUp,
  FaSortDown,
  FaPlus,
  FaEdit,
  FaTrash,
  FaRobot,
  FaMicrochip,
  FaPercent,
  FaUsers,
  FaMapMarkerAlt,
  FaEnvelope,
  FaPhone,
  FaMapPin,
  FaChartLine,
} from 'react-icons/fa';

/**
 * Direct Semantic Icon Components
 * Use these throughout the app for consistency
 */

// Search & Navigation
export const SearchIcon = (props) => <FaSearch {...props} />;
export const FilterIcon = (props) => <FaFilter {...props} />;
export const EyeIcon = (props) => <FaEye {...props} />;
export const MenuIcon = (props) => <FaBars {...props} />;
export const ChevronDownIcon = (props) => <FaChevronDown {...props} />;
export const ExternalLinkIcon = (props) => <FaExternalLinkAlt {...props} />;
export const ArrowRightIcon = (props) => <FaArrowRight {...props} />;

// Status & Validation
export const CheckIcon = (props) => <FaCheck {...props} />;
export const SuccessIcon = (props) => <FaCheckCircle {...props} />;
export const ErrorIcon = (props) => <FaTimesCircle {...props} />;
export const WarningIcon = (props) => <FaExclamationTriangle {...props} />;
export const InfoIcon = (props) => <FaInfoCircle {...props} />;
export const LoadingIcon = (props) => <FaSpinner className="spin" {...props} />;

// Actions
export const SaveIcon = (props) => <FaSave {...props} />;
export const SavePresetIcon = (props) => <FaSave {...props} />;
export const DeleteIcon = (props) => <FaTrash {...props} />;
export const EditIcon = (props) => <FaEdit {...props} />;
export const CopyIcon = (props) => <FaCopy {...props} />;
export const ShareIcon = (props) => <FaShare {...props} />;
export const DownloadIcon = (props) => <FaDownload {...props} />;
export const SyncIcon = (props) => <FaSync className="animate-spin-slow" {...props} />;
export const PlusIcon = (props) => <FaPlus {...props} />;

// Content & Organization  
export const ListIcon = (props) => <FaList {...props} />;
export const ClipboardIcon = (props) => <FaClipboardList {...props} />;
export const BookmarkIcon = (props) => <FaBookmark {...props} />;
export const BookmarkOutlineIcon = (props) => <FaRegBookmark {...props} />;
export const LinkIcon = (props) => <FaLink {...props} />;

// Domain Specific
export const BriefcaseIcon = (props) => <FaBriefcase {...props} />;
export const OrganizationIcon = (props) => <FaBuilding {...props} />;
export const SourceIcon = (props) => <FaGlobe {...props} />;
export const CodeIcon = (props) => <FaCode {...props} />;
export const UsersIcon = (props) => <FaUsers {...props} />;
export const RobotIcon = (props) => <FaRobot {...props} />;
export const ChipIcon = (props) => <FaMicrochip {...props} />;

// Analytics & Data
export const AnalyticsIcon = (props) => <FaChartBar {...props} />;
export const ChartIcon = (props) => <FaChartBar {...props} />;
export const ChartLineIcon = (props) => <FaChartLine {...props} />;
export const PercentIcon = (props) => <FaPercent {...props} />;
export const StarIcon = (props) => <FaStar {...props} />;
export const FireIcon = (props) => <FaFire {...props} />;
export const TrendingUpIcon = (props) => <FaChartLine {...props} />;

// Security & Location
export const LockIcon = (props) => <FaLock {...props} />;
export const UnlockIcon = (props) => <FaUnlock {...props} />;
export const CalendarIcon = (props) => <FaCalendarAlt {...props} />;
export const LocationIcon = (props) => <FaMapMarkerAlt {...props} />;
export const MapPinIcon = (props) => <FaMapPin {...props} />;

// Contact & Social
export const EmailIcon = (props) => <FaEnvelope {...props} />;
export const PhoneIcon = (props) => <FaPhone {...props} />;
export const TwitterIcon = (props) => <FaTwitter {...props} />;
export const LinkedinIcon = (props) => <FaLinkedin {...props} />;
export const GithubIcon = (props) => <FaGithub {...props} />;

// Sorting
export const SortIcon = (props) => <FaSort {...props} />;
export const SortUpIcon = (props) => <FaSortUp {...props} />;
export const SortDownIcon = (props) => <FaSortDown {...props} />;
