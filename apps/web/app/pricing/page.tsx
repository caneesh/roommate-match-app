import Link from 'next/link';

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link href="/" className="text-2xl font-bold text-primary-600">
              Lease Peace
            </Link>
            <Link href="/auth/login" className="text-gray-700 hover:text-primary-600">
              Login
            </Link>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900">Simple, Transparent Pricing</h1>
          <p className="mt-4 text-xl text-gray-600">Choose the plan that works for you</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Resident Pricing */}
          <div className="bg-white rounded-lg shadow-lg p-8 border-2 border-primary-600">
            <h2 className="text-2xl font-bold text-gray-900">Residents</h2>
            <div className="mt-4">
              <span className="text-5xl font-bold text-primary-600">$99</span>
              <span className="text-gray-600 ml-2">per match cycle</span>
            </div>
            <ul className="mt-8 space-y-4">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Complete compatibility assessment</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Conflict risk prediction</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Personalized mitigation tips</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Recommended house rules</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Match with multiple candidates</span>
              </li>
            </ul>
            <Link
              href="/auth/signup"
              className="mt-8 block w-full bg-primary-600 text-white text-center py-3 rounded-md font-medium hover:bg-primary-700"
            >
              Get Started
            </Link>
          </div>

          {/* Operator Pricing */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-bold text-gray-900">Operators</h2>
            <div className="mt-4">
              <span className="text-5xl font-bold text-gray-900">Custom</span>
            </div>
            <p className="mt-2 text-gray-600">$500 - $2,000+ annually</p>
            <ul className="mt-8 space-y-4">
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Unlimited property management</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Applicant intake & tracking</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Vacancy matching tools</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Dashboard & analytics</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Match reports & exports</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-500 mr-2">✓</span>
                <span>Dedicated support</span>
              </li>
            </ul>
            <Link
              href="/operator/request-pilot"
              className="mt-8 block w-full bg-gray-900 text-white text-center py-3 rounded-md font-medium hover:bg-gray-800"
            >
              Request Pilot
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
