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
    enable_logging: bool = True

    def __post_init__(self) -> None:
        logger.info("Server config: %s:%d (CORS=%s)", self.host, self.port, self.enable_cors)


@dataclass
class AudioConfig:
    """Audio processing configuration"""
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    sample_rate: int = 48000
    buffer_size: int = 512

    def __post_init__(self) -> None:
        logger.info("Audio config: %dHz @ %d samples", self.sample_rate, self.buffer_size)


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
    hybrid_node: bool = False

    def __post_init__(self) -> None:
        enabled = [k for k, v in self.__dict__.items() if v]
        logger.info("Enabled features: %s", ", ".join(enabled) if enabled else "none")


@dataclass
class NodeSyncConfig:
    """Node synchronization configuration"""
    enabled: bool = False
    role: str = "master"  # 'master' or 'client'
    master_url: Optional[str] = None

    def __post_init__(self) -> None:
        if self.enabled:
            logger.info("Node sync: role=%s, master=%s", self.role, self.master_url)


@dataclass
class PhaseNetConfig:
    """PhaseNet protocol configuration"""
    enabled: bool = False
    port: int = 9000
    encryption_key: Optional[str] = None

    def __post_init__(self) -> None:
        if self.enabled:
            encrypted = "encrypted" if self.encryption_key else "unencrypted"
            logger.info("PhaseNet: port=%d (%s)", self.port, encrypted)


@dataclass
class HardwareConfig:
    """Hardware interface configuration"""

    # Hardware bridge
    bridge_enabled: bool = False
    bridge_port: Optional[str] = None
    bridge_baudrate: int = 115200

    # Hybrid bridge (analog-DSP)
    hybrid_bridge_enabled: bool = False
    hybrid_bridge_port: Optional[str] = None
    hybrid_bridge_baudrate: int = 115200

    # Hybrid node
    hybrid_node_enabled: bool = False
    hybrid_node_input_device: Optional[int] = None
    hybrid_node_output_device: Optional[int] = None

    def __post_init__(self) -> None:
        if any([self.bridge_enabled, self.hybrid_bridge_enabled, self.hybrid_node_enabled]):
            logger.info("Hardware interfaces enabled")


@dataclass
class SoundlabConfig:
    """Complete Soundlab server configuration"""

    server: ServerConfig = field(default_factory=ServerConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    node_sync: NodeSyncConfig = field(default_factory=NodeSyncConfig)
    phasenet: PhaseNetConfig = field(default_factory=PhaseNetConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)

    @classmethod
    def from_args(cls, args) -> 'SoundlabConfig':
        """Create configuration from command-line arguments"""
        return cls(
            server=ServerConfig(
                host=args.host,
                port=args.port,
                enable_cors=True,
                enable_logging=not args.no_logging if hasattr(args, 'no_logging') else True
            ),
            audio=AudioConfig(
                input_device=args.input_device if hasattr(args, 'input_device') else None,
                output_device=args.output_device if hasattr(args, 'output_device') else None
            ),
            features=FeatureFlags(
                auto_phi=args.enable_auto_phi if hasattr(args, 'enable_auto_phi') else False,
                criticality_balancer=args.enable_criticality_balancer if hasattr(args, 'enable_criticality_balancer') else False,
                state_memory=args.enable_state_memory if hasattr(args, 'enable_state_memory') else False,
                state_classifier=args.enable_state_classifier if hasattr(args, 'enable_state_classifier') else False,
                predictive_model=args.enable_predictive_model if hasattr(args, 'enable_predictive_model') else False,
                session_recorder=not args.disable_session_recorder if hasattr(args, 'disable_session_recorder') else True,
                timeline_player=not args.disable_timeline_player if hasattr(args, 'disable_timeline_player') else True,
                data_exporter=not args.disable_data_exporter if hasattr(args, 'disable_data_exporter') else True,
                node_sync=args.enable_node_sync if hasattr(args, 'enable_node_sync') else False,
                phasenet=args.enable_phasenet if hasattr(args, 'enable_phasenet') else False,
                cluster_monitor=args.enable_cluster_monitor if hasattr(args, 'enable_cluster_monitor') else False,
                hardware_bridge=args.enable_hardware_bridge if hasattr(args, 'enable_hardware_bridge') else False,
                hybrid_bridge=args.enable_hybrid_bridge if hasattr(args, 'enable_hybrid_bridge') else False,
                hybrid_node=args.enable_hybrid_node if hasattr(args, 'enable_hybrid_node') else False
            ),
            node_sync=NodeSyncConfig(
                enabled=args.enable_node_sync if hasattr(args, 'enable_node_sync') else False,
                role=args.node_sync_role if hasattr(args, 'node_sync_role') else "master",
                master_url=args.node_sync_master_url if hasattr(args, 'node_sync_master_url') else None
            ),
            phasenet=PhaseNetConfig(
                enabled=args.enable_phasenet if hasattr(args, 'enable_phasenet') else False,
                port=args.phasenet_port if hasattr(args, 'phasenet_port') else 9000,
                encryption_key=args.phasenet_key if hasattr(args, 'phasenet_key') else None
            ),
            hardware=HardwareConfig(
                bridge_enabled=args.enable_hardware_bridge if hasattr(args, 'enable_hardware_bridge') else False,
                bridge_port=args.hardware_port if hasattr(args, 'hardware_port') else None,
                bridge_baudrate=args.hardware_baudrate if hasattr(args, 'hardware_baudrate') else 115200,
                hybrid_bridge_enabled=args.enable_hybrid_bridge if hasattr(args, 'enable_hybrid_bridge') else False,
                hybrid_bridge_port=args.hybrid_port if hasattr(args, 'hybrid_port') else None,
                hybrid_bridge_baudrate=args.hybrid_baudrate if hasattr(args, 'hybrid_baudrate') else 115200,
                hybrid_node_enabled=args.enable_hybrid_node if hasattr(args, 'enable_hybrid_node') else False,
                hybrid_node_input_device=args.hybrid_node_input_device if hasattr(args, 'hybrid_node_input_device') else None,
                hybrid_node_output_device=args.hybrid_node_output_device if hasattr(args, 'hybrid_node_output_device') else None
            )
        )

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []

        # Validate port range
        if not (1024 <= self.server.port <= 65535):
            errors.append(f"Invalid port: {self.server.port} (must be 1024-65535)")

        # Validate node sync
        if self.node_sync.enabled and self.node_sync.role == "client":
            if not self.node_sync.master_url:
                errors.append("Node sync client requires master_url")

        # Validate phasenet
        if self.phasenet.enabled:
            if not (1024 <= self.phasenet.port <= 65535):
                errors.append(f"Invalid PhaseNet port: {self.phasenet.port}")

        return errors

    def log_summary(self) -> None:
        """Log configuration summary"""
        logger.info("=" * 60)
        logger.info("Soundlab Server Configuration")
        logger.info("=" * 60)
        logger.info("Server: %s:%d", self.server.host, self.server.port)
        logger.info("Audio: %dHz @ %d samples", self.audio.sample_rate, self.audio.buffer_size)

        enabled_features = [k for k, v in self.features.__dict__.items() if v]
        if enabled_features:
            logger.info("Features: %s", ", ".join(enabled_features))

        if self.node_sync.enabled:
            logger.info("Node Sync: %s", self.node_sync.role)

        if self.phasenet.enabled:
            logger.info("PhaseNet: port %d", self.phasenet.port)

        logger.info("=" * 60)
