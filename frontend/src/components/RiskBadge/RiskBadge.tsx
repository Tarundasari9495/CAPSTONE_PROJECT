import type { RiskLevel } from '@/types/contract';
import { clsx } from 'clsx';

interface RiskBadgeProps {
  level: RiskLevel;
  size?: 'sm' | 'md';
}

const LEVEL_CONFIG: Record<RiskLevel, { label: string; className: string }> = {
  high: {
    label: 'High',
    className: 'bg-red-100 text-red-800 border-red-200',
  },
  medium: {
    label: 'Medium',
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  },
  low: {
    label: 'Low',
    className: 'bg-green-100 text-green-800 border-green-200',
  },
};

export function RiskBadge({ level, size = 'md' }: RiskBadgeProps) {
  const config = LEVEL_CONFIG[level] ?? LEVEL_CONFIG.low;
  return (
    <span
      className={clsx(
        'inline-flex items-center rounded-full border font-medium',
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm',
        config.className,
      )}
    >
      {config.label}
    </span>
  );
}
