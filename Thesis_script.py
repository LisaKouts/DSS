# -*- coding: utf-8 -*-
"""Bias Quantification Fuzzy-rough sets.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qlQIu_3If2YROmF7UfOqgyuD-pkeP2jj
"""

"""## 1. Setting up"""

import pandas as pd
from itertools import chain, permutations, combinations, product
import numpy as np
import collections
import itertools
import shelve
import math
import seaborn as sns
sns.set_style("white")
import skfuzzy as fuzz
import matplotlib
matplotlib.use("pgf")
matplotlib.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})
import matplotlib.pyplot as plt
from numpy import linalg as la
from sklearn import preprocessing
from sklearn.neighbors import DistanceMetric
from sklearn.neighbors.kde import KernelDensity
from scipy.spatial import distance
import copy
import pytest
import time
from scipy.spatial.distance import euclidean, pdist, squareform
from collections import Counter
from scipy.stats import mode

# German
df = pd.read_csv('/content/drive/My Drive/Thesis/Bias quantification/datasets/German_r.csv')
df = df.drop(['Unnamed: 0'],axis=1)
baseline_metrics = pd.read_csv('/content/drive/My Drive/Thesis/Bias quantification/datasets/Metrics.csv')
baseline_metrics = baseline_metrics.set_index('Protected_attribute')
#coding target var
df['cost_matrix'] = df['cost_matrix'].replace(1,0)
df['cost_matrix'] = df['cost_matrix'].replace(2,1)

# Compas
df_compas = pd.read_csv('/content/drive/My Drive/Thesis/Bias quantification/datasets/Compas_r_noagecat.csv')
df_compas = df_compas.drop(['Unnamed: 0'],axis=1)

"""## 2. Preprocessing"""

class PreProc:

    def __init__(self, datfr):
        self.datfr = datfr
        self.cat = pd.DataFrame()

    def make_df(self):
        num, self.cat, colnum, colcat = self.split_cat_num_df(self.datfr)
        cat2 = copy.deepcopy(self.cat)

        # replacing NAs with None
        for i in self.cat:
            self.cat[i].fillna('None', inplace=True)

        # normalizing the numerical vars
        num_norm = self.regul_num(colnum, num)
        # label encoding & normalizing cat vars
        cat_norm = self.scal_reg_cat(self.cat,colcat)

        # First df - all numeric
        df_reg_full= pd.concat([cat_norm,num_norm], axis = 1)
        # Second df - categoricals left intact & normalized numericals
        df_cat_reg_full = pd.concat([cat2,num_norm], axis = 1)

        # Reordering based on the target variable
        one = df_reg_full[df_reg_full[df_reg_full.columns[-1]] == 0.]
        two = df_reg_full[df_reg_full[df_reg_full.columns[-1]] == 1.]
        df_catreg_ord_full = pd.concat([one,two])

        one_cat = df_cat_reg_full[df_cat_reg_full[df_cat_reg_full.columns[-1]] == 0.]
        two_cat = df_cat_reg_full[df_cat_reg_full[df_cat_reg_full.columns[-1]] == 1.]
        df_catreg_ord_full_mix = pd.concat([one_cat,two_cat])
        
        return df_catreg_ord_full, df_catreg_ord_full_mix

    # spliting the dataframe into categorical and numerical vars
    def split_cat_num_df(self, datfr):
        df_num = pd.DataFrame()
        for i in self.datfr:
            if isinstance(self.datfr[i][1],np.int64):
                df_num[i] = self.datfr[i]
        df_colnames_num = list(df_num.columns)

        df_cat = pd.DataFrame()
        for i in self.datfr:
            if isinstance(self.datfr[i][1],str):
                df_cat[i] = self.datfr[i]
        df_colnames_cat = list(df_cat.columns)
        
        return df_num, df_cat, df_colnames_num, df_colnames_cat

    def regul_num(self, df_colnames_num, df_num):
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(df_num.values)
        df_num_norm = pd.DataFrame(x_scaled)
        df_num_norm.columns = df_colnames_num
          
        return df_num_norm

    def scal_reg_cat(self, df_cat, df_colnames_cat):
        # label coding
        le = preprocessing.LabelEncoder()
        for i in df_cat:
                if isinstance(df_cat[i][1],str):
                    df_cat[i]  = le.fit_transform(df_cat[i])
        # regularizing
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(df_cat.values)
        dfcat_reg = pd.DataFrame(x_scaled)
        dfcat_reg.columns = df_colnames_cat

        return dfcat_reg

_, df_mix = PreProc(df).make_df() # sex&marital_cat # age
_, compas_mix = PreProc(df_compas).make_df() # sex # race

"""## 3. Fuzzy-rough set algorithm"""

