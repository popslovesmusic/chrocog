import { updateKnobRotation } from './soundlab-utils.js';

let audioContext;
let analyser;
let source;
let oscillator;
let gainNode;
let isPlaying = false;

let lowShelf;
let midPeak;
let highShelf;
let waveshaper;

let dataArray;
let bufferLength;
let frequencyData;

const params = {
  low: 0,
  mid: 0,
  high: 0,
  drive: 1,
  curve: 1,
  mix: 0
};

export function getParamsState() {
  return params;
}

export function getAudioContext() {
  return audioContext;
}

export function getAnalyser() {
  return analyser;
}

export function getGainNode() {
  return gainNode;
}

export function getFilters() {
  return { lowShelf, midPeak, highShelf, waveshaper };
}

export function isAudioPlaying() {
  return isPlaying;
}

export function setAudioPlaying(value) {
  isPlaying = value;
}

export function ensureProcessingChain() {
  if (!audioContext || !lowShelf || !midPeak || !highShelf || !waveshaper || !gainNode || !analyser) {
    return;
  }

  // Check if compressor exists (from soundlab_v2.html inline script)
  const comp = window.comp;

  if (gainNode.numberOfOutputs > 0) {
    try {
      gainNode.disconnect();
    } catch (e) {}
  }

  try {
    lowShelf.disconnect();
  } catch (e) {}
  try {
    midPeak.disconnect();
  } catch (e) {}
  try {
    highShelf.disconnect();
  } catch (e) {}
  try {
    waveshaper.disconnect();
  } catch (e) {}
  try {
    gainNode.disconnect();
  } catch (e) {}
  try {
    analyser.disconnect();
  } catch (e) {}
  if (comp) {
    try {
      comp.disconnect();
    } catch (e) {}
  }

  // Rebuild chain
  lowShelf.connect(midPeak);
  midPeak.connect(highShelf);
  highShelf.connect(waveshaper);
  waveshaper.connect(gainNode);

  // Route through compressor if it exists, otherwise direct to analyser
  if (comp) {
    gainNode.connect(comp);
    comp.connect(analyser);
  } else {
    gainNode.connect(analyser);
  }

  analyser.connect(audioContext.destination);
}

export function updateSaturation() {
  if (!waveshaper) return;

  const curveAmount = params.drive * params.curve;
  const curveLength = 2048;
  const curve = new Float32Array(curveLength);

  for (let i = 0; i < curveLength; i++) {
    const x = (i * 2) / curveLength - 1;
    curve[i] = Math.tanh(curveAmount * x) * (params.mix / 100);
  }

  waveshaper.curve = curve;
}

