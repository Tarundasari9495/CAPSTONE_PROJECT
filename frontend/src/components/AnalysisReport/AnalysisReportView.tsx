import type { AnalysisReport } from '@/types/contract';
import { ClauseTable } from '@/components/ClauseTable/ClauseTable';
import { RiskBadge } from '@/components/RiskBadge/RiskBadge';

interface AnalysisReportViewProps {
  report: AnalysisReport;
}

function RiskScoreMeter({ score }: { score: number }) {
  const color =
    score >= 70 ? 'bg-red-500' : score >= 40 ? 'bg-yellow-500' : 'bg-green-500';
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 h-3 rounded-full bg-gray-200 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all ${color}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span
        className={`text-lg font-bold ${score >= 70 ? 'text-red-600' : score >= 40 ? 'text-yellow-600' : 'text-green-600'}`}
      >
        {score}/100
      </span>
    </div>
  );
}

export function AnalysisReportView({ report }: AnalysisReportViewProps) {
  const info = report.contract_info;
  const summary = report.summary;

  return (
    <div className="space-y-8">
      {/* Risk Score */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-800 mb-3">Overall Risk Score</h2>
        <RiskScoreMeter score={report.risk_score ?? 0} />
      </section>

      {/* Contract Information */}
      {info && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-4">Contract Information</h2>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
            {info.title && (
              <div>
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide">Title</dt>
                <dd className="mt-0.5 text-sm text-gray-800">{info.title}</dd>
              </div>
            )}
            {info.effective_date && (
              <div>
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide">Effective Date</dt>
                <dd className="mt-0.5 text-sm text-gray-800">{info.effective_date}</dd>
              </div>
            )}
            {info.expiration_date && (
              <div>
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide">Expiration Date</dt>
                <dd className="mt-0.5 text-sm text-gray-800">{info.expiration_date}</dd>
              </div>
            )}
            {info.contract_value && (
              <div>
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide">Contract Value</dt>
                <dd className="mt-0.5 text-sm font-medium text-gray-800">{info.contract_value}</dd>
              </div>
            )}
            {info.renewal_terms && (
              <div className="sm:col-span-2">
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide">Renewal Terms</dt>
                <dd className="mt-0.5 text-sm text-gray-800">{info.renewal_terms}</dd>
              </div>
            )}
            {info.parties && info.parties.length > 0 && (
              <div className="sm:col-span-2">
                <dt className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">Parties</dt>
                <dd className="flex flex-wrap gap-2">
                  {info.parties.map((p, i) => (
                    <span
                      key={i}
                      className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-3 py-1 text-xs text-blue-800"
                    >
                      <strong>{p.name}</strong> · {p.role}
                    </span>
                  ))}
                </dd>
              </div>
            )}
          </dl>
        </section>
      )}

      {/* Executive Summary */}
      {summary?.executive_summary && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Executive Summary</h2>
          <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
            {summary.executive_summary}
          </p>
        </section>
      )}

      {/* Key Terms */}
      {summary?.key_terms && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Key Terms</h2>
          <p className="text-sm text-gray-700 leading-relaxed">{summary.key_terms}</p>
        </section>
      )}

      {/* Obligations & Dates */}
      {(summary?.important_obligations?.length || summary?.important_dates?.length) && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="grid sm:grid-cols-2 gap-6">
            {summary.important_obligations && summary.important_obligations.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Important Obligations</h3>
                <ul className="space-y-1">
                  {summary.important_obligations.map((o, i) => (
                    <li key={i} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-blue-400 mt-0.5">•</span> {o}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {summary.important_dates && summary.important_dates.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Important Dates</h3>
                <ul className="space-y-1">
                  {summary.important_dates.map((d, i) => (
                    <li key={i} className="text-sm text-gray-600 flex gap-2">
                      <span className="text-blue-400 mt-0.5">•</span> {d}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Clauses */}
      <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-800 mb-4">
          Identified Clauses ({report.clauses.length} / 10)
        </h2>
        <ClauseTable clauses={report.clauses} />
      </section>

      {/* Risks */}
      {report.risks.length > 0 && (
        <section className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-800 mb-4">
            Risk Analysis ({report.risks.length} items)
          </h2>
          <div className="space-y-3">
            {report.risks.map((risk) => (
              <div
                key={risk.id}
                className="flex items-start gap-3 rounded-lg border border-gray-100 p-3"
              >
                <RiskBadge level={risk.risk_level} size="sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-700">{risk.risk_description}</p>
                  {risk.clause_type && (
                    <p className="mt-0.5 text-xs text-gray-400">Clause: {risk.clause_type}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
