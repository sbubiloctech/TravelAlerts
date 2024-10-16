import TravelAlert as ta
from AnalyzeTravelAlerts import AnalyzeTravelAlerts
from TravelAlertClassifier import TravelAlertClassifier
import asyncio



if __name__ == "__main__":

    # Start - Download travel alerts from U.S. Department of State site
    travelAlert = ta.TravelAlert()
    travelAlert.refreshAlerts()
    travelAlert.save_to_excel("Travelalerts.xlsx")
    travel_advisories = asyncio.run(travelAlert.fetch_advisories())
    travelAlert.save_to_excel("Travelalerts.xlsx") 
    # End - Download travel alerts from U.S. Department of State site

    # # Start Language Analysis - Downloaded travel alerts file
    # an_travel_alerts = AnalyzeTravelAlerts()
    # an_travel_alerts.load_from_excel("Travelalerts.xlsx")
    # clean_advisories = an_travel_alerts.clean_tokenize_alerts()
    # word_dicts = an_travel_alerts.generate_advisory_stats(clean_advisories)
    # an_travel_alerts.analyze_level(4)
    # # End Language Analysis - Downloaded travel alerts file

    # # Start Classification
    # cl_travel_alerts = TravelAlertClassifier()
    # cl_travel_alerts.load_from_excel("Travelalerts.xlsx")
    # # cl_travel_alerts.update_Country("Liechtenstein")
    # # cl_travel_alerts.update_Country("Burma")
    # # cl_travel_alerts.update_Country("India")
    # cl_travel_alerts.update_Country("Mexico")
    # # cl_travel_alerts.update_Country("Xanadu")
    # cl_travel_alerts.classifySents()
    # # End Classification

 

    
    
    
    
    
    