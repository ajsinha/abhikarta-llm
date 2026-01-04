"""
Prometheus Metrics Routes for Abhikarta-LLM Web Interface.

This module provides the /metrics endpoint for Prometheus scraping
and a metrics dashboard for viewing metrics in the web UI.

Endpoints:
    GET /metrics - Prometheus metrics endpoint (text/plain)
    GET /admin/metrics - Web UI metrics dashboard

Copyright © 2025-2030, All Rights Reserved
Ashutosh Sinha
Email: ajsinha@gmail.com

Version: 1.4.8
"""

import logging
import time
import os
import sys
import platform
import socket
from functools import wraps
from datetime import datetime, timedelta
from flask import Response, request, render_template, g

# Optional psutil import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


def get_system_info():
    """
    Gather comprehensive system information.
    
    Returns:
        dict: System information including OS, hardware, network, etc.
    """
    info = {
        'os': {},
        'hardware': {},
        'python': {},
        'network': {},
        'process': {},
        'disk': {},
        'memory': {},
    }
    
    # OS Information
    try:
        info['os'] = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor() or 'Unknown',
            'platform': platform.platform(),
            'hostname': socket.gethostname(),
        }
    except Exception as e:
        info['os']['error'] = str(e)
    
    # Python Information
    try:
        info['python'] = {
            'version': platform.python_version(),
            'implementation': platform.python_implementation(),
            'compiler': platform.python_compiler(),
            'executable': sys.executable,
            'prefix': sys.prefix,
        }
    except Exception as e:
        info['python']['error'] = str(e)
    
    # Hardware Information (requires psutil)
    if PSUTIL_AVAILABLE:
        try:
            info['hardware'] = {
                'cpu_count_logical': psutil.cpu_count(logical=True),
                'cpu_count_physical': psutil.cpu_count(logical=False),
                'cpu_freq_current': round(psutil.cpu_freq().current, 2) if psutil.cpu_freq() else 'N/A',
                'cpu_freq_max': round(psutil.cpu_freq().max, 2) if psutil.cpu_freq() else 'N/A',
                'cpu_percent': psutil.cpu_percent(interval=0.1),
            }
        except Exception as e:
            info['hardware']['error'] = str(e)
    else:
        info['hardware'] = {'error': 'psutil not installed'}
    
    # Memory Information
    if PSUTIL_AVAILABLE:
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            info['memory'] = {
                'total_gb': round(mem.total / (1024**3), 2),
                'available_gb': round(mem.available / (1024**3), 2),
                'used_gb': round(mem.used / (1024**3), 2),
                'percent': mem.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent,
            }
        except Exception as e:
            info['memory']['error'] = str(e)
    else:
        info['memory'] = {'error': 'psutil not installed'}
    
    # Disk Information
    if PSUTIL_AVAILABLE:
        try:
            disk = psutil.disk_usage('/')
            info['disk'] = {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent,
            }
        except Exception as e:
            info['disk']['error'] = str(e)
    else:
        info['disk'] = {'error': 'psutil not installed'}
    
    # Network Information
    try:
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = '127.0.0.1'
        
        info['network'] = {
            'hostname': hostname,
            'ip_address': ip_address,
        }
        
        if PSUTIL_AVAILABLE:
            net_io = psutil.net_io_counters()
            info['network'].update({
                'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
            })
    except Exception as e:
        info['network']['error'] = str(e)
    
    # Process Information
    if PSUTIL_AVAILABLE:
        try:
            process = psutil.Process(os.getpid())
            info['process'] = {
                'pid': os.getpid(),
                'name': process.name(),
                'status': process.status(),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': round(process.memory_percent(), 2),
                'memory_mb': round(process.memory_info().rss / (1024**2), 2),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections()),
                'create_time': datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Calculate uptime
            uptime_seconds = time.time() - process.create_time()
            uptime = timedelta(seconds=int(uptime_seconds))
            info['process']['uptime'] = str(uptime)
            info['process']['uptime_seconds'] = int(uptime_seconds)
        except Exception as e:
            info['process']['error'] = str(e)
    else:
        info['process'] = {
            'pid': os.getpid(),
            'error': 'psutil not installed'
        }
    
    return info