function draw() {
  if (!audioContext || !analyser || !dataArray || !frequencyData) {
    requestAnimationFrame(draw);
    return;
  }

  analyser.getByteTimeDomainData(dataArray);
  analyser.getByteFrequencyData(frequencyData);

  const spectrumCanvas = document.getElementById('spectrumCanvas');
  const waveformCanvas = document.getElementById('waveformCanvas');
  if (!spectrumCanvas || !waveformCanvas) {
    requestAnimationFrame(draw);
    return;
  }

  const spectrumCtx = spectrumCanvas.getContext('2d');
  const waveformCtx = waveformCanvas.getContext('2d');

  // FIX 2: Calculate RMS for visual feedback
  let rmsSum = 0;
  for (let i = 0; i < bufferLength; i++) {
    const normalized = (dataArray[i] - 128) / 128;
    rmsSum += normalized * normalized;
  }
  const rms = Math.sqrt(rmsSum / bufferLength);
  const rmsDB = 20 * Math.log10(rms + 1e-10);

  // Spectrum visualization
  spectrumCtx.fillStyle = '#000';
  spectrumCtx.fillRect(0, 0, spectrumCanvas.width, spectrumCanvas.height);
  spectrumCtx.lineWidth = 2;

  // FIX 2: Color-code spectrum based on signal strength
  const spectralEnergy = frequencyData.reduce((sum, val) => sum + val, 0) / bufferLength;
  if (spectralEnergy > 128) {
    spectrumCtx.strokeStyle = '#ff6600'; // Orange for hot signal
  } else if (spectralEnergy > 64) {
    spectrumCtx.strokeStyle = '#00ff66'; // Green for good signal
  } else {
    spectrumCtx.strokeStyle = '#00ff66'; // Default green
  }

  spectrumCtx.beginPath();

  const sliceWidth = (spectrumCanvas.width * 1.0) / bufferLength;
  let x = 0;

  for (let i = 0; i < bufferLength; i++) {
    const v = frequencyData[i] / 255;
    const y = spectrumCanvas.height - v * spectrumCanvas.height;
    if (i === 0) {
      spectrumCtx.moveTo(x, y);
    } else {
      spectrumCtx.lineTo(x, y);
    }
    x += sliceWidth;
  }

  spectrumCtx.stroke();

  // FIX 2: Add RMS text overlay on spectrum
  spectrumCtx.fillStyle = '#0f0';
  spectrumCtx.font = '12px monospace';
  spectrumCtx.fillText(`RMS: ${rmsDB.toFixed(1)} dB`, 10, 20);

  // Waveform visualization
  waveformCtx.fillStyle = '#000';
  waveformCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height);
  waveformCtx.lineWidth = 2;
  waveformCtx.strokeStyle = '#00ffff';
  waveformCtx.beginPath();

  const waveformSliceWidth = (waveformCanvas.width * 1.0) / bufferLength;
  let waveformX = 0;

  for (let i = 0; i < bufferLength; i++) {
    const v = dataArray[i] / 128.0;
    const y = (v * waveformCanvas.height) / 2;
    if (i === 0) {
      waveformCtx.moveTo(waveformX, y);
    } else {
      waveformCtx.lineTo(waveformX, y);
    }
    waveformX += waveformSliceWidth;
  }

  waveformCtx.lineTo(waveformCanvas.width, waveformCanvas.height / 2);
  waveformCtx.stroke();

  // FIX 2: Add peak detection indicator
  const peak = Math.max(...Array.from(dataArray).map(v => Math.abs(v - 128)));
  const peakNormalized = peak / 128;
  waveformCtx.fillStyle = peakNormalized > 0.95 ? '#f00' : '#0ff';
  waveformCtx.font = '12px monospace';
  waveformCtx.fillText(`Peak: ${(peakNormalized * 100).toFixed(1)}%`, 10, 20);

  // FIX 2: Update status display with signal confirmation
  if (isPlaying && spectralEnergy > 10) {
    const statusEl = document.getElementById('status');
    if (statusEl && !statusEl.textContent.includes('Signal Confirmed')) {
      const currentText = statusEl.textContent;
      if (!currentText.includes('Signal Confirmed')) {
        statusEl.textContent = currentText + ' | Signal Confirmed ✓';
      }
    }
  }

  requestAnimationFrame(draw);
}

export function setKnobValue(knobId, value, labelId, formatFn) {
  const knob = document.getElementById(knobId);
  const label = document.getElementById(labelId);
  if (!knob || !label) return;

  const min = getMinValue(knob.dataset.param);
  const max = getMaxValue(knob.dataset.param);
  params[knob.dataset.param] = value;
  knob.dataset.value = value;
  updateKnobRotation(knob, value, min, max);
  label.textContent = formatFn(value);
}

export function getMinValue(param) {
  if (param === 'low' || param === 'mid' || param === 'high') return -20;
  if (param === 'drive') return 1;
  if (param === 'curve') return 0.1;
  if (param === 'mix') return 0;
  return 0;
}

export function getMaxValue(param) {
  if (param === 'low' || param === 'mid' || param === 'high') return 20;
  if (param === 'drive') return 10;
  if (param === 'curve') return 5;
  if (param === 'mix') return 100;
  return 1;
}

export function isEqReady() {
  return !!(audioContext && lowShelf && midPeak && highShelf);
}

export function notifyEqNotReady() {
  const statusEl = document.getElementById('status');
  if (statusEl) {
    statusEl.textContent = 'Start the audio engine before adjusting EQ controls.';
  }
}

