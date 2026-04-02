2023 International Conference on Electrical, Computer and Communication Engineering (ECCE)

# Detection of Colon Cancer Using Inception V3 and Ensembled CNN Model

**Ishrat Jahan Swarna**  
*Department of Computer Science and Engineering*  
*Rajshahi University of Engineering and Technology*  
*Rajshahi, Bangladesh*  
ishratswarna887@gmail.com

**Emrana Kabir Hashi**  
*Department of Computer Science and Engineering*  
*Rajshahi University of Engineering and Technology*  
*Rajshahi, Bangladesh*  
emranakabir@gmail.com

---

**Abstract—Colon cancer is one of the most prevalent types of cancer. Early diagnosis of colon cancer can lead to an increased chance of successful treatment with less cost. To speed up this process deep learning can provide very useful and effective approaches. In this thesis work, two types of models were developed to classify colon cells from image data - one is the transfer learning model where a deep network Inception V3 is used as the pre-trained model and the other one is an Ensembled model which combines predictions of three simple sequential CNN models. To develop these models, 10k images were used from the LC25000 dataset and a very small Warwick-QU dataset having only 165 images was used to provide new data for retraining and testing purposes. Both models achieved a high result for the first dataset with 99.4% and 99.95% accuracy respectively, where Inception V3 showed 94.545% accuracy on new data from Warwick-QU after retraining and Ensembled model showed 78.182% accuracy. This approach can be used in research in the field of early and effective detection of colon cancer with a larger amount of varying images and more preprocessing methods to reduce overfitting and to make the model perform well in various types of images.**

**Index Terms—colon cancer, Inception V3, ensemble, deep learning, image classification.**

---

## I. INTRODUCTION

Colon cancer, also known as colorectal cancer is a type of cancer where cells of colons in our large intestine get affected. In the United States in 2022, there will be 106,180 new instances of colon cancer and 44,850 new cases of rectal cancer, as reported by the American Cancer Society. Colorectal cancer is the second most prevalent cause of cancer-caused fatalities in the United States and is in third place overall. It is predicted to result in 52,580 fatalities in 2022 [1]. Certain colorectal tumors may exist without showing any symptoms. To identify issues early, it is crucial to conduct routine colorectal screenings (examinations). The most effective screening test is a colonoscopy. Fecal occult blood tests, fecal DNA tests, flexible sigmoidoscopy, barium enema, and CT colonography are further screening methods (virtual colonoscopy). Your risk factors, particularly a genetic link of colon and rectal cancers, will determine when such screening tests start and at what age [2]. In medicinal practice, pathologists visually examine changes in cells/tissue underneath a microscope and define the level of colon cancer. However, expert pathologists frequently dispute network classifications. So we can conclude that a histopathological appraisal’s performance by expert pathologists alone is not sufficient [3]. Presently AI has a significant impact on disease diagnosis. A supervised Deep Learning model can make decisions based on results from previous experiences. Although extensive data/information is needed to get an accurate result, these techniques have created an effective alternative to all conventional methods. So a well-performed image classification model will introduce an alternate path in the diagnosis of colon cancer which will lead to the efficient management of colon cancer. Therefore to make early detection of colon cancer more effective, in our work, we tried to develop a deep learning model that detects cancer from image data of colon cells by classifying them into 2 classes ––

(i) Colon Adenocarcinoma (cancerous) and  
(ii) Colon Benign Tissue (non-cancerous).

