'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { residentAPI } from '@/lib/api';
import { getRiskColor, getScoreColor } from '@/lib/utils';

export default function ResidentDashboard() {
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const response = await residentAPI.getMatches();
      setMatches(response.data);
    } catch (error) {
      console.error('Failed to load matches', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-primary-600">Lease Peace</h1>
            <div className="flex gap-4">
              <Link href="/resident/dashboard" className="text-gray-700 hover:text-primary-600">
                Matches
              </Link>
              <Link href="/resident/settings" className="text-gray-700 hover:text-primary-600">
                Settings
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Your Roommate Matches</h2>
          <p className="mt-2 text-gray-600">
            Based on your compatibility profile, here are your best matches
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-500">Loading matches...</div>
          </div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <div className="text-gray-500 mb-4">No matches yet</div>
            <p className="text-gray-600 mb-6">
              You'll see matches here once an operator runs matching for a property you've applied to.
            </p>
          </div>
        ) : (
          <div className="grid gap-6">
            {matches.map((match) => (
              <div key={match.id} className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {match.other_resident.name}
                    </h3>
                    {match.other_resident.bio && (
                      <p className="text-gray-600 mt-1">{match.other_resident.bio}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className={`text-3xl font-bold ${getScoreColor(match.compatibility_score)}`}>
                      {Math.round(match.compatibility_score)}
                    </div>
                    <div className="text-sm text-gray-500">Compatibility</div>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6 mt-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Top Alignments</h4>
                    <ul className="space-y-1">
                      {match.top_alignments.map((alignment: string, idx: number) => (
                        <li key={idx} className="text-sm text-green-700 flex items-start">
                          <span className="mr-2">✓</span>
                          <span>{alignment}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Potential Challenges</h4>
                    <ul className="space-y-1">
                      {match.top_mismatches.map((mismatch: string, idx: number) => (
                        <li key={idx} className="text-sm text-yellow-700 flex items-start">
                          <span className="mr-2">⚠</span>
                          <span>{mismatch}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="mt-6">
                  <div className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(match.risk_level)}`}>
                    {match.risk_level.toUpperCase()} RISK
                  </div>
                </div>

                <details className="mt-6">
                  <summary className="cursor-pointer text-primary-600 font-medium">
                    View Mitigation Tips & House Rules
                  </summary>
                  <div className="mt-4 space-y-4">
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-2">Mitigation Tips</h5>
                      <ul className="space-y-1">
                        {match.mitigation_tips.map((tip: string, idx: number) => (
                          <li key={idx} className="text-sm text-gray-700">• {tip}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-semibold text-gray-900 mb-2">Recommended House Rules</h5>
                      <ul className="space-y-1">
                        {match.recommended_house_rules.map((rule: string, idx: number) => (
                          <li key={idx} className="text-sm text-gray-700">• {rule}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </details>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
