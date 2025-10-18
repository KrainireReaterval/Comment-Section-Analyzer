import React, { useState } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Play, ArrowLeft, Download, ChevronDown, ChevronUp } from 'lucide-react';

const COLORS = ['#6b46c1', '#9f7aea', '#b794f4', '#d6bcfa', '#e9d5ff', '#7c3aed'];

const ReportPage = ({ data, onBack }) => {
  const [expandedCategory, setExpandedCategory] = useState(null);

  const categoryPieData = data.categories.map((cat) => ({
    name: cat.name,
    value: cat.percentage,
    count: cat.commentCount
  }));

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-purple-100">
      {/* ... (same as original) */}
    </div>
  );
};

export default ReportPage;