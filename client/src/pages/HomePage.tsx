import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-xl font-bold text-gray-900">
                BookRec
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/auth/login"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Register
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Discover Your Next Favorite Book
          </h1>

          <p className="text-lg text-gray-600 mb-8">
            Sign in to get personalized recommendations tailored to your reading taste.
          </p>

          <div className="flex justify-center space-x-4">
            <Link
              to="/auth/login"
              className="px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-6 py-3 border border-gray-300 rounded-md shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Register
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}