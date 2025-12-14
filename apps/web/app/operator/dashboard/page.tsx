'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { operatorAPI } from '@/lib/api';

export default function OperatorDashboard() {
  const [dashboard, setDashboard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await operatorAPI.getDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error('Failed to load dashboard', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-primary-600">Lease Peace Operator</h1>
            <div className="flex gap-4">
              <Link href="/operator/dashboard" className="text-gray-700 hover:text-primary-600">
                Dashboard
              </Link>
              <Link href="/operator/properties" className="text-gray-700 hover:text-primary-600">
                Properties
              </Link>
              <Link href="/operator/applicants" className="text-gray-700 hover:text-primary-600">
                Applicants
              </Link>
              <Link href="/operator/matching" className="text-gray-700 hover:text-primary-600">
                Matching
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8">
          {dashboard?.org_name || 'Dashboard'}
        </h2>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-gray-500">Loading dashboard...</div>
          </div>
        ) : (
          <>
            <div className="grid md:grid-cols-4 gap-6 mb-12">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl font-bold text-primary-600">
                  {dashboard.properties_count}
                </div>
                <div className="text-gray-600 mt-2">Properties</div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl font-bold text-blue-600">
                  {dashboard.applicants_count}
                </div>
                <div className="text-gray-600 mt-2">Pending Applicants</div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl font-bold text-green-600">
                  {dashboard.move_ins_count}
                </div>
                <div className="text-gray-600 mt-2">Current Residents</div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-3xl font-bold text-red-600">
                  {dashboard.conflicts_count}
                </div>
                <div className="text-gray-600 mt-2">Active Conflicts</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <Link
                    href="/operator/properties/new"
                    className="block w-full bg-primary-600 text-white text-center py-2 rounded-md hover:bg-primary-700"
                  >
                    Add Property
                  </Link>
                  <Link
                    href="/operator/matching"
                    className="block w-full bg-blue-600 text-white text-center py-2 rounded-md hover:bg-blue-700"
                  >
                    Run Matching
                  </Link>
                  <Link
                    href="/operator/conflicts/new"
                    className="block w-full bg-gray-600 text-white text-center py-2 rounded-md hover:bg-gray-700"
                  >
                    Report Conflict
                  </Link>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h3>
                <div className="text-gray-600">
                  <p className="mb-2">Match runs: {dashboard.recent_match_runs}</p>
                  <p className="text-sm text-gray-500">
                    View detailed reports in the Matching section
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