class FRS_Mix:

    def __init__(self, df):

        self.df = df
        self.X = df.values
        self.D = None
        self.N = None
        self.C = None
        self.my_dic = {}
        self.sim_instance_with_instance_num = pd.DataFrame()
        self.sim_instance_with_instance_cat = pd.DataFrame()
        self.lab = []
        self.normalized_distance = 0

    def regions(self):
        
        self.D = np.unique(self.X[:,-1])

        POS = np.zeros((len(self.D), len(self.X)))
        NEG = np.zeros((len(self.D), len(self.X)))
        BND = np.zeros((len(self.D), len(self.X)))

        ## Dividing the dataframe into Numeric vars & Cat vars
        # Crate a boolean vector for cat & num columns
        for i in self.df:
            if isinstance(self.df[i][1],str):
                self.lab.append(True)
            else:
                self.lab.append(False)
        
        # Aggregate the boolean values
        content = Counter(self.lab)
        X_num, X_cat = self.X[:,-content[False]:], self.X[:,:content[True]]

        ## Numeric vars preproc.

        # Prototype for each decision class
        self.C = np.zeros((len(self.D), X_num.shape[1]))
        for k in range(len(self.D)):
            self.C[k] = (X_num[X_num[:,-1] == k]).mean(0)

        ## Similarity of every instance with one another
        self.sim_instance_with_instance_cat = squareform(pdist(
            pd.DataFrame(X_cat), self.intersection))
        self.sim_instance_with_instance_num = squareform(pdist(
            pd.DataFrame(X_num), self.similarity_num))
        dimensions = self.sim_instance_with_instance_num.shape[0]
        self.mat_all = 1 - ((self.sim_instance_with_instance_num + 
                              self.sim_instance_with_instance_cat)/
                            (self.X.shape[1]-1)) 
        self.my_dic['instance_with_instance'] = self.mat_all
        
        # similarity between instances and each class
        for k in range(len(self.D)):
            # num sim with class
            dists_class = np.zeros(shape=(len(self.X)))
            y = self.C[k][:-1]
            for x,idx in zip(X_num,range(len(self.X))):
                dists_class[idx] = np.sum(np.absolute(x[:-1] - y))

            # cat sim with class
            cat_class = np.zeros(shape=(len(self.X)))
            y = mode(X_cat[self.X[:,-1]==k])[0][0]
            for x,idx in zip(X_cat,range(len(self.X))):
                cat_class[idx] = self.intersection(x,y)
            
            self.my_dic[k] = 1.0 - ((dists_class + cat_class)/
                                    (self.X.shape[1]-1))

        for k in range(len(self.D)):
            for idx in range(len(self.X)):
                POS[k][idx], NEG[k][idx], BND[k][idx] = self.process_object(idx, k)

        return POS, NEG, BND, self.my_dic

    def process_object(self, idx, k):

        inf = 1
        sup = 0

        mem_x_k = self.membership(idx, k)

        for index in range(len(self.X)):

            sim_x_y = self.my_dic['instance_with_instance'][idx][index] 
            mem_y_k = self.membership(index, k)

            inf = min(inf, self.implicator(mem_x_k * sim_x_y, mem_y_k))
            sup = max(sup, self.conjunction(mem_y_k * sim_x_y, mem_y_k))

        inf = min(inf, mem_x_k)
        sup = max(sup, mem_x_k)

        return inf, 1-sup, sup-inf

    def similarity_num(self, x, y):
        return np.sum(np.absolute(x[:-1] - y[:-1]))
    
    def intersection(self, x, y):
        sum_sim = 0
        for i,u in zip(x,y):
            if i != u:
                sum_sim += 1
        return sum_sim

    def implicator(self, a, b):
        return min(1 - a + b, 1)

    def conjunction(self, a, b):
        return max(a + b - 1, 0)

    def membership(self, idx, k):
        
        sim_x_Ck = self.my_dic[k][idx]  
        acc = sim_x_Ck

        for j in range(len(self.D)):
            if j == k:
                pass
            else:
                acc = acc + self.my_dic[j][idx]
            
        value = (sim_x_Ck / acc)   
        return (1 + value)/2 if self.X[idx:idx+1,-1] == k else value/2

def fuzzy_regions_maker(df,algorithm,prot_attr1,prot_attr2):

    POS, NEG, BND, data_full = algorithm(df).regions()

    # removing the protected attribute sex 
    cols = list(df.columns)
    cols.remove(prot_attr1)
    POS_PA1, NEG_PA1, BND_PA1, data_PA1 = algorithm(df[cols]).regions()

    # removing the protected attribute age 
    cols = list(df.columns)
    cols.remove(prot_attr2)
    POS_PA2, NEG_PA2, BND_PA2, data_PA2 = algorithm(df[cols]).regions()

    Mix = {}
    Mix['full'] = [POS, NEG, BND]
    Mix[prot_attr1] = [POS_PA1, NEG_PA1, BND_PA1]
    Mix[prot_attr2] = [POS_PA2, NEG_PA2, BND_PA2]

    return Mix

my_dic = fuzzy_regions_maker(df_mix, FRS_Mix,'sex&marital_cat','age')
my_compas = fuzzy_regions_maker(compas_mix, FRS_Mix,'sex','race')

"""## 4. Vizualizing"""

