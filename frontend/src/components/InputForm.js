import React, { useState, useEffect } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
// --- FIX: Import named functions, not the default 'api' object ---
import { getFactors, postInput } from '../services/api';

// Styles (same as Auth.js for consistency)
const formContainerStyle = {
  maxWidth: '600px',
  margin: '2rem auto',
  padding: '2rem',
  border: '1px solid #ddd',
  borderRadius: '8px',
};
const fieldStyle = { width: '95%', padding: '8px', margin: '8px 0' };
const errorStyle = { color: 'red', fontSize: '0.8rem' };
const buttonStyle = {
  width: '100%',
  padding: '10px',
  backgroundColor: '#28a745',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};
const successStyle = { color: 'green', marginTop: '1rem' };
const serverErrorStyle = { color: 'red', marginTop: '1rem' };

// Validation Schema
const InputSchema = Yup.object().shape({
  factor_id: Yup.string().required('Activity is required'),
  activity_value: Yup.number()
    .required('Value is required')
    .positive('Value must be positive'),
  activity_unit: Yup.string().required('Unit is required'),
  date_period_start: Yup.date().required('Date is required'),
});

function InputForm() {
  const [factors, setFactors] = useState([]);
  const [selectedFactor, setSelectedFactor] = useState(null);
  const [status, setStatus] = useState({ success: '', error: '' });

  // Fetch emission factors on component mount
  useEffect(() => {
    // --- FIX: Call imported function ---
    getFactors()
      .then(response => {
        setFactors(response.data);
      })
      .catch(error => {
        console.error('Failed to fetch factors:', error);
        setStatus({ error: 'Could not load emission factors.' });
      });
  }, []);

  const handleFactorChange = (e, setFieldValue) => {
    const factorId = e.target.value;
    const factor = factors.find(f => f.id === parseInt(factorId));
    
    setSelectedFactor(factor);
    
    // Set the factor_id
    setFieldValue('factor_id', factorId);
    
    // Automatically set the unit based on the factor
    if (factor) {
      setFieldValue('activity_unit', factor.unit);
    } else {
      setFieldValue('activity_unit', '');
    }
  };

  const handleSubmit = (values, { setSubmitting, resetForm }) => {
    setStatus({ success: '', error: '' });

    // --- FIX: Call imported function ---
    postInput(values)
      .then(response => {
        setStatus({ success: 'Successfully added data!' });
        resetForm();
        setSelectedFactor(null);
      })
      .catch(error => {
        setStatus({ error: error.response?.data?.message || 'Failed to submit data.' });
      })
      .finally(() => {
        setSubmitting(false);
      });
  };

  return (
    <div style={formContainerStyle}>
      <h2>Add Activity Data</h2>
      <Formik
        initialValues={{
          factor_id: '',
          activity_value: '',
          activity_unit: '',
          date_period_start: '',
        }}
        validationSchema={InputSchema}
        onSubmit={handleSubmit}
        enableReinitialize // Allows form to update when 'activity_unit' is set
      >
        {({ isSubmitting, setFieldValue }) => (
          <Form>
            <div>
              <label>Activity Type (Emission Factor)</label>
              <Field
                as="select"
                name="factor_id"
                style={fieldStyle}
                onChange={(e) => handleFactorChange(e, setFieldValue)}
              >
                <option value="">-- Select an Activity --</option>
                {/* Group factors by category */}
                {Object.entries(
                  factors.reduce((acc, f) => {
                    if (!acc[f.category]) acc[f.category] = [];
                    acc[f.category].push(f);
                    return acc;
                  }, {})
                ).map(([category, factorsInCategory]) => (
                  <optgroup label={category} key={category}>
                    {factorsInCategory.map(factor => (
                      <option key={factor.id} value={factor.id}>
                        {factor.name} (Scope {factor.scope})
                      </option>
                    ))}
                  </optgroup>
                ))}
              </Field>
              <ErrorMessage name="factor_id" component="div" style={errorStyle} />
            </div>

            <div>
              <label>Activity Value</label>
              <Field type="number" name="activity_value" placeholder="e.g., 1000" style={fieldStyle} />
              <ErrorMessage name="activity_value" component="div" style={errorStyle} />
            </div>

            <div>
              <label>Unit</label>
              <Field as="select" name="activity_unit" style={fieldStyle}>
                {/* This is simplified. It only shows the factor's default unit. */}
                {selectedFactor ? (
                  <option value={selectedFactor.unit}>{selectedFactor.unit}</option>
                  // A more advanced version would add 'gallon' if unit is 'liter'
                ) : (
                  <option value="">-- Select activity first --</option>
                )}
              </Field>
              <ErrorMessage name="activity_unit" component="div" style={errorStyle} />
            </div>

            <div>
              <label>Date of Activity</label>
              <Field type="date" name="date_period_start" style={fieldStyle} />
              <ErrorMessage name="date_period_start" component="div" style={errorStyle} />
            </div>

            {status.error && <div style={serverErrorStyle}>{status.error}</div>}
            {status.success && <div style={successStyle}>{status.success}</div>}

            <button type="submit" disabled={isSubmitting} style={buttonStyle}>
              {isSubmitting ? 'Submitting...' : 'Add Emission Data'}
            </button>
          </Form>
        )}
      </Formik>
    </div>
  );
}

export default InputForm;