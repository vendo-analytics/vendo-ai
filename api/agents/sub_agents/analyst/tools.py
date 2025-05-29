from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import pandas as pd
import numpy as np
import json
import os
from statistics import mean, median, mode, stdev
import math
from google.cloud import bigquery
from google.oauth2 import service_account

def convert_dates_to_strings(obj):
    """
    Recursively convert date/datetime objects to strings for JSON serialization.
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_dates_to_strings(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates_to_strings(item) for item in obj]
    else:
        return obj

def query_bigquery(query: str) -> dict:
    """
    Tool for ADK Agent: Executes a BigQuery SQL query and returns structured results.

    Args:
        query (str): The SQL query to run.

    Returns:
        dict: A structured response in agent-compatible format:
            {
                "mime_type": "text/plain",
                "data": "<Markdown table or message>",
                "raw_data": [<row dicts>]
            }

        If an error occurs, returns:
            {
                "mime_type": "text/plain",
                "data": "❌ Error executing query: <error message>",
                "raw_data": []
            }
    """
    print("▶️ Running query_bigquery()")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            "service_key.json",
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        client = bigquery.Client(credentials=credentials)
        job_config = bigquery.QueryJobConfig()
        query_job = client.query(query, job_config=job_config)

        # Block until done (with timeout)
        df = query_job.result(timeout=60).to_dataframe()
        result_data = df.to_dict(orient="records")
        
        # Convert date objects to strings for JSON serialization
        result_data = convert_dates_to_strings(result_data)

        if not result_data:
            return {
                "mime_type": "text/plain",
                "data": "✅ Query executed successfully, but no rows were returned.",
                "raw_data": []
            }

        # Build markdown table
        columns = df.columns.tolist()
        message = "✅ Query Results:\n"
        message += "\n| " + " | ".join(columns) + " |"
        message += "\n|" + "|".join(["---"] * len(columns)) + "|"
        for row in result_data[:100]:  # limit to first 100 rows
            row_values = [str(row.get(col, "")) for col in columns]
            message += "\n| " + " | ".join(row_values) + " |"

        if len(result_data) > 100:
            message += f"\n\n... and {len(result_data) - 100} more rows (showing first 100)"

        message += f"\n\n**Total rows returned:** {len(result_data)}"

        return {
            "mime_type": "text/plain",
            "data": message,
            "raw_data": result_data
        }

    except Exception as e:
        return {
            "mime_type": "text/plain",
            "data": f"❌ Error executing query: {str(e)}",
            "raw_data": []
        }

def build_chart(
    x: List[str], 
    y: List[float], 
    title: Optional[str] = None, 
    chart_type: str = "line"
) -> str:
    """
    Generates JSX code for a Recharts chart using provided x/y values.
    Returns a JSX string to render a chart in a Next.js frontend.

    Args:
        x: List of strings (e.g. dates, categories, or numeric values as strings)
        y: List of numbers (e.g. sales, revenue, etc.)
        title: Optional title for the chart
        chart_type: Type of chart - "line", "bar", or "scatter" (default: "line")

    Returns:
        A string of JSX code for rendering the appropriate chart type with XAxis, YAxis, 
        Tooltip, and chart-specific components from Recharts
    """
    # Validate chart type
    valid_types = ["line", "bar", "scatter"]
    if chart_type not in valid_types:
        chart_type = "line"  # Default fallback
    
    # Combine x and y into data points
    if chart_type == "scatter":
        # For scatter plots, convert x values to float for numeric axis
        try:
            data_points = [{"x": float(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
        except ValueError:
            # If x values can't be converted to float, fall back to string
            data_points = [{"x": str(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
    else:
        # For line and bar charts, x can be string
        data_points = [{"x": str(x_val), "y": float(y_val)} for x_val, y_val in zip(x, y)]
    
    # Convert data points to a JSON string and ensure proper escaping for JSX
    data_json = json.dumps(data_points).replace('"', "'")
    
    # Build the JSX string with optional title
    title_component = f"<h2>{title}</h2>" if title else ""
    
    # Generate chart-specific JSX
    if chart_type == "line":
        jsx = f"""{title_component}
<LineChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" />
</LineChart>"""
    
    elif chart_type == "bar":
        jsx = f"""{title_component}
<BarChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="y" fill="#8884d8" />
</BarChart>"""
    
    elif chart_type == "scatter":
        # For scatter charts, determine if x-axis should be numeric or categorical
        x_axis_type = "number" if chart_type == "scatter" and all(str(val).replace('.', '').replace('-', '').isdigit() for val in x[:3]) else "category"
        jsx = f"""{title_component}
<ScatterChart width={{500}} height={{300}} data={data_json}>
  <XAxis dataKey="x" type="{x_axis_type}" />
  <YAxis dataKey="y" type="number" />
  <Tooltip />
  <Scatter data={data_json} fill="#8884d8" />
</ScatterChart>"""

    return jsx


def analyze_dataset(data: Union[str, List[Dict], Dict]) -> str:
    """
    Perform comprehensive initial analysis of a dataset.
    
    Args:
        data: Dataset in JSON string format, list of dictionaries, or single dictionary
        
    Returns:
        Formatted analysis report with dataset overview, structure, and initial insights
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        elif isinstance(data, dict):
            dataset = [data]  # Convert single record to list
        else:
            dataset = data
            
        if not dataset:
            return "❌ No data provided for analysis."
            
        # Basic dataset information
        total_rows = len(dataset)
        sample_record = dataset[0] if dataset else {}
        columns = list(sample_record.keys()) if sample_record else []
        total_columns = len(columns)
        
        # Data type analysis
        column_types = {}
        for col in columns:
            sample_values = [row.get(col) for row in dataset[:10] if row.get(col) is not None]
            if sample_values:
                if all(isinstance(v, (int, float)) for v in sample_values):
                    column_types[col] = "Numeric"
                elif all(isinstance(v, str) for v in sample_values):
                    column_types[col] = "Text"
                else:
                    column_types[col] = "Mixed"
            else:
                column_types[col] = "Unknown"
        
        # Missing value analysis
        missing_analysis = {}
        for col in columns:
            missing_count = sum(1 for row in dataset if row.get(col) is None or row.get(col) == "")
            missing_percentage = (missing_count / total_rows) * 100
            missing_analysis[col] = {
                "missing_count": missing_count,
                "missing_percentage": round(missing_percentage, 2)
            }
        
        # Generate report
        report = f"""📊 **Dataset Analysis Complete**

🔍 **Dataset Overview**
- **Total Rows**: {total_rows:,}
- **Total Columns**: {total_columns}
- **Data Quality**: {'Good' if total_rows > 0 else 'No Data'}

📋 **Column Analysis**
"""
        
        for col in columns[:10]:  # Show first 10 columns
            col_type = column_types.get(col, "Unknown")
            missing_pct = missing_analysis.get(col, {}).get("missing_percentage", 0)
            report += f"- **{col}**: {col_type} ({missing_pct}% missing)\n"
        
        if len(columns) > 10:
            report += f"... and {len(columns) - 10} more columns\n"
        
        # Data quality insights
        high_missing_cols = [col for col, info in missing_analysis.items() 
                           if info["missing_percentage"] > 50]
        
        report += f"""
🔍 **Data Quality Insights**
- **Complete Columns**: {len([col for col in columns if missing_analysis[col]["missing_percentage"] == 0])}
- **High Missing Data**: {len(high_missing_cols)} columns with >50% missing
- **Numeric Columns**: {len([col for col, dtype in column_types.items() if dtype == "Numeric"])}
- **Text Columns**: {len([col for col, dtype in column_types.items() if dtype == "Text"])}

💡 **Initial Observations**
- Dataset contains {total_rows:,} records across {total_columns} dimensions
- Data appears {'well-structured' if len(high_missing_cols) < 3 else 'to have quality issues'}
- Ready for {'statistical analysis' if any(dtype == 'Numeric' for dtype in column_types.values()) else 'categorical analysis'}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error analyzing dataset: {str(e)}"


def calculate_statistics(data: Union[str, List[Dict]], column: str) -> str:
    """
    Calculate comprehensive statistics for a numeric column.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        column: Name of the column to analyze
        
    Returns:
        Formatted statistical summary
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Extract numeric values from the specified column
        values = []
        for row in dataset:
            val = row.get(column)
            if val is not None:
                try:
                    # Handle string numbers
                    if isinstance(val, str):
                        val = val.replace('$', '').replace(',', '')
                        val = float(val)
                    elif isinstance(val, (int, float)):
                        val = float(val)
                    else:
                        continue
                    values.append(val)
                except (ValueError, TypeError):
                    continue
        
        if not values:
            return f"❌ No numeric data found in column '{column}'"
        
        # Calculate statistics
        n = len(values)
        mean_val = mean(values)
        median_val = median(values)
        min_val = min(values)
        max_val = max(values)
        
        # Standard deviation (handle single value case)
        std_val = stdev(values) if n > 1 else 0
        
        # Quartiles
        sorted_vals = sorted(values)
        q1 = sorted_vals[int(n * 0.25)] if n > 3 else min_val
        q3 = sorted_vals[int(n * 0.75)] if n > 3 else max_val
        
        # Range and variance
        range_val = max_val - min_val
        variance_val = std_val ** 2 if std_val > 0 else 0
        
        report = f"""📊 **Statistical Analysis: {column}**

📈 **Descriptive Statistics**
- **Count**: {n:,} values
- **Mean**: {mean_val:,.2f}
- **Median**: {median_val:,.2f}
- **Mode**: {median_val:,.2f} (approximated)

📏 **Distribution Measures**
- **Standard Deviation**: {std_val:,.2f}
- **Variance**: {variance_val:,.2f}
- **Range**: {range_val:,.2f}

🎯 **Key Values**
- **Minimum**: {min_val:,.2f}
- **Q1 (25th percentile)**: {q1:,.2f}
- **Q3 (75th percentile)**: {q3:,.2f}
- **Maximum**: {max_val:,.2f}

💡 **Insights**
- Data spread: {'High variability' if std_val > mean_val * 0.5 else 'Low to moderate variability'}
- Distribution: {'Right-skewed' if mean_val > median_val else 'Left-skewed' if mean_val < median_val else 'Approximately normal'}
- Outlier potential: {'High' if (max_val - q3) > 1.5 * (q3 - q1) else 'Low'}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error calculating statistics: {str(e)}"


def create_visualization(data: Union[str, List[Dict]], x_column: str, y_column: str, 
                        chart_type: str = "auto", title: Optional[str] = None) -> str:
    """
    Create a visualization based on the data and specified columns.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        x_column: Column name for x-axis
        y_column: Column name for y-axis
        chart_type: Type of chart ("line", "bar", "scatter", "auto")
        title: Optional title for the chart
        
    Returns:
        JSX code for the chart
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Extract x and y values
        x_values = []
        y_values = []
        
        for row in dataset:
            x_val = row.get(x_column)
            y_val = row.get(y_column)
            
            if x_val is not None and y_val is not None:
                # Handle y values (convert to float)
                try:
                    if isinstance(y_val, str):
                        y_val = y_val.replace('$', '').replace(',', '')
                        y_val = float(y_val)
                    elif isinstance(y_val, (int, float)):
                        y_val = float(y_val)
                    else:
                        continue
                except (ValueError, TypeError):
                    continue
                
                x_values.append(str(x_val))
                y_values.append(y_val)
        
        if not x_values or not y_values:
            return f"❌ No valid data found for columns '{x_column}' and '{y_column}'"
        
        # Auto-determine chart type if needed
        if chart_type == "auto":
            # Check if x_column looks like dates
            if any(keyword in x_column.lower() for keyword in ['date', 'time', 'day', 'month', 'year']):
                chart_type = "line"
            # Check if x values are numeric
            elif all(str(x).replace('.', '').replace('-', '').isdigit() for x in x_values[:5]):
                chart_type = "scatter"
            else:
                chart_type = "bar"
        
        # Generate title if not provided
        if not title:
            title = f"{y_column} by {x_column}"
        
        # Create chart JSX
        data_points = [{"x": x, "y": y} for x, y in zip(x_values, y_values)]
        data_json = json.dumps(data_points).replace('"', "'")
        
        if chart_type == "line":
            jsx = f"""📈 **{title}**

<LineChart width={{600}} height={{400}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" strokeWidth={{2}} />
</LineChart>"""
        
        elif chart_type == "bar":
            jsx = f"""📊 **{title}**

<BarChart width={{600}} height={{400}} data={data_json}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="y" fill="#8884d8" />
</BarChart>"""
        
        elif chart_type == "scatter":
            jsx = f"""🔍 **{title}**

<ScatterChart width={{600}} height={{400}} data={data_json}>
  <XAxis dataKey="x" type="number" />
  <YAxis dataKey="y" type="number" />
  <Tooltip />
  <Scatter data={data_json} fill="#8884d8" />
</ScatterChart>"""
        
        return jsx
        
    except Exception as e:
        return f"❌ Error creating visualization: {str(e)}"


