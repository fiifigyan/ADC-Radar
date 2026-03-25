class RadarException(Exception):
    """Base exception for Radar application"""
    pass

class ScraperException(RadarException):
    """Raised when scraping fails"""
    pass

class ClassifierException(RadarException):
    """Raised when classification fails"""
    pass

class DatabaseException(RadarException):
    """Raised when database operations fail"""
    pass

class ConfigException(RadarException):
    """Raised when configuration is invalid"""
    pass