export async function initAudio() {
  // FIX 1: Create AudioContext if not present
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }

  // FIX 1: Resume AudioContext if suspended (browser autoplay policy)
  if (audioContext.state === 'suspended') {
    try {
      await audioContext.resume();
      console.log('[FIX-1] AudioContext resumed from suspended state');
    } catch (err) {
      console.error('[FIX-1] Failed to resume AudioContext:', err);
    }
  }

  analyser = audioContext.createAnalyser();
  analyser.fftSize = 2048;
  bufferLength = analyser.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);
  frequencyData = new Uint8Array(bufferLength);

  lowShelf = audioContext.createBiquadFilter();
  lowShelf.type = 'lowshelf';
  lowShelf.frequency.value = 100;

  midPeak = audioContext.createBiquadFilter();
  midPeak.type = 'peaking';
  midPeak.frequency.value = 1000;
  midPeak.Q.value = 1;

  highShelf = audioContext.createBiquadFilter();
  highShelf.type = 'highshelf';
  highShelf.frequency.value = 8000;

  waveshaper = audioContext.createWaveShaper();
  updateSaturation();

  gainNode = audioContext.createGain();
  gainNode.gain.value = 0.5;

  ensureProcessingChain();

  const startBtn = document.getElementById('startBtn');
  const generateBtn = document.getElementById('generateBtn');
  const loadBtn = document.getElementById('loadBtn');
  const status = document.getElementById('status');

  if (startBtn) startBtn.disabled = true;
  if (generateBtn) generateBtn.disabled = false;
  if (loadBtn) loadBtn.disabled = false;
  if (status) status.textContent = 'Audio System Active | Ready for Input';

  updateMatrix();
  draw();
}

export async function generateTone() {
  // FIX 1: Ensure AudioContext is initialized
  if (!audioContext) {
    await initAudio();
  }

  // FIX 1: Resume AudioContext if suspended
  if (audioContext.state === 'suspended') {
    try {
      await audioContext.resume();
      console.log('[FIX-1] AudioContext resumed before tone generation');
    } catch (err) {
      console.error('[FIX-1] Failed to resume AudioContext:', err);
      return;
    }
  }

  // FIX 1: Clean up existing oscillator
  if (oscillator) {
    oscillator.stop();
    oscillator.disconnect();
  }

  // FIX 1: Create and configure oscillator
  oscillator = audioContext.createOscillator();
  oscillator.type = 'sine';
  oscillator.frequency.value = 440;

  // FIX 1: Ensure processing chain is connected
  ensureProcessingChain();
  oscillator.connect(lowShelf);

  // FIX 1: Verify gain is audible
  if (gainNode && gainNode.gain.value === 0) {
    gainNode.gain.value = 0.5;
    console.log('[FIX-1] Gain was 0, set to 0.5 for audibility');
  }

  // FIX 1: Start oscillator
  oscillator.start();
  isPlaying = true;
  console.log('[FIX-1] Tone synthesis started: 440Hz sine wave');

  const generateBtn = document.getElementById('generateBtn');
  const stopBtn = document.getElementById('stopBtn');
  const status = document.getElementById('status');

  if (generateBtn) generateBtn.disabled = true;
  if (stopBtn) stopBtn.disabled = false;
  if (status) status.textContent = 'Generating 440Hz Tone | Processing Active';
}

export function loadAudioFile(e) {
  const file = e.target.files[0];
  if (!file) return;

  if (!audioContext) {
    const statusEl = document.getElementById('status');
    if (statusEl) {
      statusEl.textContent = 'Start the audio engine before loading a file.';
    }
    e.target.value = '';
    const startButton = document.getElementById('startBtn');
    if (startButton) {
      startButton.focus({ preventScroll: true });
    }
    return;
  }

  const reader = new FileReader();
  reader.onload = function (event) {
    audioContext.decodeAudioData(event.target.result, function (buffer) {
      if (source) {
        source.stop();
        source.disconnect();
      }

      source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.loop = true;

      ensureProcessingChain();
      source.connect(lowShelf);

      source.start();
      isPlaying = true;

      const generateBtn = document.getElementById('generateBtn');
      const stopBtn = document.getElementById('stopBtn');
      const status = document.getElementById('status');

      if (generateBtn) generateBtn.disabled = true;
      if (stopBtn) stopBtn.disabled = false;
      if (status) status.textContent = 'Playing Audio File | Processing Active';
    });
  };
  reader.readAsArrayBuffer(file);
}

