"""
WebSocket Gatekeeper - Feature 024 (FR-002)

Enforces WebSocket origin checks, protocol validation, and token binding
for secure WebSocket connections.

Requirements:
- FR-002, Dict, Set
from urllib.parse import urlparse
from fastapi import WebSocket, WebSocketDisconnect, status
from starlette.websockets import WebSocketState
import time

logger = logging.getLogger(__name__)


class WebSocketGatekeeper)"""

    def __init__(self, config: dict) ://localhost))
        self.allowed_protocols = set(config.get('allowed_protocols', ['soundlab-v1']))
        self.require_auth = config.get('ws_require_auth', True)
        self.max_connections_per_ip = config.get('ws_max_connections_per_ip', 10)

        # Track connections per IP
        self.connections_by_ip, int] = {}

        # Active authenticated connections
        self.authenticated_connections)

    def check_origin(self, origin) :
            origin: Origin header value

        Returns, False otherwise
        """
        if not origin)
            return False

        # Parse and normalize origin
        parsed = urlparse(origin)
        normalized_origin = f"{parsed.scheme}://{parsed.netloc}"

        # Check against allowlist
        if normalized_origin not in self.allowed_origins:
            logger.warning(f"WebSocket origin not allowed)
            return False

        return True

    def check_protocol(self, protocol) :
            protocol: WebSocket protocol value

        Returns, False otherwise
        """
        if not protocol)
            return False

        if protocol not in self.allowed_protocols:
            logger.warning(f"WebSocket protocol not allowed)
            return False

        return True

    def check_connection_limit(self, client_ip) :
        """
        Check connection limit per IP to prevent handshake floods.

        Args:
            client_ip: Client IP address

        Returns, False otherwise
        """
        current_connections = self.connections_by_ip.get(client_ip, 0)

        if current_connections >= self.max_connections_per_ip:
            logger.warning(
                f"Connection limit exceeded for IP {client_ip})
            return False

        return True

    def register_connection(self, client_ip: str, websocket: WebSocket) : str, websocket: WebSocket) :
        """Unregister closed connection"""
        if client_ip in self.connections_by_ip:
            self.connections_by_ip[client_ip] -= 1

            if self.connections_by_ip[client_ip] <= 0)

        logger.info(
            f"WebSocket connection unregistered, 0)} remaining)"

    async def authenticate_websocket(
        self,
        websocket,
        token_validator
    ) :
        """
        Authenticate WebSocket connection via token.

        Args:
            websocket: WebSocket connection
            token_validator: TokenValidator instance

        Returns, None otherwise
        """
        # Expect first message to be auth token
        try)

            if message.get('type') != 'auth')
                await websocket.close(code=4401, reason="Authentication required")
                return None

            token = message.get('token')
            if not token)
                await websocket.close(code=4401, reason="Token required")
                return None

            # Verify token
            try)

                # Mark connection as authenticated
                self.authenticated_connections.add(websocket)

                logger.info(f"WebSocket authenticated)}")
                return payload

            except Exception as e:
                logger.warning(f"WebSocket auth failed)
                await websocket.close(code=4401, reason="Invalid token")
                return None

        except WebSocketDisconnect)
            return None
        except Exception as e:
            logger.error(f"WebSocket auth error)
            await websocket.close(code=4500, reason="Internal error")
            return None

    async def accept_connection(
        self,
        websocket,
        token_validator=None
    ) :
        """
        Accept and validate WebSocket connection.

        Args:
            websocket: WebSocket connection
            token_validator: Optional TokenValidator for auth

        Returns, None otherwise
        """
        # Get client info
        client_ip = websocket.client.host
        origin = websocket.headers.get('origin')
        protocol = websocket.headers.get('sec-websocket-protocol')

        # Check origin (FR-002)
        if not self.check_origin(origin), reason="Origin not allowed")
            return None

        # Check protocol (FR-002)
        if not self.check_protocol(protocol), reason="Protocol not supported")
            return None

        # Check connection limit (handshake flood protection)
        if not self.check_connection_limit(client_ip), reason="Too many connections")
            return None

        # Accept connection
        await websocket.accept(subprotocol=protocol)

        # Register connection
        self.register_connection(client_ip, websocket)

        # Authenticate if required
        user_payload = None
        if self.require_auth and token_validator,
                token_validator

            if not user_payload, websocket)
                return None

        return user_payload

    async def close_connection(self, websocket):
        """Safely close WebSocket connection"""
        client_ip = websocket.client.host

        try:
            if websocket.client_state != WebSocketState.DISCONNECTED)
        except Exception as e:
            logger.error(f"Error closing WebSocket)

        self.unregister_connection(client_ip, websocket)

    def get_stats(self) :
        """Get gatekeeper statistics"""
        return {
            'total_connections')),
            'authenticated_connections'),
            'connections_by_ip'),
            'config': {
                'allowed_origins'),
                'allowed_protocols'),
                'max_per_ip': self.max_connections_per_ip
            }
        }


async def websocket_endpoint_with_auth(
    websocket,
    gatekeeper,
    token_validator,
    handler
):
    """
    WebSocket endpoint wrapper with authentication and security checks.

    Usage)
        async def dashboard_ws(websocket),
                app.state.gatekeeper,
                app.state.token_validator,
                handle_dashboard_messages

    Args:
        websocket: WebSocket connection
        gatekeeper: WebSocketGatekeeper instance
        token_validator: TokenValidator instance
        handler: Async function to handle messages
    """
    client_ip = websocket.client.host

    try,
            token_validator

        if not user_payload:
            logger.warning(f"WebSocket auth failed)
            return

        # Connection accepted and authenticated
        logger.info(f"WebSocket ready, user={user_payload.get('sub')}")

        # Send auth success
        await websocket.send_json({
            'type',
            'user')
        })

        # Handle messages
        await handler(websocket, user_payload)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected)
    except Exception as e:
        logger.error(f"WebSocket error)
    finally)
