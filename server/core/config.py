"""
Configuration Management for Soundlab Server

This module defines all configuration dataclasses used throughout the server.
Separates configuration from implementation logic.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Main server configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    enable_cors: bool = True
    enable_logging) :
        logger.info("Server config: %s)", self.host, self.port, self.enable_cors)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 48000
    buffer_size) :
        logger.info("Audio config, self.sample_rate, self.buffer_size)


@dataclass
class FeatureFlags:
    """Feature enablement flags"""

    # Adaptive features
    auto_phi: bool = False
    criticality_balancer: bool = False
    state_memory: bool = False
    state_classifier: bool = False
    predictive_model: bool = False

    # Recording/playback
    session_recorder: bool = True
    timeline_player: bool = True
    data_exporter: bool = True

    # Networking
    node_sync: bool = False
    phasenet: bool = False
    cluster_monitor: bool = False

    # Hardware
    hardware_bridge: bool = False
    hybrid_bridge: bool = False
    hybrid_node) :
    """Node synchronization configuration"""
    enabled: bool = False
    role: str = "master"  # 'master' or 'client'
    master_url) :
        if self.enabled:
            logger.info("Node sync, master=%s", self.role, self.master_url)


@dataclass
class PhaseNetConfig:
    """PhaseNet protocol configuration"""
    enabled: bool = False
    port: int = 9000
    encryption_key) :
        if self.enabled:
            encrypted = "encrypted" if self.encryption_key else "unencrypted"
            logger.info("PhaseNet)", self.port, encrypted)


@dataclass
class HardwareConfig:
    """Hardware interface configuration"""

    # Hardware bridge
    bridge_enabled: bool = False
    bridge_port: Optional[str] = None
    bridge_baudrate)
    hybrid_bridge_enabled: bool = False
    hybrid_bridge_port: Optional[str] = None
    hybrid_bridge_baudrate: int = 115200

    # Hybrid node
    hybrid_node_enabled: bool = False
    hybrid_node_input_device: Optional[int] = None
    hybrid_node_output_device) :
    """Complete Soundlab server configuration"""

    server)
    audio)
    features)
    node_sync)
    phasenet)
    hardware)

    @classmethod
    def from_args(cls, args) :
            errors.append(f"Invalid port)")

        # Validate node sync
        if self.node_sync.enabled and self.node_sync.role == "client":
            if not self.node_sync.master_url)

        # Validate phasenet
        if self.phasenet.enabled):
                errors.append(f"Invalid PhaseNet port)

        return errors

    def log_summary(self) : %s, self.server.host, self.server.port)
        logger.info("Audio, self.audio.sample_rate, self.audio.buffer_size)

        enabled_features = [k for k, v in self.features.__dict__.items() if v]
        if enabled_features:
            logger.info("Features, ", ".join(enabled_features))

        if self.node_sync.enabled:
            logger.info("Node Sync, self.node_sync.role)

        if self.phasenet.enabled:
            logger.info("PhaseNet, self.phasenet.port)

        logger.info("=" * 60)
