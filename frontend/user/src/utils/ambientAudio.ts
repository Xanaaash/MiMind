export type AmbientSoundId = 'rain' | 'ocean' | 'forest' | 'campfire' | 'cafe' | 'pink_noise' | 'brown_noise';

export interface AmbientSound {
  id: AmbientSoundId;
  emoji: string;
  nameKey: string;
  color: string;
}

export const AMBIENT_SOUNDS: AmbientSound[] = [
  { id: 'rain', emoji: '🌧️', nameKey: 'tools.sound_rain', color: 'bg-calm-soft' },
  { id: 'ocean', emoji: '🌊', nameKey: 'tools.sound_ocean', color: 'bg-calm-soft' },
  { id: 'forest', emoji: '🌲', nameKey: 'tools.sound_forest', color: 'bg-safe-soft' },
  { id: 'campfire', emoji: '🔥', nameKey: 'tools.sound_campfire', color: 'bg-warn-soft' },
  { id: 'cafe', emoji: '☕', nameKey: 'tools.sound_cafe', color: 'bg-accent-soft' },
];

export const SENSORY_SOUNDS: AmbientSound[] = [
  { id: 'pink_noise', emoji: '🩷', nameKey: 'tools.sound_pink_noise', color: 'bg-accent-soft' },
  { id: 'brown_noise', emoji: '🤎', nameKey: 'tools.sound_brown_noise', color: 'bg-warn-soft' },
];

let ctx: AudioContext | null = null;
type TimeoutHandle = ReturnType<typeof setTimeout>;

interface AmbientChannel {
  gainNode: GainNode;
  activeNodes: AudioNode[];
  activeOscillators: OscillatorNode[];
  activeSources: AudioBufferSourceNode[];
  timeouts: Set<TimeoutHandle>;
  alive: boolean;
}

const channels = new Map<AmbientSoundId, AmbientChannel>();
let timerHandle: ReturnType<typeof setTimeout> | null = null;

function clampVolume(v: number): number {
  return Math.max(0, Math.min(1, v));
}

function getCtx(): AudioContext {
  if (!ctx) ctx = new AudioContext();
  if (ctx.state === 'suspended') ctx.resume();
  return ctx;
}

function createChannel(ac: AudioContext, volume: number): AmbientChannel {
  const gainNode = ac.createGain();
  gainNode.gain.value = clampVolume(volume);
  gainNode.connect(ac.destination);

  return {
    gainNode,
    activeNodes: [],
    activeOscillators: [],
    activeSources: [],
    timeouts: new Set(),
    alive: true,
  };
}

function scheduleChannelTimeout(channel: AmbientChannel, delayMs: number, fn: () => void) {
  const handle = setTimeout(() => {
    channel.timeouts.delete(handle);
    fn();
  }, delayMs);
  channel.timeouts.add(handle);
}

function disposeChannel(channel: AmbientChannel) {
  channel.alive = false;
  channel.timeouts.forEach((handle) => clearTimeout(handle));
  channel.timeouts.clear();
  channel.activeSources.forEach((s) => { try { s.stop(); } catch { /* already stopped */ } });
  channel.activeOscillators.forEach((o) => { try { o.stop(); } catch { /* already stopped */ } });
  channel.activeNodes.forEach((n) => { try { n.disconnect(); } catch { /* ok */ } });
  try { channel.gainNode.disconnect(); } catch { /* ok */ }
}

function createNoiseBuffer(seconds: number, type: 'white' | 'pink' | 'brown' = 'white'): AudioBuffer {
  const ac = getCtx();
  const length = ac.sampleRate * seconds;
  const buffer = ac.createBuffer(2, length, ac.sampleRate);

  for (let ch = 0; ch < 2; ch++) {
    const data = buffer.getChannelData(ch);
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    let lastOut = 0;

    for (let i = 0; i < length; i++) {
      const white = Math.random() * 2 - 1;

      if (type === 'white') {
        data[i] = white * 0.5;
      } else if (type === 'pink') {
        b0 = 0.99886 * b0 + white * 0.0555179;
        b1 = 0.99332 * b1 + white * 0.0750759;
        b2 = 0.96900 * b2 + white * 0.1538520;
        b3 = 0.86650 * b3 + white * 0.3104856;
        b4 = 0.55000 * b4 + white * 0.5329522;
        b5 = -0.7616 * b5 - white * 0.0168980;
        data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.06;
        b6 = white * 0.115926;
      } else {
        lastOut = (lastOut + (0.02 * white)) / 1.02;
        data[i] = lastOut * 3.0;
      }
    }
  }
  return buffer;
}

