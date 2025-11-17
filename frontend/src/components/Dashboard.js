import React, { useState, useEffect } from 'react';
// --- FIX: Import the function directly, not as part of the default 'api' object ---
import { getDashboardSummary } from '../services/api';
import Plot from 'react-plotly.js';

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch dashboard data
    // --- FIX: Call the function directly ---
    getDashboardSummary()
      .then(response => {
        setSummary(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch dashboard data:', err);
        setError('Could not load dashboard data.');
        setLoading(false);
      });
  }, []); // The empty dependency array means this runs once on mount

  if (loading) {
    return <div>Loading dashboard...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }

  if (!summary || summary.scope_summary.total === 0) {
    return <div>
      <h2>Dashboard</h2>
      <p>No emissions data recorded yet. Go to the "Add Data" page to get started.</p>
    </div>;
  }

  // --- Data for Plotly ---

  // 1. Pie Chart: Breakdown by Scope
  const scopeData = [
    {
      values: [
        summary.scope_summary.scope1,
        summary.scope_summary.scope2,
        summary.scope_summary.scope3,
      ],
      labels: ['Scope 1', 'Scope 2', 'Scope 3'],
      type: 'pie',
      hole: 0.4,
      textinfo: 'percent+value',
      texttemplate: '%{label}: %{value:.2f} kg',
    },
  ];

  const scopeLayout = {
    title: 'Emissions by Scope (Total)',
    annotations: [
      {
        font: { size: 20 },
        showarrow: false,
        text: `${summary.scope_summary.total.toFixed(2)} kg`,
        x: 0.5,
        y: 0.5,
      },
    ],
  };

  // 2. Line Chart: Emissions over Time
  const timeSeriesData = [
    {
      x: summary.time_series.map(d => d.month),
      y: summary.time_series.map(d => d.total_emissions),
      type: 'scatter',
      mode: 'lines+markers',
      name: 'Monthly Emissions',
    },
  ];

  const timeSeriesLayout = {
    title: 'Emissions Over Time',
    xaxis: { title: 'Month' },
    yaxis: { title: 'Emissions (kg CO2e)' },
  };

  return (
    <div>
      <h2>Dashboard</h2>
      
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '20px' }}>
        {/* Pie Chart */}
        <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '10px' }}>
          <Plot
            data={scopeData}
            layout={scopeLayout}
            config={{ responsive: true }}
          />
        </div>
        
        {/* Line Chart */}
        <div style={{ border: '1px solid #ddd', borderRadius: '8px', padding: '10px', flex: 1 }}>
          <Plot
            data={timeSeriesData}
            layout={timeSeriesLayout}
            style={{ width: '100%' }}
            config={{ responsive: true }}
          />
        </div>
      </div>
    </div>
  );
}

export default Dashboard;