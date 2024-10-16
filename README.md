# TravelAlerts
Package that downloads travel advisories from the U.S. Department of State website and classifies them

The package contains 3 classes:
1. TravelAlert - Downloads all travel advisories and saves them to an Excel file
2. TravelAlertsAnalysis - Analyzes travel advisories and generates 4 different Levels files that represent keywords for each severity level
3. TravelAlertClassifier - Classifies each sentence from an advisory to find which sentence most likely triggered the severity level
