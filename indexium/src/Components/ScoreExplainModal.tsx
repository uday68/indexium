import type { FC } from "react";
import type { ScoreExplanation } from "./hooks/useSearch";
import { Button } from "./ui/button";

interface Props {
  explanation: ScoreExplanation | null;
  onClose: () => void;
}

export const ScoreExplainModal: FC<Props> = ({ explanation, onClose }) => {
  if (!explanation) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-2xl max-w-lg w-full p-6 text-zinc-900 dark:text-zinc-100">
        <div className="flex justify-between items-center border-b border-zinc-200 dark:border-zinc-800 pb-3 mb-4">
          <h3 className="font-semibold text-lg">
            Ranking Breakdown &mdash; Document #{explanation.doc_id}
          </h3>
          <button
            onClick={onClose}
            className="text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 text-lg font-bold"
          >
            &times;
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between text-sm bg-zinc-100 dark:bg-zinc-800 p-3 rounded-lg">
            <span className="text-zinc-600 dark:text-zinc-400">Ranker Algorithm:</span>
            <span className="font-semibold uppercase tracking-wider">{explanation.ranker_name}</span>
          </div>

          <div className="flex justify-between text-sm bg-blue-50 dark:bg-blue-950/40 p-3 rounded-lg border border-blue-200 dark:border-blue-900">
            <span className="text-blue-700 dark:text-blue-300 font-medium">Final Computed Score:</span>
            <span className="font-bold text-blue-600 dark:text-blue-400 text-base">
              {explanation.final_score.toFixed(4)}
            </span>
          </div>

          {explanation.term_scores && explanation.term_scores.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                Term Contributions
              </h4>
              <div className="overflow-x-auto border border-zinc-200 dark:border-zinc-800 rounded-lg">
                <table className="w-full text-xs text-left">
                  <thead className="bg-zinc-50 dark:bg-zinc-800 border-b border-zinc-200 dark:border-zinc-800">
                    <tr>
                      <th className="p-2 font-medium">Term</th>
                      <th className="p-2 font-medium">TF</th>
                      <th className="p-2 font-medium">IDF</th>
                      <th className="p-2 font-medium">Contribution</th>
                    </tr>
                  </thead>
                  <tbody>
                    {explanation.term_scores.map((ts, idx) => (
                      <tr key={idx} className="border-b border-zinc-100 dark:border-zinc-800/50">
                        <td className="p-2 font-mono font-medium text-blue-600 dark:text-blue-400">
                          {ts.term}
                        </td>
                        <td className="p-2">{ts.tf}</td>
                        <td className="p-2">{ts.idf.toFixed(3)}</td>
                        <td className="p-2 font-bold">{ts.contribution.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {explanation.additional_factors && Object.keys(explanation.additional_factors).length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                Hyperparameters & Metadata Factors
              </h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {Object.entries(explanation.additional_factors).map(([k, v]) => (
                  <div
                    key={k}
                    className="flex justify-between bg-zinc-50 dark:bg-zinc-800/60 p-2 rounded border border-zinc-100 dark:border-zinc-800"
                  >
                    <span className="text-zinc-500 font-mono">{k}</span>
                    <span className="font-semibold">{v}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {explanation.details && (
            <p className="text-xs text-zinc-500 italic bg-zinc-50 dark:bg-zinc-800/40 p-2 rounded">
              {explanation.details}
            </p>
          )}
        </div>

        <div className="mt-6 flex justify-end">
          <Button onClick={onClose} className="bg-zinc-800 hover:bg-zinc-900 text-white">
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
