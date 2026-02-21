const CARD_WIDTH = 750;
const CARD_HEIGHT = 1334;

type NumericMap = Record<string, number>;
type Big5TraitKey = 'O' | 'C' | 'E' | 'A' | 'N';
type ShareCardCopy = {
  genericSubtitle: string;
  footerLine1: string;
  footerLine2: string;
  mbtiSubtitle: string;
  mbtiTypeLabel: string;
  big5Subtitle: string;
  big5DominantLabel: string;
  big5Traits: Record<Big5TraitKey, string>;
};
type ShareCardCopyOverride = Partial<Omit<ShareCardCopy, 'big5Traits'>> & {
  big5Traits?: Partial<ShareCardCopy['big5Traits']>;
};

const DEFAULT_SHARE_CARD_COPY: ShareCardCopy = {
  genericSubtitle: 'Personal Insight Snapshot',
  footerLine1: 'Share your profile, grow with clarity',
  footerLine2: 'Mental wellness coaching tool',
  mbtiSubtitle: 'Personality Axis Portrait',
  mbtiTypeLabel: 'TYPE',
  big5Subtitle: 'OCEAN Radar Profile',
  big5DominantLabel: 'Dominant',
  big5Traits: {
    O: 'Openness',
    C: 'Conscientiousness',
    E: 'Extraversion',
    A: 'Agreeableness',
    N: 'Neuroticism',
  },
};

function normalizeTestId(testName: string) {
  return testName.trim().toLowerCase();
}

function resolveTestTitle(testName: string) {
  const id = normalizeTestId(testName);
  if (id === 'mbti') return 'MBTI';
  if (id === '16p') return '16 Personalities';
  if (id === 'big5') return 'Big Five';
  return testName.toUpperCase();
}

function drawBaseBackground(ctx: CanvasRenderingContext2D, title: string, subtitle: string, accent = '#c6674f') {
  const grad = ctx.createLinearGradient(0, 0, CARD_WIDTH, CARD_HEIGHT);
  grad.addColorStop(0, '#fff9f2');
  grad.addColorStop(0.45, '#fff1e3');
  grad.addColorStop(1, '#f4ddc8');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, CARD_WIDTH, CARD_HEIGHT);

  ctx.fillStyle = 'rgba(61, 42, 38, 0.06)';
  ctx.beginPath();
  ctx.arc(620, 180, 220, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(120, 1160, 180, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#3d2a26';
  ctx.textAlign = 'center';
  ctx.font = 'bold 52px Fraunces, serif';
  ctx.fillText('MiMind', CARD_WIDTH / 2, 118);

  ctx.font = 'bold 44px Fraunces, serif';
  ctx.fillStyle = accent;
  ctx.fillText(title, CARD_WIDTH / 2, 204);

  ctx.font = '600 24px Nunito Sans, sans-serif';
  ctx.fillStyle = '#785c55';
  ctx.fillText(subtitle, CARD_WIDTH / 2, 246);

  ctx.strokeStyle = 'rgba(103, 71, 63, 0.22)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(130, 280);
  ctx.lineTo(620, 280);
  ctx.stroke();
}

function drawFooter(ctx: CanvasRenderingContext2D, copy: ShareCardCopy) {
  ctx.fillStyle = 'rgba(198, 103, 79, 0.16)';
  ctx.fillRect(0, 1180, CARD_WIDTH, 154);

  ctx.textAlign = 'center';
  ctx.fillStyle = '#785c55';
  ctx.font = '24px Nunito Sans, sans-serif';
  ctx.fillText(copy.footerLine1, CARD_WIDTH / 2, 1240);

  ctx.fillStyle = '#c6674f';
  ctx.font = 'bold 22px Nunito Sans, sans-serif';
  ctx.fillText(copy.footerLine2, CARD_WIDTH / 2, 1290);
}

function toNumericMap(value: unknown): NumericMap {
  if (!value || typeof value !== 'object') return {};
  const output: NumericMap = {};
  for (const [key, raw] of Object.entries(value)) {
    if (typeof raw === 'number' && Number.isFinite(raw)) {
      output[key] = raw;
    }
  }
  return output;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'number' || typeof value === 'string' || typeof value === 'boolean') {
    return String(value);
  }
  if (Array.isArray(value)) return value.map((item) => formatValue(item)).join(', ');
  if (typeof value === 'object') {
    const pairs = Object.entries(value)
      .slice(0, 3)
      .map(([k, v]) => `${k}:${formatValue(v)}`);
    return pairs.join(' | ');
  }
  return '-';
}

