import React, { useContext, useState } from 'react';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';
import AuthContext from '../context/AuthContext';

// Basic inline styles
const formContainerStyle = {
  maxWidth: '400px',
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
  backgroundColor: '#007bff',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
};

// Validation Schemas
const LoginSchema = Yup.object().shape({
  email: Yup.string().email('Invalid email').required('Required'),
  password: Yup.string().min(6, 'Too Short!').required('Required'),
});

const RegisterSchema = Yup.object().shape({
  username: Yup.string().required('Required'),
  email: Yup.string().email('Invalid email').required('Required'),
  password: Yup.string().min(6, 'Too Short!').required('Required'),
  company_name: Yup.string(),
});

function AuthComponent() {
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState(null);
  const { login, register } = useContext(AuthContext);

  const handleSubmit = async (values, { setSubmitting }) => {
    setError(null);
    let success;
    
    if (isLogin) {
      success = await login(values.email, values.password);
    } else {
      success = await register(
        values.username,
        values.email,
        values.password,
        values.company_name
      );
    }

    if (!success) {
      setError(isLogin ? 'Invalid credentials.' : 'Registration failed. User may already exist.');
    }
    // No need to redirect here, the AuthContext and App.js will handle it
    setSubmitting(false);
  };

  return (
    <div style={formContainerStyle}>
      <h2>{isLogin ? 'Login' : 'Register'}</h2>
      <Formik
        initialValues={{
          email: '',
          password: '',
          username: '',
          company_name: '',
        }}
        validationSchema={isLogin ? LoginSchema : RegisterSchema}
        onSubmit={handleSubmit}
      >
        {({ isSubmitting }) => (
          <Form>
            {!isLogin && (
              <div>
                <Field type="text" name="username" placeholder="Username" style={fieldStyle} />
                <ErrorMessage name="username" component="div" style={errorStyle} />
              </div>
            )}
            <div>
              <Field type="email" name="email" placeholder="Email" style={fieldStyle} />
              <ErrorMessage name="email" component="div" style={errorStyle} />
            </div>
            <div>
              <Field type="password" name="password" placeholder="Password" style={fieldStyle} />
              <ErrorMessage name="password" component="div" style={errorStyle} />
            </div>
            {!isLogin && (
              <div>
                <Field
                  type="text"
                  name="company_name"
                  placeholder="Company Name (Optional)"
                  style={fieldStyle}
                />
                <ErrorMessage name="company_name" component="div" style={errorStyle} />
              </div>
            )}
            
            {error && <div style={errorStyle}>{error}</div>}
            
            <button type="submit" disabled={isSubmitting} style={buttonStyle}>
              {isSubmitting ? 'Loading...' : isLogin ? 'Login' : 'Register'}
            </button>
          </Form>
        )}
      </Formik>
      <button
        onClick={() => setIsLogin(!isLogin)}
        style={{ background: 'none', border: 'none', color: '#007bff', marginTop: '1rem', cursor: 'pointer' }}
      >
        {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
      </button>
    </div>
  );
}

export default AuthComponent;