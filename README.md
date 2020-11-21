# DSS_Assignments

This repository contains three assignments that were made as part of courses of the MSc Data Science and Society, Department of Humanities and Digital Sciences at Tilburg University.

- Assignment 1: Machine Learning Challenge

This is a mandatory group-assignment that was created for the course Machine Learning during the spring semester of 2020. Team members were Mantas M., Hyun Seon P. and myself. Grade received was 9.5/10 which was worth 30% of the final grade.
The pdf file includes a description of our experiments and results including features used, learning model and algorithm, parameter tuning, description of method or system built to perform classification and references.

In this assignment there are two separate tasks. The first task (multiclass classification) is to train a model to recognize handwritten English letters (EMNIST dataset). The training dataset consists of images of handwritten English alphabets and the corresponding label. The data consist of 124800 images and labels in total. For each label 4800 different images are available.

In the second task (multilabel classification) we had to use the classifiers trained in the first task to identify a series of 5 letters in an image of size 30 × 150. However, compared to the training images, these images are noisy each consisting of a series letters. Example: The label for the first image is ‘2118161513’. The letters in the image are: ‘urpom’. We had to encode/decode the label as: u = 21, r = 18, p=16, o=15, m=13.

In this task we were judged based on top-5-accuracy.test-dataset. The test dataset is a list of 10000 images. For each image the designed classifier had to make 5 predictions. We had to submit a csv file containing 5 predicted labels separated by comma for each image. For task 2, we first had to make the classifier build in the task 1 robust against noise. We added noise to the train images and trained a new classifier on that. The output of such a classifier was a probability distribution over the 26 letters. We used the sliding window to recognise each letter in the image.

References

[1] Original Dataset https://www.nist.gov/itl/products-and-services/ emnist-dataset

[2] Gregory Cohen, Saeed Afshar, Jonathan Tapson, and Andre van Schaik EMNIST: an extension of MNIST to handwritten letter in: International Joint Conference on Neural Networks (IJCNN), 2017
