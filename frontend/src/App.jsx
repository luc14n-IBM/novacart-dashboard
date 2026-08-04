import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './utils/ThemeContext';
import LoginView     from './pages/LoginView';
import OrdersView    from './pages/OrdersView';
import ProductsView  from './pages/ProductsView';
import CustomersView from './pages/CustomersView';
import './App.css';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"          element={<Navigate to="/login" replace />} />
          <Route path="/login"     element={<LoginView />} />
          <Route path="/orders"    element={<OrdersView />} />
          <Route path="/products"  element={<ProductsView />} />
          <Route path="/customers" element={<CustomersView />} />
          <Route path="*"          element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