function buildRain(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const noise = ac.createBufferSource();
  noise.buffer = createNoiseBuffer(4, 'pink');
  noise.loop = true;

  const bp = ac.createBiquadFilter();
  bp.type = 'bandpass';
  bp.frequency.value = 2200;
  bp.Q.value = 0.6;

  const hp = ac.createBiquadFilter();
  hp.type = 'highpass';
  hp.frequency.value = 800;

  const lfo = ac.createOscillator();
  lfo.frequency.value = 0.08;
  const lfoGain = ac.createGain();
  lfoGain.gain.value = 400;
  lfo.connect(lfoGain).connect(bp.frequency);
  lfo.start();

  noise.connect(bp).connect(hp).connect(master);
  noise.start();

  const drip = ac.createBufferSource();
  drip.buffer = createNoiseBuffer(4, 'white');
  drip.loop = true;
  const dripBp = ac.createBiquadFilter();
  dripBp.type = 'bandpass';
  dripBp.frequency.value = 4500;
  dripBp.Q.value = 2;
  const dripGain = ac.createGain();
  dripGain.gain.value = 0.15;
  drip.connect(dripBp).connect(dripGain).connect(master);
  drip.start();

  channel.activeNodes.push(bp, hp, lfoGain, dripBp, dripGain);
  channel.activeOscillators.push(lfo);
  channel.activeSources.push(noise, drip);
}

function buildOcean(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const noise = ac.createBufferSource();
  noise.buffer = createNoiseBuffer(6, 'brown');
  noise.loop = true;

  const lp = ac.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 500;

  const lfo = ac.createOscillator();
  lfo.frequency.value = 0.07;
  const lfoGain = ac.createGain();
  lfoGain.gain.value = 350;
  lfo.connect(lfoGain).connect(lp.frequency);
  lfo.start();

  const lfo2 = ac.createOscillator();
  lfo2.frequency.value = 0.12;
  const lfo2Gain = ac.createGain();
  lfo2Gain.gain.value = 0.3;
  const waveGain = ac.createGain();
  waveGain.gain.value = 1;
  lfo2.connect(lfo2Gain).connect(waveGain.gain);
  lfo2.start();

  noise.connect(lp).connect(waveGain).connect(master);
  noise.start();

  const foam = ac.createBufferSource();
  foam.buffer = createNoiseBuffer(4, 'white');
  foam.loop = true;
  const foamBp = ac.createBiquadFilter();
  foamBp.type = 'highpass';
  foamBp.frequency.value = 3000;
  const foamGain = ac.createGain();
  foamGain.gain.value = 0.08;
  const foamLfo = ac.createOscillator();
  foamLfo.frequency.value = 0.05;
  const foamLfoGain = ac.createGain();
  foamLfoGain.gain.value = 0.06;
  foamLfo.connect(foamLfoGain).connect(foamGain.gain);
  foamLfo.start();
  foam.connect(foamBp).connect(foamGain).connect(master);
  foam.start();

  channel.activeNodes.push(lp, lfoGain, lfo2Gain, waveGain, foamBp, foamGain, foamLfoGain);
  channel.activeOscillators.push(lfo, lfo2, foamLfo);
  channel.activeSources.push(noise, foam);
}