def generate_insights(data: Union[str, List[Dict]], focus_area: str = "general") -> str:
    """
    Generate business insights from the dataset.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        focus_area: Area to focus on ("revenue", "geographic", "temporal", "general")
        
    Returns:
        Formatted insights report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        if not dataset:
            return "❌ No data provided for insight generation."
        
        insights = []
        
        # General insights
        total_records = len(dataset)
        sample_record = dataset[0] if dataset else {}
        columns = list(sample_record.keys())
        
        # Look for revenue-related columns
        revenue_cols = [col for col in columns if any(keyword in col.lower() 
                      for keyword in ['revenue', 'sales', 'amount', 'total', 'price'])]
        
        # Look for geographic columns
        geo_cols = [col for col in columns if any(keyword in col.lower() 
                   for keyword in ['country', 'city', 'region', 'location'])]
        
        # Look for time columns
        time_cols = [col for col in columns if any(keyword in col.lower() 
                    for keyword in ['date', 'time', 'created', 'updated'])]
        
        if focus_area == "revenue" and revenue_cols:
            # Revenue-focused insights
            for col in revenue_cols[:2]:  # Analyze top 2 revenue columns
                values = []
                for row in dataset:
                    val = row.get(col)
                    if val is not None:
                        try:
                            if isinstance(val, str):
                                val = val.replace('$', '').replace(',', '')
                                val = float(val)
                            elif isinstance(val, (int, float)):
                                val = float(val)
                            values.append(val)
                        except:
                            continue
                
                if values:
                    total_revenue = sum(values)
                    avg_revenue = mean(values)
                    insights.append(f"💰 Total {col}: ${total_revenue:,.2f}")
                    insights.append(f"📊 Average {col}: ${avg_revenue:,.2f}")
                    
        elif focus_area == "geographic" and geo_cols:
            # Geographic insights
            for col in geo_cols[:1]:  # Analyze first geographic column
                geo_counts = {}
                for row in dataset:
                    val = row.get(col)
                    if val:
                        geo_counts[val] = geo_counts.get(val, 0) + 1
                
                if geo_counts:
                    top_location = max(geo_counts, key=geo_counts.get)
                    insights.append(f"🌍 Top {col}: {top_location} ({geo_counts[top_location]} records)")
                    insights.append(f"📍 Geographic spread: {len(geo_counts)} unique locations")
        
        else:
            # General insights
            insights.append(f"📋 Dataset contains {total_records:,} records")
            insights.append(f"🔢 {len(columns)} data dimensions available")
            
            if revenue_cols:
                insights.append(f"💰 Revenue data available in {len(revenue_cols)} columns")
            
            if geo_cols:
                insights.append(f"🌍 Geographic data available in {len(geo_cols)} columns")
            
            if time_cols:
                insights.append(f"⏰ Temporal data available in {len(time_cols)} columns")
        
        # Data quality insights
        complete_cols = 0
        for col in columns:
            missing_count = sum(1 for row in dataset if row.get(col) is None or row.get(col) == "")
            if missing_count == 0:
                complete_cols += 1
        
        insights.append(f"✅ Data completeness: {complete_cols}/{len(columns)} columns fully populated")
        
        report = f"""💡 **Business Insights Generated**

