import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# For better visuals
sns.set(style="whitegrid")
df = pd.read_csv("NVMe_Drive_Failure_Dataset.csv")

print(df.head())
print(df.info())
print(df.describe())
# Check missing values
print(df.isnull().sum())

# Drop or fill missing values
df = df.dropna()   # simple approach
print(df["Failure_Flag"].value_counts())

sns.countplot(x="Failure_Flag", data=df)
plt.title("Failure vs Healthy Drives")
plt.show()
#temp vs failures
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Temperature_C", data=df)
plt.title("Temperature vs Failure")
plt.show()
#Power_on hours vs failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Power_On_Hours", data=df)
plt.title("Usage (Hours) vs Failure")
plt.show()
#error count vs failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Media_Errors", data=df)
plt.title("Media Errors vs Failure")
plt.show()
#sns.boxplot(x="Failure_Flag", y="CRC_Errors", data=df)
#corealtion vs heatmap
# plt.figure(figsize=(12,8))
# corr = df.corr(numeric_only=True)

# sns.heatmap(corr, annot=True, cmap="coolwarm")
# plt.title("Correlation Heatmap")
# plt.show()
plt.figure(figsize=(12,8))
corr = df.corr(numeric_only=True)

sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.show()
#usuage vs temperature
plt.figure(figsize=(8,5))
sns.scatterplot(
    x="Power_On_Hours",
    y="Temperature",
    hue="Failure_Flag",
    data=df
)
plt.title("Usage vs Temperature vs Failure")
plt.show()
#failure model distribution
plt.figure(figsize=(8,5))
sns.countplot(x="Failure_Mode", data=df)
plt.title("Failure Mode Distribution")
plt.show()
df.groupby("Failure_Flag").mean(numeric_only=True)
#overall relationship view
sns.pairplot(df, hue="Failure_Flag")
plt.show()
#percent life used vs failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Power_On_Hours", data=df)
plt.title("Usage Hours vs Failure")
plt.show()
#power on hours vs failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Power_On_Hours", data=df)
plt.title("Usage Hours vs Failure")
plt.show()
#Media Errors vs Failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Media_Errors", data=df)
plt.title("Media Errors vs Failure")
plt.show()
#Unsafe Shutdowns vs Failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Unsafe_Shutdowns", data=df)
plt.title("Unsafe Shutdowns vs Failure")
plt.show()
#Error Rates vs Failure
plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Read_Error_Rate", data=df)
plt.title("Read Error Rate vs Failure")
plt.show()

plt.figure(figsize=(8,5))
sns.boxplot(x="Failure_Flag", y="Write_Error_Rate", data=df)
plt.title("Write Error Rate vs Failure")
plt.show()
# 1. Drives with higher temperature show increased failure rates.
# 2. Media errors and CRC errors are strong indicators of failure.
# 3. Higher power-on hours correlate with wear-out failures.
# 4. Thermal and wear-out failures are the most common types.
df["Failure_Mode"].value_counts()
#failure mode analysis
plt.figure(figsize=(8,5))
sns.countplot(x="Failure_Mode", data=df)
plt.title("Failure Mode Distribution")
plt.show()


# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.express as px

# # -------------------------------
# # 🔹 STYLE SETTINGS (IMPORTANT)
# # -------------------------------
# sns.set_theme(style="darkgrid", palette="Set2")
# plt.rcParams['figure.figsize'] = (10,6)

# # -------------------------------
# # 🔹 LOAD DATA
# # -------------------------------
# df = pd.read_csv("NVMe_Drive_Failure_Dataset.csv")

# # Basic info
# print(df.head())
# print(df.info())
# print(df.describe())

# # -------------------------------
# # 🔹 CLEANING
# # -------------------------------
# print(df.isnull().sum())
# df = df.dropna()

# # Better labels
# df["Failure_Label"] = df["Failure_Flag"].map({0: "Healthy", 1: "Failed"})

# # -------------------------------
# # 🔹 FAILURE DISTRIBUTION
# # -------------------------------
# print(df["Failure_Flag"].value_counts())

# sns.countplot(x="Failure_Label", data=df, palette=["green", "red"])
# plt.title("Failure vs Healthy Drives")
# plt.show()

