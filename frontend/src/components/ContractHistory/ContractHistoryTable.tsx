import { useNavigate } from 'react-router-dom';
import { Trash2, ChevronRight, FileText, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import type { ContractHistoryItem, ContractStatus } from '@/types/contract';
import { deleteContract } from '@/services/api';
import { RiskBadge } from '@/components/RiskBadge/RiskBadge';

interface ContractHistoryTableProps {
  contracts: ContractHistoryItem[];
}

function StatusIcon({ status }: { status: ContractStatus }) {
  switch (status) {
    case 'completed':
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    case 'failed':
      return <XCircle className="h-4 w-4 text-red-500" />;
    case 'processing':
      return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
    default:
      return <Clock className="h-4 w-4 text-gray-400" />;
  }
}

export function ContractHistoryTable({ contracts }: ContractHistoryTableProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: deleteContract,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['contracts', 'history'] });
    },
  });

  if (contracts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 py-16 text-gray-400">
        <FileText className="h-10 w-10 mb-3" />
        <p className="text-sm">No contracts analyzed yet.</p>
        <p className="text-xs mt-1">Upload a contract to get started.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              File
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              Date
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              Status
            </th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              Risk
            </th>
            <th className="px-4 py-3 w-16" />
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {contracts.map((contract) => (
            <tr
              key={contract.id}
              className="hover:bg-gray-50 cursor-pointer"
              onClick={() => navigate(`/contracts/${contract.id}`)}
            >
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <span className="text-sm font-medium text-gray-800 truncate max-w-[200px]">
                    {contract.file_name}
                  </span>
                </div>
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">
                {new Date(contract.upload_date).toLocaleDateString()}
              </td>
              <td className="px-4 py-3">
                <span className="flex items-center gap-1.5 text-sm text-gray-600 capitalize">
                  <StatusIcon status={contract.status} />
                  {contract.status}
                </span>
              </td>
              <td className="px-4 py-3">
                {contract.risk_score != null ? (
                  <RiskBadge
                    level={
                      contract.risk_score >= 70
                        ? 'high'
                        : contract.risk_score >= 40
                          ? 'medium'
                          : 'low'
                    }
                    size="sm"
                  />
                ) : (
                  <span className="text-xs text-gray-400">—</span>
                )}
              </td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-1 justify-end" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteMutation.mutate(contract.id);
                    }}
                    disabled={deleteMutation.isPending}
                    className="rounded p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                    title="Delete contract"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                  <ChevronRight className="h-4 w-4 text-gray-300" />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
