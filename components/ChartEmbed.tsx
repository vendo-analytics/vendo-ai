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
  ResponsiveContainer as ResponsiveContainerType
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
  ResponsiveContainer
} from 'recharts';

interface ChartEmbedProps {
  chartJsx: string;
}

const ChartEmbed: React.FC<ChartEmbedProps> = ({ chartJsx }) => {
  // Function to safely parse and extract chart data
  const extractChartData = (jsx: string) => {
    try {
      console.log('Raw JSX:', jsx);
      
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
      
      console.log('Data match:', dataMatch[1]);
      
      // Parse the data string into actual array
      const dataStr = dataMatch[1].replace(/'/g, '"');
      console.log('Processed data string:', dataStr);
      
      const parsedData = JSON.parse(dataStr);
      console.log('Parsed data:', parsedData);
      
      return parsedData;
    } catch (error) {
      console.error('Error parsing chart data:', error);
      console.error('Input JSX:', jsx);
      return [];
    }
  };

  // Function to detect chart type from JSX
  const detectChartType = (jsx: string): 'line' | 'bar' | 'scatter' => {
    if (jsx.includes('<BarChart')) return 'bar';
    if (jsx.includes('<ScatterChart')) return 'scatter';
    return 'line'; // default
  };

  // Extract title if present
  const titleMatch = chartJsx.match(/<h2>(.*?)<\/h2>/);
  const title = titleMatch ? titleMatch[1] : '';

  // Extract chart data and type
  const data = extractChartData(chartJsx);
  const chartType = detectChartType(chartJsx);

  console.log('Chart type detected:', chartType);
  console.log('Final data for chart:', data);

  // Render appropriate chart based on type
  const renderChart = () => {
    switch (chartType) {
      case 'bar':
        return (
          <BarChart data={data}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="y" fill="#8884d8" />
          </BarChart>
        );
      
      case 'scatter':
        return (
          <ScatterChart data={data}>
            <XAxis dataKey="x" type="number" />
            <YAxis dataKey="y" type="number" />
            <Tooltip />
            <Scatter data={data} fill="#8884d8" />
          </ScatterChart>
        );
      
      case 'line':
      default:
        return (
          <LineChart data={data}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="y" stroke="#8884d8" />
          </LineChart>
        );
    }
  };

  return (
    <div className="chart-container">
      {title && <h2 className="text-xl font-semibold mb-4">{title}</h2>}
      <div className="w-full h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChartEmbed; 