import pandas as pd



class Categories:
    def __init__(self):
        self.blazer = pd.read_csv('categories/Vision taxonomy - Blazers.csv')
        self.blouse = pd.read_csv('categories/Vision taxonomy - Blouse.csv')
        self.dresses = pd.read_csv('categories/Vision taxonomy - Dresses.csv')
        self.jumpsuits = pd.read_csv('categories/Vision taxonomy - Jumpsuits.csv')
        self.pants = pd.read_csv('categories/Vision taxonomy - Pants.csv')
        self.polo = pd.read_csv('categories/Vision taxonomy - Polo.csv')
        self.shirt = pd.read_csv('categories/Vision taxonomy - Shirt.csv')
        self.shorts = pd.read_csv('categories/Vision taxonomy - Shorts.csv')
        self.skirts = pd.read_csv('categories/Vision taxonomy - Skirts.csv')
        self.tshirts = pd.read_csv('categories/Vision taxonomy - T-shirt.csv')
        self.category_features = {}
        if len(self.category_features) < 1:
            self.initiate_category_features()


    def initiate_category_features(self):
        for i, row in self.blazer.iterrows():
            if "Blazers" not in self.category_features:
              self.category_features['Blazers'] = []
            self.category_features['Blazers'].append({row['Property']: row['Examples']})

        for i, row in self.blouse.iterrows():
            if "Blouse" not in self.category_features:
              self.category_features['Blouse'] = []
            self.category_features['Blouse'].append({row['Property']: row['Examples']})

        for i, row in self.dresses.iterrows():
            if "Dresses" not in self.category_features:
              self.category_features['Dresses'] = []
            self.category_features['Dresses'].append({row['Property']: row['Examples']})

        for i, row in self.jumpsuits.iterrows():
            if "Jumpsuits" not in self.category_features:
              self.category_features['Jumpsuits'] = []
            self.category_features['Jumpsuits'].append({row['Property']: row['Examples']})

        for i, row in self.pants.iterrows():
            if "Pants" not in self.category_features:
              self.category_features['Pants'] = []
            self.category_features['Pants'].append({row['Property']: row['Examples']})

        for i, row in self.polo.iterrows():
            if "Polo" not in self.category_features:
              self.category_features['Polo'] = []
            self.category_features['Polo'].append({row['Property']: row['Examples']})

        for i, row in self.shirt.iterrows():
            if "Shirts" not in self.category_features:
              self.category_features['Shirts'] = []
            self.category_features['Shirts'].append({row['Property']: row['Examples']})

        for i, row in self.shorts.iterrows():
            if "Shorts" not in self.category_features:
              self.category_features['Shorts'] = []
            self.category_features['Shorts'].append({row['Property']: row['Examples']})

        for i, row in self.skirts.iterrows():
            if "Skirts" not in self.category_features:
              self.category_features['Skirts'] = []
            self.category_features['Skirts'].append({row['Property']: row['Examples']})
        
        for i, row in self.tshirts.iterrows():
            if "T-shirt" not in self.category_features:
              self.category_features['T-shirt'] = []
            self.category_features['T-shirt'].append({row['Property']: row['Examples']})       

    def get_category_features(self, categories):
       unique_features = []

       for category in categories:
          unique_features.append({
             "category_name": category,
             "category_features": self.category_features[category]
             })
        
       return unique_features
    

# categories = Categories()
# categories_list = ["Dresses"]

# x = categories.get_category_features(categories=categories_list)
# for a in x:
#   print(a)
#   print('\n\n')