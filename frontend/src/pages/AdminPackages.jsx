import React, { useEffect, useState } from 'react';
import api from '../api/axiosClient';

const AdminPackages = () => {
    const [packages, setPackages] = useState([]);
    const [features, setFeatures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [form, setForm] = useState({ name: '', description: '', price: 0, credits_awarded: 0, feature_ids: [] });
    const [editing, setEditing] = useState(null);

    useEffect(() => {
        fetchAll();
    }, []);

    const fetchAll = async () => {
        try {
            setLoading(true);
            const [pRes, fRes] = await Promise.all([
                api.get('/api/packages'),
                api.get('/api/features')
            ]);
            setPackages(pRes.data || []);
            setFeatures(fRes.data || []);
        } catch (err) {
            console.error('Lỗi load admin data:', err);
            alert('Không thể tải dữ liệu admin');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (editing) {
                await api.put(`/api/packages/${editing}`, form);
                alert('Cập nhật thành công');
            } else {
                await api.post('/api/packages', form);
                alert('Tạo gói mới thành công');
            }
            setForm({ name: '', description: '', price: 0, credits_awarded: 0, feature_ids: [] });
            setEditing(null);
            fetchAll();
        } catch (err) {
            console.error('Lỗi tạo/cập nhật:', err);
            alert(err?.response?.data?.detail || 'Lỗi hệ thống');
        }
    };

    const startEdit = (p) => {
        setEditing(p.id);
        setForm({
            name: p.name,
            description: p.description,
            price: p.price,
            credits_awarded: p.credits_awarded,
            feature_ids: (p.features || []).map(f => f.id)
        });
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Bạn có chắc chắn muốn xóa gói này?')) return;
        try {
            await api.delete(`/api/packages/${id}`);
            alert('Đã xóa thành công');
            fetchAll();
        } catch (err) {
            console.error('Lỗi xóa:', err);
            alert('Xóa thất bại');
        }
    };

    // ==========================================
    // KHU VỰC STYLE GIAO DIỆN XỊN SÒ
    // ==========================================
    const styles = {
        card: { background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', marginBottom: '16px' },
        input: { width: '100%', padding: '10px 12px', border: '1px solid #d1d5db', borderRadius: '6px', outline: 'none', marginBottom: '15px', boxSizing: 'border-box' },
        label: { display: 'block', fontWeight: 'bold', marginBottom: '6px', color: '#374151', fontSize: '14px' },
        buttonPrimary: { padding: '10px 16px', background: '#db2777', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
        buttonSecondary: { padding: '10px 16px', background: '#6b7280', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '10px' },
        buttonEdit: { padding: '6px 12px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', marginRight: '8px' },
        buttonDelete: { padding: '6px 12px', background: '#ef4444', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' },
        featureBox: { border: '1px solid #d1d5db', borderRadius: '6px', padding: '10px', maxHeight: '150px', overflowY: 'auto', background: '#f9fafb', marginBottom: '15px' },
        checkboxItem: { display: 'flex', alignItems: 'center', marginBottom: '8px', cursor: 'pointer', fontSize: '14px' }
    };

    if (loading) return <div>Đang tải kho vũ khí...</div>;

    return (
        <div>
            <h2 style={{ marginBottom: '20px', color: '#1f2937' }}>⚙️ Quản Lý Kho Vũ Khí (Packages)</h2>

            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                
                {/* CỘT TRÁI: FORM TẠO/SỬA GÓI */}
                <div style={{ flex: '1 1 400px', ...styles.card }}>
                    <h3 style={{ marginTop: 0, color: '#db2777' }}>{editing ? '🔧 Chỉnh Sửa Gói' : '➕ Tạo Gói Mới'}</h3>
                    <form onSubmit={handleSubmit}>
                        <label style={styles.label}>Tên Gói</label>
                        <input style={styles.input} value={form.name} onChange={e => setForm({...form, name: e.target.value})} required placeholder="Ví dụ: Gói Siêu Cấp" />

                        <label style={styles.label}>Mô Tả</label>
                        <textarea style={{...styles.input, minHeight: '80px'}} value={form.description} onChange={e => setForm({...form, description: e.target.value})} placeholder="Mô tả công dụng của gói..." />

                        <div style={{ display: 'flex', gap: '15px' }}>
                            <div style={{ flex: 1 }}>
                                <label style={styles.label}>Số Credits (Nhận được)</label>
                                <input style={styles.input} type="number" value={form.credits_awarded} onChange={e => setForm({...form, credits_awarded: Number(e.target.value)})} required />
                            </div>
                            <div style={{ flex: 1 }}>
                                <label style={styles.label}>Giá Bán (VNĐ)</label>
                                <input style={styles.input} type="number" value={form.price} onChange={e => setForm({...form, price: Number(e.target.value)})} required />
                            </div>
                        </div>

                        <label style={styles.label}>Mở Khóa Tools (Chọn nhiều)</label>
                        <div style={styles.featureBox}>
                            {features.length === 0 ? <span style={{color: '#9ca3af', fontStyle: 'italic'}}>Chưa có tool nào trong DB!</span> : 
                                features.map(f => (
                                    <label key={f.id} style={styles.checkboxItem}>
                                        <input 
                                            type="checkbox" 
                                            style={{ marginRight: '8px', transform: 'scale(1.2)' }}
                                            checked={form.feature_ids.includes(f.id)} 
                                            onChange={(e) => {
                                                const next = Array.from(new Set([...form.feature_ids]));
                                                if (e.target.checked) next.push(f.id); 
                                                else {
                                                    const idx = next.indexOf(f.id); 
                                                    if (idx !== -1) next.splice(idx, 1);
                                                }
                                                setForm({...form, feature_ids: next});
                                            }} 
                                        /> 
                                        <strong>{f.name}</strong> <span style={{ color: '#6b7280', marginLeft: '5px' }}>({f.code})</span>
                                    </label>
                                ))
                            }
                        </div>

                        <div style={{ marginTop: '10px' }}>
                            <button type="submit" style={styles.buttonPrimary}>{editing ? '💾 Lưu Cập Nhật' : '🚀 Đăng Bán Gói Này'}</button>
                            {editing && <button type="button" style={styles.buttonSecondary} onClick={() => { setEditing(null); setForm({ name: '', description: '', price: 0, credits_awarded: 0, feature_ids: [] })}}>❌ Hủy Bỏ</button>}
                        </div>
                    </form>
                </div>

                {/* CỘT PHẢI: DANH SÁCH GÓI HIỆN CÓ */}
                <div style={{ flex: '2 1 500px' }}>
                    <h3 style={{ marginTop: 0, color: '#1f2937' }}>📋 Danh Sách Gói Đang Bán</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                        {packages.map(p => (
                            <div key={p.id} style={{ ...styles.card, marginBottom: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <h4 style={{ margin: '0 0 5px 0', fontSize: '18px', color: '#1f2937', textTransform: 'capitalize' }}>{p.name}</h4>
                                    <p style={{ margin: '0 0 10px 0', color: '#6b7280', fontSize: '14px' }}>{p.description}</p>
                                    <div style={{ fontSize: '14px' }}>
                                        <span style={{ color: '#059669', fontWeight: 'bold' }}>+{p.credits_awarded} Credits</span> | Giá: <strong>{p.price.toLocaleString('vi-VN')} VNĐ</strong>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    <button style={styles.buttonEdit} onClick={() => startEdit(p)}>Sửa</button>
                                    <button style={styles.buttonDelete} onClick={() => handleDelete(p.id)}>Xóa</button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
}

export default AdminPackages;