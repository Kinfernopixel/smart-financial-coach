import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Dashboard() {
  const [insights, setInsights] = useState(null);

  useEffect(() => {
    axios.get("http://localhost:8000/api/insights")
      .then(r => setInsights(r.data.insights))
      .catch(err => console.error(err));
  }, []);

  if (!insights) return <div>Loading...</div>;

  return (
    <section>
      <h2 className="text-xl font-semibold mb-2">Insights</h2>
      <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(insights, null, 2)}</pre>
    </section>
  );
}
