export type NeuroSharePreset = 'xiaohongshu' | 'instagram' | 'tiktok';

type Dimension = {
  label: string;
  score: number;
  max: number;
  color: string;
};

type Payload = {
  scaleId: string;
  levelLabel: string;
  summary: string;
  total: number;
  maxTotal: number;
  dimensions: Dimension[];
  archetypeTitle: string;
  archetypeTags: string[];
};

const PRESET_SIZE: Record<NeuroSharePreset, { width: number; height: number }> = {
  xiaohongshu: { width: 1080, height: 1440 },
  instagram: { width: 1080, height: 1080 },
  tiktok: { width: 1080, height: 1920 },
};

const ARCHETYPE_COPY: Record<string, Record<string, { title: string; tags: string[] }>> = {
  asrs: {
    low: { title: '稳定节奏型 / Steady Flow', tags: ['节奏稳定', '执行平衡', '可持续推进'] },
    moderate: { title: '猎人型倾向 / Hunter Lean', tags: ['高唤醒启动', '任务切换快', '需要结构化'] },
    high: { title: '猎人型执行者 / Hunter Executor', tags: ['高能量驱动', '冲刺型完成', '微结构最友好'] },
  },
  aq10: {
    low: { title: '均衡社交型 / Social Balance', tags: ['社交信号均衡', '情境适配强', '沟通弹性好'] },
    moderate: { title: '系统化倾向 / System Lean', tags: ['细节敏锐', '深度聚焦', '偏好清晰规则'] },
    high: { title: '系统化分析者 / System Builder', tags: ['模式识别强', '结构思维强', '信息压缩效率高'] },
  },
  hsp: {
    low: { title: '稳态感知型 / Stable Sensor', tags: ['刺激耐受高', '环境适配快', '情绪波动平稳'] },
    moderate: { title: '敏锐感知型 / Sensitive Lean', tags: ['环境察觉快', '情绪共鸣强', '需要节奏留白'] },
    high: { title: '感知放大器 / Sensory Amplifier', tags: ['高分辨感知', '深度情绪加工', '恢复窗口重要'] },
  },
};

