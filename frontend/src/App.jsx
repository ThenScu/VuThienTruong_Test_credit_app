import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Import các trang của bro vào đây
import Login from './pages/Login';
import Register from './pages/Register';
import MainLayout from './layout/MainLayout';
import Shop from './pages/Shop';
import Profile from './pages/Profile';
import Tools from './pages/Tools';
import AdminPackages from './pages/AdminPackages';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 1. Tuyến đường độc lập: Trang Login KHÔNG nằm trong Layout */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 2. Tuyến đường được bảo vệ: Mọi thứ bên trong MainLayout */}
        <Route path="/" element={<MainLayout />}>
          {/* Outlet của MainLayout sẽ render các trang này dựa trên URL */}
          <Route index element={<Navigate to="/shop" replace />} /> {/* Mặc định vào '/' sẽ tự động đẩy sang '/shop' */}
          <Route path="shop" element={<Shop />} />
          <Route path="profile" element={<Profile />} />
          <Route path="tools" element={<Tools />} />
          <Route path="admin/packages" element={<AdminPackages />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;