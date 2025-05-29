# Analyst Agent

The Analyst Agent is a specialized sub-agent designed to perform comprehensive data analysis, generate insights, and create visualizations. It's built to analyze datasets retrieved from the query agent and provide actionable business intelligence.

## Purpose

The Analyst Agent serves as your data science expert, capable of:
- Analyzing dataset structure and quality
- Generating statistical insights and summaries
- Creating visualizations and charts
- Detecting patterns, trends, and outliers
- Providing strategic recommendations based on data

## Core Capabilities

### 1. Dataset Analysis & Overview
- **Initial Data Scan**: Examines dataset structure, dimensions, data types, and quality
- **Data Cleaning Assessment**: Identifies missing values, inconsistencies, and anomalies
- **Column Definition**: Clearly explains what each column represents and its business significance
- **Data Quality Report**: Assesses completeness, accuracy, and reliability of the data

### 2. Statistical Analysis
- **Descriptive Statistics**: Calculates mean, median, mode, standard deviation, quartiles
- **Distribution Analysis**: Analyzes data distributions and identifies patterns
- **Correlation Analysis**: Identifies relationships between variables
- **Trend Analysis**: Detects patterns and trends over time
- **Variance Analysis**: Understands data spread and variability

### 3. Visualization & Charts
- **Automatic Chart Selection**: Chooses appropriate chart types based on data structure
- **Time Series Visualizations**: Line charts for trends over time
- **Categorical Comparisons**: Bar charts for category-based analysis
- **Correlation Plots**: Scatter plots for relationship analysis
- **Geographic Visualizations**: Maps and regional analysis charts

### 4. Advanced Analytics
- **Outlier Detection**: Identifies unusual data points and anomalies
- **Segmentation Analysis**: Groups data into meaningful segments
- **Cohort Analysis**: Analyzes user/customer behavior over time
- **Geographic Analysis**: Regional performance and distribution analysis
- **Performance Benchmarking**: Compares metrics across different dimensions

## Available Tools

### Core Analysis Tools
1. **`analyze_dataset`** - Comprehensive initial analysis of any dataset
2. **`calculate_statistics`** - Detailed statistical analysis for numeric columns
3. **`generate_insights`** - Business insights generation with focus areas
4. **`create_visualization`** - Chart and visualization creation

### Advanced Analysis Tools
5. **`detect_outliers`** - Outlier detection using IQR and Z-score methods
6. **`perform_correlation_analysis`** - Correlation analysis between variables
7. **`segment_data`** - Data segmentation and segment performance analysis
8. **`time_series_analysis`** - Temporal pattern and trend analysis
9. **`geographic_analysis`** - Geographic performance and distribution analysis

## Usage Examples

### Basic Dataset Analysis
```
@analyst analyze my revenue data and tell me what you see
```

### Specific Analysis Types
```
@analyst perform time series analysis on my sales data
@analyst segment my customers by country and analyze revenue
@analyst detect outliers in my transaction amounts
@analyst create a visualization showing revenue by month
```

### Advanced Analytics
```
@analyst perform correlation analysis between marketing spend and revenue
@analyst analyze geographic performance across all regions
@analyst generate insights focused on revenue trends
```

## Analysis Workflow

The Analyst Agent follows a structured 5-phase approach:

### Phase 1: Initial Assessment
1. Dataset overview and structure analysis
2. Data quality assessment
3. Column mapping and business context
4. Initial observations and insights

### Phase 2: Statistical Analysis
1. Descriptive statistics calculation
2. Distribution analysis
3. Correlation identification
4. Trend detection

### Phase 3: Visualization
1. Chart type selection
2. Interactive visualization creation
3. Multiple analytical perspectives
4. Visual storytelling

### Phase 4: Advanced Insights
1. Data segmentation
2. Outlier analysis
3. Performance comparisons
4. Predictive insights

### Phase 5: Recommendations
1. Strategic insights
2. Next steps suggestions
3. Optimization opportunities
4. Risk assessment

## Communication Style

The Analyst Agent communicates using:
- **Professional & Insightful**: Clear, data-driven insights with business context
- **Comprehensive Yet Accessible**: Technical concepts explained in business-friendly terms
- **Proactive & Strategic**: Anticipates follow-up questions and suggests additional analyses
- **Visual Enhancement**: Strategic use of emojis and formatting for readability

## Integration

### With Query Agent
- Receives datasets from query agent for analysis
- Requests additional data cuts when needed
- Provides feedback on data quality and completeness

### With Root Agent
- Routes requests for external data or market research
- Escalates when analysis requires unavailable data
- Collaborates on strategic recommendations

## Example Analysis Output

```
📊 Dataset Analysis Complete

🔍 **Initial Overview**
- Total Rows: 220
- Total Columns: 19
- Data Quality: Good

📈 **Key Insights**
- Revenue shows strong upward trend (+15% growth)
- Geographic concentration in UK and Australia
- Fee impact minimal at 2.9% of total revenue

📊 **Statistical Summary**
- Average transaction: $147.50
- Revenue range: $125 - $3,237
- Low volatility indicates stable performance

🎯 **Strategic Recommendations**
- Focus expansion efforts on UK market
- Investigate success factors in top-performing regions
- Monitor fee structures for optimization opportunities

🔄 **Suggested Next Analyses**
1. Time Series Deep Dive
2. Geographic Expansion Analysis
3. Customer Segmentation
4. Product Performance Analysis
5. Correlation Analysis
```

## Error Handling

The Analyst Agent handles various scenarios:
- **Missing Data**: Explains impact and suggests handling strategies
- **Insufficient Data**: Clearly states when more data is needed
- **Data Quality Issues**: Identifies and recommends solutions
- **Analysis Limitations**: Acknowledges constraints and suggests alternatives

## Best Practices

1. **Start with Overview**: Always begin with `analyze_dataset` for new data
2. **Progressive Analysis**: Move from general to specific insights
3. **Multiple Perspectives**: Use different analysis types for comprehensive understanding
4. **Actionable Focus**: Prioritize insights that lead to business decisions
5. **Follow-up Ready**: Be prepared to dive deeper based on initial findings

## Future Enhancements

Planned improvements include:
- Machine learning model integration
- Automated report generation
- Real-time data streaming analysis
- Advanced statistical modeling
- Industry-specific analysis templates 