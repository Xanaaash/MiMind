export interface MeditationTrackConfig {
  id: string;
  src: string;
  minutes: number;
  titleKey: string;
  descKey: string;
}

// Frontend-configured playlist. Replace audio files and this list to update the meditation library.
export const meditationPlaylist: MeditationTrackConfig[] = [
  {
    id: 'calm-10',
    src: '/audio/meditation/calm-reset.m4a',
    minutes: 10,
    titleKey: 'tools.meditation_track_calm_title',
    descKey: 'tools.meditation_track_calm_desc',
  },
  {
    id: 'focus-15',
    src: '/audio/meditation/focus-grounding.m4a',
    minutes: 15,
    titleKey: 'tools.meditation_track_focus_title',
    descKey: 'tools.meditation_track_focus_desc',
  },
  {
    id: 'sleep-20',
    src: '/audio/meditation/sleep-winddown.m4a',
    minutes: 20,
    titleKey: 'tools.meditation_track_sleep_title',
    descKey: 'tools.meditation_track_sleep_desc',
  },
];
