import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-2xl font-bold text-primary-600">Lease Peace</h1>
            </div>
            <div className="flex gap-4">
              <Link href="/pricing" className="text-gray-700 hover:text-primary-600">
                Pricing
              </Link>
              <Link href="/auth/login" className="text-gray-700 hover:text-primary-600">
                Login
              </Link>
              <Link href="/auth/signup" className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700">
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 sm:text-6xl">
            Find Your Perfect
            <span className="text-primary-600"> Roommate Match</span>
          </h1>
          <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
            Predict roommate conflicts before move-in using deep compatibility analysis.
            Reduce turnover, increase renewals, and create harmonious living spaces.
          </p>
          <div className="mt-10 flex gap-4 justify-center">
            <Link
              href="/auth/signup"
              className="bg-primary-600 text-white px-8 py-3 rounded-md text-lg font-medium hover:bg-primary-700"
            >
              Get Started - $99
            </Link>
            <Link
              href="/operator/request-pilot"
              className="bg-white text-primary-600 px-8 py-3 rounded-md text-lg font-medium border-2 border-primary-600 hover:bg-primary-50"
            >
              Operator Pilot Program
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="mt-24 grid md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">🎯</div>
            <h3 className="text-xl font-bold mb-2">Deep Compatibility</h3>
            <p className="text-gray-600">
              Match on 25+ dimensions including sleep, cleanliness, guests, communication style, and more.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">⚠️</div>
            <h3 className="text-xl font-bold mb-2">Conflict Prediction</h3>
            <p className="text-gray-600">
              AI-powered risk assessment identifies potential friction points before they become problems.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl mb-4">🏠</div>
            <h3 className="text-xl font-bold mb-2">Actionable Insights</h3>
            <p className="text-gray-600">
              Get personalized mitigation tips and recommended house rules for every match.
            </p>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-24 bg-white rounded-lg shadow-lg p-12">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-primary-600">85%</div>
              <div className="text-gray-600 mt-2">Conflict Reduction</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600">40%</div>
              <div className="text-gray-600 mt-2">Higher Renewals</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-primary-600">$99</div>
              <div className="text-gray-600 mt-2">Per Match Cycle</div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center text-gray-500">
            <p>&copy; 2024 Lease Peace. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
