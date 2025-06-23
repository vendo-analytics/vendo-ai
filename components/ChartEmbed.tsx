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

interface JsonChartData {
  type: 'line' | 'bar' | 'scatter';
  title?: string;
  x: string[];
  y: number[];
  yAxisLabel?: string;
}

// Extract caption from first <div>...</div>
const extractCaption = (jsx: string): string | undefined => {
  const match = jsx.match(/<div[^>]*>(.*?)<\/div>/s);
  return match ? match[1].trim() : undefined;
};

// Extract title from first <h2>...</h2>
const extractTitle = (jsx: string): string | undefined => {
  const match = jsx.match(/<h2[^>]*>(.*?)<\/h2>/s);
  return match ? match[1].trim() : undefined;
};

// Extract chart block and type
const extractChartBlock = (jsx: string): { type: string, chart: string } | undefined => {
  const chartTypes = ['BarChart', 'LineChart', 'ScatterChart'];
  for (const type of chartTypes) {
    const regex = new RegExp(`<${type}[^>]*>.*?<\/${type}>`, 's');
    const match = jsx.match(regex);
    if (match) return { type, chart: match[0] };
  }
  return undefined;
};

// Extract data array from chart block
const extractDataArray = (chartBlock: string): any[] => {
  // Match data prop: data=[{...}] or data={<array>}
  const match = chartBlock.match(/data=\{?(\[.*?\])\}?/s);
  if (!match) return [];
  try {
    // Replace single quotes with double quotes for JSON parsing
    const jsonStr = match[1].replace(/'/g, '"');
    return JSON.parse(jsonStr);
  } catch {
      return [];
    }
  };

const ChartEmbed: React.FC<ChartEmbedProps> = ({ chartJsx }) => {
  const caption = extractCaption(chartJsx);
  const title = extractTitle(chartJsx);
  const chartBlock = extractChartBlock(chartJsx);

  if (!chartBlock) return <div>Invalid chart data</div>;

  const data = extractDataArray(chartBlock.chart);

  // Render chart based on type
  const renderChart = () => {
    switch (chartBlock.type) {
      case 'BarChart':
        return (
          <BarChart data={data} width={500} height={300}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="y" fill="#2563eb" />
          </BarChart>
        );
      case 'LineChart':
        return (
          <LineChart data={data} width={500} height={300}>
            <XAxis dataKey="x" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="y" stroke="#2563eb" />
          </LineChart>
        );
      case 'ScatterChart':
        return (
          <ScatterChart data={data} width={500} height={300}>
            <XAxis dataKey="x" />
            <YAxis dataKey="y" />
            <Tooltip />
            <Legend />
            <Scatter data={data} fill="#2563eb" />
          </ScatterChart>
        );
      default:
        return <div>Unsupported chart type</div>;
    }
  };

  return (
    <div className="chart-container w-full max-w-4xl mx-auto p-4 bg-white rounded-lg shadow-sm">
      {title && <h2 className="text-xl font-semibold mb-4 text-center text-gray-800">{title}</h2>}
      <div className="w-full h-[400px] min-h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          {renderChart()}
        </ResponsiveContainer>
      </div>
      {caption && <div className="mt-4 text-base text-gray-600 text-center">{caption}</div>}
    </div>
  );
};

export default ChartEmbed; 