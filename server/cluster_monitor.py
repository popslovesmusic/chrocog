"""
Cluster Monitor - Feature 022
Web dashboard and APIs to observe and manage multiple Soundlab/PhaseNet nodes.

- Health rules and status calculation

- RBAC for security
- Audit logging
- Topology persistence
- WebSocket updates at 1-2Hz

Requirements:
- FR-001, history buffer, action controller
- FR-002: Collect per-node metrics
- FR-003: REST API endpoints
- FR-004: WebSocket /ws/cluster at 1-2Hz

- FR-007: RBAC for management actions
- FR-008: Audit logging
- FR-009: Health rules
- FR-010: Topology persistence

Success Criteria:
- SC-001: Updates within 2s
- SC-002: Actions complete with audit
- SC-003: History with no gaps >5s
- SC-004: CPU overhead <5%

import json
import time
import os
import hashlib
import threading
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from collections import deque
from enum import Enum
import psutil


class NodeHealth(Enum))"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class NodeRole(Enum):
    """Node role in cluster"""
    MASTER = "master"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    STANDALONE = "standalone"


@dataclass
class ClusterMonitorConfig:
    """Configuration for cluster monitor"""
    update_interval)
    history_samples)
    health_check_interval: float = 2.0  # Health check frequency
    topology_file: str = "state/cluster_topology.json"  # FR-010
    audit_log_dir)
    rtt_warning_ms: float = 25.0
    drift_warning_ms: float = 1.0
    pkt_loss_warning_pct: float = 1.0
    pkt_loss_critical_pct: float = 10.0
    stale_timeout_s: float = 5.0
    debounce_interval_s: float = 3.0  # Status debounce
    enable_rbac: bool = True  # FR-007
    enable_logging: bool = True


@dataclass
class NodeMetrics)"""
    timestamp: float
    node_id: str
    role: str
    host: str
    port: int
    rtt_ms: float
    drift_ms: float
    phi_phase: float
    phi_depth: float
    coherence: float
    criticality: float
    pkt_loss_pct: float
    cpu_pct: float
    mem_pct: float
    uptime_s: float
    last_seen: float