function drawGenericCard(
  ctx: CanvasRenderingContext2D,
  testName: string,
  summary: Record<string, unknown>,
  copy: ShareCardCopy,
) {
  drawBaseBackground(ctx, resolveTestTitle(testName), copy.genericSubtitle);

  const entries = Object.entries(summary).filter(([, value]) => value !== null && value !== undefined).slice(0, 12);
  ctx.textAlign = 'left';
  let y = 348;

  for (const [key, value] of entries) {
    ctx.fillStyle = '#785c55';
    ctx.font = '600 24px Nunito Sans, sans-serif';
    ctx.fillText(key, 88, y);

    ctx.fillStyle = '#3d2a26';
    ctx.font = 'bold 24px Nunito Sans, sans-serif';
    ctx.fillText(formatValue(value), 370, y);
    y += 64;
  }
}

function drawMbtiCard(
  ctx: CanvasRenderingContext2D,
  testName: string,
  summary: Record<string, unknown>,
  copy: ShareCardCopy,
) {
  drawBaseBackground(ctx, resolveTestTitle(testName), copy.mbtiSubtitle, '#b3543f');

  const mbtiType = typeof summary.type === 'string' ? summary.type : '----';
  const strengths = toNumericMap(summary.dimension_strength);
  const axes = [
    ['E', 'I'],
    ['S', 'N'],
    ['T', 'F'],
    ['J', 'P'],
  ] as const;

  ctx.fillStyle = '#fff6ee';
  ctx.strokeStyle = 'rgba(179, 84, 63, 0.2)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.roundRect(86, 330, 578, 218, 28);
  ctx.fill();
  ctx.stroke();

  ctx.textAlign = 'center';
  ctx.fillStyle = '#785c55';
  ctx.font = '600 24px Nunito Sans, sans-serif';
  ctx.fillText(copy.mbtiTypeLabel, CARD_WIDTH / 2, 386);
  ctx.fillStyle = '#b3543f';
  ctx.font = 'bold 106px Fraunces, serif';
  ctx.fillText(mbtiType, CARD_WIDTH / 2, 506);

  let y = 630;
  for (const [left, right] of axes) {
    const leftValue = strengths[left] ?? 0;
    const rightValue = strengths[right] ?? 0;
    const total = leftValue + rightValue;
    const ratio = total > 0 ? leftValue / total : 0.5;

    ctx.fillStyle = '#785c55';
    ctx.textAlign = 'left';
    ctx.font = 'bold 26px Nunito Sans, sans-serif';
    ctx.fillText(`${left}  /  ${right}`, 88, y + 12);

    ctx.fillStyle = 'rgba(198, 103, 79, 0.18)';
    ctx.beginPath();
    ctx.roundRect(205, y - 16, 420, 30, 14);
    ctx.fill();

    ctx.fillStyle = '#c6674f';
    ctx.beginPath();
    ctx.roundRect(205, y - 16, 420 * ratio, 30, 14);
    ctx.fill();

    const winner = leftValue >= rightValue ? left : right;
    ctx.textAlign = 'right';
    ctx.fillStyle = '#3d2a26';
    ctx.font = '600 24px Nunito Sans, sans-serif';
    ctx.fillText(`${winner} ${Math.max(leftValue, rightValue).toFixed(0)}`, 650, y + 12);
    y += 90;
  }
}

