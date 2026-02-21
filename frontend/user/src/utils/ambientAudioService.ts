import {
  clearTimer,
  isPlaying,
  isSoundPlaying,
  setAmbientVolume as setEngineSoundVolume,
  setTimer as setEngineTimer,
  startAmbient,
  stopAmbient,
  stopAmbientSound,
  type AmbientSoundId,
} from './ambientAudio';
import { useToolStore } from '../stores/useToolStore';

function computeRemainingSounds(soundId: AmbientSoundId): AmbientSoundId[] {
  const state = useToolStore.getState();
  if (state.ambient.activeSoundIds.includes(soundId)) {
    return state.ambient.activeSoundIds.filter((id) => id !== soundId);
  }
  return [...state.ambient.activeSoundIds, soundId];
}

export function toggleAmbientPlayback(soundId: AmbientSoundId) {
  const state = useToolStore.getState();
  const volume = state.ambient.volumes[soundId] ?? 0.7;
  const nextSounds = computeRemainingSounds(soundId);

  if (isSoundPlaying(soundId)) {
    stopAmbientSound(soundId);
    state.toggleAmbientSound(soundId);
    if (nextSounds.length === 0) {
      clearTimer();
      state.setAmbientStartedAt(null);
      state.setAmbientTimer(0);
    }
    return;
  }

  startAmbient(soundId, volume);
  state.toggleAmbientSound(soundId);
  if (!state.ambient.startedAtMs) {
    state.setAmbientStartedAt(Date.now());
  }

  if (state.ambient.timerMin > 0) {
    setEngineTimer(state.ambient.timerMin, () => {
      stopAllAmbientPlayback();
    });
  }
}

export function setAmbientPlaybackVolume(soundId: AmbientSoundId, volume: number) {
  const state = useToolStore.getState();
  state.setAmbientVolume(soundId, volume);
  if (isSoundPlaying(soundId)) {
    setEngineSoundVolume(soundId, volume);
  }
}

export function setAmbientPlaybackTimer(timerMin: number) {
  const state = useToolStore.getState();
  state.setAmbientTimer(timerMin);

  if (!isPlaying()) {
    return;
  }

  if (timerMin > 0) {
    setEngineTimer(timerMin, () => {
      stopAllAmbientPlayback();
    });
  } else {
    clearTimer();
  }
}

export function stopAllAmbientPlayback() {
  stopAmbient();
  useToolStore.getState().clearAmbient();
}
