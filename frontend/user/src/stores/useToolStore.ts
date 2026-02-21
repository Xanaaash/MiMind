import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import { AMBIENT_SOUNDS, type AmbientSoundId } from '../utils/ambientAudio';

type PomodoroMode = 'idle' | 'work' | 'break';
type ActivePanel = 'pomodoro' | 'ambient';
type SoundVolumeMap = Record<AmbientSoundId, number>;

interface PomodoroPreset {
  workMin: number;
  breakMin: number;
  label: string;
}

interface ToolStoreState {
  pomodoro: {
    remainingSec: number;
    isRunning: boolean;
    mode: PomodoroMode;
    preset: PomodoroPreset;
    completedToday: number;
    completedDateKey: string;
  };
  ambient: {
    activeSoundIds: AmbientSoundId[];
    volumes: SoundVolumeMap;
    timerMin: number;
    isPlaying: boolean;
    startedAtMs: number | null;
  };
  ui: {
    isRightSidebarOpen: boolean;
    activePanel: ActivePanel;
  };
  setRightSidebarOpen: (open: boolean) => void;
  toggleRightSidebar: () => void;
  setActivePanel: (panel: ActivePanel) => void;
  setPomodoroPreset: (preset: PomodoroPreset) => void;
  startPomodoro: (mode: PomodoroMode, remainingSec: number) => void;
  setPomodoroRemaining: (remainingSec: number) => void;
  stopPomodoro: () => void;
  incrementPomodoroCompleted: () => void;
  syncPomodoroDate: () => void;
  toggleAmbientSound: (soundId: AmbientSoundId) => void;
  setAmbientVolume: (soundId: AmbientSoundId, volume: number) => void;
  setAmbientTimer: (timerMin: number) => void;
  setAmbientStartedAt: (startedAtMs: number | null) => void;
  clearAmbient: () => void;
  resetTools: () => void;
}

const DEFAULT_PRESET: PomodoroPreset = {
  workMin: 25,
  breakMin: 5,
  label: '25 / 5',
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function todayKey(): string {
  return new Date().toDateString();
}

function buildDefaultVolumes(): SoundVolumeMap {
  return AMBIENT_SOUNDS.reduce((acc, sound) => {
    acc[sound.id] = 0.7;
    return acc;
  }, {} as SoundVolumeMap);
}

const buildDefaultState = () => ({
  pomodoro: {
    remainingSec: 0,
    isRunning: false,
    mode: 'idle' as PomodoroMode,
    preset: DEFAULT_PRESET,
    completedToday: 0,
    completedDateKey: todayKey(),
  },
  ambient: {
    activeSoundIds: [] as AmbientSoundId[],
    volumes: buildDefaultVolumes(),
    timerMin: 0,
    isPlaying: false,
    startedAtMs: null as number | null,
  },
  ui: {
    isRightSidebarOpen: false,
    activePanel: 'pomodoro' as ActivePanel,
  },
});

export const useToolStore = create<ToolStoreState>()(
  persist(
    (set) => ({
      ...buildDefaultState(),

      setRightSidebarOpen: (open) => set((state) => ({ ui: { ...state.ui, isRightSidebarOpen: open } })),

      toggleRightSidebar: () =>
        set((state) => ({ ui: { ...state.ui, isRightSidebarOpen: !state.ui.isRightSidebarOpen } })),

      setActivePanel: (panel) => set((state) => ({ ui: { ...state.ui, activePanel: panel } })),

      setPomodoroPreset: (preset) =>
        set((state) => ({
          pomodoro: {
            ...state.pomodoro,
            preset: {
              workMin: clamp(Math.round(preset.workMin), 1, 180),
              breakMin: clamp(Math.round(preset.breakMin), 1, 60),
              label: preset.label || `${preset.workMin} / ${preset.breakMin}`,
            },
          },
        })),

      startPomodoro: (mode, remainingSec) =>
        set((state) => ({
          pomodoro: {
            ...state.pomodoro,
            mode,
            isRunning: mode !== 'idle',
            remainingSec: clamp(Math.floor(remainingSec), 0, 24 * 60 * 60),
          },
        })),

      setPomodoroRemaining: (remainingSec) =>
        set((state) => ({
          pomodoro: {
            ...state.pomodoro,
            remainingSec: clamp(Math.floor(remainingSec), 0, 24 * 60 * 60),
          },
        })),

      stopPomodoro: () =>
        set((state) => ({
          pomodoro: {
            ...state.pomodoro,
            isRunning: false,
            mode: 'idle',
            remainingSec: 0,
          },
        })),

      incrementPomodoroCompleted: () =>
        set((state) => {
          const key = todayKey();
          const baseCount = state.pomodoro.completedDateKey === key ? state.pomodoro.completedToday : 0;
          return {
            pomodoro: {
              ...state.pomodoro,
              completedDateKey: key,
              completedToday: baseCount + 1,
            },
          };
        }),

      syncPomodoroDate: () =>
        set((state) => {
          const key = todayKey();
          if (state.pomodoro.completedDateKey === key) return state;
          return {
            pomodoro: {
              ...state.pomodoro,
              completedDateKey: key,
              completedToday: 0,
            },
          };
        }),

      toggleAmbientSound: (soundId) =>
        set((state) => {
          const exists = state.ambient.activeSoundIds.includes(soundId);
          const nextIds = exists
            ? state.ambient.activeSoundIds.filter((id) => id !== soundId)
            : [...state.ambient.activeSoundIds, soundId];
          return {
            ambient: {
              ...state.ambient,
              activeSoundIds: nextIds,
              isPlaying: nextIds.length > 0,
            },
          };
        }),

      setAmbientVolume: (soundId, volume) =>
        set((state) => ({
          ambient: {
            ...state.ambient,
            volumes: {
              ...state.ambient.volumes,
              [soundId]: clamp(volume, 0, 1),
            },
          },
        })),

      setAmbientTimer: (timerMin) =>
        set((state) => ({
          ambient: {
            ...state.ambient,
            timerMin: clamp(Math.floor(timerMin), 0, 180),
          },
        })),

      setAmbientStartedAt: (startedAtMs) =>
        set((state) => ({
          ambient: {
            ...state.ambient,
            startedAtMs,
          },
        })),

      clearAmbient: () =>
        set((state) => ({
          ambient: {
            ...state.ambient,
            activeSoundIds: [],
            timerMin: 0,
            isPlaying: false,
            startedAtMs: null,
          },
        })),

      resetTools: () => set(buildDefaultState()),
    }),
    {
      name: 'mc_tool_store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        pomodoro: {
          preset: state.pomodoro.preset,
          completedToday: state.pomodoro.completedToday,
          completedDateKey: state.pomodoro.completedDateKey,
        },
        ambient: {
          volumes: state.ambient.volumes,
          timerMin: state.ambient.timerMin,
        },
        ui: state.ui,
      }),
      merge: (persisted, current) => {
        const data = persisted as Partial<ToolStoreState> | undefined;
        return {
          ...current,
          ...data,
          pomodoro: {
            ...current.pomodoro,
            ...(data?.pomodoro ?? {}),
            mode: 'idle',
            isRunning: false,
            remainingSec: 0,
          },
          ambient: {
            ...current.ambient,
            ...(data?.ambient ?? {}),
            activeSoundIds: [],
            isPlaying: false,
            startedAtMs: null,
          },
          ui: {
            ...current.ui,
            ...(data?.ui ?? {}),
          },
        };
      },
    },
  ),
);

export type { ActivePanel, PomodoroMode, PomodoroPreset };
