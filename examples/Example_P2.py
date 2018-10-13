# coding: utf-8
"""
====================================================================
Example P2 Problem
====================================================================

This example shows the power of dynamic selection (DS) techniques which can
solve complex non-linear classification near classifiers. It also compares
the performance of DS techniques with some baseline classification methods
such as Random Forests, AdaBoost and SVMs.

The P2 is a two-class problem, presented by Valentini, in which each class
is defined in multiple decision regions delimited by polynomial and
trigonometric functions. Here, $E4$ was modified such that the area of
each class is equal (Henniges, 2005). It is impossible to solve this problem
using a single linear classifier, and the performance of the best possible
linear classifier is around 50\%.

"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from deslib.util.datasets import make_P2

# Importing DS techniques
from deslib.dcs.ola import OLA
from deslib.dcs.rank import Rank
from deslib.des.des_p import DESP
from deslib.des.knora_e import KNORAE


def make_grid(x, y, h=.02):

    x_min, x_max = x.min() - 1, x.max() + 1
    y_min, y_max = y.min() - 1, y.max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                         np.arange(y_min, y_max, h))
    return xx, yy


def plot_classifier_decision(ax, clf, X, mode='line', **params):

    xx, yy = make_grid(X[:, 0], X[:, 1])

    Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    if mode == 'line':
       ax.contour(xx, yy, Z, **params)
    else:
       ax.contourf(xx, yy, Z, **params)
    ax.set_xlim((np.min(X[:, 0]), np.max(X[:, 0])))
    ax.set_ylim((np.min(X[:, 1]), np.max(X[:, 0])))


def plot_dataset(X, y, ax=None, title=None, **params):

    if ax is None:
        ax = plt.gca()
    ax.scatter(X[:, 0], X[:, 1], marker='o', c=y, s=25,
               edgecolor='k', **params)
    ax.set_xlabel('Feature 1')
    ax.set_ylabel('Feature 2')
    if title is not None:
        ax.set_title(title)
    return ax


# Generating and plotting the P2 Dataset:
X, y = make_P2([1000, 1000])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5)
fig, axs = plt.subplots(1, 2, figsize=(15, 5))
plt.subplots_adjust(wspace=0.4, hspace=0.4)
plot_dataset(X_train, y_train, ax=axs[0], title='Training set')
plot_dataset(X_test, y_test, ax=axs[1], title='Test set')

# Baseline using standard classification methods
# 
# First we analyze the performance of a few baseline classifiers:
# 
# - SVM with RBF kernel;
# - MLP neural network
# - Random Forest
# - AdaBoost

# Setting classifiers
svm = SVC(gamma='scale').fit(X_train, y_train)
mlp = MLPClassifier(max_iter=10000).fit(X_train, y_train)
forest = RandomForestClassifier(n_estimators=10).fit(X_train,
                                                     y_train)
boosting = AdaBoostClassifier().fit(X_train, y_train)

# evaluating classifiers
print('SVM score = {}'.format(svm.score(X_test, y_test)))
print('MLP score = {}'.format(mlp.score(X_test, y_test)))
print('RF score = {}'.format(forest.score(X_test, y_test)))
print('Boosting score = {}'.format(boosting.score(X_test, y_test)))

# # Plotting the decision of the baseline methods

fig2, sub = plt.subplots(2, 2, figsize=(15, 10))
plt.subplots_adjust(wspace=0.4, hspace=0.4)
titles = ['SVM decision', 'MLP decision', 'RF decision', 'Boosting decision']
classifiers = [svm, mlp, forest, boosting]
for clf, ax, title in zip(classifiers, sub.flatten(), titles):
    plot_classifier_decision(ax, clf, X_test)
    plot_dataset(X_test, y_test, ax=ax)
    ax.set_xlim(np.min(X[:, 0]), np.max(X[:, 0]))
    ax.set_ylim(np.min(X[:, 1]), np.max(X[:, 1]))
    ax.set_title(title)

# Evaluating the performance of dynamic selection methods

# First generating a pool composed of 5 Decision Stumps using AdaBoost.
# 
# These are weak linear models. Each base classifier
# has a classification performance close to 50%.

pool_classifiers = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1),
                                      n_estimators=5).fit(X_train, y_train)
ax = plot_dataset(X_train, y_train, title='Five Decision Stumps set')
for clf in pool_classifiers:
    plot_classifier_decision(ax, clf, X_train)
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))

# Comparison with Dynamic Selection techniques.
# In this example we evaluate the performance of two DES:
# - KNORA-Eliminate (KNORAE)
# - DES-Performance (DESP)
# 
# and two DCS: 
# - Overall local accuracy (OLA)
# - Modified rank (Rank)
knora_e = KNORAE(pool_classifiers).fit(X_train, y_train)
desp = DESP(pool_classifiers).fit(X_train, y_train)
ola = OLA(pool_classifiers).fit(X_train, y_train)
rank = Rank(pool_classifiers).fit(X_train, y_train)

print('KNORAE score = {}'.format(knora_e.score(X_test, y_test)))
print('DESP score = {}'.format(desp.score(X_test, y_test)))
print('OLA score = {}'.format(ola.score(X_test, y_test)))
print('Rank score = {}'.format(rank.score(X_test, y_test)))

# Plotting the Decision Border of the DS methods.
fig2, sub = plt.subplots(2, 2, figsize=(15, 10))
plt.subplots_adjust(wspace=0.4, hspace=0.4)
titles = ['KNORA-Eliminate', 'DES-P', 'Overal Local Accuracy (OLA)',
          'Modified Rank']

classifiers = [knora_e, desp, ola, rank]
for clf, ax, title in zip(classifiers, sub.flatten(), titles):
    plot_classifier_decision(ax, clf, X_train)
    plot_dataset(X_test, y_test, ax=ax)
    ax.set_xlim(np.min(X[:, 0]), np.max(X[:, 0]))
    ax.set_ylim(np.min(X[:, 1]), np.max(X[:, 1]))
    ax.set_title(title)

plt.show()
