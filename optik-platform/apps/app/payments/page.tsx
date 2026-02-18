'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface Plan {
  id: string;
  name: string;
  price: number;
  currency: string;
  features: string[];
}

export default function PaymentsPage() {
  const showTestData =
    process.env.NODE_ENV !== 'production' &&
    process.env.NEXT_PUBLIC_SHOW_TEST_PAYMENTS === 'true';
  const [plans, setPlans] = useState<Record<string, Plan>>({});
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const data = await api<{ plans: Record<string, Plan> }>('/api/v1/payments/plans');
      setPlans(data.plans || {});
    } catch (error) {
      console.error('Error fetching plans:', error);
      setError('Failed to load plans.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (planId: string) => {
    setSelectedPlan(planId);
    
    try {
      const data = await api<{ checkout_url: string }>('/api/v1/payments/checkout', {
        method: 'POST',
        body: JSON.stringify({
          plan_id: planId,
          success_url: `${window.location.origin}/success`,
          cancel_url: `${window.location.origin}/payments`,
        }),
      });

      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      } else {
        setError('Payment error. Please try again.');
      }
    } catch (error) {
      console.error('Checkout error:', error);
      setError('Payment failed. Please try again.');
    } finally {
      setSelectedPlan(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading payment plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your DApp Conversion Plan
          </h1>
          <p className="text-xl text-gray-600">
            Transform your e-commerce store into a Web3 powerhouse
          </p>
          {error && <p className="text-sm text-red-600 mt-3">{error}</p>}
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {Object.entries(plans).map(([planId, plan]) => (
            <div
              key={planId}
              className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow border border-gray-100"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h2>
                <div className="text-4xl font-bold text-blue-600">
                  ${(plan.price / 100).toFixed(0)}
                  <span className="text-lg text-gray-500">/one-time</span>
                </div>
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-gray-700">
                    <svg className="w-5 h-5 text-green-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                onClick={() => handleCheckout(planId)}
                disabled={selectedPlan === planId}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-xl font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {selectedPlan === planId ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </span>
                ) : (
                  'Get Started'
                )}
              </button>
            </div>
          ))}
        </div>

        {showTestData && (
          <>
            <div className="mt-12 text-center">
              <div className="bg-white rounded-xl p-6 max-w-2xl mx-auto shadow-lg">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Test Payment Information
                </h3>
                <div className="text-sm text-gray-600 space-y-1">
                  <p><strong>Test Card:</strong> 4242 4242 4242 4242</p>
                  <p><strong>Expiry:</strong> Any future date</p>
                  <p><strong>CVC:</strong> Any 3 digits</p>
                  <p><strong>Email:</strong> test@example.com</p>
                </div>
              </div>
            </div>

            <div className="mt-8 text-center">
              <p className="text-sm text-gray-500">
                This is a test environment. No real charges will be made.
              </p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
