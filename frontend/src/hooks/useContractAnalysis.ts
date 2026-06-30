import { useState, useCallback, useRef } from 'react';
import { analyzeContractStream, uploadContract } from '@/services/api';
import type { AnalysisReport, ProgressEvent, ProgressStage } from '@/types/contract';

interface AnalysisState {
  contractId: string | null;
  isUploading: boolean;
  isAnalyzing: boolean;
  currentStage: ProgressStage | null;
  stageMessages: Record<string, string>;
  completedStages: ProgressStage[];
  report: AnalysisReport | null;
  error: string | null;
}

const INITIAL_STATE: AnalysisState = {
  contractId: null,
  isUploading: false,
  isAnalyzing: false,
  currentStage: null,
  stageMessages: {},
  completedStages: [],
  report: null,
  error: null,
};

export function useContractAnalysis() {
  const [state, setState] = useState<AnalysisState>(INITIAL_STATE);
  const fileRef = useRef<File | null>(null);

  const startAnalysis = useCallback(async (file: File) => {
    fileRef.current = file;
    setState({ ...INITIAL_STATE, isUploading: true });

    try {
      // Step 1: Upload
      const uploadResponse = await uploadContract(file);
      const contractId = uploadResponse.contract_id;

      setState((prev) => ({
        ...prev,
        contractId,
        isUploading: false,
        isAnalyzing: true,
        currentStage: 'extracting',
      }));

      // Step 2: Stream analysis
      for await (const rawEvent of analyzeContractStream(contractId, file)) {
        let event: ProgressEvent;
        try {
          event = JSON.parse(rawEvent) as ProgressEvent;
        } catch {
          continue;
        }

        if (event.stage === 'complete' && event.report) {
          setState((prev) => ({
            ...prev,
            isAnalyzing: false,
            currentStage: 'complete',
            completedStages: [...prev.completedStages, 'complete'],
            report: event.report!,
          }));
          break;
        }

        if (event.stage === 'error') {
          setState((prev) => ({
            ...prev,
            isAnalyzing: false,
            error: event.message,
          }));
          break;
        }

        setState((prev) => ({
          ...prev,
          currentStage: event.stage,
          stageMessages: { ...prev.stageMessages, [event.stage]: event.message },
          completedStages: prev.completedStages.includes(event.stage)
            ? prev.completedStages
            : [...prev.completedStages, event.stage],
        }));
      }
    } catch (err) {
      setState((prev) => ({
        ...prev,
        isUploading: false,
        isAnalyzing: false,
        error: err instanceof Error ? err.message : 'Analysis failed.',
      }));
    }
  }, []);

  const reset = useCallback(() => {
    setState(INITIAL_STATE);
    fileRef.current = null;
  }, []);

  return { ...state, startAnalysis, reset };
}
