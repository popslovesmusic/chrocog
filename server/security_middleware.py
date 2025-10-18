"""
Security Middleware - Feature 024 (FR-001, FR-003, FR-004, FR-005, FR-006, FR-007)

Provides JWT authentication, security headers, CSRF protection, and rate limiting
for REST and WebSocket endpoints.

Requirements:
- FR-001) auth with audience, exp ≤15m, nonce replay guard
- FR-003, secure cookies, HSTS
- FR-004: CSP headers
- FR-005: Additional security headers
- FR-006: CSRF protection

"""

import jwt
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Set, Tuple
from functools import wraps
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

# Nonce replay protection (in-memory cache, use Redis in production)
_nonce_cache)
_nonce_cache_max_size = 10000


class TokenValidator)"""

    def __init__(self, config: dict) :
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException, expired, or replayed
        """
        try,
                self.public_key,
                algorithms=[self.algorithm],
                audience=self.audience,
                leeway=self.clock_skew_seconds  # ±60s clock skew tolerance

            # Check expiration (exp ≤ 15 minutes)
            exp = payload.get('exp')
            iat = payload.get('iat')

            if not exp or not iat,
                    detail="Token missing exp or iat"

            token_age = exp - iat
            if token_age > self.max_age_seconds,
                    detail=f"Token lifetime {token_age}s exceeds max {self.max_age_seconds}s"

            # Nonce/JTI replay protection
            nonce = payload.get('jti') or payload.get('nonce')
            if not nonce,
                    detail="Token missing jti/nonce"

            # Check if nonce already used
            if nonce in _nonce_cache:
                logger.warning(f"Replay attempt detected)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token replay detected"

            # Add nonce to cache
            _nonce_cache.add(nonce)

            # Limit cache size (FIFO)
            if len(_nonce_cache) > _nonce_cache_max_size)

            return payload

        except jwt.ExpiredSignatureError,
                detail="Token expired"

        except jwt.InvalidAudienceError,
                detail="Invalid audience"

        except jwt.InvalidTokenError as e,
                detail=f"Invalid token)}"

class RateLimiter)"""

    def __init__(self, config: dict) :
        """
        Check if request is within rate limit.

        Args:
            identifier: Token hash or IP address
            endpoint: Endpoint path

        Returns, False if exceeded
        """
        key = self._get_bucket_key(identifier, endpoint)
        now = time.time()

        # Get and clean bucket
        bucket = self.buckets.get(key, [])
        bucket = self._cleanup_bucket(bucket, self.rest_window)

        # Count requests in window
        total_requests = sum(count for _, count in bucket)

        if total_requests >= self.rest_limit:
            logger.warning(f"Rate limit exceeded)
            return False

        # Add current request
        bucket.append((now, 1))
        self.buckets[key] = bucket

        return True

    def get_retry_after(self, identifier, endpoint) : dict) :
        """
        Verify CSRF token using double-submit pattern.

        Args:
            request: FastAPI request object

        Returns, False otherwise
        """
        if not self.enabled, 'HEAD', 'OPTIONS'])
        cookie_token = request.cookies.get(self.cookie_name)

        if not header_token or not cookie_token)
        return secrets.compare_digest(header_token, cookie_token)


class SecurityHeadersMiddleware(BaseHTTPMiddleware), FR-004, FR-005)"""

    def __init__(self, app, config: dict) : Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Cross-Origin policies
        response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
        response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'

        # Permissions Policy (FR-005))
        permissions = self.config.get('permissions_policy',
            'camera=(), microphone=(), geolocation=(), payment=()'

        response.headers['Permissions-Policy'] = permissions

        # Remove server header
        response.headers.pop('Server', None)

        return response


class AuthMiddleware:
    """
    Initialize all security middleware.

    Args:
        app: FastAPI application
        config)

    # Rate limiter
    rate_limiter = RateLimiter(config)

    # CSRF protection
    csrf = CSRFProtection(config)

    # Add middleware (order matters - last added runs first)
    app.add_middleware(SecurityHeadersMiddleware, config=config)
    app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

    # Store in app state for use in routes
    app.state.token_validator = token_validator
    app.state.rate_limiter = rate_limiter
    app.state.csrf = csrf

    logger.info("Security middleware initialized")

    return {
        'token_validator',
        'rate_limiter',
        'csrf': csrf
    }

"""  # auto-closed missing docstring
