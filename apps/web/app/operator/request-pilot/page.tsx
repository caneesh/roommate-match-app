'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { publicAPI } from '@/lib/api';

export default function RequestPilotPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    org_name: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    property_count: '',
    unit_count: '',
    message: '',
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await publicAPI.submitLead({
        ...formData,
        property_count: formData.property_count ? parseInt(formData.property_count) : null,
        unit_count: formData.unit_count ? parseInt(formData.unit_count) : null,
      });
      setSubmitted(true);
    } catch (error) {
      alert('Failed to submit request. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Thank you for your interest!
          </h2>
          <p className="text-gray-600 mb-6">
            We'll review your request and get back to you within 2 business days.
          </p>
          <Link href="/" className="text-primary-600 hover:underline">
            Return to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4">
        <div className="text-center mb-8">
          <Link href="/" className="text-2xl font-bold text-primary-600">
            Lease Peace
          </Link>
          <h1 className="mt-6 text-3xl font-bold text-gray-900">
            Request Pilot Program Access
          </h1>
          <p className="mt-2 text-gray-600">
            Join our pilot program and help us reduce conflicts in co-living spaces
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Organization Name *
              </label>
              <input
                type="text"
                required
                value={formData.org_name}
                onChange={(e) => setFormData({ ...formData, org_name: e.target.value })}
                className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact Name *
              </label>
              <input
                type="text"
                required
                value={formData.contact_name}
                onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
                className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contact Email *
              </label>
              <input
                type="email"
                required
                value={formData.contact_email}
                onChange={(e) => setFormData({ ...formData, contact_email: e.target.value })}
                className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.contact_phone}
                onChange={(e) => setFormData({ ...formData, contact_phone: e.target.value })}
                className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Number of Properties
                </label>
                <input
                  type="number"
                  value={formData.property_count}
                  onChange={(e) => setFormData({ ...formData, property_count: e.target.value })}
                  className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Total Units
                </label>
                <input
                  type="number"
                  value={formData.unit_count}
                  onChange={(e) => setFormData({ ...formData, unit_count: e.target.value })}
                  className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tell us about your needs
              </label>
              <textarea
                rows={4}
                value={formData.message}
                onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500"
                placeholder="What challenges are you facing with roommate conflicts?"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-3 rounded-md font-medium hover:bg-primary-700 disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit Request'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
