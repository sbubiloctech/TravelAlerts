from TravelAlert import TravelAlert
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords 
from string import punctuation
from nltk import WordNetLemmatizer
from tqdm import tqdm
from pandas import DataFrame, read_excel
import os

class AnalyzeTravelAlerts:
    def __init__(self, ta_obj:TravelAlert = None):
        self.travelAlert = TravelAlert() if not ta_obj else ta_obj
        self.word_dicts = None
        self.advisory_sents = []
        self.clean_advisories = None
        

    def load_from_excel(self, filename):
        self.travelAlert.load_from_excel(filename)

    def clean_tokenize_alerts(self):
        if self.travelAlert.travel_df is None:
            raise ValueError("Advisories have not been loaded! Either pass a travelalert object or load advisories from an excel file first!")
        
        lemmatizer = WordNetLemmatizer()
        clean_advisories = []
        punctuation_list = list(punctuation)
        stop_words = stopwords.words("english")
        for i in tqdm(range(0, len(self.travelAlert.travel_df.index)),desc="Cleaning advisories..."):
            advisory_sents = sent_tokenize(self.travelAlert.travel_df.iloc[i]["Advisory Text"])
            advisory_word_tokenize = [word_tokenize(sent) for sent in advisory_sents]
            advisory_words = []
            for sent in advisory_word_tokenize:
                advisory_words.append([lemmatizer.lemmatize(word.lower()) for word in sent 
                                       if word not in punctuation_list and word not in stop_words])
            clean_advisories.append(advisory_words)
        return clean_advisories
    
    def generate_advisory_stats(self, clean_advisories = None):
        if self.travelAlert.travel_df is None:
            raise ValueError("Advisories have not been loaded! Either pass a travelalert object or load advisories from an excel file first!")
        
        self.travelAlert.append_threat_level()
        
        word_dicts = []
        if clean_advisories is None: clean_advisories = self.clean_tokenize_alerts()

        for advisory in clean_advisories:
            x = self.merge_advisory(advisory)
            word_dicts.append(self.summarize_advisory(x))
        self.word_dicts = word_dicts
        return word_dicts
    
    def merge_advisory(self, advisory):
        words = [word for sent in advisory for word in sent]
        return words
    
    def summarize_advisory(self, advisory):
        word_key = set(advisory)
        advisory_dict = dict([(word, advisory.count(word)) for word in word_key])
        return advisory_dict
    
    def analyze_level(self, level = 1):
        if self.travelAlert.travel_df is None:
            raise ValueError("Advisories have not been loaded! Either pass a travelalert object or load advisories from an excel file first!")

        if self.word_dicts is None: self.generate_advisory_stats()

        if level > 1:
            level_df = self.generate_level_df(level)
            for lower_level in tqdm(range(level-1, 0, -1),desc="Removing previous advisory elements..."):
                filename = "Level" + str(lower_level) + "Analysis.xlsx"
                if not os.path.exists(filename): self.analyze_level(lower_level)
                ll_keys = read_excel(filename)["Word"].to_list()
                for key in ll_keys: level_df = level_df.drop(level_df[level_df["Word"] == key].index) 
                    
            filename = "Level" + str(level) + "Analysis.xlsx"
            level_df.to_excel(filename)
        else:
            l1_df = self.generate_level_df(1)
            l1_df.to_excel("Level1Analysis.xlsx")
            
    def generate_level_df(self, level = 1):
        l1_list = self.travelAlert.travel_df.index[self.travelAlert.travel_df["Threat Level"] == level].to_list()
        l1_dict = {}
        for i in l1_list:
            keys = self.word_dicts[i].keys()
            for key in keys:
                l1_dict[key] = l1_dict[key] + self.word_dicts[i][key] if key in l1_dict else self.word_dicts[i][key] 

        l1_df = DataFrame({"Word":l1_dict.keys(), "Counts":l1_dict.values()})
        word_total = l1_df["Counts"].sum()
        l1_df["Percentage"] = l1_df["Counts"] / word_total * 100
        l1_df.sort_values(by=["Percentage"], inplace=True, ascending=False)
        cdf = []
        for i in range(0, len(l1_df.index)):
            cdf.append(l1_df.iloc[i]["Percentage"] if i == 0 else l1_df.iloc[i]["Percentage"] + cdf[i-1])
        l1_df["CDF"] = cdf
        l1_df = l1_df.drop(l1_df[l1_df["CDF"] > 80].index)
        return l1_df





