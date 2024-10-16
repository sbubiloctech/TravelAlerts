import requests
from bs4 import BeautifulSoup
from pandas import DataFrame, read_excel
import asyncio
import aiohttp

"""
Defines a class TravelAlert to retrieve travel advisories from the State Department website

"""

class TravelAlert:
    """
    Class TravelAlert: Retrieves travel advisories from the U.S. State Department website
    The class contains the following variables:
    1. State Department travel advisories URL
    2. State Department base URL
    3. Pandas Dataframe to store retrieved travel advisories

    Methods:
    1. Constructor (__init__): Does not take any arguments and returns a TravelAlert object.
    2. refreshAlerts: Does not take arguments. Updates travel alert dataframe with initial data that contains links to the detailed travel advisories for each country.
    3. fetch_advisories: Asynchronous function to fetch the detailed advisory for each country and update dataframe.
    4. save_to_excel: Takes one argument for filename. Saves travel advisories dataframe to excel file.
    5. load_from_excel: Takes one argument for filename. Loads data from excel file into dataframe in the class.

    Recommended sequence for methods: 
    1. Initialize object -> refreshAlerts -> fetch_advisories -> save_to_excel
    2. Initialize object -> load_from_excel

    """

    def __init__(self):
        self.ta_url = "https://travel.state.gov/content/travel/en/traveladvisories/traveladvisories.html/"
        self.base_url = "https://travel.state.gov"   
        self.travel_df = None
            
    def refreshAlerts(self):
        """
        Create travel advisory dataframe and populate with data from State department summary table
        """

        request_data = self.getValidatedRequest(self.ta_url)
        self.travel_df = self.parseTable(request_data)
        if (len(list(self.travel_df.index))) > 0: self.append_threat_level()

    def getValidatedRequest(self, url):
        """
        Validates if a URL exists and returns URL contents, if valid.
        Argument: URL
        Return: URL content
        """
        try:
            response = requests.get(url)
        except Exception as e:
            message = e.args
            print(f"No such url! Failed to resolve {url}" )
            raise Exception(message)
        
        if response.ok: 
            return response.content
        else: print(f'Error retrieving url. Error code: {response.status_code}')

    def parseTable(self, rdata):
        """
        Generates a pandas dataframe with summary table and assigns it to the TravelAlert object
        Arguments: html data from State Department URL
        Returns: Dataframe with summary advisory table from U.S. State Department website
        """
        try:
            soup = BeautifulSoup(rdata,"html.parser")
        except Exception as e:
            print("No content. Check weblink!")
            raise e

        body = soup.body
        if body == None: return None
        table = body.find_all(attrs={"class":"table-data data-date"})[0].tbody
        if table == None: return None
        table_rows = table.find_all("tr")
        if table_rows == None: return None
        headings_tag = table_rows[0].find_all("th")
        column_headings = [heading.text for heading in headings_tag]
        column_headings.append("Link")
        table_data = [self.parseRow(table_rows[i]) for i in range(1, len(table_rows)-1)]
        travel_df = DataFrame(table_data, columns=column_headings)
        return travel_df
        
    
    def parseRow(self, tr):
        row_data_tags = tr.find_all("td")
        link = self.base_url + row_data_tags[0].find("a").get("href", None)
        row_data = [tag.text for tag in row_data_tags]
        row_data.append(link)
        return row_data
    
    def save_to_csv(self, filename):
        """
        Saves travel advisories to specified file in csv format.
        Arguments: filename
        """

        self.travel_df.to_csv(filename)
    
    def save_to_excel(self, filename):
        """
        Saves travel advisories to specified file in xlsx format after appending threat level.
        Arguments: filename
        """

        self.append_threat_level()
        self.travel_df.to_excel(filename)
    
    def load_from_excel(self, filename):
        """
        Loads travel advisories from specified file in xlsx format.
        Arguments: filename
        """

        self.travel_df = read_excel(filename, index_col=0)



    def sync_fetch_link_info(self, link_idx):
        if link_idx >= len(self.travel_df.index):
            return " "
        
        request_data = self.getValidatedRequest(self.travel_df.iloc[link_idx]["Link"])
        return self.parseTravelAlertStatus(request_data) 
        
    
    def parseTravelAlertStatus(self, rdata):
        soup = BeautifulSoup(rdata,"html.parser")
        alert_content = soup.find_all(attrs={"class":"tsg-rwd-emergency-alert-text"})[0]
        alert_paras_tags = alert_content.find_all("p")
        alert_paras = [alert.text for alert in alert_paras_tags]
        alert_paras.pop()
        alert_paras.pop()
        alert_string = "\n".join(alert_paras)
        return alert_string
                

    
    async def fetch_link_info(self, session:aiohttp.ClientSession, link_idx):
        if link_idx >= len(self.travel_df.index):
            return " "
        
        try:
            async with session.get(self.travel_df.iloc[link_idx]["Link"]) as request_data:
                rdata = await request_data.text()
                if request_data.status == 200: return self.parseTravelAlertStatus(rdata)
                else: return ""
        except Exception as e:
            return ""


    async def fetch_advisories(self):
        """
        Fetches travel advisories from U.S. State Department website based on links in summary table of main page
        --Arguments: None
        --Returns: Advisories
        """
         
        async with aiohttp.ClientSession() as session:
            print("In main loop")
            task_list = [self.fetch_link_info(session, link_idx) for link_idx in range(0, len(self.travel_df.index))]
            result = await asyncio.gather(*task_list)
            print("End main loop")
            self.addColumn("Advisory Text",result)
            return result


    def addColumn(self, column_name, alist):
        self.travel_df[column_name] = alist
    
    def append_threat_level(self):
        """
        Appends country and threat level information to the summary table dataframe
        """

        if self.travel_df is None:
            raise ValueError("Advisories have not been loaded! Either pass a travelalert object or load advisories from an excel file first!")

        threat_level = []
        country = []
        for i in range(0, len(self.travel_df.index)):
            x = str(self.travel_df.iloc[i]["Level"]).split(" ")
            if len(x) > 1: threat_level.append(int(x[1].split(":")[0]))
            else: threat_level.append(0)
            country.append(str(self.travel_df.iloc[i]["Advisory"]).split(" ")[0])
        
        if "Threat Level" not in self.travel_df.columns:self.addColumn("Threat Level", threat_level)
        if "Country" not in self.travel_df.columns:self.addColumn("Country",country)

 

    


    

