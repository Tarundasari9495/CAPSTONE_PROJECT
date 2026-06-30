import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface ContractUploadProps {
  onFileSelected: (file: File) => void;
  isLoading?: boolean;
  error?: string | null;
}

const MAX_SIZE_BYTES = 20 * 1024 * 1024; // 20 MB

export function ContractUpload({ onFileSelected, isLoading, error }: ContractUploadProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onFileSelected(accepted[0]);
    },
    [onFileSelected],
  );

  const { getRootProps, getInputProps, isDragActive, fileRejections, acceptedFiles } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: MAX_SIZE_BYTES,
    maxFiles: 1,
    disabled: isLoading,
  });

  const rejectionMessage =
    fileRejections[0]?.errors[0]?.code === 'file-too-large'
      ? `File exceeds maximum size of 20 MB.`
      : fileRejections[0]?.errors[0]?.code === 'file-invalid-type'
        ? 'Only PDF and DOCX files are accepted.'
        : null;

  const selectedFile = acceptedFiles[0];

  return (
    <div className="w-full max-w-xl">
      <div
        {...getRootProps()}
        className={clsx(
          'flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 transition-colors cursor-pointer',
          isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:bg-gray-100',
          isLoading && 'opacity-50 cursor-not-allowed',
        )}
      >
        <input {...getInputProps()} />
        <Upload className="h-10 w-10 text-gray-400 mb-3" />
        {selectedFile ? (
          <div className="flex items-center gap-2 text-sm text-gray-700">
            <FileText className="h-4 w-4 text-blue-500" />
            <span className="font-medium">{selectedFile.name}</span>
            <span className="text-gray-400">({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)</span>
          </div>
        ) : (
          <>
            <p className="text-sm font-medium text-gray-700">
              {isDragActive ? 'Drop your contract here' : 'Drag & drop or click to upload'}
            </p>
            <p className="mt-1 text-xs text-gray-400">PDF or DOCX — max 20 MB</p>
          </>
        )}
      </div>

      {(rejectionMessage || error) && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span>{rejectionMessage ?? error}</span>
        </div>
      )}
    </div>
  );
}