![Fig. 1: Sample images of colon cancerous cells(on left) and colon non-cancerous cells(on right)](https://placeholder.com/figure1)
*Fig. 1: Sample images of colon cancerous cells (on left) and colon non-cancerous cells (on right)*

We made an effort to introduce two distinct models: one that uses transfer learning and the other that uses ensemble. Three CNN models were chosen for ensembling to make the process simple. In order to expose the models to a variety of data, they were trained on two different datasets.

---

## II. RELATED WORKS

For colon cancer cell detection various classification models have been built on different datasets till today. But most of them used the LC25000 dataset which is available online. And many models have been worked on both Lung and colon cells as this dataset contains both. A.H. Chehade et al. [4] worked on this dataset with five different models. Among them, XGBoost achieved the best accuracy of 99% for the classification of 5 subtypes of colon and lung cancer with 99.3% accuracy for the classification of colon cancer. Z Tasnim et al. [5] also chose the same dataset but only worked with 10k images of colon cells. In their work, the CNN algorithm with max and average pooling layers showed high accuracy of 97.49% and 95.48% respectively. A transfer learning MobileNetV2 model achieved a high accuracy of 99.67%. Using CNN and DIP techniques Masud et al. [6] built a classification model which showed a detection accuracy of up to 96.33% for cancer tissues on this dataset. In another work on this dataset, Garg et al. [7] used 8 different pre-trained models and their accuracy was 97% to 100%. Bukhari et al. [8] used LC25000 for training and validation and used another dataset CRAG for training and testing the multiple models they built. Among them, ResNet-50 showed 93.91% accuracy.

D. Sarwinda et al. [3] used a small Warwick-QU dataset to develop two ResNet architectural models and ResNet-50 showed higher accuracy than ResNet-18 where Resnet-50 and Resnet-18 had an accuracy of 88% and 85% respectively when train-test data distribution was like 80%:20%. In the research of Toraman et al. [9] Fourier Transform Infrared (FTIR) spectroscopy signals were used to categorize the probability of colon cancer. After collecting statistical characteristics from the signals they used SVM and ANN to classify the data. For ANN the accuracy was 95.71%.

In the proposed work, both models were retrained using a different dataset after being trained on a large amount of data. Despite the fact that the second dataset only contains a very tiny amount of data, we enhanced it and used it for testing. Thus, various data are supplied to the models, making them more reliable and efficient.

---

## III. METHODOLOGY

A workflow diagram shows all the steps followed in the experiment in an ordered way. As for our work, The process starts with collecting/loading data from publicly available datasets. Then it includes preprocessing the data to make it eligible for the models. Then it follows the implementation of classification models and performance evaluation for those models. Fig. 2 shows all the steps followed in the experiment in an ordered way.

### A. Dataset Description

In this work two online available datasets were used.

**Lung and Colon Cancer Histopathological Image Dataset (LC25000) published in 2019 [10]:** This dataset contains total 25000 images of 5 different classes for both lungs and colon. Therefore only 10000 colon images of two class: Colon Adenocarcinoma and colon benign were used Each class contains 5000 images. The image size 768 × 768 pixels is same for all images.

**Colorectal gland images from Warwick-QU dataset [11]:** This dataset is of total 165 images of two class: Colon Adenocarcinoma and colon Benign. For colon Adenocarcinoma there are 91 images and for colon Benign tissue it has 74 images. So the dataset is not well distributed. And the images size also differs from 567 × 430 to 775 × 522 pixels.

### B. Data Preprocessing

To prepare data for the next step, the following tasks were performed:

*   **File Conversion:** Images in dataset-2 were in .bmp format. They were converted into .jpeg format to match with the format in dataset 1.
*   **Data split:** Dataset-1: 80:20, Dataset-2: 40:60. Dataset 1 was used for model training and validation. And so dataset-1 was split at ratio 80%:20% ie. 8000:2000 images. To make the model predict most accurate results, it can be retrained with new and up-to-date data without altering the parameters and variables. Dataset-2 was used to provide new data and for retraining and testing purpose. And so it was split into 2 sets at the ratio of 40%:60%. We tried to provide more data for testing because the main goal is to test the model’s performance.
*   **Dataset Balancing:** In dataset 2, there are 91 images of colon_aca and 74 of colon_n. In order to avoid a biased model, we balanced this dataset by doing oversampling. As we only used this dataset for retraining and testing purpose, we performed data augmentation to colon_n images after data splitting in order to make equal number of images in both classes.
*   **Resizing & Rescaling:** Images in both datasets are resized into 224 × 224 pixels and then rescaled.
*   **Data Augmentation:** we have used ImageDataGenerator from keras for run-time data augmentation.

| Total=165 | Colon_ACA | Colon_N |
| :-------- | :-------- | :------ |
| Train     | 36        | 29      |
| Test      | 55        | 45      |

**TABLE I: Dataset 2 before balancing**

| Total=182 | Colon_ACA | Colon_N |
| :-------- | :-------- | :------ |
| Train     | 36        | 36      |
| Test      | 55        | 55      |

**TABLE II: Dataset 2 after Balancing**

### C. Classification Models

To develop the models in this work, four steps were followed. Fig. 3 shows the process. At first they were trained and validated on LC25000 dataset and then they were retrained and tested on new data from Warwick_QU dataset.

---

![Fig. 2: Workflow diagram](https://placeholder.com/figure2)
*Fig. 2: Workflow diagram*

![Fig. 3: Steps in developing models](https://placeholder.com/figure3)
*Fig. 3: Steps in developing models*

| Parameters         | Values     |
| :----------------- | :--------- |
| horizontal_flip    | True       |
| brightness_range   | [0.7, 1.3] |
| width_shift_range  | 0.2        |
| height_shift_range | 0.2        |
| fill_mode          | nearest    |

**TABLE III: Data Augmentation used in this work**

#### 1) Inception V3:
To develop the transfer learning model Inception V3 was used as a pre-trained model. First, the pre-trained model was loaded without including the topmost layer. All convolutional layers in the pre-trained model were frozen during training because we wanted to keep the weights unchanged and just wanted to train the top layers. The last layer was flattened into a single array and then two dense layers were added. The last layer contains 2 neurons with a ‘softmax’ activation function. Each neuron represents one class in our work. To compile this model, we used ‘categorical_crossentropy’ as the loss function and ‘adam’ as the optimizer. And 8 epochs were used to train this model. Once the model was trained and validated on dataset 1, we tried to test our model. And as there were differences in the two datasets we used, we had to retrain our model to be adjusted to the new data. For retraining our model we used only 40% of the new data ie. 72 images belonging to two classes. The developed model was saved after training on dataset 1, and at this stage, it was loaded and we started to retrain this model with the previously saved weights. Once the retraining process was completed, we tested the final model on 60% of dataset 2. We evaluated the performance of these new 110 images and all the findings were noted.

#### 2) Weighted Average Ensemble:
Ensemble learning is an approach to increase performance by taking the predictions from multiple models and using a combination of them to make the best prediction. Though there are variations in this technique the general idea is the same. And by following that we can build a Weighted Average Approach where firstly the predictions of each model were multiplied by the weight corresponding to that model and then the final result was calculated by averaging them. These weights act as the significance of the models in predicting results that are close to the true values. The best combination of weights for each model was found by performing a grid search. To develop the Ensembled CNN model for this work we followed a similar approach mentioned earlier in Inception V3. But at this time we had to develop three different sequential CNN models first and they were ensembled together to get the best of them.

*   CNN Model-1 with 6 convolutional layers.
*   CNN Model-2 with 6 convolutional layers but different architecture.
*   CNN Model-3 with 7 convolutional layers.

|                         | CNN Model-1                     | CNN Model-2                     | CNN Model-3                     |
| :---------------------- | :------------------------------ | :------------------------------ | :------------------------------ |
| Loss function           | categorical\_crossentropy       | categorical\_crossentropy       | categorical\_crossentropy       |
| Optimizer               | adam                            | adam                            | adam                            |
| Activation function     | softmax(last layer), relu(rest) | softmax(last layer), relu(rest) | softmax(last layer), relu(rest) |
| Learning rate           | 0.001                           | 0.001                           | 0.001                           |
| No of Conv2D layers     | 6                               | 6                               | 7                               |
| No of filters in Conv2D | [64, 128, 128, 64, 32, 32]      | [64, 128, 128, 64, 32, 32]      | [64, 64, 128, 128, 64, 32, 32]  |
| No of Dropout layers    | 3                               | 4                               | 4                               |
| No of Dense layers      | 1                               | 3                               | 1                               |
| No of epoch             | 12                              | 15                              | 13                              |

**TABLE IV: Layers and parameters in CNN models**

### D. Performance Evaluation

To evaluate the models some performance evaluation metrices were used such as- accuracy, precision, recall/sensitivity, F1-score etc.

**Confusion Matrix-** to get the values for True Positive(TP), True Negative(TN), False Positive(FP) and False Negative(FN).

| Confusion Matrix    | Predicted Positive  | Predicted Negative  |
| :------------------ | :------------------ | :------------------ |
| **Actual Positive** | True Positive (TP)  | False Negative (FN) |
| **Actual Negative** | False Positive (FP) | True Negative (TN)  |

**TABLE V: Confusion Matrix**

$$Accuracy = \frac{TP + TN}{TP + FP + TN + FN} \qquad (1)$$

$$Precision = \frac{TP}{TP + FP} \qquad (2)$$

$$Recall/Sensitivity = \frac{TP}{TP + FN} \qquad (3)$$

$$F1-Score = 2 \times \frac{Precision \times Recall}{Precision + Recall} \qquad (4)$$

---

## IV. RESULT AND DISCUSSION

Both models were developed by following the mentioned approach. At each step their performance- loss and accuracy curves were noticed and performance of the models were calculated using mentioned metrices.

### A. Performance of Inception V3 Model

At first Inception V3 model was trained and validated on 10K images from LC25000 with data augmentation at a ratio of 80:20. Fig. 4 shows how loss curves on both training and validation were decreasing and accuracy curves were increasing. We stopped training at epoch 8 as more training caused the model overfitting. Fig. 5 shows the accuracy and loss curves for the second step where the model was retrained on new data (40% of Warwick-QU) for 20 epochs. Finally the model was tested on new data (60% of Warwick which was separated before training). Test accuracy, precision, recall and F1-score were calculated and mentioned in table VI.

| Dataset    | Train Accuracy | Test Accuracy | Precision | Recall  | F1-Score |
| :--------- | :------------- | :------------ | :-------- | :------ | :------- |
| LC25000    | 98.56%         | 99.4%         | 99.4%     | 99.4%   | 99.4%    |
| Warwick-QU | 95.44%         | 94.545%       | 94.782%   | 94.545% | 94.538%  |

**TABLE VI: Performance of Inception V3**

### B. Performance of Ensembled CNN Model

Ensembled model also followed the same approach. The loss curves and accuracy curves during training and validation were plotted for all the three CNN models at fig. 6, fig. 7 and fig. 8 respectively. Epochs= 12, epochs=15 and epochs=13 were used for these models in this process.

![Fig. 4: Model trained and validated on dataset 1](https://placeholder.com/figure4)
*Fig. 4: Model trained and validated on dataset 1. (a) Loss curve, (b) Accuracy Curve*

![Fig. 5: Model retrained on new data from dataset 2](https://placeholder.com/figure5)
*Fig. 5: Model retrained on new data from dataset 2. (a) Loss curve, (b) Accuracy Curve*

![Fig. 6: CNN Model-1 trained and validated on dataset 1](https://placeholder.com/figure6)
*Fig. 6: CNN Model-1 trained and validated on dataset 1. (a) Loss curve, (b) Accuracy Curve*

![Fig. 7: CNN Model-2 trained and validated on dataset 1](https://placeholder.com/figure7)
*Fig. 7: CNN Model-2 trained and validated on dataset 1. (a) Loss curve, (b) Accuracy Curve*

![Fig. 8: CNN Model-3 trained and validated on dataset 1](https://placeholder.com/figure8)
*Fig. 8: CNN Model-3 trained and validated on dataset 1. (a) Loss curve, (b) Accuracy Curve*

---

![Fig. 9: CNN Models re-trained on dataset 2](https://placeholder.com/figure9)
*Fig. 9: CNN Models re-trained on dataset 2. (a) Loss curve for model 1, (b) Loss curve for model 2, (c) Loss curve for model 3*

Fig. 9 shows three loss curves for the three CNN models at this retraining phase. We used epochs 15, 20, and 20 respectively at this step to cope with the new data without being overfitted. And finally, these three models were tested. The prediction was made by combining the results we got from each model in a weighted average approach. The weights we used were w1=0.2, w2=0.4, and w3=0.4 for model1, model2, and model3 respectively. The best combination of weights was found by performing a grid search on trained data. Table VII shows the results we achieved from this approach.

| Dataset    | Model         | Train Accuracy | Test Accuracy | Precision | Recall  | F1-Score |
| :--------- | :------------ | :------------- | :------------ | :-------- | :------ | :------- |
| LC25000    | CNN Model1    | 98.86%         | 99.65%        | 99.65%    | 99.65%  | 99.65%   |
|            | CNN Model2    | 96.86%         | 98.90%        | 98.924%   | 98.900% | 98.900%  |
|            | CNN Model3    | 98.89%         | 97.95%        | 98.023%   | 97.95%  | 97.949%  |
|            | Ensembled CNN | -              | 99.95%        | 99.70%    | 99.67%  | 99.67%   |
| Warwick QU | CNN Model1    | 88.90%         | 88.182%       | 88.296%   | 88.182% | 88.173%  |
|            | CNN Model2    | 72.22%         | 70.909%       | 72.842%   | 70.909% | 70.280%  |
|            | CNN Model3    | 77.78%         | 70.909%       | 71.020%   | 70.909% | 70.871%  |
|            | Ensembled CNN | -              | 78.182%       | 81.562%   | 78.182% | 77.582%  |

**TABLE VII: Performance of CNN Models**

### C. Performance Comparison

Table VIII shows a comparison between our work and some previous work in this field. Inception V3 has a pretty good result with an accuracy of 99.4% compared to all the models we have seen. It has a very good accuracy for the new data also which is 94.545%. This result introduces a good scope as the other studies only work on the LC25000 dataset. We saw that at D. Sarwinda et al. [3] work ResNet-50 was developed only using Warwick-QU data and comparing this to our work, our model gives a better result. The ensembled CNN approach shows a very high accuracy of 99.95% for the LC25000 dataset but this performance decreases (78.182%) when it was tested on the Warwick-QU dataset.

## V. CONCLUSION AND FUTURE WORK

The objective of this thesis was to explore different methods to implement and then compare them to find out an effective approach in the field of detecting colon cancerous cells. The main focus was to build a general model by using different images. To reach this goal we developed two models- the Transfer Learning Inception V3 model and the Ensembled CNN model where they were first trained and validated using the LC25000 dataset with enough images and secondly to cope with new data these two models were retrained on a smaller portion(only 40%) and then tested on another portion(60%) of Warwick-QU dataset. Inception V3 achieved 99.4% accuracy and 94.545% accuracy in our approach for LC25000 and Warwick\_QU datasets. On the other side, the process of ensembling the predictions of three different models shows the increment in performance where the Ensembled model achieved high accuracy for the LC25000 dataset. But it shows only 78.182% accuracy for the Warwick\_QU dataset. As the CNN models were of only 6-7 layers they were not strong enough to retrieve important features from a very small amount of new data. Thus it remains to be explored how our model performs in a large data pool to prove its effectiveness in real life and how the result changes with deeper CNN architectures.

Although we have many models developed in this field, our approach introduces an alternative way where we tried to make it reliable with different datasets. It is expected that more data along with more image preprocessing methods can improve the classification approach. Future works regarding this work entail training and testing on bigger data sets and real life. A K-fold cross validation can be used to validate the performance. Also better CNN architecture will lead to a better result, so finding a better combination of layers and all other relevant parameters is a good point to start with.

| Studies                 | Dataset    | Model         | Accuracy | Precision | Recall  | F1-Score |
| :---------------------- | :--------- | :------------ | :------- | :-------- | :------ | :------- |
| Proposed Study          | LC25000    | Inception V3  | 99.4%    | 99.4%     | 99.4%   | 99.4%    |
|                         |            | Ensembled CNN | 99.95%   | 99.70%    | 99.67%  | 99.67%   |
|                         | Warwick-QU | Inception V3  | 94.545%  | 94.782%   | 94.545% | 94.538%  |
|                         |            | Ensembled CNN | 78.182%  | 81.562%   | 78.182% | 77.582%  |
| Z. Tasnim et al. [5]    | LC25000    | Max-Pooling   | 97.49%   | -         | -       | -        |
|                         |            | Avg-Pooling   | 95.48%   | -         | -       | -        |
|                         |            | MobileNet V2  | 99.67%   | -         | -       | -        |
| D.Sarwinda et al. [3]   | Warwick-QU | ResNet-50     | 88%      | -         | 93%     | -        |
| A.H. Chehade et al. [4] | LC25000    | XGBoost       | 95.67%   | 95.8%     | 96%     | 95.9%    |

**TABLE VIII: Performance Comparison with other studies**

---

## REFERENCES

[1] “Colorectal cancer statistics — how common is colorectal cancer?” https://www.cancer.org/cancer/colon-rectal-cancer/about/key-statistics.html, (accessed Nov. 29, 2022).  
[2] “Colon cancer: Symptoms, stages & treatment,” https://my.clevelandclinic.org/health/diseases/14501-colorectal-colon-cancer, (accessed Nov. 29, 2022).  
[3] D. Sarwinda, R. H. Paradisa, A. Bustamam, and P. Anggia, “Deep learning in image classification using residual network (resnet) variants for detection of colorectal cancer,” *Procedia Computer Science*, vol. 179, pp. 423–431, 2021.  
[4] A. H. Chehade, N. Abdallah, J.-M. Marion, M. Oueidat, and P. Chauvet, “Lung and colon cancer classification using medical imaging: A feature engineering approach,” 2022.  
[5] Z. Tasnim, S. Chakraborty, F. Shamrat, A. N. Chowdhury, H. A. Nuha, A. Karim, S. B. Zahir, M. M. Billah et al., “Deep learning predictive model for colon cancer patient using cnn-based classification,” *Int. J. Adv. Comput. Sci. Appl*, vol. 12, 2021.  
[6] M. Masud, N. Sikder, A.-A. Nahid, A. K. Bairagi, and M. A. AlZain, “A machine learning approach to diagnosing lung and colon cancer using a deep learning-based classification framework,” *Sensors*, vol. 21, no. 3, p. 748, 2021.  
[7] S. Garg and S. Garg, “Prediction of lung and colon cancer through analysis of histopathological images by utilizing pre-trained cnn models with visualization of class activation and saliency maps,” in *2020 3rd Artificial Intelligence and Cloud Computing Conference*, 2020, pp. 38–45.  
[8] S. U. K. Bukhari, A. Syed, S. K. A. Bokhari, S. S. Hussain, S. U. Armaghan, and S. S. H. Shah, “The histological diagnosis of colonic adenocarcinoma by applying partial self supervised learning,” *MedRxiv*, 2020.  
[9] S. Toraman, M. Girgin, B. Üstündag, and İ. Türkoğlu, “Classification of the likelihood of colon cancer with machine learning techniques using ftir signals obtained from plasma,” *Turkish Journal of Electrical Engineering and Computer Sciences*, vol. 27, no. 3, pp. 1765–1779, 2019.  
[10] A. Borkowski, M. Bui, L. Thomas, C. Wilson, L. DeLand, and S. Mastorides, “Lc25000 lung and colon histopathological image dataset,” 2021.  
[11] K. Sirinukunwattana, J. P. W. Pluim, H. Chen, X. Qi, P.-A. Heng, Y. B. Guo, L. Y. Wang, B. J. Matuszewski, E. Bruni, U. Sanchez, A. Böhm, O. Ronneberger, B. B. Cheikh, D. Racoceanu, P. Kainz, M. Pfeiffer, M. Urschler, D. R. J. Snead, and N. M. Rajpoot, “Gland segmentation in colon histology images: The glas challenge contest,” 2016. [Online]. Available: https://arxiv.org/abs/1603.00275

---
979-8-3503-4536-0/23/$31.00 ©2023 IEEE  
Authorized licensed use limited to: Charles Darwin University. Downloaded on April 21,2023 at 05:48:51 UTC from IEEE Xplore. Restrictions apply.