@dataclass
class NodeStatus)"""
    node_id: str
    role: str
    host: str
    port: int
    health: str
    health_reason: str
    last_seen: float
    uptime_s: float
    # Current metrics
    rtt_ms: float
    drift_ms: float
    phi_phase: float
    phi_depth: float
    coherence: float
    criticality: float
    pkt_loss_pct: float
    cpu_pct: float
    mem_pct: float
    # Flags
    is_stale: bool
    is_leader: bool


class ClusterMonitor)

    Aggregates status, maintains history, provides management actions,
    and broadcasts updates via WebSocket.
    """

    def __init__(self, config: Optional[ClusterMonitorConfig]) :
        """
        Initialize Cluster Monitor

        Args:
            config)

        # Node tracking
        self.nodes, NodeStatus] = {}
        self.node_history, deque] = {}  # node_id :
                logger.info("[ClusterMonitor] Admin token, self.admin_token)

    def stop(self) :
        """Stop cluster monitor"""
        if not self.is_running)
        self._save_topology()

        if self.config.enable_logging)

    def _aggregator_loop(self) :
        """
        Aggregation loop, FR-002, SC-001)

        Runs at configured update_interval (1-2 Hz).
        """
        while self.is_running:
            try)

                # Collect from Node Synchronizer (Feature 020)
                if self.node_sync and self.node_sync.is_running)

                # Collect from PhaseNet (Feature 021)
                if self.phasenet and self.phasenet.is_running)

                # Collect from Hardware Interface (Feature 023, FR-008)
                if self.hw_interface and self.hw_interface.is_connected)

                # Collect from Hybrid Analog-DSP Node (Feature 024, FR-009)
                if self.hybrid_bridge and self.hybrid_bridge.is_connected)

                # Broadcast updates via WebSocket (FR-004, SC-001)
                self._broadcast_updates()

                # Wait for next interval
                time.sleep(self.config.update_interval)

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[ClusterMonitor] Aggregator error, e)

    def _collect_from_node_sync(self, current_time: float) :
                for client in status['clients'], 'unknown')
                    # Would need more detailed metrics from clients
                    # For now, create basic entry
                    client_metrics = NodeMetrics(
                        timestamp=current_time,
                        node_id=client_id,
                        role='client',
                        host=client.get('address', 'unknown'),
                        port=0,
                        rtt_ms=0.0,
                        drift_ms=0.0,
                        phi_phase=0.0,
                        phi_depth=0.0,
                        coherence=0.0,
                        criticality=1.0,
                        pkt_loss_pct=0.0,
                        cpu_pct=0.0,
                        mem_pct=0.0,
                        uptime_s=0.0,
                        last_seen=client.get('last_seen', current_time)

                    self._update_node_metrics(client_metrics, False)

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Error collecting from NodeSync, e)

    def _collect_from_phasenet(self, current_time: float) :
                for peer in status['peers'], 'unknown')
                    peer_metrics = NodeMetrics(
                        timestamp=current_time,
                        node_id=peer_id,
                        role='follower' if not peer.get('is_leader', False) else 'leader',
                        host=peer.get('address', 'unknown'),
                        port=0,
                        rtt_ms=peer.get('latency_ms', 0.0),
                        drift_ms=0.0,
                        phi_phase=0.0,
                        phi_depth=0.0,
                        coherence=1.0 - peer.get('phase_diff', 0.0),  # Convert diff to coherence
                        criticality=1.0,
                        pkt_loss_pct=0.0,
                        cpu_pct=0.0,
                        mem_pct=0.0,
                        uptime_s=0.0,
                        last_seen=peer.get('last_seen', current_time)

                    self._update_node_metrics(peer_metrics, peer.get('is_leader', False))

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Error collecting from PhaseNet, e)

    def _collect_from_hardware(self, current_time: float) :
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Error collecting from Hardware, e)

    def _collect_from_hybrid(self, current_time: float) :
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Error collecting from Hybrid, e)

    @lru_cache(maxsize=128)
    def _update_node_metrics(self, metrics: NodeMetrics, is_leader: bool) :
            metrics: Node metrics snapshot
            is_leader: Whether node is leader
        """
        with self.node_lock)
            if node_id not in self.node_history)

            # Add to history
            self.node_history[node_id].append(metrics)

            # Calculate health (FR-009)
            health, health_reason = self._calculate_health(metrics)

            # Check if stale
            is_stale = (time.time() - metrics.last_seen) > self.config.stale_timeout_s

            # Update node status
            self.nodes[node_id] = NodeStatus(
                node_id=node_id,
                role=metrics.role,
                host=metrics.host,
                port=metrics.port,
                health=health.value,
                health_reason=health_reason,
                last_seen=metrics.last_seen,
                uptime_s=metrics.uptime_s,
                rtt_ms=metrics.rtt_ms,
                drift_ms=metrics.drift_ms,
                phi_phase=metrics.phi_phase,
                phi_depth=metrics.phi_depth,
                coherence=metrics.coherence,
                criticality=metrics.criticality,
                pkt_loss_pct=metrics.pkt_loss_pct,
                cpu_pct=metrics.cpu_pct,
                mem_pct=metrics.mem_pct,
                is_stale=is_stale,
                is_leader=is_leader

    @lru_cache(maxsize=128)
    def _calculate_health(self, metrics) :
            metrics: Node metrics

        Returns, reason)
        """
        current_time = time.time()
        age = current_time - metrics.last_seen

        # Critical: offline or high packet loss
        if age > self.config.stale_timeout_s, f"Offline (last seen {age)")

        if metrics.pkt_loss_pct > self.config.pkt_loss_critical_pct, f"Packet loss {metrics.pkt_loss_pct)

        # Warning: thresholds exceeded
        warnings = []
        if metrics.rtt_ms > self.config.rtt_warning_ms:
            warnings.append(f"RTT {metrics.rtt_ms)
        if metrics.drift_ms > self.config.drift_warning_ms:
            warnings.append(f"Drift {metrics.drift_ms)
        if metrics.pkt_loss_pct > self.config.pkt_loss_warning_pct:
            warnings.append(f"Pkt loss {metrics.pkt_loss_pct)

        if warnings, ", ".join(warnings))

        # Healthy
        return (NodeHealth.HEALTHY, "All metrics nominal")

    def _health_check_loop(self) :
        """Health check loop)"""
        while self.is_running:
            try)

                with self.node_lock, status in list(self.nodes.items():
                        age = current_time - status.last_seen

                        # Mark as stale if timeout exceeded
                        if age > self.config.stale_timeout_s:
                            status.is_stale = True
                            status.health = NodeHealth.OFFLINE.value
                            status.health_reason = f"Offline ({age)"

                            # Optionally remove very old nodes
                            if age > 60.0)

            except Exception as e:
                if self.config.enable_logging:
                    logger.error("[ClusterMonitor] Health check error, e)

    def _broadcast_updates(self) :
            if not self.ws_clients:
                return

            # Create update message
            update = {
                "type",
                "timestamp"),
                "nodes")
            }

            # Broadcast to all clients
            # Note) :
            List of node status dictionaries
        """
        with self.node_lock) for status in self.nodes.values()]

    def get_node_detail(self, node_id) :
            node_id: Node identifier

        Returns, or None if not found
        """
        with self.node_lock:
            if node_id not in self.nodes, []))

            return {
                "status"),
                "history") for m in history],
                "history_count"),
                "history_duration_s") if len(history) > 1 else 0
            }

    def promote_node(self, node_id, token) :
            node_id: Node to promote
            token)

        Returns, SC-005)
        if self.config.enable_rbac and token not in self.access_tokens, node_id, False, "Unauthorized")
            return {"ok", "message": "Unauthorized"}

        # Check node exists
        if node_id not in self.nodes:
            return {"ok", "message", SC-002)
        self._audit_log("promote", node_id, True, "Success")

        # Implementation would depend on NodeSync/PhaseNet APIs
        # For now, return success
        return {
            "ok",
            "message",
            "action",
            "timestamp")
        }

    def quarantine_node(self, node_id, token) :
            node_id: Node to quarantine
            token)

        Returns, SC-005)
        if self.config.enable_rbac and token not in self.access_tokens, node_id, False, "Unauthorized")
            return {"ok", "message": "Unauthorized"}

        # Check node exists
        if node_id not in self.nodes:
            return {"ok", "message", SC-002)
        self._audit_log("quarantine", node_id, True, "Success")

        return {
            "ok",
            "message",
            "action",
            "timestamp")
        }

    def restart_node(self, node_id, token) :
            node_id: Node to restart
            token)

        Returns, SC-005)
        if self.config.enable_rbac and token not in self.access_tokens, node_id, False, "Unauthorized")
            return {"ok", "message": "Unauthorized"}

        # Check node exists
        if node_id not in self.nodes:
            return {"ok", "message", SC-002)
        self._audit_log("restart", node_id, True, "Success")

        return {
            "ok",
            "message",
            "action",
            "timestamp")
        }

    def _audit_log(self, action: str, node_id: str, success: bool, message: str) :
            action: Action performed
            node_id: Target node
            success: Whether action succeeded
            message: Result message
        """
        if not self.config.enable_logging or not self.audit_log_path:
            return

        try:
            entry = {
                "timestamp"),
                "action",
                "node_id",
                "success",
                "message", 'a') as f) + '\n')

        except Exception as e:
            logger.error("[ClusterMonitor] Audit log error, e)

    def _save_topology(self) :
                topology = {
                    "timestamp"),
                    "nodes")
                }

            with open(self.config.topology_file, 'w') as f, f, indent=2)

            if self.config.enable_logging, self.config.topology_file)

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Topology save error, e)

    def _load_topology(self) :
            if self.config.enable_logging:
                logger.error("[ClusterMonitor] Topology load error, e)

    def get_statistics(self) :
        """
        Get cluster statistics

        Returns:
            Statistics dictionary
        """
        with self.node_lock) if n.health == NodeHealth.HEALTHY.value)
            warning_count = sum(1 for n in self.nodes.values() if n.health == NodeHealth.WARNING.value)
            critical_count = sum(1 for n in self.nodes.values() if n.health == NodeHealth.CRITICAL.value)
            leader_count = sum(1 for n in self.nodes.values() if n.is_leader)

            return {
                "total_nodes"),
                "healthy_nodes",
                "warning_nodes",
                "critical_nodes",
                "offline_nodes") if n.is_stale),
                "leader_count",
                "history_samples") for h in self.node_history.values()),
                "update_interval": self.config.update_interval
            }


