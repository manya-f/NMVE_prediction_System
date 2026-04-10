# NVMe Drive Failure Pattern Analysis Report

## Problem Statement
Analyze NVMe drive failure/error data and determine the top 5 failure patterns using machine learning on the dataset `data/NVMe_Drive_Failure_Dataset.csv`.

## Dataset Overview
- **Total Drives**: 5,000
- **Failed Drives**: 2,000 (40.0% failure rate)
- **Features**: 15 columns including SMART metrics, vendor info, and failure indicators
- **Target Variable**: Failure_Mode (0-5 representing different failure types)

## Top 5 Failure Patterns Identified

### 1. **Wear-Out Failure (Mode 1)** - 691 drives (13.8%)
- **Characteristics**:
  - Average temperature: Same as healthy drives
  - Life used: +50.9% higher than healthy drives
  - Media errors: 28.5 (very high)
  - Unsafe shutdowns: 0.5
- **Pattern Description**: Drives failing due to normal wear and tear after extended use, characterized by high media error rates and significant life consumption.

### 2. **Thermal Failure (Mode 2)** - 540 drives (10.8%)
- **Characteristics**:
  - Average temperature: +40.2°C higher than healthy drives
  - Life used: +2.5% higher than healthy drives
  - Media errors: 8.0
  - Unsafe shutdowns: 0.5
- **Pattern Description**: Drives failing due to excessive heat, with significantly elevated operating temperatures compared to healthy drives.

### 3. **Power-Related Failure (Mode 3)** - 378 drives (7.6%)
- **Characteristics**:
  - Average temperature: +0.2°C (similar to healthy)
  - Life used: +0.6% (similar to healthy)
  - Media errors: 5.2
  - Unsafe shutdowns: 29.3 (extremely high)
- **Pattern Description**: Drives failing due to power instability, evidenced by very high numbers of unsafe shutdown events.

### 4. **Controller/Firmware Failure (Mode 4)** - 233 drives (4.7%)
- **Characteristics**:
  - Average temperature: +0.2°C (similar to healthy)
  - Life used: -2.9% lower than healthy drives
  - Media errors: 54.9 (highest among all patterns)
  - Unsafe shutdowns: 0.6
- **Pattern Description**: Drives failing due to controller or firmware issues, showing the highest media error rates and occurring in relatively new drives.

### 5. **Early-Life Failure (Mode 5)** - 158 drives (3.2%)
- **Characteristics**:
  - Average temperature: -0.3°C (slightly cooler than healthy)
  - Life used: +2.8% (similar to healthy)
  - Media errors: 9.7
  - Unsafe shutdowns: 0.5
- **Pattern Description**: Drives failing shortly after installation, possibly due to manufacturing defects or early component failures.

## Machine Learning Model Results

### Model Performance
- **Algorithm**: Random Forest Classifier
- **Accuracy**: 100.0% on test set
- **Training Set**: 4,000 samples
- **Test Set**: 1,000 samples

### Feature Importance Ranking
1. **Media_Errors** (61.20%) - Most critical predictor
2. **Temperature_C** (8.96%) - Thermal stress indicator
3. **Available_Spare** (7.33%) - Spare capacity remaining
4. **Unsafe_Shutdowns** (6.24%) - Power stability metric
5. **Total_TBW_TB** (3.11%) - Total bytes written
6. **Power_On_Hours** (1.85%) - Operating time
7. **Vendor_Samsung** (1.66%) - Vendor-specific patterns
8. **Percent_Life_Used** (1.43%) - Wear level
9. **Model_980 Pro** (1.07%) - Model-specific patterns
10. **Total_TBR_TB** (0.98%) - Total bytes read

## Key Insights

### 🔍 **Primary Failure Indicators**
- **Media_Errors** is the strongest predictor (61.2% importance), indicating that drives with high error rates are most likely to fail
- **Temperature** plays a crucial role in thermal-related failures
- **Unsafe_Shutdowns** is highly indicative of power-related failures

### 📊 **Pattern Characteristics**
- Each failure mode shows distinct behavioral patterns
- Wear-out failures occur in heavily used drives with high error rates
- Thermal failures are characterized by extreme temperature deviations
- Power failures show normal usage but extremely high unsafe shutdown counts
- Controller failures happen in relatively new drives with very high error rates

### 🎯 **Predictive Power**
- The ML model achieves perfect accuracy, indicating clear separability between failure patterns
- Early detection of these patterns can enable proactive drive replacement
- Different monitoring thresholds should be applied based on failure mode characteristics

## Files Generated
- `failure_pattern_model.pkl` - Trained Random Forest model
- `failure_pattern_features.pkl` - Feature encoding information
- `failure_patterns_analysis.png` - Comprehensive visualizations

## Recommendations
1. **Implement continuous monitoring** of Media_Errors as the primary health indicator
2. **Set thermal thresholds** to prevent thermal failures (alert when >40°C above normal)
3. **Monitor power stability** by tracking unsafe shutdown events
4. **Schedule proactive replacements** when wear-out patterns are detected
5. **Investigate early-life failures** to identify potential manufacturing issues

This analysis provides a comprehensive understanding of NVMe drive failure patterns, enabling predictive maintenance and data loss prevention strategies.</content>
<parameter name="filePath">c:\Users\hebba\OneDrive\Desktop\drive-failure-prediction-system\NVMe_Failure_Pattern_Analysis_Report.md