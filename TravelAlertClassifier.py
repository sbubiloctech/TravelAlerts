from TravelAlert import TravelAlert
from TravelAlert import TravelAlert
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords 
from string import punctuation, printable
from nltk import WordNetLemmatizer
from tqdm import tqdm
from pandas import DataFrame, read_excel


class TravelAlertClassifier:
    def __init__(self, ta_obj: TravelAlert = None):
        self.country = None
        self.travelAlert = TravelAlert() if not ta_obj else ta_obj
        self.advisory_sents = None
        self.clean_advisory = None

    def load_from_excel(self, filename):
        self.travelAlert.load_from_excel(filename)
        self.travelAlert.append_threat_level()

    def update_Country(self, country:str):
        if country == None or not country.isalpha(): raise ValueError("Please check country name.")

        correct_country = country.lower().capitalize()
        if self.travelAlert == None: raise ValueError("Please update Travel Alerts first! Please load from an excel file or pass it to the Classifier object.")
        
        if not (self.travelAlert.travel_df["Country"] == correct_country).any(): raise ValueError("Country does not exist in Travel Advisories.")

        self.country = correct_country
        self.parseCountryTravelAlert()
    
    def parseCountryTravelAlert(self):
        advisory = self.travelAlert.travel_df["Advisory Text"][self.travelAlert.travel_df["Country"] == self.country].values[0]
       
        self.advisory_sents = sent_tokenize(advisory)
        token_word_advisory = [word_tokenize(sent) for sent in self.advisory_sents]
        punctuation_list = list(punctuation)
        stop_words = stopwords.words("english")

        word_advisory = []
        for sent in token_word_advisory:
            word_advisory.append([word for word in sent if word not in stop_words 
                                  and word not in punctuation_list])

        lemmatizer = WordNetLemmatizer()
        self.clean_advisory = []
        for sent in word_advisory:
            self.clean_advisory.append([lemmatizer.lemmatize(word) for word in sent])

    def classifySents(self):
        if self.clean_advisory == None or self.clean_advisory == "": return None

        level_word_list = []
        for i in range(1, 5):
            filename = "Level" + str(i) + "Analysis.xlsx"
            try:
                level_df = read_excel(filename)
                level_word_list.append(level_df["Word"].to_list())
            except Exception as e:
                level_word_list.append([])
                continue
        
        self.classifiedSents = {"Level1":[], "Level2":[], "Level3": [], "Level4": []}
        for i in range(0, len(self.clean_advisory)):
            level = 1
            for word in self.clean_advisory[i]:
                for j in range(3,0,-1):
                    level = j + 1 if word in level_word_list[j] and level < (j+1) else level
            
            for j in range(1, 5):
                if j == level: self.classifiedSents["Level" + str(level)].append(self.advisory_sents[i])
                else: self.classifiedSents["Level" + str(j)].append(" ")   

        # for j in range(1, 5): print(f'Level{j}: {len(self.classifiedSents["Level"+str(j)])}')
        classifiedSents_df = DataFrame(self.classifiedSents)
        filename = self.country + ".xlsx"
        classifiedSents_df.to_excel(filename)



            
            

