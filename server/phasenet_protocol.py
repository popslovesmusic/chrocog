"""
PhaseNet Protocol - Feature 021
Low-latency distributed mesh network for synchronizing Φ-phase, coherence, and criticality
data between Soundlab nodes.

- UDP socket transport for low latency
- AES-128 packet encryption
- Per-node drift compensation
- Topology healing and auto-reconnect
- Network monitoring and metrics

Requirements:
- FR-001: PhaseNetNode class

- FR-003, authentication, master election
- FR-004, phi_phase, phi_depth, criticality, coherence}
- FR-005: Per-node drift table with adaptive compensation
- FR-006: AES-128 encryption
- FR-007: Auto-reconnect and topology healing
- FR-008: Network status API

Success Criteria:
- SC-001, jitter <2ms
- SC-002: Phase coherence ≥0.99
- SC-003: Master election <2s

import socket
import json
import time
import threading
import struct
import hashlib
from typing import Optional, Dict, List, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import statistics


# Encryption support
try, algorithms, modes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import padding
    ENCRYPTION_AVAILABLE = True
except ImportError))"""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"


@dataclass
class PhaseNetConfig:
    """Configuration for PhaseNet node"""
    node_id: Optional[str] = None  # Auto-generated if None
    bind_address: str = "0.0.0.0"
    bind_port: int = 9000
    broadcast_address: str = "255.255.255.255"
    broadcast_port: int = 9001
    network_key)
    election_timeout)
    heartbeat_interval: float = 0.5  # Leader heartbeat interval
    sync_rate: int = 30  # Phase sync rate in Hz
    max_drift_samples)
    enable_encryption)
    enable_logging: bool = True


