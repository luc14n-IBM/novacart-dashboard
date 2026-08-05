import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './utils/ThemeContext';
import LoginView     from './pages/LoginView';
import OrdersView    from './pages/OrdersView';
import ProductsView  from './pages/ProductsView';
import CustomersView from './pages/CustomersView';
import './App.css';

export default function App() {
  const [startDate, setStartDate] = useState('2022-01-01');
  const [endDate,   setEndDate]   = useState('2022-12-31');

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/"          element={<Navigate to="/login" replace />} />
          <Route path="/login"     element={<LoginView />} />
          <Route path="/orders"    element={
            <OrdersView
              startDate={startDate} endDate={endDate}
              setStartDate={setStartDate} setEndDate={setEndDate}
            />
          } />
          <Route path="/products"  element={
            <ProductsView
              startDate={startDate} endDate={endDate}
              setStartDate={setStartDate} setEndDate={setEndDate}
            />
          } />
          <Route path="/customers" element={
            <CustomersView
              startDate={startDate} endDate={endDate}
              setStartDate={setStartDate} setEndDate={setEndDate}
            />
          } />
          <Route path="*"          element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