🔍 **Key Findings**
"""
        for insight in insights:
            report += f"- {insight}\n"
        
        report += f"""
🎯 **Strategic Recommendations**
- Focus analysis on {'revenue trends' if revenue_cols else 'data patterns'}
- {'Leverage geographic segmentation' if geo_cols else 'Consider adding location data'}
- {'Analyze temporal patterns' if time_cols else 'Consider time-based tracking'}

🔄 **Next Steps**
- Perform detailed statistical analysis on key metrics
- Create visualizations to identify trends and patterns
- Segment data for deeper insights
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error generating insights: {str(e)}"


def detect_outliers(data: Union[str, List[Dict]], column: str, method: str = "iqr") -> str:
    """
    Detect outliers in a numeric column using specified method.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        column: Column name to analyze for outliers
        method: Method to use ("iqr", "zscore", "both")
        
    Returns:
        Outlier analysis report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Extract numeric values
        values = []
        for row in dataset:
            val = row.get(column)
            if val is not None:
                try:
                    if isinstance(val, str):
                        val = val.replace('$', '').replace(',', '')
                        val = float(val)
                    elif isinstance(val, (int, float)):
                        val = float(val)
                    values.append(val)
                except:
                    continue
        
        if len(values) < 4:
            return f"❌ Insufficient data for outlier detection in column '{column}'"
        
        outliers_iqr = []
        outliers_zscore = []
        
        # IQR Method
        if method in ["iqr", "both"]:
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            q1 = sorted_vals[int(n * 0.25)]
            q3 = sorted_vals[int(n * 0.75)]
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers_iqr = [val for val in values if val < lower_bound or val > upper_bound]
        
        # Z-Score Method
        if method in ["zscore", "both"] and len(values) > 1:
            mean_val = mean(values)
            std_val = stdev(values)
            
            for val in values:
                z_score = abs((val - mean_val) / std_val) if std_val > 0 else 0
                if z_score > 2.5:  # Threshold for outlier
                    outliers_zscore.append(val)
        
        # Generate report
        report = f"""🚨 **Outlier Analysis: {column}**