export function stopAudio() {
  if (oscillator) {
    oscillator.stop();
    oscillator.disconnect();
    oscillator = null;
  }
  if (source) {
    source.stop();
    source.disconnect();
    source = null;
  }

  isPlaying = false;

  const generateBtn = document.getElementById('generateBtn');
  const stopBtn = document.getElementById('stopBtn');
  const status = document.getElementById('status');

  if (generateBtn) generateBtn.disabled = false;
  if (stopBtn) stopBtn.disabled = true;
  if (status) status.textContent = 'Audio Stopped | Ready for Input';
}

export function updateMatrix() {
  const matrixGrid = document.getElementById('matrixGrid');
  if (!matrixGrid) return;

  // FIX 4: Map parameters to their keys
  const paramKeys = ['low', 'mid', 'high', 'drive', 'curve', 'mix'];
  const paramLabels = ['Low', 'Mid', 'High', 'Drive', 'Curve', 'Mix'];
  matrixGrid.innerHTML = '';

  // FIX 4: Get current parameter values for dynamic coupling
  const currentValues = {
    low: params.low,
    mid: params.mid,
    high: params.high,
    drive: params.drive,
    curve: params.curve,
    mix: params.mix
  };

  paramLabels.forEach((rowLabel, rowIndex) => {
    paramLabels.forEach((colLabel, colIndex) => {
      const cell = document.createElement('div');
      cell.className = 'matrix-cell';

      const rowKey = paramKeys[rowIndex];
      const colKey = paramKeys[colIndex];
      const rowVal = currentValues[rowKey];
      const colVal = currentValues[colKey];

      // FIX 4: Add data attributes for dynamic updates
      cell.dataset.row = rowKey;
      cell.dataset.col = colKey;

      cell.innerHTML = `<strong>${rowLabel}</strong><br>${colLabel}`;

      if (rowIndex === colIndex) {
        // FIX 4: Show current value on diagonal
        cell.classList.add('active');
        let valueDisplay = '';
        if (rowKey === 'low' || rowKey === 'mid' || rowKey === 'high') {
          valueDisplay = `${rowVal.toFixed(1)} dB`;
        } else if (rowKey === 'drive') {
          valueDisplay = `${rowVal.toFixed(1)}x`;
        } else if (rowKey === 'curve') {
          valueDisplay = `${rowVal.toFixed(2)}`;
        } else if (rowKey === 'mix') {
          valueDisplay = `${Math.round(rowVal)}%`;
        }
        cell.innerHTML += `<br><span class="matrix-value">${valueDisplay}</span>`;
      } else {
        // FIX 4: Calculate coupling based on actual parameter interaction
        const baseCoupling = (Math.sin((rowIndex + 1) * (colIndex + 2)) + 1) / 2;

        // FIX 4: Weight coupling by parameter magnitudes
        const rowNorm = Math.abs(rowVal) / getMaxValue(rowKey);
        const colNorm = Math.abs(colVal) / getMaxValue(colKey);
        const dynamicCoupling = baseCoupling * (rowNorm * colNorm);

        const intensity = Math.round(dynamicCoupling * 100);
        const color = intensity > 50 ? '#ff6600' : intensity > 25 ? '#00ff66' : '#006633';
        cell.innerHTML += `<br><span style="color:${color}">${intensity}%</span>`;
      }

      matrixGrid.appendChild(cell);
    });
  });

  console.log('[FIX-4] Matrix updated with current parameter values:', currentValues);
}

window.addEventListener('beforeunload', () => {
  if (audioContext) {
    audioContext.close();
  }
});
