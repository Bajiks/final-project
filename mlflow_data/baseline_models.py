#import pandas as pd
import numpy as np
#import mlflow
#from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
import pickle

# %%
class RS_baseline_usr_mov:
    def __init__(self, p):
        self.p = p
    def fit(self, df_scores_train):
        df_scores_train["user_id"] = df_scores_train["user_id"].apply(lambda x:int(x))
        self.mean_usr = df_scores_train.groupby("user_id").rating.mean()
        df_scores_train["movie_id"] = df_scores_train["movie_id"].apply(lambda x:int(x))
        self.mean_mov = df_scores_train.groupby("movie_id").rating.mean()
        self.mean = df_scores_train.rating.mean()
    def predict(self, X): #usr,mov
        scores = list()
        for row in X:
            if row[0] in self.mean_usr:
                usr = self.mean_usr[row[0]]
            else:
                usr = self.mean
            if row[1] in self.mean_mov:
                mov = self.mean_mov[row[1]]
            else:
                mov = self.mean
            scores.append(self.p*usr + (1-self.p)*mov)
        return np.array(scores)

    def score(self, X, y):
        y_pred = self.predict(X)
        return np.sqrt((y-y_pred)**2).mean()
    def save_model(self,filename):
        with open(filename, "wb") as f:
            pickle.dump([self.mean_usr, self.mean_mov, self.mean, self.p],f)

    @classmethod
    def load_model(cls, filename):
        with open(filename, "rb") as f:
            mean_usr, mean_mov, mean, p = pickle.load(f)
        model = RS_baseline_usr_mov(p)
        model.mean_usr = mean_usr
        model.mean_mov = mean_mov
        model.mean = mean
        model.p = p
        return model

class RS_baseline:
    def fit(self, df_scores_train):
        df_scores_train["user_id"] = df_scores_train["user_id"].apply(lambda x:int(x))
        self.mean_usr = df_scores_train.groupby("user_id").rating.mean()
        df_scores_train["movie_id"] = df_scores_train["movie_id"].apply(lambda x:int(x))
        self.mean_mov = df_scores_train.groupby("movie_id").rating.mean()
        self.mean = df_scores_train.rating.mean()
    def predict(self, X): #usr,mov
        scores = list()
        for row in X:
            scores.append(self.mean)
        return np.array(scores)

    def score(self, X, y):
        y_pred = self.predict(X)
        return np.sqrt((y-y_pred)**2).mean()
    def save_model(self,filename):
        with open(filename, "wb") as f:
            pickle.dump(self.mean,f)

    @classmethod
    def load_model(cls, filename):
        with open(filename, "rb") as f:
            mean = pickle.load(f)
        model = RS_baseline(p)
        model.mean_usr = mean_usr
        model.mean_mov = mean_mov
        model.mean = mean
        model.p = p
        return model