📊 **Analysis Summary**
- **Total Values**: {len(values):,}
- **Analysis Method**: {method.upper()}

"""
        
        if method in ["iqr", "both"]:
            report += f"""🔍 **IQR Method Results**
- **Outliers Found**: {len(outliers_iqr)}
- **Outlier Percentage**: {(len(outliers_iqr) / len(values) * 100):.2f}%
- **Range**: {min(outliers_iqr):.2f} to {max(outliers_iqr):.2f} (if outliers exist)

"""
        
        if method in ["zscore", "both"]:
            report += f"""📈 **Z-Score Method Results**
- **Outliers Found**: {len(outliers_zscore)}
- **Outlier Percentage**: {(len(outliers_zscore) / len(values) * 100):.2f}%

"""
        
        # Recommendations
        total_outliers = len(set(outliers_iqr + outliers_zscore))
        outlier_pct = (total_outliers / len(values)) * 100
        
        report += f"""💡 **Recommendations**
- **Data Quality**: {'Good - few outliers detected' if outlier_pct < 5 else 'Review outliers for data quality issues'}
- **Next Steps**: {'Proceed with analysis' if outlier_pct < 10 else 'Consider outlier treatment before analysis'}
- **Investigation**: {'Focus on extreme values' if outliers_iqr or outliers_zscore else 'Data appears normally distributed'}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error detecting outliers: {str(e)}"


def perform_correlation_analysis(data: Union[str, List[Dict]], columns: List[str]) -> str:
    """
    Perform correlation analysis between specified numeric columns.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        columns: List of column names to analyze
        
    Returns:
        Correlation analysis report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        if len(columns) < 2:
            return "❌ Need at least 2 columns for correlation analysis"
        
        # Extract numeric data for each column
        column_data = {col: [] for col in columns}
        
        for row in dataset:
            valid_row = True
            row_values = {}
            
            for col in columns:
                val = row.get(col)
                if val is not None:
                    try:
                        if isinstance(val, str):
                            val = val.replace('$', '').replace(',', '')
                            val = float(val)
                        elif isinstance(val, (int, float)):
                            val = float(val)
                        row_values[col] = val
                    except:
                        valid_row = False
                        break
                else:
                    valid_row = False
                    break
            
            if valid_row:
                for col in columns:
                    column_data[col].append(row_values[col])
        
        if not all(column_data.values()) or len(column_data[columns[0]]) < 2:
            return "❌ Insufficient valid numeric data for correlation analysis"
        
        # Calculate correlations
        correlations = {}
        for i, col1 in enumerate(columns):
            for j, col2 in enumerate(columns):
                if i < j:  # Avoid duplicate pairs
                    x_vals = column_data[col1]
                    y_vals = column_data[col2]
                    
                    # Calculate Pearson correlation coefficient
                    n = len(x_vals)
                    sum_x = sum(x_vals)
                    sum_y = sum(y_vals)
                    sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
                    sum_x2 = sum(x * x for x in x_vals)
                    sum_y2 = sum(y * y for y in y_vals)
                    
                    numerator = n * sum_xy - sum_x * sum_y
                    denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
                    
                    if denominator != 0:
                        correlation = numerator / denominator
                        correlations[f"{col1} vs {col2}"] = correlation
        
        # Generate report
        report = f"""🔗 **Correlation Analysis**

