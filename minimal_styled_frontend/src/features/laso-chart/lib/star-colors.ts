import type { Star } from '@/lib/api/schemas';

export function isCat(star: Star) {
  return star.sao_type?.includes('Cát') ?? true;
}

export function isHung(star: Star) {
  return star.sao_type?.includes('Hung') ?? false;
}

const STAR_COLOR_MAP: Record<string, string> = {
  'tử vi': 'var(--element-tho)',
  'thiên phủ': 'var(--element-tho)',
  'thái dương': 'var(--element-hoa)',
  'vũ khúc': 'var(--element-kim)',
  'liêm trinh': 'var(--element-hoa)',
  'thất sát': 'var(--element-kim)',
  'tham lang': 'var(--element-thuy)',
  'phá quân': 'var(--element-thuy)',
  'thiên đồng': 'var(--element-thuy)',
  'thiên cơ': 'var(--element-moc)',
  'thái âm': 'var(--element-thuy)',
  'thiên lương': 'var(--element-moc)',
  'cự môn': 'var(--element-thuy)',
  'thiên tướng': 'var(--element-thuy)',
};

export function getStarColorVar(starWithStatus: string): string {
  const baseName = starWithStatus.split(' (')[0]?.toLowerCase() ?? '';
  return STAR_COLOR_MAP[baseName] ?? 'var(--element-default)';
}

const ELEMENT_COLOR_MAP: Record<string, string> = {
  kim: 'var(--element-kim)',
  mộc: 'var(--element-moc)',
  thủy: 'var(--element-thuy)',
  hỏa: 'var(--element-hoa)',
  thổ: 'var(--element-tho)',
};

export function getElementColorVar(element: string): string {
  return ELEMENT_COLOR_MAP[element.toLowerCase()] ?? 'var(--element-default)';
}