function drawBackground(ctx: CanvasRenderingContext2D, width: number, height: number): void {
  const gradient = ctx.createLinearGradient(0, 0, width, height);
  gradient.addColorStop(0, '#fffaf3');
  gradient.addColorStop(0.5, '#ffefd9');
  gradient.addColorStop(1, '#f9dcc6');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  ctx.fillStyle = 'rgba(199, 103, 79, 0.12)';
  ctx.beginPath();
  ctx.arc(width * 0.86, height * 0.16, width * 0.22, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(width * 0.13, height * 0.88, width * 0.18, 0, Math.PI * 2);
  ctx.fill();
}

function clampSummary(summary: string): string {
  if (summary.length <= 170) {
    return summary;
  }
  return `${summary.slice(0, 167)}...`;
}

export function buildNeuroArchetype(scaleId: string, level: string): { title: string; tags: string[] } {
  const normalizedScale = scaleId.toLowerCase();
  const normalizedLevel = level.toLowerCase();
  const fallback = { title: '认知特质画像 / Cognitive Profile', tags: ['神经多样性', '特质探索', '非临床诊断'] };

  const byScale = ARCHETYPE_COPY[normalizedScale];
  if (!byScale) {
    return fallback;
  }
  return byScale[normalizedLevel] ?? fallback;
}

export function generateNeuroShareCard(payload: Payload, preset: NeuroSharePreset): HTMLCanvasElement {
  const { width, height } = PRESET_SIZE[preset];
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return canvas;
  }

  drawBackground(ctx, width, height);

  const contentX = Math.round(width * 0.08);
  const contentWidth = Math.round(width * 0.84);

  ctx.fillStyle = '#3d2a26';
  ctx.textAlign = 'center';
  ctx.font = `bold ${Math.round(width * 0.07)}px Fraunces, serif`;
  ctx.fillText('MiMind', width / 2, Math.round(height * 0.08));

  ctx.fillStyle = '#b4553f';
  ctx.font = `bold ${Math.round(width * 0.05)}px Fraunces, serif`;
  ctx.fillText('你的大脑说明书 · Brain Manual', width / 2, Math.round(height * 0.13));

  ctx.fillStyle = '#6d4c45';
  ctx.font = `${Math.round(width * 0.024)}px Nunito Sans, sans-serif`;
  ctx.fillText(payload.scaleId.toUpperCase(), width / 2, Math.round(height * 0.165));

  const topCardY = Math.round(height * 0.2);
  const topCardH = Math.round(height * 0.17);
  ctx.fillStyle = 'rgba(255, 246, 237, 0.95)';
  ctx.strokeStyle = 'rgba(180, 85, 63, 0.25)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(contentX, topCardY, contentWidth, topCardH, 28);
  ctx.fill();
  ctx.stroke();

  ctx.textAlign = 'left';
  ctx.fillStyle = '#5f4039';
  ctx.font = `600 ${Math.round(width * 0.026)}px Nunito Sans, sans-serif`;
  ctx.fillText(payload.levelLabel, contentX + 26, topCardY + 40);

  ctx.fillStyle = '#b4553f';
  ctx.font = `bold ${Math.round(width * 0.055)}px Fraunces, serif`;
  ctx.fillText(payload.archetypeTitle, contentX + 26, topCardY + 88);

  ctx.fillStyle = '#7a5a54';
  ctx.font = `${Math.round(width * 0.024)}px Nunito Sans, sans-serif`;
  ctx.fillText(`Score ${payload.total} / ${payload.maxTotal}`, contentX + 26, topCardY + topCardH - 20);

  const tagY = topCardY + topCardH + 24;
  let tagX = contentX;
  payload.archetypeTags.forEach((tag) => {
    const paddingX = 14;
    const textWidth = ctx.measureText(tag).width;
    const pillWidth = textWidth + paddingX * 2;
    const pillHeight = 36;

    if (tagX + pillWidth > contentX + contentWidth) {
      tagX = contentX;
    }

    ctx.fillStyle = 'rgba(180, 85, 63, 0.14)';
    ctx.beginPath();
    ctx.roundRect(tagX, tagY, pillWidth, pillHeight, 18);
    ctx.fill();

    ctx.fillStyle = '#8a5f57';
    ctx.font = `600 ${Math.round(width * 0.02)}px Nunito Sans, sans-serif`;
    ctx.fillText(tag, tagX + paddingX, tagY + 24);
    tagX += pillWidth + 10;
  });

  const chartY = tagY + 56;
  const rowHeight = 56;
  payload.dimensions.slice(0, 5).forEach((dimension, idx) => {
    const y = chartY + idx * rowHeight;
    const ratio = dimension.max > 0 ? Math.max(0, Math.min(dimension.score / dimension.max, 1)) : 0;

    ctx.fillStyle = '#6f4f48';
    ctx.font = `600 ${Math.round(width * 0.024)}px Nunito Sans, sans-serif`;
    ctx.fillText(dimension.label, contentX, y + 18);

    ctx.fillStyle = 'rgba(120, 92, 85, 0.18)';
    ctx.beginPath();
    ctx.roundRect(contentX, y + 26, contentWidth, 16, 8);
    ctx.fill();

    ctx.fillStyle = dimension.color || '#c6674f';
    ctx.beginPath();
    ctx.roundRect(contentX, y + 26, contentWidth * ratio, 16, 8);
    ctx.fill();

    ctx.textAlign = 'right';
    ctx.fillStyle = '#5c3f39';
    ctx.fillText(`${dimension.score} / ${dimension.max}`, contentX + contentWidth, y + 18);
    ctx.textAlign = 'left';
  });

  const summaryY = chartY + rowHeight * 5 + 12;
  const summaryH = Math.round(height * 0.17);
  ctx.fillStyle = 'rgba(255, 246, 237, 0.95)';
  ctx.beginPath();
  ctx.roundRect(contentX, summaryY, contentWidth, summaryH, 24);
  ctx.fill();

  ctx.fillStyle = '#7b5b54';
  ctx.font = `600 ${Math.round(width * 0.022)}px Nunito Sans, sans-serif`;
  ctx.fillText('Insight', contentX + 20, summaryY + 30);

  ctx.fillStyle = '#4f3530';
  ctx.font = `${Math.round(width * 0.022)}px Nunito Sans, sans-serif`;
  const summary = clampSummary(payload.summary);
  const words = summary.split('');
  let line = '';
  let lineY = summaryY + 62;
  const maxLineWidth = contentWidth - 40;
  words.forEach((char) => {
    const next = line + char;
    if (ctx.measureText(next).width > maxLineWidth) {
      ctx.fillText(line, contentX + 20, lineY);
      line = char;
      lineY += 30;
    } else {
      line = next;
    }
  });
  if (line) {
    ctx.fillText(line, contentX + 20, lineY);
  }

  ctx.textAlign = 'center';
  ctx.fillStyle = '#8a665e';
  ctx.font = `${Math.round(width * 0.02)}px Nunito Sans, sans-serif`;
  ctx.fillText('Neurodiversity Trait Exploration · Not a Clinical Diagnosis', width / 2, Math.round(height * 0.965));

  return canvas;
}
