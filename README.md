### Lisa Koutsoviti | TiU MSc Data Science Society | Assignments

This repository contains three assignments that were made as part of courses of the MSc Data Science and Society, Department of Humanities and Digital Sciences at Tilburg University. The pdf files include a description of our experiments and results including features used, learning model and algorithm, parameter tuning, description of method or system built and references.

- Assignment 1: Machine Learning Challenge

  This is a mandatory group-assignment that was created for the course Machine Learning during the spring semester of 2020. Team members were Mantas M., Hyun Seon P. and myself. Grade received was 9.5/10 which was worth 30% of the final grade. Achieved accuracy was 11%. We were among the first ten groups (out of 48 in total) that achieved the highest level of accuracy. 

  In this assignment there were two separate tasks. The first task (multiclass classification) was to train a model to recognize handwritten English letters (124800 images and labels, 4800 different images per label.

  In the second task (multilabel classification) we had to use the classifiers trained in the first task to identify a series of 5 letters in an image of size 30 × 150. These images were noisy. Example: The label for the first image is ‘2118161513’. The letters in the image are: ‘urpom’. We had to encode/decode the label as: u = 21, r = 18, p=16, o=15, m=13. We had to submit a csv file containing 5 predicted labels per image based on a probability distribution over the 26 letters.

      References

      [1] Original Dataset https://www.nist.gov/itl/products-and-services/ emnist-dataset

      [2] Gregory Cohen, Saeed Afshar, Jonathan Tapson, and Andre van Schaik EMNIST: an extension of MNIST to handwritten letter in: International Joint Conference on Neural Networks (IJCNN), 2017

- Assignment 2: Deep Learning 

  This is a mandatory group-assignment that was created for the course Deep Learning during the winter semester of 2020. Team members were Agapi V., Hyun Seon P. and myself. Grade received was 8.5/10 which was worth 30% of the final grade. The task was predicting whether an English sentence is an original English text or a (human) translation from French into English (classification). The provided data had been balanced. The final accuracy achieved was 77.35% (7th highest out of 54 groups). 

  The data provided consists of transcribed English speech. Some of these sentences were originally uttered in English (label 0), others were originally uttered in French and then translated by a human translator into English (label 1).

- Assignment 3: 

  This is a mandatory group-assignment that was created for the course Programming with R during the winter semester of 2020. Team members were Vira H., Trang L., Sue Y., Jennifer Z.L. and myself. Grade received was 10/10 which was worth 30% of the final grade. The teams had to chose a dataset and a reasearch topic and write a short research paper using R software environment. 
  
  We attempted to predict song popularity based on Kaggle’s Spotify dataset (Singh, 2020). We had to preprocess the data (cleaning, EDA) and fit models using the knn and logistic regression classifiers. Main packages used were dplyr, ggplot2 and caret. The highest accuracy score was 64% using logistic regression on the full set of attributes. 