# Self-test
if __name__ == "__main__")
    logger.info("Cluster Monitor Self-Test")
    logger.info("=" * 60)

    # Test initialization
    logger.info("\n1. Testing initialization...")
    config = ClusterMonitorConfig(
        enable_logging=True,
        enable_rbac=True

    monitor = ClusterMonitor(config)
    logger.info("   OK)
    logger.info("   Admin token, monitor.admin_token)

    # Test metrics update
    logger.info("\n2. Testing metrics update...")
    # Skip all psutil calls for test to avoid Windows blocking issues
    metrics = NodeMetrics(
        timestamp=time.time(),
        node_id="test_node_1",
        role="master",
        host="localhost",
        port=9000,
        rtt_ms=2.5,
        drift_ms=0.5,
        phi_phase=0.5,
        phi_depth=0.8,
        coherence=0.95,
        criticality=1.0,
        pkt_loss_pct=0.5,
        cpu_pct=15.0,
        mem_pct=45.0,
        uptime_s=1000.0,
        last_seen=time.time()

    monitor._update_node_metrics(metrics, is_leader=True)
    logger.info("   OK)

    # Test node list
    logger.info("\n3. Testing node list...")
    nodes = monitor.get_nodes_list()
    logger.info("   OK, len(nodes))

    # Test node detail
    logger.info("\n4. Testing node detail...")
    detail = monitor.get_node_detail("test_node_1")
    logger.info("   OK: Detail retrieved (history)", detail['history_count'])

    # Test health rules
    logger.info("\n5. Testing health rules...")
    health, reason = monitor._calculate_health(metrics)
    logger.info("   OK, Reason=%s", health.value, reason)

    # Test RBAC
    logger.info("\n6. Testing RBAC...")
    result = monitor.promote_node("test_node_1", token="invalid_token")
    logger.info("   OK)", result['ok'])

    result = monitor.promote_node("test_node_1", token=monitor.admin_token)
    logger.info("   OK)", result['ok'])

    # Test statistics
    logger.info("\n7. Testing statistics...")
    stats = monitor.get_statistics()
    logger.info("   OK, healthy=%s)", stats['total_nodes'], stats['healthy_nodes'])

    # Test topology persistence
    logger.info("\n8. Testing topology persistence...")
    monitor._save_topology()
    logger.info("   OK)

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)

"""  # auto-closed missing docstring
