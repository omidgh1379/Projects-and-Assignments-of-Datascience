# Multi-Layer Perceptron and SVM from Scratch with Fine-Tuning

This repository contains the implementation of a **Multi-Layer Perceptron (MLP)** and **Support Vector Machine (SVM)** from scratch, with fine-tuning on three different datasets. The implementation includes:

- **Multi-Layer Perceptron (MLP)**: Developed from scratch and optimized using gradient descent.
- **Support Vector Machine (SVM)**: Implemented for classification, including optimization via the dual problem.

Both models have been fine-tuned using hyperparameter optimization techniques and tested on various datasets to achieve optimal performance.

## Table of Contents

- [Datasets](#datasets)
- [Implementation Details](#implementation-details)
  - [1. Multi-Layer Perceptron (MLP)](#1-multi-layer-perceptron-mlp)
  - [2. Support Vector Machine (SVM)](#2-support-vector-machine-svm)
- [Usage](#usage)
  - [1. MLP Training](#1-mlp-training)
  - [2. SVM Training](#2-svm-training)
- [Results](#results)
  - [Multi-Layer Perceptron](#multi-layer-perceptron)
  - [Support Vector Machine (Gender Classification)](#support-vector-machine-gender-classification)
  - [Support Vector Machine (Q3 Dataset)](#support-vector-machine-q3-dataset)
- [License](#license)

## Datasets

Three different datasets were used for training and testing the models:

- **Dataset 1**: A dataset used to evaluate the performance of the Multi-Layer Perceptron.
- **Dataset 2**: Gender classification dataset for SVM.
- **Dataset 3**: Another dataset used for further evaluation of the SVM model.

The datasets are assumed to be in CSV format, with preprocessing steps handled in the code.

## Implementation Details

### 1. Multi-Layer Perceptron (MLP)

- **Architecture**: The MLP was built with several hidden layers, with each layer using the **Rectified Linear Unit (ReLU)** as the activation function for better numerical stability.
- **Optimization**: Gradient Descent was used to optimize the cost function, with a maximum of **1500 iterations**.
- **Hyperparameter Tuning**: Cross-validation was used to select the best combination of hyperparameters (lambda, number of neurons in each layer, and learning rate).

**Final architecture**:

| Layer          | Neurons | Activation Function |
| -------------- | ------- | ------------------- |
| Input Layer    | -       | -                   |
| Hidden Layer 1 | 32      | ReLU                |
| Hidden Layer 2 | 80      | ReLU                |
| Hidden Layer 3 | 60      | ReLU                |
| Hidden Layer 4 | 20      | ReLU                |
| Output Layer   | -       | Softmax             |

### 2. Support Vector Machine (SVM)

- **Kernel**: A **Gaussian kernel** was selected as the best-performing kernel after hyperparameter tuning.
- **Optimization**: The SVM is solved using the **dual problem**, where the optimization routine is handled using the `cvxopt` library for solving quadratic programming problems.
- **Hyperparameter Tuning**: Grid search was used to fine-tune the hyperparameter **C** (regularization term). The best C value selected for the dual problem was **C = 1**, with **gamma = 0.5**.

## Usage

### 1. MLP Training

You can find the full implementation and training process for the Multi-Layer Perceptron in the `Multi_Layer_Perceptron_Final.ipynb` file.

To run the MLP model:

1. Ensure the required dependencies are installed (`numpy`, `pandas`, `matplotlib`, etc.).
2. Load your dataset and preprocess it as per the notebook.
3. Run the notebook, following the steps to train and evaluate the model.

### 2. SVM Training

The implementation of SVM for gender classification and further tasks is in `SVM_Classification.ipynb`.

To run the SVM model:

1. Install the required dependencies (`numpy`, `cvxopt` for quadratic programming).
2. Load the gender classification dataset.
3. Run the notebook, which will optimize the dual problem for SVM classification.

## Results

### Multi-Layer Perceptron

- **Final Training Error**: 23.55%
- **Final Validation Error**: 23.81%
- **Final Test Error**: 26.91%
- **MAPE on Training Set**: 27.83%
- **MAPE on Validation Set**: 27.84%
- **MAPE on Test Set**: 28.63%

### Support Vector Machine (Gender Classification)

- **Training Accuracy (Q2)**: 92%
- **Test Accuracy (Q2)**: 92%
- **Cross-Validation Accuracy (Q2)**: 91.8%
- **Optimization Performance**: 81 seconds CPU time for Q2.

### Support Vector Machine (Q3 Dataset)

- **Training Accuracy (Q3)**: 91%
- **Test Accuracy (Q3)**: 90.33%
- **Optimization Performance (Q3)**: 6.03 seconds CPU time.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