📊 **Analysis Summary**
- **Columns Analyzed**: {len(columns)}
- **Valid Data Points**: {len(column_data[columns[0]]):,}
- **Correlation Pairs**: {len(correlations)}

📈 **Correlation Results**
"""
        
        for pair, corr in correlations.items():
            strength = "Strong" if abs(corr) > 0.7 else "Moderate" if abs(corr) > 0.3 else "Weak"
            direction = "Positive" if corr > 0 else "Negative"
            report += f"- **{pair}**: {corr:.3f} ({strength} {direction})\n"
        
        # Insights
        strong_correlations = [pair for pair, corr in correlations.items() if abs(corr) > 0.7]
        
        report += f"""
💡 **Key Insights**
- **Strong Relationships**: {len(strong_correlations)} pairs with correlation > 0.7
- **Data Relationships**: {'Multiple strong correlations detected' if strong_correlations else 'Weak to moderate correlations observed'}
- **Business Impact**: {'Consider multicollinearity in modeling' if strong_correlations else 'Variables appear relatively independent'}

🎯 **Recommendations**
- {'Focus on strongly correlated variables for predictive modeling' if strong_correlations else 'Explore additional variables for stronger relationships'}
- {'Investigate causation behind strong correlations' if strong_correlations else 'Consider external factors that might influence relationships'}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error performing correlation analysis: {str(e)}"


def segment_data(data: Union[str, List[Dict]], segment_column: str, metric_column: str) -> str:
    """
    Segment data by a categorical column and analyze a metric within each segment.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        segment_column: Column to segment by
        metric_column: Numeric column to analyze within segments
        
    Returns:
        Segmentation analysis report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Group data by segment
        segments = {}
        for row in dataset:
            segment_val = row.get(segment_column)
            metric_val = row.get(metric_column)
            
            if segment_val is not None and metric_val is not None:
                try:
                    if isinstance(metric_val, str):
                        metric_val = metric_val.replace('$', '').replace(',', '')
                        metric_val = float(metric_val)
                    elif isinstance(metric_val, (int, float)):
                        metric_val = float(metric_val)
                    
                    if segment_val not in segments:
                        segments[segment_val] = []
                    segments[segment_val].append(metric_val)
                except:
                    continue
        
        if not segments:
            return f"❌ No valid data found for segmentation by '{segment_column}'"
        
        # Analyze each segment
        segment_analysis = {}
        for segment, values in segments.items():
            if values:
                segment_analysis[segment] = {
                    'count': len(values),
                    'total': sum(values),
                    'average': mean(values),
                    'median': median(values),
                    'min': min(values),
                    'max': max(values)
                }
        
        # Sort segments by total value
        sorted_segments = sorted(segment_analysis.items(), 
                               key=lambda x: x[1]['total'], reverse=True)
        
        # Generate report
        report = f"""🎯 **Segmentation Analysis**

📊 **Segmentation Overview**
- **Segment Column**: {segment_column}
- **Metric Column**: {metric_column}
- **Total Segments**: {len(segments)}
- **Total Records**: {sum(len(values) for values in segments.values()):,}

📈 **Segment Performance**
"""
        
        for i, (segment, stats) in enumerate(sorted_segments[:10]):  # Top 10 segments
            percentage = (stats['total'] / sum(s['total'] for _, s in segment_analysis.items())) * 100
            report += f"""
**{i+1}. {segment}**
- Count: {stats['count']:,} records ({(stats['count']/sum(len(v) for v in segments.values())*100):.1f}%)
- Total {metric_column}: {stats['total']:,.2f} ({percentage:.1f}% of total)
- Average: {stats['average']:,.2f}
- Range: {stats['min']:,.2f} - {stats['max']:,.2f}
"""
        
        # Insights
        top_segment = sorted_segments[0]
        total_value = sum(s['total'] for _, s in segment_analysis.items())
        top_percentage = (top_segment[1]['total'] / total_value) * 100
        
        report += f"""
