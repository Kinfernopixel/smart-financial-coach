import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard() {
  const [insights, setInsights] = useState(null);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    amount: "",
    category: "",
    description: "",
  });
  const [loading, setLoading] = useState(false);
  const [goalAmount, setGoalAmount] = useState("");
  const [goalDate, setGoalDate] = useState("");
  const [goalData, setGoalData] = useState(null);

  const fetchInsights = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/insights");
      setInsights(res.data.insights);
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.amount || !formData.category) return;
    setLoading(true);
    try {
      await axios.post("http://localhost:8000/api/transactions", {
        amount: parseFloat(formData.amount),
        category: formData.category,
        description: formData.description,
      });
      setFormData({ amount: "", category: "", description: "" });
      await fetchInsights();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGoalSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post("http://localhost:8000/api/goal", {
        goal_amount: parseFloat(goalAmount),
        target_date: goalDate,
      });
      setGoalData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (error) return <div className="text-red-600">Error: {error}</div>;
  if (!insights) return <div className="text-gray-400">Loading insights...</div>;

  const { category_spend_last_30d, subscriptions, anomalies, tips } = insights;

  return (
    <div className="w-full flex justify-center">
      <div className="w-full max-w-3xl space-y-8">
        <h2 className="text-3xl font-semibold text-center mb-6">
          Insights Overview
        </h2>

        {/* Transaction Input Form */}
        <div className="bg-gray-800 text-white p-6 rounded-2xl shadow-lg">
          <h3 className="text-lg font-semibold mb-3">Add New Transaction</h3>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div>
              <label className="block text-sm mb-1">Amount</label>
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
                placeholder="Enter amount"
                required
              />
            </div>
            <div>
              <label className="block text-sm mb-1">Category</label>
              <input
                type="text"
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
                placeholder="e.g. Food, Rent, Salary"
                required
              />
            </div>
            <div>
              <label className="block text-sm mb-1">Description</label>
              <input
                type="text"
                name="description"
                value={formData.description}
                onChange={handleChange}
                className="w-full px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
                placeholder="Optional"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 py-2 rounded font-semibold"
            >
              {loading ? "Saving..." : "Add Transaction"}
            </button>
          </form>
        </div>

        {/* Goal Setting */}
        <div className="bg-gray-800 text-white p-6 rounded-2xl shadow-lg">
          <h3 className="text-lg font-semibold mb-3">Set Financial Goal</h3>
          <form onSubmit={handleGoalSubmit} className="space-y-3">
            <div>
              <label className="block text-sm mb-1">Goal Amount</label>
              <input
                type="number"
                value={goalAmount}
                onChange={(e) => setGoalAmount(e.target.value)}
                className="w-full px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
                placeholder="Enter target amount"
                required
              />
            </div>
            <div>
              <label className="block text-sm mb-1">Target Date</label>
              <input
                type="date"
                value={goalDate}
                onChange={(e) => setGoalDate(e.target.value)}
                className="w-full px-3 py-2 rounded bg-gray-700 text-white focus:outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-emerald-600 hover:bg-emerald-700 py-2 rounded font-semibold"
            >
              Set Goal
            </button>
          </form>

          {/* Display Recommendation */}
          {goalData && (
            <div className="mt-4 p-4 bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-300">
                <span className="font-semibold text-white">Goal:</span> Save $
                {goalData.goal.goal_amount} by {goalData.goal.target_date}
              </p>
              <p className="mt-2 text-green-400 italic">
                {goalData.recommendation}
              </p>
            </div>
          )}
        </div>

        {/* Category Spend */}
        <div className="bg-gradient-to-br from-indigo-500 to-blue-600 text-white shadow-lg rounded-2xl p-6">
          <h3 className="text-lg font-semibold mb-4">
            Spending by Category (Last 30 Days)
          </h3>
          <div className="divide-y divide-white/20">
            {Object.entries(category_spend_last_30d).map(([cat, amt]) => (
              <div
                key={cat}
                className="flex items-center justify-between py-2 px-2 hover:bg-white/10 rounded-md transition"
              >
                <span className="font-medium">{cat}</span>
                <span className="font-semibold">${amt.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Subscriptions */}
        <div className="bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg rounded-2xl p-5">
          <h3 className="text-lg font-semibold mb-3">Recurring Subscriptions</h3>
          {subscriptions.length > 0 ? (
            <ul className="space-y-2">
              {subscriptions.map((s, i) => (
                <li
                  key={i}
                  className="flex justify-between border-b border-white/20 pb-1"
                >
                  <span>{s.merchant}</span>
                  <span>
                    ${s.avg_amount} × {s.occurrences}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p>No recurring subscriptions found.</p>
          )}
        </div>

        {/* Anomalies */}
        {anomalies.length > 0 && (
          <div className="bg-gradient-to-br from-rose-500 to-red-500 text-white shadow-lg rounded-2xl p-5">
            <h3 className="text-lg font-semibold mb-3">
              Spending Anomalies Detected
            </h3>
            <ul className="space-y-2">
              {anomalies.map((a, i) => (
                <li
                  key={i}
                  className="flex justify-between border-b border-white/20 pb-1"
                >
                  <span>{a.category}</span>
                  <span>${a.latest_total.toFixed(2)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Tips */}
        {tips.length > 0 && (
          <div className="bg-gradient-to-br from-green-400 to-emerald-500 text-white shadow-lg rounded-2xl p-5">
            <h3 className="text-lg font-semibold mb-3">Smart Financial Tips</h3>
            <ul className="list-disc list-inside space-y-1">
              {tips.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