class MetricsRoutes:
    """
    Flask routes for Prometheus metrics.
    
    Provides:
    - /metrics endpoint for Prometheus scraping
    - Request timing middleware
    - Metrics dashboard
    """
    
    def __init__(self, app, prop_conf=None):
        """
        Initialize metrics routes.
        
        Args:
            app: Flask application instance
            prop_conf: Properties configuration (optional)
        """
        self.app = app
        self.prop_conf = prop_conf
        self.metrics_enabled = True
        self.metrics_path = '/metrics'
        self.start_time = time.time()
        
        # Get configuration
        if prop_conf:
            self.metrics_enabled = prop_conf.get_bool('monitoring.prometheus.enabled', True)
            self.metrics_path = prop_conf.get('monitoring.metrics.path', '/metrics')
        
        # Import metrics
        try:
            from abhikarta.monitoring import (
                metrics,
                PROMETHEUS_AVAILABLE,
                get_metrics_output,
                get_content_type,
                init_app_info,
                set_start_time,
                HTTP_REQUESTS,
                HTTP_REQUEST_DURATION,
                ACTIVE_REQUESTS,
            )
            self.metrics = metrics
            self.prometheus_available = PROMETHEUS_AVAILABLE
            self.get_metrics_output = get_metrics_output
            self.get_content_type = get_content_type
            self.HTTP_REQUESTS = HTTP_REQUESTS
            self.HTTP_REQUEST_DURATION = HTTP_REQUEST_DURATION
            self.ACTIVE_REQUESTS = ACTIVE_REQUESTS
            
            # Initialize app info
            init_app_info(version='1.4.8', environment='production')
            set_start_time()
            
            logger.info(f"Prometheus metrics available: {PROMETHEUS_AVAILABLE}")
        except ImportError as e:
            logger.warning(f"Could not import metrics module: {e}")
            self.prometheus_available = False
            self.metrics = None
        
        self._register_routes()
        
        if self.metrics_enabled and self.prometheus_available:
            self._register_middleware()
    
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route(self.metrics_path, methods=['GET'])
        def prometheus_metrics():
            """
            Prometheus metrics endpoint.
            
            Returns Prometheus-formatted metrics for scraping.
            """
            if not self.metrics_enabled:
                return Response(
                    "# Metrics disabled\n",
                    mimetype='text/plain',
                    status=503
                )
            
            if not self.prometheus_available:
                return Response(
                    "# prometheus_client not installed\n",
                    mimetype='text/plain',
                    status=503
                )
            
            try:
                output = self.get_metrics_output()
                return Response(
                    output,
                    mimetype=self.get_content_type()
                )
            except Exception as e:
                logger.error(f"Error generating metrics: {e}")
                return Response(
                    f"# Error generating metrics: {e}\n",
                    mimetype='text/plain',
                    status=500
                )
        
        @self.app.route('/admin/metrics', methods=['GET'], endpoint='metrics_dashboard')
        def metrics_dashboard():
            """
            Web UI metrics dashboard.
            
            Displays metrics in a human-readable format with system information.
            """
            metrics_data = {
                'enabled': self.metrics_enabled,
                'available': self.prometheus_available,
                'endpoint': self.metrics_path,
                'server_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # Get system information
            metrics_data['system'] = get_system_info()
            
            # Get current metric values if available
            if self.prometheus_available and self.metrics:
                try:
                    from prometheus_client import REGISTRY
                    
                    # Collect all metrics
                    collected_metrics = []
                    metrics_by_category = {
                        'agent': [],
                        'workflow': [],
                        'swarm': [],
                        'aiorg': [],
                        'llm': [],
                        'http': [],
                        'db': [],
                        'tool': [],
                        'mcp': [],
                        'actor': [],
                        'script': [],
                        'system': [],
                        'other': [],
                    }
                    
                    for metric in REGISTRY.collect():
                        for sample in metric.samples:
                            metric_entry = {
                                'name': sample.name,
                                'labels': dict(sample.labels),
                                'value': sample.value,
                            }
                            collected_metrics.append(metric_entry)
                            
                            # Categorize
                            name = sample.name.lower()
                            if 'agent' in name:
                                metrics_by_category['agent'].append(metric_entry)
                            elif 'workflow' in name:
                                metrics_by_category['workflow'].append(metric_entry)
                            elif 'swarm' in name:
                                metrics_by_category['swarm'].append(metric_entry)
                            elif 'aiorg' in name:
                                metrics_by_category['aiorg'].append(metric_entry)
                            elif 'llm' in name:
                                metrics_by_category['llm'].append(metric_entry)
                            elif 'http' in name:
                                metrics_by_category['http'].append(metric_entry)
                            elif 'db' in name:
                                metrics_by_category['db'].append(metric_entry)
                            elif 'tool' in name:
                                metrics_by_category['tool'].append(metric_entry)
                            elif 'mcp' in name:
                                metrics_by_category['mcp'].append(metric_entry)
                            elif 'actor' in name:
                                metrics_by_category['actor'].append(metric_entry)
                            elif 'script' in name:
                                metrics_by_category['script'].append(metric_entry)
                            elif 'system' in name or 'uptime' in name or 'app' in name:
                                metrics_by_category['system'].append(metric_entry)
                            else:
                                metrics_by_category['other'].append(metric_entry)
                    
                    metrics_data['metrics'] = collected_metrics[:200]  # Limit display
                    metrics_data['metrics_by_category'] = metrics_by_category
                    metrics_data['total_metrics'] = len(collected_metrics)
                    
                    # Calculate category counts
                    metrics_data['category_counts'] = {
                        k: len(v) for k, v in metrics_by_category.items()
                    }
                except Exception as e:
                    logger.error(f"Error collecting metrics: {e}")
                    metrics_data['error'] = str(e)
            
            return render_template(
                'admin/metrics_dashboard.html',
                metrics=metrics_data
            )
        
        @self.app.route('/api/metrics/summary', methods=['GET'])
        def api_metrics_summary():
            """
            API endpoint for metrics summary.
            
            Returns JSON summary of key metrics.
            """
            if not self.prometheus_available:
                return {
                    'success': False,
                    'error': 'Prometheus not available'
                }, 503
            
            try:
                from prometheus_client import REGISTRY
                
                # Collect summary metrics
                summary = {
                    'agents': {},
                    'workflows': {},
                    'swarms': {},
                    'aiorgs': {},
                    'llm': {},
                    'http': {},
                    'system': get_system_info(),
                }
                
                for metric in REGISTRY.collect():
                    for sample in metric.samples:
                        name = sample.name
                        
                        # Categorize metrics
                        if 'agent' in name and 'total' in name:
                            summary['agents'][name] = sample.value
                        elif 'workflow' in name and 'total' in name:
                            summary['workflows'][name] = sample.value
                        elif 'swarm' in name and 'total' in name:
                            summary['swarms'][name] = sample.value
                        elif 'aiorg' in name and 'total' in name:
                            summary['aiorgs'][name] = sample.value
                        elif 'llm' in name and 'total' in name:
                            summary['llm'][name] = sample.value
                        elif 'http' in name and 'total' in name:
                            summary['http'][name] = sample.value
                
                return {
                    'success': True,
                    'summary': summary
                }
            except Exception as e:
                logger.error(f"Error generating metrics summary: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }, 500
        
        @self.app.route('/api/system/info', methods=['GET'])
        def api_system_info():
            """
            API endpoint for system information.
            
            Returns JSON with OS, hardware, network info.
            """
            return {
                'success': True,
                'system': get_system_info(),
                'timestamp': datetime.now().isoformat()
            }
    
    def _register_middleware(self):
        """Register request timing middleware."""
        
        @self.app.before_request
        def before_request():
            """Track request start time."""
            g.start_time = time.time()
            self.ACTIVE_REQUESTS.inc()
        
        @self.app.after_request
        def after_request(response):
            """Track request metrics."""
            self.ACTIVE_REQUESTS.dec()
            
            # Skip metrics endpoint to avoid recursion
            if request.path == self.metrics_path:
                return response
            
            # Get duration
            duration = time.time() - getattr(g, 'start_time', time.time())
            
            # Normalize endpoint for cardinality control
            endpoint = self._normalize_endpoint(request.path)
            
            # Record metrics
            self.HTTP_REQUESTS.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=str(response.status_code)
            ).inc()
            
            self.HTTP_REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            return response
    
    def _normalize_endpoint(self, path: str) -> str:
        """
        Normalize endpoint path to control cardinality.
        
        Replaces dynamic path segments (IDs, UUIDs) with placeholders.
        
        Args:
            path: Request path
            
        Returns:
            Normalized path
        """
        import re
        
        # Replace UUIDs
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}',
            path,
            flags=re.IGNORECASE
        )
        
        # Replace numeric IDs
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        
        # Replace common patterns
        path = re.sub(r'/agent-[a-z0-9-]+', '/agent-{id}', path)
        path = re.sub(r'/workflow-[a-z0-9-]+', '/workflow-{id}', path)
        path = re.sub(r'/swarm-[a-z0-9-]+', '/swarm-{id}', path)
        path = re.sub(r'/org-[a-z0-9-]+', '/org-{id}', path)
        
        return path


def init_metrics_routes(app, prop_conf=None):
    """
    Initialize metrics routes.
    
    Args:
        app: Flask application
        prop_conf: Properties configuration
        
    Returns:
        MetricsRoutes instance
    """
    return MetricsRoutes(app, prop_conf)
