import { CheckCircle, Circle, Loader2, XCircle } from 'lucide-react';
import type { ProgressStage } from '@/types/contract';

interface Stage {
  key: ProgressStage;
  label: string;
}

const STAGES: Stage[] = [
  { key: 'extracting', label: 'Extracting document text' },
  { key: 'clauses', label: 'Identifying clauses' },
  { key: 'risks', label: 'Analyzing risks' },
  { key: 'summary', label: 'Generating summary' },
  { key: 'report', label: 'Building final report' },
];

interface StreamingProgressProps {
  currentStage: ProgressStage | null;
  completedStages: ProgressStage[];
  isAnalyzing: boolean;
  error?: string | null;
}

export function StreamingProgress({
  currentStage,
  completedStages,
  isAnalyzing,
  error,
}: StreamingProgressProps) {
  return (
    <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Analysis Progress
      </h2>
      <ol className="space-y-3">
        {STAGES.map((stage) => {
          const isCompleted = completedStages.includes(stage.key);
          const isActive = currentStage === stage.key && !isCompleted;

          return (
            <li key={stage.key} className="flex items-center gap-3">
              {isCompleted ? (
                <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
              ) : isActive ? (
                <Loader2 className="h-5 w-5 text-blue-500 animate-spin flex-shrink-0" />
              ) : (
                <Circle className="h-5 w-5 text-gray-300 flex-shrink-0" />
              )}
              <span
                className={
                  isCompleted
                    ? 'text-sm text-gray-700 font-medium'
                    : isActive
                      ? 'text-sm text-blue-600 font-medium'
                      : 'text-sm text-gray-400'
                }
              >
                {stage.label}
              </span>
            </li>
          );
        })}
      </ol>

      {error && (
        <div className="mt-4 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <XCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {completedStages.includes('complete') && (
        <div className="mt-4 flex items-center gap-2 rounded-lg bg-green-50 p-3 text-sm text-green-700 font-medium">
          <CheckCircle className="h-4 w-4 flex-shrink-0" />
          Analysis complete!
        </div>
      )}

      {isAnalyzing && !completedStages.includes('complete') && (
        <p className="mt-4 text-xs text-gray-400 text-center">
          This may take up to 2 minutes for large contracts.
        </p>
      )}
    </div>
  );
}