function buildForest(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const wind = ac.createBufferSource();
  wind.buffer = createNoiseBuffer(6, 'pink');
  wind.loop = true;
  const windLp = ac.createBiquadFilter();
  windLp.type = 'lowpass';
  windLp.frequency.value = 600;
  const windGain = ac.createGain();
  windGain.gain.value = 0.5;
  const windLfo = ac.createOscillator();
  windLfo.frequency.value = 0.04;
  const windLfoG = ac.createGain();
  windLfoG.gain.value = 200;
  windLfo.connect(windLfoG).connect(windLp.frequency);
  windLfo.start();
  wind.connect(windLp).connect(windGain).connect(master);
  wind.start();

  const leaves = ac.createBufferSource();
  leaves.buffer = createNoiseBuffer(4, 'white');
  leaves.loop = true;
  const leavesBp = ac.createBiquadFilter();
  leavesBp.type = 'bandpass';
  leavesBp.frequency.value = 5000;
  leavesBp.Q.value = 1.5;
  const leavesGain = ac.createGain();
  leavesGain.gain.value = 0.06;
  leaves.connect(leavesBp).connect(leavesGain).connect(master);
  leaves.start();

  function scheduleBird() {
    const delay = 2 + Math.random() * 6;
    scheduleChannelTimeout(channel, delay * 1000, () => {
      if (!channel.alive) return;
      const osc = ac.createOscillator();
      osc.type = 'sine';
      const baseFreq = 2000 + Math.random() * 2000;
      osc.frequency.value = baseFreq;
      const birdGain = ac.createGain();
      birdGain.gain.value = 0;
      const now = ac.currentTime;
      const dur = 0.1 + Math.random() * 0.15;
      const chirps = 2 + Math.floor(Math.random() * 3);
      for (let c = 0; c < chirps; c++) {
        const t = now + c * (dur + 0.05);
        birdGain.gain.setValueAtTime(0, t);
        birdGain.gain.linearRampToValueAtTime(0.03 + Math.random() * 0.02, t + dur * 0.3);
        osc.frequency.setValueAtTime(baseFreq + Math.random() * 500, t);
        osc.frequency.linearRampToValueAtTime(baseFreq + 200 + Math.random() * 600, t + dur);
        birdGain.gain.linearRampToValueAtTime(0, t + dur);
      }
      osc.connect(birdGain).connect(master);
      osc.start(now);
      osc.stop(now + chirps * (dur + 0.05) + 0.1);
      scheduleBird();
    });
  }
  scheduleBird();

  channel.activeNodes.push(windLp, windGain, windLfoG, leavesBp, leavesGain);
  channel.activeOscillators.push(windLfo);
  channel.activeSources.push(wind, leaves);
}

function buildCampfire(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const noise = ac.createBufferSource();
  noise.buffer = createNoiseBuffer(4, 'brown');
  noise.loop = true;
  const lp = ac.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 300;
  const baseGain = ac.createGain();
  baseGain.gain.value = 0.6;
  noise.connect(lp).connect(baseGain).connect(master);
  noise.start();

  const crackle = ac.createBufferSource();
  crackle.buffer = createNoiseBuffer(4, 'white');
  crackle.loop = true;
  const crackleBp = ac.createBiquadFilter();
  crackleBp.type = 'bandpass';
  crackleBp.frequency.value = 3000;
  crackleBp.Q.value = 3;
  const crackleGain = ac.createGain();
  crackleGain.gain.value = 0.1;
  crackle.connect(crackleBp).connect(crackleGain).connect(master);
  crackle.start();

  function schedulePop() {
    const delay = 0.3 + Math.random() * 2;
    scheduleChannelTimeout(channel, delay * 1000, () => {
      if (!channel.alive) return;
      const pop = ac.createBufferSource();
      const len = 256;
      const buf = ac.createBuffer(1, len, ac.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < len; i++) {
        d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (len * 0.1));
      }
      pop.buffer = buf;
      const popBp = ac.createBiquadFilter();
      popBp.type = 'bandpass';
      popBp.frequency.value = 1500 + Math.random() * 3000;
      popBp.Q.value = 5;
      const popGain = ac.createGain();
      popGain.gain.value = 0.15 + Math.random() * 0.15;
      pop.connect(popBp).connect(popGain).connect(master);
      pop.start();
      schedulePop();
    });
  }
  schedulePop();

  channel.activeNodes.push(lp, baseGain, crackleBp, crackleGain);
  channel.activeSources.push(noise, crackle);
}

