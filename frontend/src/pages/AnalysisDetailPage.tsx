import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, AlertCircle, Loader2 } from 'lucide-react';
import { getContractAnalysis, getContract } from '@/services/api';
import { AnalysisReportView } from '@/components/AnalysisReport/AnalysisReportView';

export function AnalysisDetailPage() {
  const { contractId } = useParams<{ contractId: string }>();
  const navigate = useNavigate();

  const { data: contract, isLoading: contractLoading } = useQuery({
    queryKey: ['contracts', contractId],
    queryFn: () => getContract(contractId!),
    enabled: !!contractId,
  });

  const {
    data: report,
    isLoading: reportLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ['contracts', contractId, 'analysis'],
    queryFn: () => getContractAnalysis(contractId!),
    enabled: !!contractId,
  });

  const isLoading = contractLoading || reportLoading;

  return (
    <div className="mx-auto max-w-4xl py-10 px-4">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <button
          onClick={() => navigate('/history')}
          className="flex items-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            {contract?.file_name ?? 'Contract Analysis'}
          </h1>
          {contract && (
            <p className="text-xs text-gray-400">
              Uploaded {new Date(contract.upload_date).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      {/* Loading */}
      {isLoading && (
        <div className="flex items-center justify-center py-24 gap-3 text-gray-400">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span className="text-sm">Loading analysis...</span>
        </div>
      )}

      {/* Error */}
      {isError && (
        <div className="rounded-xl bg-red-50 p-5 flex items-start gap-3 text-red-700">
          <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-sm">Failed to load analysis report</p>
            <p className="text-xs mt-0.5 text-red-500">
              {(error as { response?: { data?: { detail?: { message?: string } } } })?.response?.data?.detail?.message ??
                'The analysis may not have been run yet.'}
            </p>
          </div>
        </div>
      )}

      {/* Report */}
      {!isLoading && !isError && report && <AnalysisReportView report={report} />}
    </div>
  );
}
