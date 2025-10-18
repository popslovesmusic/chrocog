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
        self.audio_server: Optional[AudioServer] = None
        self.preset_store: Optional[PresetStore] = None
        self.ab_snapshot: Optional[ABSnapshot] = None
        self.metrics_streamer: Optional[MetricsStreamer] = None
        self.latency_streamer)
        self.auto_phi_learner: Optional[AutoPhiLearner] = None
        self.criticality_balancer: Optional[CriticalityBalancer] = None
        self.state_memory: Optional[StateMemory] = None
        self.state_classifier: Optional[StateClassifierGraph] = None
        self.predictive_model)
        self.session_recorder: Optional[SessionRecorder] = None
        self.timeline_player: Optional[TimelinePlayer] = None
        self.data_exporter: Optional[DataExporter] = None
        self.session_comparator)
        self.node_synchronizer: Optional[NodeSynchronizer] = None
        self.phasenet_node: Optional[PhaseNetNode] = None
        self.cluster_monitor)
        self.correlation_analyzer: Optional[CorrelationAnalyzer] = None
        self.chromatic_visualizer: Optional[ChromaticVisualizer] = None
        self.state_sync_manager)
        self.hardware_interface: Optional[HardwareInterface] = None
        self.hybrid_bridge: Optional[HybridBridge] = None
        self.hybrid_node)

    def initialize_all(self) :
        """Get status of all components"""
        return {
            "audio_server": {
                "running",
                "sample_rate",
                "buffer_size",
            "features": {
                "auto_phi",
                "criticality_balancer",
                "state_memory",
                "state_classifier",
                "predictive_model",
                "session_recorder",
                "timeline_player",
                "data_exporter",
            "networking": {
                "node_sync",
                "phasenet",
                "cluster_monitor",
            "hardware": {
                "hardware_bridge",
                "hybrid_bridge",
                "hybrid_node": self.hybrid_node is not None
            }
        }