function buildCafe(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const chatter = ac.createBufferSource();
  chatter.buffer = createNoiseBuffer(6, 'pink');
  chatter.loop = true;
  const chatterBp = ac.createBiquadFilter();
  chatterBp.type = 'bandpass';
  chatterBp.frequency.value = 400;
  chatterBp.Q.value = 0.5;
  const chatterGain = ac.createGain();
  chatterGain.gain.value = 0.35;
  const chatterLfo = ac.createOscillator();
  chatterLfo.frequency.value = 0.15;
  const chatterLfoG = ac.createGain();
  chatterLfoG.gain.value = 0.1;
  chatterLfo.connect(chatterLfoG).connect(chatterGain.gain);
  chatterLfo.start();
  chatter.connect(chatterBp).connect(chatterGain).connect(master);
  chatter.start();

  const ambient = ac.createBufferSource();
  ambient.buffer = createNoiseBuffer(4, 'brown');
  ambient.loop = true;
  const ambientLp = ac.createBiquadFilter();
  ambientLp.type = 'lowpass';
  ambientLp.frequency.value = 200;
  const ambientGain = ac.createGain();
  ambientGain.gain.value = 0.3;
  ambient.connect(ambientLp).connect(ambientGain).connect(master);
  ambient.start();

  function scheduleClink() {
    const delay = 3 + Math.random() * 8;
    scheduleChannelTimeout(channel, delay * 1000, () => {
      if (!channel.alive) return;
      const osc = ac.createOscillator();
      osc.type = 'sine';
      osc.frequency.value = 3000 + Math.random() * 2000;
      const g = ac.createGain();
      const now = ac.currentTime;
      g.gain.setValueAtTime(0.02 + Math.random() * 0.02, now);
      g.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
      osc.connect(g).connect(master);
      osc.start(now);
      osc.stop(now + 0.5);
      scheduleClink();
    });
  }
  scheduleClink();

  channel.activeNodes.push(chatterBp, chatterGain, chatterLfoG, ambientLp, ambientGain);
  channel.activeOscillators.push(chatterLfo);
  channel.activeSources.push(chatter, ambient);
}

function buildPinkNoise(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const src = ac.createBufferSource();
  src.buffer = createNoiseBuffer(6, 'pink');
  src.loop = true;
  const lp = ac.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 8000;
  src.connect(lp).connect(master);
  src.start();
  channel.activeNodes.push(lp);
  channel.activeSources.push(src);
}

function buildBrownNoise(ac: AudioContext, channel: AmbientChannel) {
  const master = channel.gainNode;
  const src = ac.createBufferSource();
  src.buffer = createNoiseBuffer(6, 'brown');
  src.loop = true;
  const lp = ac.createBiquadFilter();
  lp.type = 'lowpass';
  lp.frequency.value = 600;
  src.connect(lp).connect(master);
  src.start();
  channel.activeNodes.push(lp);
  channel.activeSources.push(src);
}

const builders: Record<AmbientSoundId, (ac: AudioContext, channel: AmbientChannel) => void> = {
  rain: buildRain,
  ocean: buildOcean,
  forest: buildForest,
  campfire: buildCampfire,
  cafe: buildCafe,
  pink_noise: buildPinkNoise,
  brown_noise: buildBrownNoise,
};

export function startAmbient(soundId: AmbientSoundId, volume = 0.7) {
  const existing = channels.get(soundId);
  if (existing) {
    existing.gainNode.gain.value = clampVolume(volume);
    return;
  }

  const ac = getCtx();
  const channel = createChannel(ac, volume);
  channels.set(soundId, channel);
  builders[soundId](ac, channel);
}

export function stopAmbientSound(soundId: AmbientSoundId) {
  const channel = channels.get(soundId);
  if (!channel) return;

  disposeChannel(channel);
  channels.delete(soundId);

  if (channels.size === 0) {
    clearTimer();
  }
}

export function playAmbient(soundId: AmbientSoundId, volume = 0.7) {
  stopAmbient();
  startAmbient(soundId, volume);
}

export function stopAmbient() {
  clearTimer();
  channels.forEach((channel) => disposeChannel(channel));
  channels.clear();
}

export function setAmbientVolume(soundId: AmbientSoundId, v: number) {
  const channel = channels.get(soundId);
  if (!channel) return;
  channel.gainNode.gain.value = clampVolume(v);
}

export function getAmbientVolume(soundId: AmbientSoundId): number | null {
  const channel = channels.get(soundId);
  return channel ? channel.gainNode.gain.value : null;
}

export function setVolume(v: number) {
  const volume = clampVolume(v);
  channels.forEach((channel) => {
    channel.gainNode.gain.value = volume;
  });
}

export function setTimer(minutes: number, onEnd: () => void) {
  clearTimer();
  timerHandle = setTimeout(() => {
    stopAmbient();
    onEnd();
  }, Math.max(0, minutes) * 60 * 1000);
}

export function clearTimer() {
  if (timerHandle) {
    clearTimeout(timerHandle);
    timerHandle = null;
  }
}

export function isPlaying(): boolean {
  return channels.size > 0;
}

export function isSoundPlaying(soundId: AmbientSoundId): boolean {
  return channels.has(soundId);
}

export function getPlayingSounds(): AmbientSoundId[] {
  return Array.from(channels.keys());
}

export function getCurrentSound(): AmbientSoundId | null {
  return getPlayingSounds()[0] ?? null;
}
