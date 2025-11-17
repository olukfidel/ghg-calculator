import React, { useState, useEffect } from 'react';
import { getReports, postReport } from '../services/api';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

// --- Import PDF and CSV libraries ---
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

// --- Styles (same as before) ---
const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  marginTop: '1rem',
};
const thStyle = {
  border: '1px solid #ddd',
  padding: '8px',
  backgroundColor: '#f2f2f2',
  textAlign: 'left',
};
const tdStyle = {
  border: '1px solid #ddd',
  padding: '8px',
};
const formContainerStyle = {
  maxWidth: '600px',
  margin: '2rem 0',
  padding: '1rem',
  border: '1px solid #ddd',
  borderRadius: '8px',
};
const fieldStyle = { padding: '8px', margin: '8px' };
const buttonStyle = {
  padding: '10px',
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  margin: '8px'
};

// --- Validation Schema (same as before) ---
const ReportSchema = Yup.object().shape({
  report_name: Yup.string().required('Report name is required'),
  start_date: Yup.date().required('Start date is required'),
  end_date: Yup.date()
    .required('End date is required')
    .min(Yup.ref('start_date'), 'End date must be after start date'),
});

function Report() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formStatus, setFormStatus] = useState({ success: '', error: '' });

  // Function to fetch reports (same as before)
  const fetchReports = () => {
    setLoading(true);
    getReports()
      .then(response => {
        setReports(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch reports:', err);
        setError('Could not load reports.');
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchReports();
  }, []);

  // Handle new report generation (same as before)
  const handleGenerateReport = (values, { setSubmitting, resetForm }) => {
    setFormStatus({ success: '', error: '' });
    postReport(values)
      .then(response => {
        setFormStatus({ success: 'Report generated successfully!' });
        resetForm();
        fetchReports(); // Refresh the list of reports
      })
      .catch(err => {
        setFormStatus({ error: err.response?.data?.message || 'Failed to generate report.' });
      })
      .finally(() => {
        setSubmitting(false);
      });
  };
  
  // --- START OF CSV/PDF LOGIC ---

  // Helper function to find a report by ID
  const getReportById = (id) => {
    return reports.find(report => report.id === id);
  };

  // CSV Export Handler
  const handleExportCSV = (reportId) => {
    const report = getReportById(reportId);
    if (!report) return;

    // Define CSV headers
    const headers = [
      'Report Name',
      'Start Date',
      'End Date',
      'Scope 1 (kg)',
      'Scope 2 (kg)',
      'Scope 3 (kg)',
      'Total (kg)',
      'Generated At'
    ];
    
    // Define CSV data row
    const data = [
      report.report_name,
      report.start_date,
      report.end_date,
      report.total_scope1_kg.toFixed(2),
      report.total_scope2_kg.toFixed(2),
      report.total_scope3_kg.toFixed(2),
      report.total_all_scopes_kg.toFixed(2),
      report.generated_at
    ];

    // Create CSV content
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += headers.join(",") + "\n";
    csvContent += data.join(",") + "\n";
    
    // Create and trigger download link
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${report.report_name.replace(/ /g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // PDF Export Handler
  const handleExportPDF = (reportId) => {
    const report = getReportById(reportId);
    if (!report) return;

    const doc = new jsPDF();

    // Add Title
    doc.setFontSize(18);
    doc.text(`GHG Emissions Report: ${report.report_name}`, 14, 22);

    // Add Subtitle (Date Range)
    doc.setFontSize(12);
    doc.text(`Reporting Period: ${report.start_date} to ${report.end_date}`, 14, 30);
    doc.text(`Generated On: ${report.generated_at.split('T')[0]}`, 14, 36);

    // Add Summary Table
    doc.autoTable({
      startY: 50,
      head: [['Scope', 'Emissions (kg CO₂e)']],
      body: [
        ['Scope 1', report.total_scope1_kg.toFixed(2)],
        ['Scope 2', report.total_scope2_kg.toFixed(2)],
        ['Scope 3', report.total_scope3_kg.toFixed(2)],
      ],
      // Add a footer row for the total
      foot: [['Total Emissions', report.total_all_scopes_kg.toFixed(2)]],
      footStyles: {
        fillColor: [41, 128, 185], // A blue color
        textColor: 255,
        fontStyle: 'bold',
      },
      theme: 'grid',
    });

    // Save the PDF
    doc.save(`${report.report_name.replace(/ /g, '_')}.pdf`);
  };

  // --- END OF CSV/PDF LOGIC ---

  return (
    <div>
      <h2>Reports</h2>

      {/* --- Generate New Report Form (same as before) --- */}
      <div style={formContainerStyle}>
        <h3>Generate New Report</h3>
        <Formik
          initialValues={{
            report_name: '',
            start_date: '',
            end_date: '',
          }}
          validationSchema={ReportSchema}
          onSubmit={handleGenerateReport}
        >
          {({ isSubmitting }) => (
            <Form>
              <Field type="text" name="report_name" placeholder="Report Name" style={fieldStyle} />
              <ErrorMessage name="report_name" component="div" style={{ color: 'red' }} />
              
              <label>Start Date:</label>
              <Field type="date" name="start_date" style={fieldStyle} />
              <ErrorMessage name="start_date" component="div" style={{ color: 'red' }} />
              
              <label>End Date:</label>
              <Field type="date" name="end_date" style={fieldStyle} />
              <ErrorMessage name="end_date" component="div" style={{ color: 'red' }} />
              
              <button type="submit" disabled={isSubmitting} style={buttonStyle}>
                {isSubmitting ? 'Generating...' : 'Generate Report'}
              </button>
              {formStatus.success && <div style={{ color: 'green' }}>{formStatus.success}</div>}
              {formStatus.error && <div style={{ color: 'red' }}>{formStatus.error}</div>}
            </Form>
          )}
        </Formik>
      </div>

      {/* --- Historical Reports Table (with new onClick handlers) --- */}
      <h3>Historical Reports</h3>
      {loading && <div>Loading reports...</div>}
      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      {!loading && !error && (
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={thStyle}>Report Name</th>
              <th style={thStyle}>Generated</th>
              <th style={thStyle}>Period</th>
              <th style={thStyle}>Scope 1 (kg)</th>
              <th style={thStyle}>Scope 2 (kg)</th>
              <th style={thStyle}>Scope 3 (kg)</th>
              <th style={thStyle}>Total (kg)</th>
              <th style={thStyle}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.length > 0 ? (
              reports.map(report => (
                <tr key={report.id}>
                  <td style={tdStyle}>{report.report_name}</td>
                  <td style={tdStyle}>{report.generated_at.split('T')[0]}</td>
                  <td style={tdStyle}>{report.start_date} to {report.end_date}</td>
                  <td style={tdStyle}>{report.total_scope1_kg.toFixed(2)}</td>
                  <td style={tdStyle}>{report.total_scope2_kg.toFixed(2)}</td>
                  <td style={tdStyle}>{report.total_scope3_kg.toFixed(2)}</td>
                  <td style={tdStyle}><strong>{report.total_all_scopes_kg.toFixed(2)}</strong></td>
                  <td style={tdStyle}>
                    {/* --- These buttons now call the new functions --- */}
                    <button onClick={() => handleExportCSV(report.id)} style={{fontSize: '0.8rem', margin: '2px'}}>CSV</button>
                    <button onClick={() => handleExportPDF(report.id)} style={{fontSize: '0.8rem', margin: '2px'}}>PDF</button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="8" style={{...tdStyle, textAlign: 'center'}}>No reports found.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Report;