function drawBigFiveCard(
  ctx: CanvasRenderingContext2D,
  testName: string,
  summary: Record<string, unknown>,
  copy: ShareCardCopy,
) {
  drawBaseBackground(ctx, resolveTestTitle(testName), copy.big5Subtitle, '#3c8a90');

  const rawScores = toNumericMap(summary.scores);
  const traits = ['O', 'C', 'E', 'A', 'N'];
  const labels: Record<string, string> = copy.big5Traits;
  const scores = traits.map((trait) => rawScores[trait] ?? rawScores[trait.toLowerCase()] ?? 0);

  const cx = CARD_WIDTH / 2;
  const cy = 660;
  const radius = 220;

  ctx.strokeStyle = 'rgba(60, 138, 144, 0.24)';
  ctx.lineWidth = 2;
  for (let layer = 1; layer <= 5; layer += 1) {
    const r = (radius / 5) * layer;
    ctx.beginPath();
    for (let i = 0; i < traits.length; i += 1) {
      const angle = -Math.PI / 2 + (i * 2 * Math.PI) / traits.length;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  for (let i = 0; i < traits.length; i += 1) {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / traits.length;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(x, y);
    ctx.stroke();

    const labelX = cx + Math.cos(angle) * (radius + 54);
    const labelY = cy + Math.sin(angle) * (radius + 54);
    ctx.fillStyle = '#4a6365';
    ctx.textAlign = 'center';
    ctx.font = 'bold 20px Nunito Sans, sans-serif';
    ctx.fillText(traits[i], labelX, labelY);
  }

  ctx.beginPath();
  for (let i = 0; i < traits.length; i += 1) {
    const angle = -Math.PI / 2 + (i * 2 * Math.PI) / traits.length;
    const normalized = Math.max(0, Math.min(scores[i], 100)) / 100;
    const x = cx + Math.cos(angle) * radius * normalized;
    const y = cy + Math.sin(angle) * radius * normalized;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = 'rgba(60, 138, 144, 0.35)';
  ctx.strokeStyle = '#3c8a90';
  ctx.lineWidth = 3;
  ctx.fill();
  ctx.stroke();

  const dominant = typeof summary.dominant_trait === 'string' ? summary.dominant_trait.toUpperCase() : null;
  if (dominant && labels[dominant]) {
    ctx.fillStyle = '#3c8a90';
    ctx.textAlign = 'center';
    ctx.font = 'bold 28px Nunito Sans, sans-serif';
    ctx.fillText(`${copy.big5DominantLabel}: ${labels[dominant]}`, cx, 968);
  }

  let y = 1018;
  for (let i = 0; i < traits.length; i += 1) {
    ctx.fillStyle = '#5b7375';
    ctx.textAlign = 'left';
    ctx.font = '600 21px Nunito Sans, sans-serif';
    ctx.fillText(labels[traits[i]], 112, y);

    ctx.fillStyle = '#234b4f';
    ctx.textAlign = 'right';
    ctx.font = 'bold 22px Nunito Sans, sans-serif';
    ctx.fillText(String(Math.round(scores[i])), 640, y);
    y += 44;
  }
}

export function generateShareCard(
  testName: string,
  summary: Record<string, unknown>,
  copyOverride?: ShareCardCopyOverride,
): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = CARD_WIDTH;
  canvas.height = CARD_HEIGHT;
  const ctx = canvas.getContext('2d');
  if (!ctx) {
    return canvas;
  }
  const copy: ShareCardCopy = {
    ...DEFAULT_SHARE_CARD_COPY,
    ...copyOverride,
    big5Traits: {
      ...DEFAULT_SHARE_CARD_COPY.big5Traits,
      ...(copyOverride?.big5Traits ?? {}),
    },
  };

  const id = normalizeTestId(testName);
  if (id === 'mbti' || id === '16p') {
    drawMbtiCard(ctx, testName, summary, copy);
  } else if (id === 'big5') {
    drawBigFiveCard(ctx, testName, summary, copy);
  } else {
    drawGenericCard(ctx, testName, summary, copy);
  }

  drawFooter(ctx, copy);
  return canvas;
}

export function downloadShareCard(canvas: HTMLCanvasElement, filename: string) {
  const link = document.createElement('a');
  link.download = `${filename}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

export function canShare() {
  return typeof navigator.share === 'function';
}

export async function shareImage(canvas: HTMLCanvasElement, title: string) {
  const blob = await new Promise<Blob>((resolve) => {
    canvas.toBlob((b) => resolve(b!), 'image/png');
  });
  const file = new File([blob], `${title}.png`, { type: 'image/png' });

  if (navigator.share) {
    await navigator.share({
      title: `MiMind - ${title}`,
      files: [file],
    });
  }
}