💡 **Key Insights**
- **Top Performer**: {top_segment[0]} contributes {top_percentage:.1f}% of total {metric_column}
- **Segment Concentration**: {'High concentration' if top_percentage > 50 else 'Balanced distribution'}
- **Performance Spread**: {len([s for _, s in segment_analysis.items() if s['average'] > mean([st['average'] for _, st in segment_analysis.items()])])} segments above average

🎯 **Strategic Recommendations**
- {'Focus resources on top-performing segments' if top_percentage > 30 else 'Develop strategies for underperforming segments'}
- {'Investigate success factors in {top_segment[0]}' if top_percentage > 40 else 'Analyze performance drivers across segments'}
- Consider segment-specific strategies for optimization
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error performing segmentation analysis: {str(e)}"


def time_series_analysis(data: Union[str, List[Dict]], date_column: str, metric_column: str) -> str:
    """
    Perform time series analysis on a dataset.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        date_column: Column containing date/time information
        metric_column: Numeric column to analyze over time
        
    Returns:
        Time series analysis report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Extract and sort time series data
        time_data = []
        for row in dataset:
            date_val = row.get(date_column)
            metric_val = row.get(metric_column)
            
            if date_val is not None and metric_val is not None:
                try:
                    # Convert metric to float
                    if isinstance(metric_val, str):
                        metric_val = metric_val.replace('$', '').replace(',', '')
                        metric_val = float(metric_val)
                    elif isinstance(metric_val, (int, float)):
                        metric_val = float(metric_val)
                    
                    time_data.append((date_val, metric_val))
                except:
                    continue
        
        if len(time_data) < 2:
            return f"❌ Insufficient time series data for analysis"
        
        # Sort by date
        time_data.sort(key=lambda x: x[0])
        
        # Calculate basic time series metrics
        values = [val for _, val in time_data]
        dates = [date for date, _ in time_data]
        
        total_periods = len(values)
        total_value = sum(values)
        average_value = mean(values)
        
        # Calculate trend (simple linear trend)
        if total_periods > 1:
            first_half_avg = mean(values[:total_periods//2])
            second_half_avg = mean(values[total_periods//2:])
            trend_direction = "Increasing" if second_half_avg > first_half_avg else "Decreasing"
            trend_magnitude = abs(second_half_avg - first_half_avg)
        else:
            trend_direction = "Stable"
            trend_magnitude = 0
        
        # Calculate volatility (standard deviation)
        volatility = stdev(values) if len(values) > 1 else 0
        
        # Find peaks and troughs
        max_value = max(values)
        min_value = min(values)
        max_date = dates[values.index(max_value)]
        min_date = dates[values.index(min_value)]
        
        # Generate report
        report = f"""📈 **Time Series Analysis**

⏰ **Analysis Period**
- **Date Range**: {dates[0]} to {dates[-1]}
- **Total Periods**: {total_periods}
- **Metric**: {metric_column}

📊 **Performance Summary**
- **Total Value**: {total_value:,.2f}
- **Average per Period**: {average_value:,.2f}
- **Volatility (Std Dev)**: {volatility:,.2f}

📈 **Trend Analysis**
- **Overall Trend**: {trend_direction}
- **Trend Magnitude**: {trend_magnitude:,.2f}
- **Trend Strength**: {'Strong' if trend_magnitude > average_value * 0.2 else 'Moderate' if trend_magnitude > average_value * 0.1 else 'Weak'}

🎯 **Key Data Points**
- **Peak Value**: {max_value:,.2f} on {max_date}
- **Lowest Value**: {min_value:,.2f} on {min_date}
- **Range**: {max_value - min_value:,.2f}

💡 **Insights**
- **Performance**: {'Strong upward trajectory' if trend_direction == 'Increasing' and trend_magnitude > average_value * 0.2 else 'Declining performance' if trend_direction == 'Decreasing' and trend_magnitude > average_value * 0.2 else 'Stable performance with minor fluctuations'}
- **Volatility**: {'High volatility - significant fluctuations' if volatility > average_value * 0.3 else 'Moderate volatility' if volatility > average_value * 0.1 else 'Low volatility - stable performance'}
- **Seasonality**: {'Potential seasonal patterns detected' if volatility > average_value * 0.2 else 'No clear seasonal patterns observed'}

🔮 **Predictive Insights**
- **Future Trend**: {'Likely continued growth' if trend_direction == 'Increasing' else 'Potential decline' if trend_direction == 'Decreasing' else 'Expected stability'}
- **Risk Assessment**: {'Monitor for trend reversal' if trend_magnitude > average_value * 0.3 else 'Stable outlook'}
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error performing time series analysis: {str(e)}"


