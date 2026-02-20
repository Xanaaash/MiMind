export function generateShareCard(
  testName: string,
  summary: Record<string, unknown>,
): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = 750;
  canvas.height = 1334;
  const ctx = canvas.getContext('2d')!;

  // Background gradient
  const grad = ctx.createLinearGradient(0, 0, 750, 1334);
  grad.addColorStop(0, '#fff9f2');
  grad.addColorStop(0.5, '#ffeede');
  grad.addColorStop(1, '#f6decb');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, 750, 1334);

  // Accent circle decoration
  ctx.fillStyle = 'rgba(198, 103, 79, 0.1)';
  ctx.beginPath();
  ctx.arc(600, 200, 250, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(150, 1100, 200, 0, Math.PI * 2);
  ctx.fill();

  // Title
  ctx.fillStyle = '#3d2a26';
  ctx.font = 'bold 48px Fraunces, serif';
  ctx.textAlign = 'center';
  ctx.fillText('MiMind', 375, 120);

  // Test name
  ctx.font = 'bold 40px Fraunces, serif';
  ctx.fillStyle = '#c6674f';
  ctx.fillText(testName, 375, 220);

  // Divider
  ctx.strokeStyle = 'rgba(103, 71, 63, 0.2)';
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(150, 270);
  ctx.lineTo(600, 270);
  ctx.stroke();

  // Summary entries
  ctx.textAlign = 'left';
  ctx.font = '600 28px Nunito Sans, sans-serif';
  const entries = Object.entries(summary).filter(([, v]) => v !== null && v !== undefined);
  let y = 340;
  for (const [key, value] of entries.slice(0, 10)) {
    ctx.fillStyle = '#785c55';
    ctx.fillText(key, 100, y);
    ctx.fillStyle = '#3d2a26';
    ctx.font = 'bold 28px Nunito Sans, sans-serif';
    ctx.fillText(String(value), 500, y);
    ctx.font = '600 28px Nunito Sans, sans-serif';
    y += 55;
  }

  // Footer
  ctx.fillStyle = 'rgba(198, 103, 79, 0.15)';
  ctx.fillRect(0, 1180, 750, 154);
  ctx.fillStyle = '#785c55';
  ctx.font = '24px Nunito Sans, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('扫码或搜索 MiMind 开始你的探索', 375, 1240);
  ctx.fillStyle = '#c6674f';
  ctx.font = 'bold 22px Nunito Sans, sans-serif';
  ctx.fillText('非医疗产品 · 心理教练工具', 375, 1290);

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
