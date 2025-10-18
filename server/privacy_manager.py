"""
Privacy Manager - Feature 024 (FR-009, FR-010, FR-011)

Handles data privacy, PII redaction, retention policies, and data purging.

Requirements:
- FR-009, no raw payloads
- FR-010: Retention policy enforcement and purge CLI
- FR-011, no secrets in localStorage
"""

import re
import json
import logging
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import glob

logger = logging.getLogger(__name__)


class PIIRedactor)"""

    # Regex patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
    CREDIT_CARD_PATTERN = re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b')
    IP_ADDRESS_PATTERN = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    # Fields to always redact
    SENSITIVE_FIELDS = {
        'password', 'token', 'secret', 'api_key', 'authorization',
        'credit_card', 'ssn', 'social_security', 'passport'
    }

    @staticmethod
    def redact_text(text, preserve_domain) :
        """
        Redact PII from text.

        Args:
            text: Input text
            preserve_domain, keep email domains

        Returns:
            Redacted text
        """
        if not text:
            return text

        # Redact emails
        if preserve_domain:
            text = PIIRedactor.EMAIL_PATTERN.sub(
                lambda m).split('@')[1]}",
                text

        else, text)

        # Redact phone numbers
        text = PIIRedactor.PHONE_PATTERN.sub('[PHONE]', text)

        # Redact SSN
        text = PIIRedactor.SSN_PATTERN.sub('[SSN]', text)

        # Redact credit cards
        text = PIIRedactor.CREDIT_CARD_PATTERN.sub('[CARD]', text)

        # Redact IP addresses (partial)
        text = PIIRedactor.IP_ADDRESS_PATTERN.sub(
            lambda m).split('.')[, '***']),
            text

        return text

    @staticmethod
    def redact_dict(data, hash_fields) :
        """
        Redact PII from dictionary.

        Args:
            data: Input dictionary
            hash_fields, hash sensitive values instead of redacting

        Returns, dict), value in data.items())

            # Check if field is sensitive
            is_sensitive = any(
                sensitive in key_lower
                for sensitive in PIIRedactor.SENSITIVE_FIELDS

            if is_sensitive, str))).hexdigest()[:16]
                else, str))
            elif isinstance(value, dict), hash_fields)
            elif isinstance(value, list), hash_fields)
                    if isinstance(item, dict)
                    else PIIRedactor.redact_text(str(item))
                    if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                redacted[key] = value

        return redacted

    @staticmethod
    def should_log_payload(endpoint, method) :
        """
        Determine if request/response payload should be logged.

        Args:
            endpoint: API endpoint
            method: HTTP method

        Returns, False otherwise
        """
        # Never log auth payloads
        if 'auth' in endpoint.lower() or 'login' in endpoint.lower()) for x in ['audio', 'upload', 'stream']):
            return False

        return True


class RetentionPolicy)"""

    def __init__(self, config_path: str) :
            # Default policy
            return {
                'retention_periods': {
                    'logs',  # days
                    'session_metrics',
                    'audit_logs',
                    'temp_files',
                    'recordings',
                'auto_purge_enabled',
                'purge_schedule') as f)

    def get_retention_period(self, data_type) : str) :
        """
        Purge expired data files.

        Args:
            data_type, session_metrics, etc.)
            search_pattern: Glob pattern to find files
            dry_run, only report what would be deleted

        Returns, search_pattern)

        stats = {
            'data_type',
            'files_found'),
            'files_deleted',
            'bytes_freed',
            'dry_run',
            'deleted_files': []
        }

        for file_path in expired_files:
            try).st_size
                stats['bytes_freed'] += file_size

                if not dry_run)
                    stats['files_deleted'] += 1

                stats['deleted_files'].append({
                    'path'),
                    'size',
                    'age_days') - datetime.fromtimestamp(file_path.stat().st_mtime)
                    ).days if file_path.exists() else 0
                })

            except Exception as e:
                logger.error(f"Error purging {file_path})

        return stats

    def purge_all_expired(self, dry_run) :
        """
        Purge all expired data based on retention policy.

        Args:
            dry_run, only report what would be deleted

        Returns, 'logs/**/*.log'),
            ('session_metrics', 'logs/**/*_metrics.csv'),
            ('temp_files', 'temp/**/*'),
            ('recordings', 'recordings/**/*.wav')
        ]

        results = []
        total_files = 0
        total_bytes = 0

        for data_type, pattern in purge_targets, pattern, dry_run)
            results.append(stats)
            total_files += stats['files_deleted']
            total_bytes += stats['bytes_freed']

        return {
            'timestamp').isoformat(),
            'dry_run',
            'total_files_deleted',
            'total_bytes_freed',
            'results', purge_stats) :
        """Create audit log entry for purge action"""
        audit_entry = {
            'timestamp').isoformat(),
            'action',
            'dry_run', False),
            'files_deleted', 0),
            'bytes_freed', 0),
            'details', [])
        }

        # Write to audit log
        audit_log_path = Path('logs/audit.log')
        audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(audit_log_path, 'a') as f) + '\n')

        logger.info(f"Purge audit logged)

    def validate_frontend_storage(self, storage_data) :
            storage_data: Frontend localStorage contents

        Returns, value in storage_data.items())

            if any(s in key_lower for s in ['token', 'secret', 'password', 'key']))
                warnings.append(f"Secret found in localStorage)

        # Check data size
        total_size = sum(len(str(v)) for v in storage_data.values())
        if total_size > 5 * 1024 * 1024:  # 5MB
            warnings.append(f"localStorage exceeds 5MB)

        return {
            'valid') == 0,
            'warnings',
            'secrets_found',
            'total_size_bytes',
            'recommendations',
                'Use session storage for temporary data',
                'Never store tokens or secrets in localStorage'
            ]
        }


def create_audit_log_entry(action, user, details) :
    """Create structured audit log entry"""
    return {
        'timestamp').isoformat(),
        'action',
        'user',
        'details',
        'correlation_id').isoformat()}".encode()
        ).hexdigest()[:16]
    }

"""  # auto-closed missing docstring