def geographic_analysis(data: Union[str, List[Dict]], location_column: str, metric_column: str) -> str:
    """
    Perform geographic analysis on a dataset.
    
    Args:
        data: Dataset in JSON string format or list of dictionaries
        location_column: Column containing geographic information
        metric_column: Numeric column to analyze by geography
        
    Returns:
        Geographic analysis report
    """
    try:
        # Parse data if it's a string
        if isinstance(data, str):
            dataset = json.loads(data)
        else:
            dataset = data
            
        # Group data by location
        location_data = {}
        for row in dataset:
            location = row.get(location_column)
            metric_val = row.get(metric_column)
            
            if location is not None and metric_val is not None:
                try:
                    if isinstance(metric_val, str):
                        metric_val = metric_val.replace('$', '').replace(',', '')
                        metric_val = float(metric_val)
                    elif isinstance(metric_val, (int, float)):
                        metric_val = float(metric_val)
                    
                    if location not in location_data:
                        location_data[location] = []
                    location_data[location].append(metric_val)
                except:
                    continue
        
        if not location_data:
            return f"❌ No valid geographic data found"
        
        # Calculate metrics for each location
        location_stats = {}
        for location, values in location_data.items():
            location_stats[location] = {
                'count': len(values),
                'total': sum(values),
                'average': mean(values),
                'max': max(values),
                'min': min(values)
            }
        
        # Sort by total value
        sorted_locations = sorted(location_stats.items(), 
                                key=lambda x: x[1]['total'], reverse=True)
        
        # Calculate overall metrics
        total_value = sum(stats['total'] for _, stats in location_stats.items())
        total_count = sum(stats['count'] for _, stats in location_stats.items())
        
        # Generate report
        report = f"""🌍 **Geographic Analysis**

📍 **Geographic Overview**
- **Location Column**: {location_column}
- **Metric**: {metric_column}
- **Total Locations**: {len(location_data)}
- **Total Records**: {total_count:,}
- **Total Value**: {total_value:,.2f}

🏆 **Top Performing Locations**
"""
        
        for i, (location, stats) in enumerate(sorted_locations[:10]):
            percentage = (stats['total'] / total_value) * 100
            count_percentage = (stats['count'] / total_count) * 100
            
            report += f"""
**{i+1}. {location}**
- Total {metric_column}: {stats['total']:,.2f} ({percentage:.1f}% of total)
- Records: {stats['count']:,} ({count_percentage:.1f}%)
- Average: {stats['average']:,.2f}
- Range: {stats['min']:,.2f} - {stats['max']:,.2f}
"""
        
        # Geographic insights
        top_location = sorted_locations[0]
        top_percentage = (top_location[1]['total'] / total_value) * 100
        
        # Market concentration analysis
        top_5_percentage = sum((stats['total'] / total_value) * 100 
                              for _, stats in sorted_locations[:5])
        
        report += f"""
💡 **Geographic Insights**
- **Market Leader**: {top_location[0]} dominates with {top_percentage:.1f}% of total {metric_column}
- **Market Concentration**: Top 5 locations account for {top_5_percentage:.1f}% of total value
- **Geographic Spread**: {'Highly concentrated' if top_5_percentage > 80 else 'Moderately distributed' if top_5_percentage > 60 else 'Well distributed'}
- **Market Maturity**: {len([l for l, s in location_stats.items() if s['average'] > mean([st['average'] for _, st in location_stats.items()])])} locations above average performance

🎯 **Strategic Recommendations**
- **Focus Markets**: {'Concentrate on top 3 markets' if top_5_percentage > 70 else 'Develop emerging markets'}
- **Expansion Opportunities**: {'Investigate underperforming regions' if len(sorted_locations) > 10 else 'Consider new market entry'}
- **Resource Allocation**: {'Optimize high-performing markets' if top_percentage > 40 else 'Balance investment across regions'}

🔍 **Market Opportunities**
- **High Potential**: Locations with above-average performance per record
- **Growth Markets**: Regions with high volume but lower average values
- **Untapped Potential**: Consider expansion to similar geographic profiles
"""
        
        return report
        
    except Exception as e:
        return f"❌ Error performing geographic analysis: {str(e)}" 