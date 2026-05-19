import React, { useEffect, useState } from 'react';
import api from '../api/axiosClient';

const Profile = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                setLoading(true);
                const res = await api.get('/api/users/me');
                setUser(res.data);
            } catch (err) {
                console.error('Lỗi lấy profile:', err);
                setError('Không thể tải thông tin người dùng.');
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    if (loading) return <div>Đang tải profile...</div>;
    if (error) return <div style={{ color: 'red' }}>{error}</div>;

    return (
        <div>
            <h2>👤 Hồ sơ</h2>
            <div style={{ background: '#fff', padding: 16, borderRadius: 8 }}>
                <p><strong>Username:</strong> {user.username}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Balance:</strong> {user.balance} credits</p>
                <p><strong>Tier:</strong> {user.tier}</p>
                <h4>Features unlocked</h4>
                <ul>
                    {(user.unlocked_features || []).map(uf => (
                        <li key={`${uf.feature_id}`}>{uf.feature?.name || 'Feature ' + uf.feature_id}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default Profile;
