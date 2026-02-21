import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  getAmbientVolume,
  getPlayingSounds,
  getCurrentSound,
  isPlaying,
  isSoundPlaying,
  playAmbient,
  setAmbientVolume,
  setTimer,
  setVolume,
  startAmbient,
  stopAmbient,
  stopAmbientSound,
} from '../../utils/ambientAudio';

class MockAudioParam {
  value = 0;

  setValueAtTime(value: number): void {
    this.value = value;
  }

  linearRampToValueAtTime(value: number): void {
    this.value = value;
  }

  exponentialRampToValueAtTime(value: number): void {
    this.value = value;
  }
}

class MockAudioNode {
  connect(): this {
    return this;
  }

  disconnect(): void {
    // noop for tests
  }
}

class MockGainNode extends MockAudioNode {
  gain = new MockAudioParam();
}

class MockBiquadFilterNode extends MockAudioNode {
  type: BiquadFilterType = 'lowpass';
  frequency = new MockAudioParam();
  Q = new MockAudioParam();
}

class MockAudioBuffer {
  private readonly channels: Float32Array[];

  constructor(channelCount: number, length: number) {
    this.channels = Array.from({ length: channelCount }, () => new Float32Array(length));
  }

  getChannelData(channel: number): Float32Array {
    return this.channels[channel];
  }
}

class MockBufferSourceNode extends MockAudioNode {
  buffer: AudioBuffer | null = null;
  loop = false;

  start(): void {
    // noop for tests
  }

  stop(): void {
    // noop for tests
  }
}

class MockOscillatorNode extends MockAudioNode {
  type: OscillatorType = 'sine';
  frequency = new MockAudioParam();

  start(): void {
    // noop for tests
  }

  stop(): void {
    // noop for tests
  }
}

class MockAudioContext {
  state: AudioContextState = 'running';
  sampleRate = 16;
  currentTime = 0;
  destination = new MockAudioNode() as unknown as AudioDestinationNode;

  resume(): Promise<void> {
    this.state = 'running';
    return Promise.resolve();
  }

  createGain(): GainNode {
    return new MockGainNode() as unknown as GainNode;
  }

  createBufferSource(): AudioBufferSourceNode {
    return new MockBufferSourceNode() as unknown as AudioBufferSourceNode;
  }

  createBiquadFilter(): BiquadFilterNode {
    return new MockBiquadFilterNode() as unknown as BiquadFilterNode;
  }

  createOscillator(): OscillatorNode {
    return new MockOscillatorNode() as unknown as OscillatorNode;
  }

  createBuffer(channelCount: number, length: number): AudioBuffer {
    return new MockAudioBuffer(channelCount, length) as unknown as AudioBuffer;
  }
}

beforeEach(() => {
  vi.useFakeTimers();
  Object.defineProperty(globalThis, 'AudioContext', {
    value: MockAudioContext,
    configurable: true,
    writable: true,
  });
  stopAmbient();
});

afterEach(() => {
  stopAmbient();
  vi.runOnlyPendingTimers();
  vi.useRealTimers();
});

describe('ambientAudio utility', () => {
  it('supports multi-sound playback and per-sound volume changes', () => {
    startAmbient('pink_noise', 0.3);
    startAmbient('brown_noise', 0.8);

    expect(isPlaying()).toBe(true);
    expect(isSoundPlaying('pink_noise')).toBe(true);
    expect(isSoundPlaying('brown_noise')).toBe(true);
    expect(getPlayingSounds()).toEqual(['pink_noise', 'brown_noise']);
    expect(getAmbientVolume('pink_noise')).toBeCloseTo(0.3, 5);
    expect(getAmbientVolume('brown_noise')).toBeCloseTo(0.8, 5);

    setAmbientVolume('pink_noise', 1.5);
    setAmbientVolume('brown_noise', -1);
    expect(getAmbientVolume('pink_noise')).toBe(1);
    expect(getAmbientVolume('brown_noise')).toBe(0);
  });

  it('playAmbient replaces previous channels with a single active sound', () => {
    startAmbient('pink_noise', 0.2);
    startAmbient('brown_noise', 0.4);
    expect(getPlayingSounds().length).toBe(2);

    playAmbient('brown_noise', 0.7);
    expect(getPlayingSounds()).toEqual(['brown_noise']);
    expect(getCurrentSound()).toBe('brown_noise');
    expect(getAmbientVolume('brown_noise')).toBeCloseTo(0.7, 5);
  });

  it('setVolume applies global volume to all active channels', () => {
    startAmbient('pink_noise', 0.1);
    startAmbient('brown_noise', 0.9);

    setVolume(0.6);
    expect(getAmbientVolume('pink_noise')).toBeCloseTo(0.6, 5);
    expect(getAmbientVolume('brown_noise')).toBeCloseTo(0.6, 5);
  });

  it('timer callback stops all channels when reaching timeout', () => {
    const onEnd = vi.fn();
    startAmbient('pink_noise', 0.5);
    setTimer(0.01, onEnd);
    expect(isPlaying()).toBe(true);

    vi.advanceTimersByTime(600);
    expect(onEnd).toHaveBeenCalledTimes(1);
    expect(isPlaying()).toBe(false);
    expect(getPlayingSounds()).toEqual([]);
  });

  it('stopAmbientSound only removes one channel and keeps others active', () => {
    startAmbient('pink_noise', 0.5);
    startAmbient('brown_noise', 0.5);

    stopAmbientSound('pink_noise');
    expect(isSoundPlaying('pink_noise')).toBe(false);
    expect(isSoundPlaying('brown_noise')).toBe(true);
    expect(getPlayingSounds()).toEqual(['brown_noise']);
  });
});
