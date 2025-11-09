import React from "react";
import Dashboard from "./components/Dashboard";

export default function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-gray-100 p-6">
      <h1 className="text-3xl font-bold mb-6">Smart Financial Coach</h1>
      <Dashboard />
    </div>
  );
}
