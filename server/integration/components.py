"""
Component Registry and Initialization

This module handles initialization of all Soundlab components based on configuration.
Centralizes component lifecycle management.
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

from server.core.config import SoundlabConfig

# Import all components
from server.audio_server import AudioServer
from server.preset_store import PresetStore
from server.ab_snapshot import ABSnapshot
from server.metrics_streamer import MetricsStreamer
from server.latency_api import LatencyStreamer
from server.auto_phi import AutoPhiLearner, AutoPhiConfig
from server.criticality_balancer import CriticalityBalancer, CriticalityBalancerConfig
from server.state_memory import StateMemory, StateMemoryConfig
from server.state_classifier import StateClassifierGraph, StateClassifierConfig
from server.predictive_model import PredictiveModel, PredictiveModelConfig
from server.session_recorder import SessionRecorder, SessionRecorderConfig
from server.timeline_player import TimelinePlayer, TimelinePlayerConfig
from server.data_exporter import DataExporter, ExportConfig
from server.node_sync import NodeSynchronizer, NodeSyncConfig, NodeRole
from server.phasenet_protocol import PhaseNetNode, PhaseNetConfig as PhaseNetProtoConfig
from server.cluster_monitor import ClusterMonitor, ClusterMonitorConfig
from server.hw_interface import HardwareInterface
from server.hybrid_bridge import HybridBridge
from server.hybrid_node import HybridNode, HybridNodeConfig, PhiSource
from server.session_comparator import SessionComparator
from server.correlation_analyzer import CorrelationAnalyzer
from server.chromatic_visualizer import ChromaticVisualizer, VisualizerConfig
from server.state_sync_manager import StateSyncManager, SyncConfig

logger = logging.getLogger(__name__)


class ComponentRegistry:
    """
    Central registry for all Soundlab components

    Manages lifecycle of all system components based on configuration.
    Provides centralized access to initialized components.
    """

    def __init__(self, config: SoundlabConfig):
        """Initialize component registry"""
        self.config = config

        # Core components (always initialized)
        self.audio_server: Optional[AudioServer] = None
        self.preset_store: Optional[PresetStore] = None
        self.ab_snapshot: Optional[ABSnapshot] = None
        self.metrics_streamer: Optional[MetricsStreamer] = None
        self.latency_streamer: Optional[LatencyStreamer] = None

        # Adaptive features (optional)
        self.auto_phi_learner: Optional[AutoPhiLearner] = None
        self.criticality_balancer: Optional[CriticalityBalancer] = None
        self.state_memory: Optional[StateMemory] = None
        self.state_classifier: Optional[StateClassifierGraph] = None
        self.predictive_model: Optional[PredictiveModel] = None

        # Recording/playback (optional)
        self.session_recorder: Optional[SessionRecorder] = None
        self.timeline_player: Optional[TimelinePlayer] = None
        self.data_exporter: Optional[DataExporter] = None
        self.session_comparator: Optional[SessionComparator] = None

        # Networking (optional)
        self.node_synchronizer: Optional[NodeSynchronizer] = None
        self.phasenet_node: Optional[PhaseNetNode] = None
        self.cluster_monitor: Optional[ClusterMonitor] = None

        # Visualization/analysis (optional)
        self.correlation_analyzer: Optional[CorrelationAnalyzer] = None
        self.chromatic_visualizer: Optional[ChromaticVisualizer] = None
        self.state_sync_manager: Optional[StateSyncManager] = None

        # Hardware (optional)
        self.hardware_interface: Optional[HardwareInterface] = None
        self.hybrid_bridge: Optional[HybridBridge] = None
        self.hybrid_node: Optional[HybridNode] = None

        logger.info("ComponentRegistry initialized")

    def initialize_all(self) -> None:
        """Initialize all enabled components"""
        logger.info("Initializing components...")

        # Core components (always enabled)
        self._init_core_components()

        # Optional features
        if self.config.features.auto_phi:
            self._init_auto_phi()

        if self.config.features.criticality_balancer:
            self._init_criticality_balancer()

        if self.config.features.state_memory:
            self._init_state_memory()

        if self.config.features.state_classifier:
            self._init_state_classifier()

        if self.config.features.predictive_model:
            self._init_predictive_model()

        if self.config.features.session_recorder:
            self._init_session_recorder()

        if self.config.features.timeline_player:
            self._init_timeline_player()

        if self.config.features.data_exporter:
            self._init_data_exporter()

        if self.config.features.node_sync:
            self._init_node_sync()

        if self.config.features.phasenet:
            self._init_phasenet()

        if self.config.features.cluster_monitor:
            self._init_cluster_monitor()

        if self.config.hardware.bridge_enabled:
            self._init_hardware_bridge()

        if self.config.hardware.hybrid_bridge_enabled:
            self._init_hybrid_bridge()

        if self.config.hardware.hybrid_node_enabled:
            self._init_hybrid_node()

        # Analysis/visualization
        self._init_correlation_analyzer()
        self._init_chromatic_visualizer()
        self._init_state_sync_manager()
        self._init_session_comparator()

        logger.info("Component initialization complete")

    def _init_core_components(self) -> None:
        """Initialize core components"""
        logger.info("Initializing core components...")

        # Audio server
        self.audio_server = AudioServer(
            input_device=self.config.audio.input_device,
            output_device=self.config.audio.output_device,
            enable_logging=self.config.server.enable_logging
        )

        # Preset management
        self.preset_store = PresetStore()
        self.ab_snapshot = ABSnapshot()

        # Streaming
        self.metrics_streamer = MetricsStreamer()
        self.latency_streamer = LatencyStreamer()

        logger.info("Core components initialized")

    def _init_auto_phi(self) -> None:
        """Initialize Auto-Φ Learner"""
        logger.info("Initializing Auto-Φ Learner...")
        config = AutoPhiConfig(
            enabled=True,
            k_depth=0.25,
            gamma_phase=0.1,
            enable_logging=self.config.server.enable_logging
        )
        self.auto_phi_learner = AutoPhiLearner(config)

    def _init_criticality_balancer(self) -> None:
        """Initialize Criticality Balancer"""
        logger.info("Initializing Criticality Balancer...")
        config = CriticalityBalancerConfig(
            enabled=True,
            beta_coupling=0.1,
            delta_amplitude=0.05,
            enable_logging=self.config.server.enable_logging
        )
        self.criticality_balancer = CriticalityBalancer(config)

    def _init_state_memory(self) -> None:
        """Initialize State Memory"""
        logger.info("Initializing State Memory...")
        config = StateMemoryConfig(
            enabled=True,
            buffer_size=256,
            trend_window=30,
            enable_logging=self.config.server.enable_logging
        )
        self.state_memory = StateMemory(config)

    def _init_state_classifier(self) -> None:
        """Initialize State Classifier"""
        logger.info("Initializing State Classifier...")
        config = StateClassifierConfig(
            hysteresis_threshold=0.1,
            min_state_duration=0.5,
            enable_logging=self.config.server.enable_logging
        )
        self.state_classifier = StateClassifierGraph(config)

    def _init_predictive_model(self) -> None:
        """Initialize Predictive Model"""
        logger.info("Initializing Predictive Model...")
        config = PredictiveModelConfig(
            buffer_size=128,
            prediction_horizon=1.5,
            min_buffer_size=50,
            enable_logging=self.config.server.enable_logging
        )
        self.predictive_model = PredictiveModel(config)

    def _init_session_recorder(self) -> None:
        """Initialize Session Recorder"""
        logger.info("Initializing Session Recorder...")
        config = SessionRecorderConfig(
            storage_dir=Path("data/sessions"),
            enable_logging=self.config.server.enable_logging
        )
        self.session_recorder = SessionRecorder(config)

    def _init_timeline_player(self) -> None:
        """Initialize Timeline Player"""
        logger.info("Initializing Timeline Player...")
        config = TimelinePlayerConfig(
            storage_dir=Path("data/sessions"),
            enable_logging=self.config.server.enable_logging
        )
        self.timeline_player = TimelinePlayer(config)

    def _init_data_exporter(self) -> None:
        """Initialize Data Exporter"""
        logger.info("Initializing Data Exporter...")
        config = ExportConfig(
            output_dir=Path("data/exports"),
            enable_logging=self.config.server.enable_logging
        )
        self.data_exporter = DataExporter(config)

    def _init_node_sync(self) -> None:
        """Initialize Node Synchronizer"""
        logger.info("Initializing Node Synchronizer...")
        role = NodeRole.MASTER if self.config.node_sync.role == "master" else NodeRole.CLIENT
        config = NodeSyncConfig(
            role=role,
            master_url=self.config.node_sync.master_url,
            enable_logging=self.config.server.enable_logging
        )
        self.node_synchronizer = NodeSynchronizer(config)

    def _init_phasenet(self) -> None:
        """Initialize PhaseNet Protocol"""
        logger.info("Initializing PhaseNet...")
        config = PhaseNetProtoConfig(
            port=self.config.phasenet.port,
            encryption_key=self.config.phasenet.encryption_key,
            enable_logging=self.config.server.enable_logging
        )
        self.phasenet_node = PhaseNetNode(config)

    def _init_cluster_monitor(self) -> None:
        """Initialize Cluster Monitor"""
        logger.info("Initializing Cluster Monitor...")
        config = ClusterMonitorConfig(
            enable_logging=self.config.server.enable_logging
        )
        self.cluster_monitor = ClusterMonitor(config)

    def _init_hardware_bridge(self) -> None:
        """Initialize Hardware I²S Bridge"""
        logger.info("Initializing Hardware Bridge...")
        self.hardware_interface = HardwareInterface(
            port=self.config.hardware.bridge_port,
            baudrate=self.config.hardware.bridge_baudrate
        )

    def _init_hybrid_bridge(self) -> None:
        """Initialize Hybrid Analog-DSP Bridge"""
        logger.info("Initializing Hybrid Bridge...")
        self.hybrid_bridge = HybridBridge(
            port=self.config.hardware.hybrid_bridge_port,
            baudrate=self.config.hardware.hybrid_bridge_baudrate
        )

    def _init_hybrid_node(self) -> None:
        """Initialize Hybrid Node"""
        logger.info("Initializing Hybrid Node...")
        config = HybridNodeConfig(
            analog_input_device=self.config.hardware.hybrid_node_input_device,
            analog_output_device=self.config.hardware.hybrid_node_output_device,
            phi_source=PhiSource.EXTERNAL,
            enable_logging=self.config.server.enable_logging
        )
        self.hybrid_node = HybridNode(config)

    def _init_correlation_analyzer(self) -> None:
        """Initialize Correlation Analyzer"""
        logger.info("Initializing Correlation Analyzer...")
        self.correlation_analyzer = CorrelationAnalyzer()

    def _init_chromatic_visualizer(self) -> None:
        """Initialize Chromatic Visualizer"""
        logger.info("Initializing Chromatic Visualizer...")
        config = VisualizerConfig(
            enable_logging=self.config.server.enable_logging
        )
        self.chromatic_visualizer = ChromaticVisualizer(config)

    def _init_state_sync_manager(self) -> None:
        """Initialize State Sync Manager"""
        logger.info("Initializing State Sync Manager...")
        config = SyncConfig(
            enable_logging=self.config.server.enable_logging
        )
        self.state_sync_manager = StateSyncManager(config)

    def _init_session_comparator(self) -> None:
        """Initialize Session Comparator"""
        logger.info("Initializing Session Comparator...")
        self.session_comparator = SessionComparator()

    def shutdown_all(self) -> None:
        """Shutdown all components gracefully"""
        logger.info("Shutting down components...")

        if self.audio_server:
            self.audio_server.stop()

        if self.session_recorder:
            self.session_recorder.stop_recording()

        if self.node_synchronizer:
            self.node_synchronizer.disconnect()

        if self.phasenet_node:
            self.phasenet_node.disconnect()

        if self.hardware_interface:
            self.hardware_interface.disconnect()

        if self.hybrid_bridge:
            self.hybrid_bridge.disconnect()

        logger.info("All components shut down")

    def get_status(self) -> Dict[str, Any]:
        """Get status of all components"""
        return {
            "audio_server": {
                "running": self.audio_server.is_running if self.audio_server else False,
                "sample_rate": self.audio_server.SAMPLE_RATE if self.audio_server else None,
                "buffer_size": self.audio_server.BUFFER_SIZE if self.audio_server else None
            },
            "features": {
                "auto_phi": self.auto_phi_learner is not None,
                "criticality_balancer": self.criticality_balancer is not None,
                "state_memory": self.state_memory is not None,
                "state_classifier": self.state_classifier is not None,
                "predictive_model": self.predictive_model is not None,
                "session_recorder": self.session_recorder is not None,
                "timeline_player": self.timeline_player is not None,
                "data_exporter": self.data_exporter is not None
            },
            "networking": {
                "node_sync": self.node_synchronizer is not None,
                "phasenet": self.phasenet_node is not None,
                "cluster_monitor": self.cluster_monitor is not None
            },
            "hardware": {
                "hardware_bridge": self.hardware_interface is not None,
                "hybrid_bridge": self.hybrid_bridge is not None,
                "hybrid_node": self.hybrid_node is not None
            }
        }
