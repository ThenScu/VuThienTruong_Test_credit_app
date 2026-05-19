import React, { useState } from 'react';
import axiosClient from '../api/axiosClient';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const res = await axiosClient.post('/api/auth/register', form);
            if (res.status === 200) {
                alert('Đăng ký thành công! Vui lòng đăng nhập.');
                navigate('/login');
            }
        } catch (err) {
            console.error('Lỗi đăng ký', err, err.response && err.response.data);
            setError(err?.response?.data?.detail || 'Đăng ký thất bại');
        }
    }

    const styles = {
        container: {
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f3f4f6',
            fontFamily: 'sans-serif'
        },
        card: {
            backgroundColor: '#ffffff',
            padding: '40px',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            width: '100%',
            maxWidth: '420px'
        },
        title: {
            textAlign: 'center',
            margin: '0 0 10px 0',
            color: '#1f2937',
            fontSize: '24px',
            fontWeight: 'bold'
        },
        formGroup: { marginBottom: '14px' },
        label: { display: 'block', marginBottom: '6px', color: '#374151' },
        input: { width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: 8 },
        button: { width: '100%', padding: '12px', backgroundColor: '#db2777', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.title}>Đăng ký</h2>
                {error && <div style={{ color: 'red', marginBottom: 12 }}>{error}</div>}
                <form onSubmit={handleSubmit}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Username</label>
                        <input style={styles.input} value={form.username} onChange={e => setForm({...form, username: e.target.value})} required />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Email</label>
                        <input style={styles.input} value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Password</label>
                        <input style={styles.input} type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
                    </div>
                    <div style={{ marginTop: 12 }}>
                        <button type="submit" style={styles.button}>Đăng ký</button>
                    </div>
                </form>
                <div style={{ marginTop: 12, textAlign: 'center' }}>
                    <a href="/login" style={{ color: '#007bff' }}>Quay về đăng nhập</a>
                </div>
            </div>
        </div>
    )
}

export default Register;