# Vizualization function
def vizual(region_mat,reg,att_set):
    
    fig, axes = plt.subplots(1, 2, figsize=(19, 4.5))

    for i in range(len(region_mat[0])):
        ax = axes.reshape(-1)[i]
        ax.set_xlabel('$x \in \mathcal{X}$ of class ' + str(i)+' attribute set: '+att_set, fontsize=20)
        ax.set_ylabel('membership', fontsize=20)

        ax.plot(region_mat[0][i])
        ax.plot(region_mat[1][i])
        ax.plot(region_mat[2][i])
        
        ax.legend(["$POS$", "$NEG$", "$BND$"])
        
    #fig.set_size_inches(w=4.7747, h=3.5) - maybe play around with this
    fig.savefig("Reg"+reg+".pgf")

my_dic['sexgerman'] = my_dic['sex&marital_cat']
del my_dic['sex&marital_cat']

# German dataset
for att_set,reg in zip(my_dic,['POS','NEG','BND']):
    vizual(my_dic[str(att_set)],reg,att_set)

# Compas dataset
for att_set,reg in zip(my_compas,['POS','NEG','BND']):
    vizual(my_compas[att_set],reg,att_set)

def comparison_df(diction):
  compare_dic = {}
  
  regions = ['POS','NEG','BND']
  for att_set in diction:
    compare = pd.DataFrame()
    for region in range(len(diction[att_set])):
      for dec_class in range(len(diction[att_set][region])):
        title = regions[region]+'_class'+str(dec_class)
        compare[title] = diction[att_set][region][dec_class]
    compare_dic[att_set] = compare
  return compare_dic

print(comparison_df(my_compas)['full'].loc[3360:3365].to_latex(index=True,multicolumn_format=True))
print(comparison_df(my_compas)['race'].loc[3360:3365].to_latex(index=True,multicolumn_format=True))
print(comparison_df(my_compas)['sex'].loc[3360:3365].to_latex(index=True,multicolumn_format=True))

"""## 5. Local change measures

"""

def overlap(all,attributes):
  dic = {}
  
  for protected in attributes:
    dic[protected] = {}
    #norm = np.sum()
    for region,name in zip(range(np.array(all['full']).shape[0]),["POS_change","NEG_change","BND_change"]):
      # Positive to Positive
      if region == 0:
        # class0
        nom = np.sum(np.abs(np.minimum(all['full'][region][0],all['full'][region][1]) - np.minimum(all['full'][region][0],all[protected][region][1])))
        denom =  np.sum(np.maximum.reduce([all['full'][region][0],all['full'][region][1],all[protected][region][1]]))
        dic[protected][str(name+' class0')] = nom / denom
        # class1
        nom = np.sum(np.abs(np.minimum(all['full'][region][1],all['full'][region][0]) - np.minimum(all['full'][region][1],all[protected][region][0])))
        denom =  np.sum(np.maximum.reduce([all['full'][region][1],all['full'][region][0],all[protected][region][0]]))
        dic[protected][str(name+' class1')] = nom / denom
      elif region == 2:
        # class0
        nom = np.sum(np.abs(np.minimum(all['full'][0][0],all['full'][region][1]) - np.minimum(all['full'][region][0],all[protected][region][1])))
        denom =  np.sum(np.maximum.reduce([all['full'][region][0],all['full'][region][1],all[protected][region][1]]))
        dic[protected][str(name+' class0')] = nom / denom
        # class1
        nom = np.sum(np.abs(np.minimum(all['full'][0][1],all['full'][region][0]) - np.minimum(all['full'][region][1],all[protected][region][0])))
        denom =  np.sum(np.maximum.reduce([all['full'][0][1],all['full'][region][0],all[protected][region][0]]))
        dic[protected][str(name+' class1')] = nom / denom
      else:
        pass
  return dic

theta_overlap_german = pd.DataFrame(overlap(my_dic,['age','sex&marital_cat']))
theta_german = theta_overlap_german.T
theta_german

theta_overlap_compas = pd.DataFrame(overlap(my_compas,['race','sex']))
theta_compas = theta_overlap_compas.T
theta_compas

"""## 6. Global change measures"""

def glob(all,attributes):
  dic = {}
  for protected in attributes:
    dic[protected] = {}
    for region,name in zip(range(np.array(all['full']).shape[0]),["POS_change","NEG_change","BND_change"]):
      # class 0
      nom = np.sum(np.abs(all['full'][region][0] - all[protected][region][0]))
      denom = (max(np.maximum(all['full'][region][0],all[protected][region][0])) - min(np.minimum(all['full'][region][0],all[protected][region][0])))*all['full'][0][0].shape[0]
      class0 = nom / denom
      # class 1
      nom = np.sum(np.abs(all['full'][region][1] - all[protected][region][1]))
      denom = (max(np.maximum(all['full'][region][1],all[protected][region][1])) - min(np.minimum(all['full'][region][1],all[protected][region][1])))*all['full'][0][0].shape[0]
      class1 = nom / denom
      # sum
      dic[protected][str(name+' sum')] = class0 + class1
  return dic

omega_comp = pd.DataFrame(glob(my_compas,['race','sex']))
omega_comp=omega_comp.T
omega_comp

omega_ger = pd.DataFrame(glob(my_dic,['age','sex&marital_cat']))
omega_ger=omega_ger.T
omega_ger