@dataclass
class PhasePacket)"""
    t: float  # Timestamp
    phi_phase: float
    phi_depth: float
    criticality: float
    coherence: float
    ici: float
    node_id: str
    sequence: int


@dataclass
class PeerInfo:
    """Peer node information"""
    node_id: str
    address: str
    port: int
    last_seen: float
    is_leader: bool = False
    drift_offset)
    latency: float = 0.0  # Network latency
    phase_diff: float = 0.0  # Phase coherence difference


class PhaseNetNode)

    Distributed mesh network for phase-locked synchronization across multiple nodes.
    Supports dynamic master election, encryption, and topology healing.
    """

    def __init__(self, config: Optional[PhaseNetConfig]) :
        """
        Initialize PhaseNet node

        Args:
            config)

        # Generate node ID if not provided
        if not self.config.node_id) * 1000)}"

        self.node_id = self.config.node_id

        # Network state
        self.socket = None
        self.is_running = False

        # Raft-lite state (FR-003)
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.leader_id = None
        self.last_heartbeat = 0.0
        self.election_timer = None
        self.heartbeat_timer = None

        # Peers (mesh network)
        self.peers, PeerInfo] = {}
        self.peer_lock = threading.Lock()

        # Phase synchronization
        self.local_phase = PhasePacket(
            t=time.time(),
            phi_phase=0.0,
            phi_depth=0.0,
            criticality=1.0,
            coherence=0.0,
            ici=0.0,
            node_id=self.node_id,
            sequence=0

        self.sequence_counter = 0

        # Drift compensation (FR-005)
        self.drift_table, deque] = {}  # node_id : Optional[Callable] = None  # Called on phase update
        self.leader_callback: Optional[Callable] = None  # Called on leader change

        # Background threads
        self.receiver_thread = None
        self.discovery_thread = None
        self.health_check_thread = None

        if self.config.enable_logging, self.node_id)

    def _init_encryption(self) :16]
        # Use first 16 bytes for AES-128
        self.encryption_key = key

        if self.config.enable_logging)")

    def start(self) :
            logger.info("[PhaseNet] Started on %s, self.config.bind_address, self.config.bind_port)

    def stop(self) :
        """Stop PhaseNet node"""
        if not self.is_running:
            return

        self.is_running = False

        # Cancel timers
        if self.election_timer)
        if self.heartbeat_timer)

        # Close socket
        if self.socket)

        if self.config.enable_logging)

    def update_phase(self, phi_phase, phi_depth,
                     criticality, coherence, ici))

        Args:
            phi_phase: Current phi phase
            phi_depth: Current phi depth
            criticality: Current criticality
            coherence: Current coherence
            ici),
            phi_phase=phi_phase,
            phi_depth=phi_depth,
            criticality=criticality,
            coherence=coherence,
            ici=ici,
            node_id=self.node_id,
            sequence=self.sequence_counter

        self.sequence_counter += 1

        # Broadcast to all peers
        self._broadcast_phase()

    def _broadcast_phase(self) :
            return

        # Create packet
        packet_data = {
            "type",
            "t",
            "phi_phase",
            "phi_depth",
            "criticality",
            "coherence",
            "ici",
            "node_id",
            "sequence")
        packet_bytes = self._encrypt_packet(packet_data)

        # Send to all known peers
        with self.peer_lock):
                try, (peer.address, peer.port))
                    self.packets_sent += 1
                except Exception as e:
                    if self.config.enable_logging:
                        logger.error("[PhaseNet] Send error to %s, peer.node_id, e)

    def _encrypt_packet(self, data) :
            data: Packet data dictionary

        Returns).encode('utf-8')

        # If encryption enabled, encrypt
        if self.cipher and self.config.enable_encryption and ENCRYPTION_AVAILABLE).padder()
            padded_data = padder.update(json_bytes) + padder.finalize()

            # Generate random IV
            import os
            iv = os.urandom(16)

            # Encrypt
            cipher = Cipher(
                algorithms.AES(self.encryption_key),
                modes.CBC(iv),
                backend=default_backend()

            encryptor = cipher.encryptor()
            encrypted = encryptor.update(padded_data) + encryptor.finalize()

            # Prepend IV to encrypted data
            return iv + encrypted
        else, return plain JSON
            return json_bytes

    def _decrypt_packet(self, data) :
            data: Encrypted packet bytes

        Returns:
            Decrypted packet dictionary or None if failed
        """
        try, decrypt
            if self.cipher and self.config.enable_encryption and ENCRYPTION_AVAILABLE)
                iv = data[:16]
                encrypted = data[16),
                    modes.CBC(iv),
                    backend=default_backend()

                decryptor = cipher.decryptor()
                padded_data = decryptor.update(encrypted) + decryptor.finalize()

                # Remove PKCS7 padding
                unpadder = padding.PKCS7(128).unpadder()
                json_bytes = unpadder.update(padded_data) + unpadder.finalize()
            else, parse plain JSON
                json_bytes = data

            # Parse JSON
            return json.loads(json_bytes.decode('utf-8'))

        except Exception as e:
            if self.config.enable_logging:
                logger.error("[PhaseNet] Decrypt error, e)
            self.packets_dropped += 1
            return None

    @lru_cache(maxsize=128)
    def _receiver_loop(self) :
            try, addr = self.socket.recvfrom(4096)
                receive_time = time.time()

                # Decrypt packet
                packet = self._decrypt_packet(data)
                if not packet)

                if packet_type == "phase", addr, receive_time)
                elif packet_type == "discovery", addr)
                elif packet_type == "heartbeat", addr)
                elif packet_type == "vote_request", addr)
                elif packet_type == "vote_response", addr)

            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running and self.config.enable_logging:
                    logger.error("[PhaseNet] Receiver error, e)

    def _handle_phase_packet(self, packet: Dict, addr: Tuple, receive_time: float) :
            packet: Phase packet data
            addr: Sender address
            receive_time)
        if node_id == self.node_id:
            return  # Ignore own packets

        # Update peer info
        with self.peer_lock:
            if node_id not in self.peers,
                    address=addr[0],
                    port=addr[1],
                    last_seen=receive_time

            else)
            packet_time = packet.get("t", 0)
            latency = receive_time - packet_time

            # Update latency table
            if node_id not in self.latency_table)
            self.latency_table[node_id].append(latency)

            # Calculate drift offset (simple moving average)
            peer.latency = statistics.mean(self.latency_table[node_id]) if self.latency_table[node_id] else 0

            # Calculate phase coherence (SC-002)
            peer.phase_diff = abs(packet.get("phi_phase", 0) - self.local_phase.phi_phase)
            self.coherence_history.append(1.0 - min(peer.phase_diff, 1.0))

            # Track jitter
            if len(self.latency_table[node_id]) > 1)
                jitter = abs(latencies[-1] - latencies[-2])
                self.jitter_history.append(jitter)

        # Call phase callback if registered
        if self.phase_callback)

    def _discovery_loop(self) :
            try:
                # Broadcast discovery packet
                discovery_packet = {
                    "type",
                    "node_id",
                    "port")

                self.socket.sendto(
                    packet_bytes,
                    (self.config.broadcast_address, self.config.broadcast_port)

                # Wait before next discovery
                time.sleep(5.0)

            except Exception as e:
                if self.is_running and self.config.enable_logging:
                    logger.error("[PhaseNet] Discovery error, e)

    def _handle_discovery_packet(self, packet: Dict, addr: Tuple) :
            packet: Discovery packet data
            addr)
        if node_id == self.node_id, self.config.bind_port)

        # Add peer if not known
        with self.peer_lock:
            if node_id not in self.peers,
                    address=addr[0],
                    port=port,
                    last_seen=time.time()

                if self.config.enable_logging:
                    logger.info("[PhaseNet] Discovered peer: %s at %s, node_id, addr[0], port)

    def _health_check_loop(self) :
            try)

                # Remove stale peers (not seen for 10 seconds)
                with self.peer_lock, peer in self.peers.items()
                        if current_time - peer.last_seen > 10.0
                    ]

                    for peer_id in stale_peers:
                        if self.config.enable_logging:
                            logger.info("[PhaseNet] Removing stale peer, peer_id)
                        del self.peers[peer_id]

                # Wait before next check
                time.sleep(2.0)

            except Exception as e:
                if self.is_running and self.config.enable_logging:
                    logger.error("[PhaseNet] Health check error, e)

    def _reset_election_timer(self) :
            return

        # Become candidate
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        votes_received = 1  # Vote for self

        if self.config.enable_logging)", self.current_term)

        # Request votes from all peers
        vote_request = {
            "type",
            "node_id",
            "term")

        with self.peer_lock):
                try, (peer.address, peer.port))
                except)
        time.sleep(0.5)

        # Check if won election (majority)
        with self.peer_lock) + 1
            if votes_received > total_nodes / 2)
            else)

    def _become_leader(self) :
            return

        # Send heartbeat
        heartbeat = {
            "type",
            "node_id",
            "term")

        with self.peer_lock):
                try, (peer.address, peer.port))
                except,
            self._send_heartbeat

        self.heartbeat_timer.daemon = True
        self.heartbeat_timer.start()

    def _handle_heartbeat_packet(self, packet: Dict, addr: Tuple) :
                self.state = NodeState.FOLLOWER

                # Call leader callback
                if self.leader_callback)

            # Reset election timer
            self._reset_election_timer()

            # Mark peer as leader
            with self.peer_lock:
                if node_id in self.peers, packet: Dict, addr: Tuple) :
            self.current_term = term
            self.voted_for = node_id

            # Send vote response
            vote_response = {
                "type",
                "node_id",
                "term",
                "vote_granted")
            self.socket.sendto(packet_bytes, addr)

    def _handle_vote_response(self, packet: Dict, addr: Tuple) :
            Status dictionary
        """
        with self.peer_lock:
            return {
                "node_id",
                "state",
                "is_leader",
                "leader_id",
                "current_term",
                "peer_count"),
                "peers": [
                    {
                        "node_id",
                        "address",
                        "is_leader",
                        "latency_ms",
                        "phase_diff",
                        "last_seen")
                ],
                "packets_sent",
                "packets_received",
                "packets_dropped") :
            Statistics dictionary
        """
        stats = {
            "node_id",
            "state")
        if self.latency_history:
            stats["latency"] = {
                "mean_ms") * 1000,
                "max_ms") * 1000,
                "min_ms") * 1000,
                "target_ms")
        if self.jitter_history:
            stats["jitter"] = {
                "mean_ms") * 1000,
                "max_ms") * 1000,
                "target_ms")
        if self.coherence_history:
            stats["coherence"] = {
                "mean"),
                "min"),
                "target": 0.99  # SC-002
            }

        # Packet statistics
        total_packets = self.packets_sent + self.packets_received
        stats["packets"] = {
            "sent",
            "received",
            "dropped",
            "drop_rate": self.packets_dropped / total_packets if total_packets > 0 else 0
        }

        return stats


