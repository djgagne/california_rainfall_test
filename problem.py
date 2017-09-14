from __future__ import division, print_function
import os
import numpy as np
import pandas as pd
import xarray as xr
import rampwf as rw
from glob import glob
from os.path import join
from sklearn.model_selection import LeaveOneGroupOut


problem_title = 'California Winter Extreme Rainfall Prediction'
_prediction_label_names = [0, 1]

Predictions = rw.prediction_types.make_multiclass(label_names=_prediction_label_names)
workflow = rw.workflows.GridFeatureExtractorClassifier()
score_types = [
    rw.score_types.BrierSkillScore(name="BSS", precision=3),
    rw.score_types.BrierScore(name="BS", precision=3),
    rw.score_types.BrierScoreReliability(name="BS Rel", precision=3),
    rw.score_types.BrierScoreResolution(name="BS Res", precision=3),
    rw.score_types.ROCAUC(name="AUC", precision=3),
]


def get_cv(X, y):
    groups = np.zeros(y.shape)
    i = 0
    t_size = 1155
    n_members = int(y.size / t_size)
    for g in range(n_members):
        groups[i: i + t_size] = g
        i += t_size
    cv = LeaveOneGroupOut()
    X_cv = np.zeros((y.shape[0], 2))
    return cv.split(X_cv, y, groups)

def _read_data(path, f_prefix):
    data_vars = ["TS", "PSL", "TMQ"]
    X_coll = []
    for data_var in data_vars:
        nc_file = join(path, "data", f_prefix + "_{0}.nc".format(data_var))
        print(nc_file)
        ds = xr.open_dataset(nc_file, decode_times=False)
        ds.load()
        X_coll.append(ds[data_var].stack(enstime=("ens", "time")).transpose("enstime", "lat", "lon"))
        ds.close()
    X_ds = xr.merge(X_coll)
    y = pd.read_csv(join(path, "data", f_prefix + "_precip_90.csv"), index_col="Year")
    y_array = np.concatenate([y[c] for c in y.columns])
    return X_ds, y_array


def get_train_data(path='./'):
    return _read_data(path, 'train')


def get_test_data(path='./data'):
    return _read_data(path, 'test')
