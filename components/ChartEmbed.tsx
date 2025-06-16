import React from 'react';
import dynamic from 'next/dynamic';
import type { 
  LineChart as LineChartType,
  Line as LineType,
  BarChart as BarChartType,
  Bar as BarType,
  ScatterChart as ScatterChartType,
  Scatter as ScatterType,
  XAxis as XAxisType,
  YAxis as YAxisType,
  Tooltip as TooltipType,
  ResponsiveContainer as ResponsiveContainerType,
  Legend as LegendType
} from 'recharts';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface ChartEmbedProps {
  chartJsx: string;
}

const ChartEmbed: React.FC<ChartEmbedProps> = ({ chartJsx }) => {
  // Function to safely parse and extract chart data
  const extractChartData = (jsx: string) => {
    try {
      // Extract data prop content - handle both {[...]} and [...] formats
      let dataMatch = jsx.match(/data=\{(\[.*?\])\}/s);
      if (!dataMatch) {
        // Try direct array format
        dataMatch = jsx.match(/data=(\[.*?\])/s);
      }
      
      if (!dataMatch) {
        console.log('No data match found');
        return [];
      }
      
      // Parse the data string into actual array
      const dataStr = dataMatch[1].replace(/'/g, '"');
      const parsedData = JSON.parse(dataStr);
      return parsedData;
    } catch (error) {
      console.error('Error parsing chart data:', error);
      return [];
    }
  };

  // Function to detect chart type from JSX
  const detectChartType = (jsx: string): 'line' | 'bar' | 'scatter' => {
    if (jsx.includes('<BarChart')) return 'bar';
    if (jsx.includes('<ScatterChart')) return 'scatter';
    return 'line'; // default
  };

  // Extract title if present - handle both h2 and style-based titles
  const extractTitle = (jsx: string): string => {
    // Try to extract from h2 tag first
    const h2Match = jsx.match(/<h2[^>]*>(.*?)<\/h2>/);
    if (h2Match) return h2Match[1];

    // Try to extract from style-based title
    const styleMatch = jsx.match(/<h2 style=\{.*?\}>(.*?)<\/h2>/);
    if (styleMatch) return styleMatch[1];

    // Default title based on chart type
    const chartType = detectChartType(jsx);
    switch (chartType) {
      case 'bar':
        return 'Bar Chart Visualization';
      case 'scatter':
        return 'Scatter Plot Visualization';
      case 'line':
      default:
        return 'Line Chart Visualization';
    }
  };

  // Extract chart data and type
  const data = extractChartData(chartJsx);
  const chartType = detectChartType(chartJsx);
  const title = extractTitle(chartJsx);

  // Render appropriate chart based on type
  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <BarChart data={data}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="y" fill="#2563eb" />
          </BarChart>
        );
      
      case 'scatter':
        return (
          <ScatterChart data={data}>
            <XAxis dataKey="x" type="number" />
            <YAxis dataKey="y" type="number" />
            <Tooltip />
            <Legend />
            <Scatter data={data} fill="#2563eb" />
          </ScatterChart>
        );
      
      case 'line':
      default:
        return (
          <LineChart data={data}>
            <XAxis 
              dataKey="x" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
              }}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              label={{ value: 'y', angle: -90, position: 'insideLeft', fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value: number) => [`${value} views`, 'Page Views']}
              labelFormatter={(label) => {
                const date = new Date(label);
                return date.toLocaleDateString('en-US', { 
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                });
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="y" 
              stroke="#2563eb" 
              strokeWidth={2}
              dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        );
    }
  };

  return (
    <div className="chart-container w-full max-w-4xl mx-auto">
      <h2 className="text-xl font-semibold mb-4 text-center">{title}</h2>
      <div className="w-full h-[400px] min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChartEmbed; 