import React from 'react';
import dynamic from 'next/dynamic';
import type { 
  LineChart as LineChartType,
  Line as LineType,
  XAxis as XAxisType,
  YAxis as YAxisType,
  Tooltip as TooltipType,
  ResponsiveContainer as ResponsiveContainerType
} from 'recharts';
import {
  LineChart,
  Line,
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
      // Extract data prop content using regex
      const dataMatch = jsx.match(/data=(\[.*?\])/);
      if (!dataMatch) return [];
      
      // Parse the data string into actual array
      const dataStr = dataMatch[1].replace(/'/g, '"');
      return JSON.parse(dataStr);
    } catch (error) {
      console.error('Error parsing chart data:', error);
      return [];
    }
  };

  // Extract title if present
  const titleMatch = chartJsx.match(/<h2>(.*?)<\/h2>/);
  const title = titleMatch ? titleMatch[1] : '';

  // Extract chart data
  const data = extractChartData(chartJsx);

  return (
    <div className="chart-container">
      {title && <h2 className="text-xl font-semibold mb-4">{title}</h2>}
      <div className="w-full h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="y" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChartEmbed; 