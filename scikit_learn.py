# Avazu CTR prediction
# SGD Logistic regression + hashing trick.

import pandas as pd
import numpy as np
from datetime import datetime, date, time
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.preprocessing import LabelEncoder

cols = ["C1","banner_pos","site_category", "device_type","device_conn_type","C14","C15","C16","C17","C18","C19","C20","C21", "hour"]

# add two columns for hour and weekday
def dayhour(timestr):
    d = datetime.strptime(str(x), "%y%m%d%H")
    return [float(d.weekday()), float(d.hour)]

fh = FeatureHasher(n_features = 2**20, input_type="string")

# Train classifier
clf = SGDClassifier(loss="log", n_iter=1)
train = pd.read_csv("../Data/train.csv", chunksize = 1000000, iterator = True)
all_classes = np.array([0, 1])
for chunk in train:
    y_train = chunk["click"]
    chunk = chunk[cols]
    chunk = chunk.join(pd.DataFrame([dayhour(x) for x in chunk.hour], columns=["wd", "hr"]))
    chunk.drop("hour", axis=1, inplace = True)
    Xcat = fh.transform(np.asarray(chunk.astype(str)))
    clf.partial_fit(Xcat, y_train, classes=all_classes)
    
# Create a submission file
X_test = pd.read_csv("../Data/test.csv", usecols = cols + ["id"])
X_test = X_test.join(pd.DataFrame([dayhour(x) for x in X_test.hour], columns=["wd", "hr"]))
X_test.drop("hour", axis=1, inplace = True)

X_enc_test = fh.transform(np.asarray(X_test.astype(str)))

y_pred = clf.predict_proba(X_enc_test)[:, 1]
with open("../Data/submission.csv", "w") as f:
    f.write("id,click\n")
    for idx, xid in enumerate(X_test.id):
        f.write(str(xid) + "," + "{0:.10f}".format(y_pred[idx]) + "\n")
f.close()