# Self-test
if __name__ == "__main__")
    logger.info("PhaseNet Protocol Self-Test")
    logger.info("=" * 60)

    # Test node initialization
    logger.info("\n1. Testing node initialization...")
    config = PhaseNetConfig(
        node_id="test_node_1",
        bind_port=9000,
        enable_logging=True

    node = PhaseNetNode(config)
    logger.info("   OK)

    # Test phase update
    logger.info("\n2. Testing phase update...")
    node.update_phase(
        phi_phase=0.5,
        phi_depth=0.8,
        criticality=1.0,
        coherence=0.7,
        ici=0.3

    logger.info("   OK)

    # Test status
    logger.info("\n3. Testing status...")
    status = node.get_status()
    logger.info("   OK, peers=%s)", status['state'], status['peer_count'])

    # Test statistics
    logger.info("\n4. Testing statistics...")
    stats = node.get_statistics()
    logger.info("   OK)", stats['packets'])

    # Test encryption if available
    if ENCRYPTION_AVAILABLE and config.network_key)
        config_enc = PhaseNetConfig(
            node_id="test_node_2",
            network_key="test_key_12345",
            enable_encryption=True,
            enable_logging=True

        node_enc = PhaseNetNode(config_enc)
        logger.info("   OK)
    else)")

    logger.info("\n" + "=" * 60)
    logger.info("Self-Test PASSED")
    logger.info("=" * 60)
    logger.info("Note)

