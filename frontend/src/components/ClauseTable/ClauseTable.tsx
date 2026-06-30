import { CheckCircle, XCircle } from 'lucide-react';
import type { Clause } from '@/types/contract';

const ALL_CLAUSE_TYPES = [
  'termination',
  'liability',
  'confidentiality',
  'indemnification',
  'payment_terms',
  'renewal',
  'governing_law',
  'intellectual_property',
  'non_compete',
  'force_majeure',
];

const CLAUSE_LABELS: Record<string, string> = {
  termination: 'Termination',
  liability: 'Liability',
  confidentiality: 'Confidentiality',
  indemnification: 'Indemnification',
  payment_terms: 'Payment Terms',
  renewal: 'Renewal',
  governing_law: 'Governing Law',
  intellectual_property: 'Intellectual Property',
  non_compete: 'Non-Compete',
  force_majeure: 'Force Majeure',
};

interface ClauseTableProps {
  clauses: Clause[];
}

export function ClauseTable({ clauses }: ClauseTableProps) {
  const clauseMap = new Map(clauses.map((c) => [c.clause_type, c]));

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 w-8">
              #
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              Clause Type
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 w-24">
              Status
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              Excerpt
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {ALL_CLAUSE_TYPES.map((type, idx) => {
            const clause = clauseMap.get(type);
            return (
              <tr key={type} className={clause ? '' : 'bg-gray-50/50'}>
                <td className="px-4 py-3 text-sm text-gray-400">{idx + 1}</td>
                <td className="px-4 py-3 text-sm font-medium text-gray-800">
                  {CLAUSE_LABELS[type] ?? type}
                </td>
                <td className="px-4 py-3">
                  {clause ? (
                    <span className="flex items-center gap-1 text-xs font-medium text-green-700">
                      <CheckCircle className="h-3.5 w-3.5" /> Found
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-xs font-medium text-gray-400">
                      <XCircle className="h-3.5 w-3.5" /> Not found
                    </span>
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 max-w-sm">
                  {clause ? (
                    <span className="line-clamp-2">{clause.clause_text}</span>
                  ) : (
                    <span className="italic text-gray-300">—</span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
