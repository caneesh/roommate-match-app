'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { residentAPI } from '@/lib/api';

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    // Sleep & Noise
    sleep_schedule_weekday: 5,
    sleep_schedule_weekend: 5,
    light_sensitivity: 5,
    noise_tolerance: 5,
    quiet_hours_importance: 5,
    // Cleanliness
    cleanliness_kitchen: 5,
    cleanliness_bathroom: 5,
    cleanliness_common: 5,
    chore_frequency: 3,
    clutter_tolerance: 5,
    // Guests & Social
    guests_overnight_per_week: 1,
    partner_frequency: 5,
    party_frequency: 2,
    social_level_home: 5,
    introvert_extrovert: 5,
    // Environment
    thermostat_preference: 70,
    thermostat_flexibility: 5,
    wfh_frequency: 3,
    shared_space_work_need: 5,
    // Sharing
    food_sharing_comfort: 5,
    toiletries_sharing_comfort: 3,
    borrowing_comfort: 5,
    // Lifestyle
    has_pets: false,
    pet_types: [],
    has_allergies: false,
    allergy_details: [],
    smoking_tolerance: 0,
    vaping_tolerance: 0,
    drug_tolerance: 0,
    alcohol_comfort: 5,
    // Communication
    communication_directness: 5,
    communication_channel: 'text',
    response_time_expectation: 24,
    conflict_style: 'collaborative',
    // Budget
    budget_stress: 5,
    expense_splitting_preference: 'equal',
    // Values
    spirituality_importance: 5,
    political_discussion_comfort: 5,
    sustainability_importance: 5,
    // Open ended
    dealbreakers: [],
    flexible_on: [],
    pet_peeves: '',
    ideal_roommate_description: '',
  });

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await residentAPI.submitQuestionnaire(formData);
      router.push('/resident/dashboard');
    } catch (error) {
      console.error('Failed to submit questionnaire', error);
      alert('Failed to submit questionnaire. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateField = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Complete Your Compatibility Profile
          </h1>
          <p className="text-gray-600 mb-8">
            Step {step} of 5 - Help us find your perfect roommate match
          </p>

          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Sleep & Noise Preferences</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Weekday Sleep Schedule: {formData.sleep_schedule_weekday === 0 ? 'Early Bird' : formData.sleep_schedule_weekday === 10 ? 'Night Owl' : 'Moderate'}
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.sleep_schedule_weekday}
                  onChange={(e) => updateField('sleep_schedule_weekday', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Early (9 PM)</span>
                  <span>Late (2 AM)</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Noise Tolerance: {formData.noise_tolerance}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.noise_tolerance}
                  onChange={(e) => updateField('noise_tolerance', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Very Quiet</span>
                  <span>Tolerates Loud</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Quiet Hours Importance: {formData.quiet_hours_importance}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.quiet_hours_importance}
                  onChange={(e) => updateField('quiet_hours_importance', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Cleanliness Standards</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kitchen Cleanliness: {formData.cleanliness_kitchen}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.cleanliness_kitchen}
                  onChange={(e) => updateField('cleanliness_kitchen', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Relaxed</span>
                  <span>Spotless</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bathroom Cleanliness: {formData.cleanliness_bathroom}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.cleanliness_bathroom}
                  onChange={(e) => updateField('cleanliness_bathroom', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Chore Frequency (times per week): {formData.chore_frequency}
                </label>
                <input
                  type="range"
                  min="0"
                  max="7"
                  value={formData.chore_frequency}
                  onChange={(e) => updateField('chore_frequency', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Guests & Social Life</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Overnight Guests Per Week: {formData.guests_overnight_per_week}
                </label>
                <input
                  type="range"
                  min="0"
                  max="7"
                  value={formData.guests_overnight_per_week}
                  onChange={(e) => updateField('guests_overnight_per_week', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Party Frequency: {formData.party_frequency}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.party_frequency}
                  onChange={(e) => updateField('party_frequency', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Never</span>
                  <span>Weekly</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Introvert/Extrovert: {formData.introvert_extrovert}/10
                </label>
                <input
                  type="range"
                  min="0"
                  max="10"
                  value={formData.introvert_extrovert}
                  onChange={(e) => updateField('introvert_extrovert', parseInt(e.target.value))}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Introvert</span>
                  <span>Extrovert</span>
                </div>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Communication & Lifestyle</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Communication Style
                </label>
                <select
                  value={formData.conflict_style}
                  onChange={(e) => updateField('conflict_style', e.target.value)}
                  className="w-full border border-gray-300 rounded-md py-2 px-3"
                >
                  <option value="collaborative">Collaborative - work together</option>
                  <option value="assertive">Assertive - direct and clear</option>
                  <option value="avoidant">Avoidant - prefer to avoid conflict</option>
                  <option value="compromising">Compromising - meet in the middle</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Preferred Channel
                </label>
                <select
                  value={formData.communication_channel}
                  onChange={(e) => updateField('communication_channel', e.target.value)}
                  className="w-full border border-gray-300 rounded-md py-2 px-3"
                >
                  <option value="text">Text/Messaging</option>
                  <option value="call">Phone Call</option>
                  <option value="in_person">In Person</option>
                  <option value="any">Any</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Thermostat Preference: {formData.thermostat_preference}°F
                </label>
                <input
                  type="range"
                  min="60"
                  max="80"
                  value={formData.thermostat_preference}
                  onChange={(e) => updateField('thermostat_preference', parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.has_pets}
                    onChange={(e) => updateField('has_pets', e.target.checked)}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">I have pets</span>
                </label>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-6">
              <h2 className="text-xl font-semibold">Deal-breakers & Preferences</h2>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  My absolute deal-breakers (select all that apply)
                </label>
                <div className="space-y-2">
                  {['no_pets', 'no_smoking', 'no_overnight_guests', 'no_parties'].map((item) => (
                    <label key={item} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={formData.dealbreakers.includes(item)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            updateField('dealbreakers', [...formData.dealbreakers, item]);
                          } else {
                            updateField('dealbreakers', formData.dealbreakers.filter((d: string) => d !== item));
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm">{item.replace(/_/g, ' ').replace('no ', 'No ')}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What drives you crazy in shared living? (optional)
                </label>
                <textarea
                  value={formData.pet_peeves}
                  onChange={(e) => updateField('pet_peeves', e.target.value)}
                  rows={3}
                  className="w-full border border-gray-300 rounded-md py-2 px-3"
                  placeholder="e.g., Dirty dishes in the sink overnight..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Describe your ideal roommate (optional)
                </label>
                <textarea
                  value={formData.ideal_roommate_description}
                  onChange={(e) => updateField('ideal_roommate_description', e.target.value)}
                  rows={3}
                  className="w-full border border-gray-300 rounded-md py-2 px-3"
                  placeholder="e.g., Someone who is respectful, clean, and friendly..."
                />
              </div>
            </div>
          )}

          <div className="mt-8 flex justify-between">
            <button
              onClick={() => setStep(Math.max(1, step - 1))}
              disabled={step === 1}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Previous
            </button>

            {step < 5 ? (
              <button
                onClick={() => setStep(step + 1)}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Next
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Complete Profile'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
