import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileCheck } from 'lucide-react';
import { ContractUpload } from '@/components/ContractUpload/ContractUpload';
import { StreamingProgress } from '@/components/StreamingProgress/StreamingProgress';
import { useContractAnalysis } from '@/hooks/useContractAnalysis';

export function UploadPage() {
  const navigate = useNavigate();
  const {
    contractId,
    isUploading,
    isAnalyzing,
    currentStage,
    completedStages,
    report,
    error,
    startAnalysis,
    reset,
  } = useContractAnalysis();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelected = useCallback((file: File) => {
    setSelectedFile(file);
    reset();
  }, [reset]);

  const handleAnalyze = useCallback(() => {
    if (selectedFile) {
      startAnalysis(selectedFile);
    }
  }, [selectedFile, startAnalysis]);

  // Navigate to result once complete
  if (report && contractId) {
    return (
      <div className="flex flex-col items-center gap-6 py-12">
        <FileCheck className="h-16 w-16 text-green-500" />
        <h2 className="text-xl font-semibold text-gray-800">Analysis Complete!</h2>
        <button
          onClick={() => navigate(`/contracts/${contractId}`)}
          className="rounded-lg bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
        >
          View Analysis Report
        </button>
      </div>
    );
  }

  const isInProgress = isUploading || isAnalyzing;

  return (
    <div className="mx-auto max-w-2xl py-12 px-4">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900">Contract Analysis</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload a PDF or DOCX contract to begin AI-powered analysis
        </p>
      </div>

      <div className="flex flex-col items-center gap-6">
        <ContractUpload
          onFileSelected={handleFileSelected}
          isLoading={isInProgress}
          error={error}
        />

        {selectedFile && !isInProgress && !report && (
          <button
            onClick={handleAnalyze}
            className="w-full max-w-xl rounded-lg bg-blue-600 py-3 text-sm font-medium text-white hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            Analyze Contract
          </button>
        )}

        {isInProgress && (
          <StreamingProgress
            currentStage={currentStage}
            completedStages={completedStages}
            isAnalyzing={isAnalyzing}
            error={error}
          />
        )}
      </div>
    </div>
  );
}