# # -------------------------------
# # 🔥 MINI DASHBOARD (BEST PART)
# # -------------------------------
# fig, axes = plt.subplots(2, 2, figsize=(14,10))

# sns.boxplot(x="Failure_Label", y="Temperature_C", data=df, ax=axes[0,0])
# axes[0,0].set_title("Temperature vs Failure")

# sns.boxplot(x="Failure_Label", y="Percent_Life_Used", data=df, ax=axes[0,1])
# axes[0,1].set_title("Life Used vs Failure")

# sns.boxplot(x="Failure_Label", y="Media_Errors", data=df, ax=axes[1,0])
# axes[1,0].set_title("Media Errors vs Failure")

# sns.boxplot(x="Failure_Mode", y="Temperature_C", data=df, ax=axes[1,1])
# axes[1,1].set_title("Temperature vs Failure Mode")

# plt.tight_layout()
# plt.show()

# # -------------------------------
# # 🔹 VIOLIN PLOTS (ADVANCED)
# # -------------------------------
# sns.violinplot(x="Failure_Label", y="Temperature_C", data=df)
# plt.title("Temperature Distribution by Failure")
# plt.show()

# # -------------------------------
# # 🔹 KDE PLOT (VERY IMPRESSIVE)
# # -------------------------------
# sns.kdeplot(data=df, x="Temperature_C", hue="Failure_Label", fill=True)
# plt.title("Temperature Density: Failed vs Healthy")
# plt.show()

# # -------------------------------
# # 🔹 POWER ON HOURS vs FAILURE
# # -------------------------------
# sns.boxplot(x="Failure_Label", y="Power_On_Hours", data=df)
# plt.title("Usage Hours vs Failure")
# plt.show()

# # -------------------------------
# # 🔹 ERROR ANALYSIS
# # -------------------------------
# sns.boxplot(x="Failure_Label", y="Media_Errors", data=df)
# plt.title("Media Errors vs Failure")
# plt.show()

# sns.boxplot(x="Failure_Label", y="Unsafe_Shutdowns", data=df)
# plt.title("Unsafe Shutdowns vs Failure")
# plt.show()

# sns.boxplot(x="Failure_Label", y="Read_Error_Rate", data=df)
# plt.title("Read Error Rate vs Failure")
# plt.show()

# sns.boxplot(x="Failure_Label", y="Write_Error_Rate", data=df)
# plt.title("Write Error Rate vs Failure")
# plt.show()

# # -------------------------------
# # 🔹 CORRELATION HEATMAP
# # -------------------------------
# plt.figure(figsize=(12,8))
# corr = df.corr(numeric_only=True)

# sns.heatmap(corr, annot=True, cmap="coolwarm")
# plt.title("Correlation Heatmap")
# plt.show()

# # -------------------------------
# # 🔹 SCATTER (FIXED COLUMN NAME)
# # -------------------------------
# sns.scatterplot(
#     x="Power_On_Hours",
#     y="Temperature_C",
#     hue="Failure_Label",
#     data=df
# )
# plt.title("Usage vs Temperature vs Failure")
# plt.show()

# # -------------------------------
# # 🔹 FAILURE MODE DISTRIBUTION
# # -------------------------------
# sns.countplot(x="Failure_Mode", data=df)
# plt.title("Failure Mode Distribution")
# plt.show()

# # -------------------------------
# # 🔹 GROUP ANALYSIS
# # -------------------------------
# print(df.groupby("Failure_Flag").mean(numeric_only=True))

# # -------------------------------
# # 🔹 PAIRPLOT (SAMPLED FOR SPEED)
# # -------------------------------
# sns.pairplot(df.sample(500), hue="Failure_Label")
# plt.show()

# # -------------------------------
# # 🔹 INTERACTIVE PLOT (PLOTLY 🔥)
# # -------------------------------
# fig = px.scatter(
#     df,
#     x="Power_On_Hours",
#     y="Temperature_C",
#     color="Failure_Label",
#     title="Interactive: Usage vs Temperature vs Failure"
# )
# fig.show()

# # -------------------------------
# # 🔹 FAILURE MODE COUNT
# # -------------------------------
# print(df["Failure_Mode"].value_counts())