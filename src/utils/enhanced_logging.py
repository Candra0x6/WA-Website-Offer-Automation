"""
Enhanced Logging System

Provides comprehensive logging capabilities:
- Multiple log handlers (console, file, rotating file)
- Structured logging with JSON support
- Log level filtering
- Performance metrics tracking
- Error tracking and aggregation

Author: WhatsApp Automation System
Date: 2025-10-16
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import traceback


@dataclass
class LogConfig:
    """Configuration for logging system."""
    
    # Log levels
    console_level: int = logging.INFO
    file_level: int = logging.DEBUG
    
    # File settings
    log_dir: str = "logs"
    log_file: str = "whatsapp_automation.log"
    error_log_file: str = "errors.log"
    
    # Rotation settings
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    
    # Format settings
    use_json: bool = False
    include_timestamp: bool = True
    include_module: bool = True
    
    # Performance tracking
    track_performance: bool = True


@dataclass
class PerformanceMetrics:
    """Track performance metrics."""
    
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration: float = 0.0
    operation_times: List[float] = field(default_factory=list)
    
    def add_operation(self, success: bool, duration: float):
        """Record an operation."""
        self.total_operations += 1
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1
        self.total_duration += duration
        self.operation_times.append(duration)
    
    def get_average_duration(self) -> float:
        """Get average operation duration."""
        if self.total_operations == 0:
            return 0.0
        return self.total_duration / self.total_operations
    
    def get_success_rate(self) -> float:
        """Get success rate percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100


class JsonFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        
        # Add module info
        if hasattr(record, 'module'):
            log_data['module'] = record.module
        
        # Add function info
        if hasattr(record, 'funcName'):
            log_data['function'] = record.funcName
        
        # Add line number
        if hasattr(record, 'lineno'):
            log_data['line'] = record.lineno
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'extra_data'):
            log_data['data'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class EnhancedLogger:
    """
    Enhanced logging system with multiple handlers and features.
    
    Features:
    - Console and file logging
    - Rotating file handlers
    - JSON formatting option
    - Error aggregation
    - Performance tracking
    """
    
    def __init__(self, config: Optional[LogConfig] = None):
        """
        Initialize enhanced logger.
        
        Args:
            config: Logging configuration (uses defaults if None)
        """
        self.config = config or LogConfig()
        self.log_dir = Path(self.config.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}
        
        # Error tracking
        self.error_count = 0
        self.error_log: List[Dict[str, Any]] = []
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging handlers and formatters."""
        # Get root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.config.console_level)
        
        if self.config.use_json:
            console_handler.setFormatter(JsonFormatter())
        else:
            console_format = self._create_format_string()
            console_handler.setFormatter(logging.Formatter(console_format))
        
        root_logger.addHandler(console_handler)
        
        # Rotating file handler (main log)
        main_log_path = self.log_dir / self.config.log_file
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_path,
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.config.file_level)
        
        if self.config.use_json:
            file_handler.setFormatter(JsonFormatter())
        else:
            file_format = self._create_format_string(detailed=True)
            file_handler.setFormatter(logging.Formatter(file_format))
        
        root_logger.addHandler(file_handler)
        
        # Error file handler (errors only)
        error_log_path = self.log_dir / self.config.error_log_file
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=self.config.max_bytes,
            backupCount=self.config.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        error_format = self._create_format_string(detailed=True)
        error_handler.setFormatter(logging.Formatter(error_format))
        
        root_logger.addHandler(error_handler)
        
        logging.info("Enhanced logging system initialized")
        logging.info(f"Log directory: {self.log_dir.absolute()}")
        logging.info(f"Main log: {main_log_path.name}")
        logging.info(f"Error log: {error_log_path.name}")
    
    def _create_format_string(self, detailed: bool = False) -> str:
        """Create log format string."""
        parts = []
        
        if self.config.include_timestamp:
            parts.append('%(asctime)s')
        
        parts.append('%(levelname)-8s')
        
        if self.config.include_module:
            if detailed:
                parts.append('[%(name)s:%(funcName)s:%(lineno)d]')
            else:
                parts.append('[%(name)s]')
        
        parts.append('%(message)s')
        
        return ' - '.join(parts)
    
    def track_operation(self, operation_name: str, success: bool, duration: float):
        """
        Track operation performance.
        
        Args:
            operation_name: Name of the operation
            success: Whether operation succeeded
            duration: Operation duration in seconds
        """
        if not self.config.track_performance:
            return
        
        if operation_name not in self.performance_metrics:
            self.performance_metrics[operation_name] = PerformanceMetrics()
        
        self.performance_metrics[operation_name].add_operation(success, duration)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """
        Log error with context and stack trace.
        
        Args:
            error: Exception that occurred
            context: Additional context information
        """
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'context': context or {}
        }
        
        self.error_log.append(error_info)
        
        # Log to file
        logging.error(
            f"Error #{self.error_count}: {type(error).__name__}: {str(error)}",
            exc_info=True
        )
        
        if context:
            logging.error(f"Context: {json.dumps(context, indent=2)}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance metrics summary.
        
        Returns:
            Dict with performance statistics
        """
        summary = {}
        
        for operation_name, metrics in self.performance_metrics.items():
            summary[operation_name] = {
                'total_operations': metrics.total_operations,
                'successful': metrics.successful_operations,
                'failed': metrics.failed_operations,
                'success_rate': f"{metrics.get_success_rate():.2f}%",
                'average_duration': f"{metrics.get_average_duration():.3f}s",
                'total_duration': f"{metrics.total_duration:.3f}s",
            }
        
        return summary
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get error tracking summary.
        
        Returns:
            Dict with error statistics
        """
        # Count errors by type
        error_types: Dict[str, int] = {}
        for error_info in self.error_log:
            error_type = error_info['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': self.error_count,
            'error_types': error_types,
            'recent_errors': self.error_log[-5:] if self.error_log else [],
        }
    
    def print_statistics(self):
        """Print logging and performance statistics."""
        print("\n" + "=" * 60)
        print("📊 LOGGING SYSTEM STATISTICS")
        print("=" * 60)
        
        # Error summary
        error_summary = self.get_error_summary()
        print(f"\n❌ Errors:")
        print(f"   Total: {error_summary['total_errors']}")
        if error_summary['error_types']:
            print(f"   By Type:")
            for error_type, count in error_summary['error_types'].items():
                print(f"      {error_type}: {count}")
        
        # Performance summary
        if self.config.track_performance:
            perf_summary = self.get_performance_summary()
            if perf_summary:
                print(f"\n⚡ Performance Metrics:")
                for operation, metrics in perf_summary.items():
                    print(f"   {operation}:")
                    print(f"      Total: {metrics['total_operations']}")
                    print(f"      Success: {metrics['successful']}/{metrics['failed']}")
                    print(f"      Success Rate: {metrics['success_rate']}")
                    print(f"      Avg Duration: {metrics['average_duration']}")
        
        print("\n" + "=" * 60)
    
    def export_logs_to_json(self, output_file: Optional[str] = None) -> str:
        """
        Export logs to JSON file.
        
        Args:
            output_file: Output file path (auto-generated if None)
            
        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"logs/export_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'error_summary': self.get_error_summary(),
            'performance_summary': self.get_performance_summary(),
            'log_files': {
                'main_log': str(self.log_dir / self.config.log_file),
                'error_log': str(self.log_dir / self.config.error_log_file),
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Logs exported to: {output_path}")
        return str(output_path)


def setup_enhanced_logging(
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    use_json: bool = False,
    log_dir: str = "logs"
) -> EnhancedLogger:
    """
    Setup enhanced logging system.
    
    Args:
        console_level: Console log level
        file_level: File log level
        use_json: Use JSON formatting
        log_dir: Log directory path
        
    Returns:
        EnhancedLogger instance
    """
    config = LogConfig(
        console_level=console_level,
        file_level=file_level,
        use_json=use_json,
        log_dir=log_dir,
    )
    
    return EnhancedLogger(config=config)


# Global logger instance
_enhanced_logger: Optional[EnhancedLogger] = None


def get_logger() -> EnhancedLogger:
    """Get global enhanced logger instance."""
    global _enhanced_logger
    
    if _enhanced_logger is None:
        _enhanced_logger = setup_enhanced_logging()
    
    return _enhanced_logger
