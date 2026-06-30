import { useQuery } from '@tanstack/react-query';
import { Plus, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getContractHistory } from '@/services/api';
import { ContractHistoryTable } from '@/components/ContractHistory/ContractHistoryTable';

export function HistoryPage() {
  const navigate = useNavigate();

  const { data: contracts = [], isLoading, isError, refetch } = useQuery({
    queryKey: ['contracts', 'history'],
    queryFn: getContractHistory,
    refetchInterval: 10_000, // refresh every 10 seconds for in-progress items
  });

  return (
    <div className="mx-auto max-w-4xl py-10 px-4">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Contract History</h1>
          <p className="mt-0.5 text-sm text-gray-500">{contracts.length} contract(s) analyzed</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Refresh
          </button>
          <button
            onClick={() => navigate('/upload')}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            New Analysis
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-14 animate-pulse rounded-lg bg-gray-100" />
          ))}
        </div>
      )}

      {isError && (
        <div className="rounded-xl bg-red-50 p-4 text-sm text-red-700">
          Failed to load contract history. Please try refreshing.
        </div>
      )}

      {!isLoading && !isError && <ContractHistoryTable contracts={contracts} />}
    </div>
  );
}
