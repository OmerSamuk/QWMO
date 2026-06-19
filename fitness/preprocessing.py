import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold


def preprocess_train(X, y, variance_threshold=0.01, corr_threshold=0.95):
    """Fit preprocessor on training data only (no leakage).

    Returns:
        X_processed, fitted_preprocessor
    """
    from sklearn.decomposition import PCA

    pipe = {
        "imputer": SimpleImputer(strategy="median"),
        "scaler": StandardScaler(),
        "var_filter": VarianceThreshold(threshold=variance_threshold),
        "corr_filter": CorrelationFilter(threshold=corr_threshold),
    }

    X_pp = pipe["imputer"].fit_transform(X)
    X_pp = pipe["scaler"].fit_transform(X_pp)
    X_pp = pipe["var_filter"].fit_transform(X_pp)
    X_pp = pipe["corr_filter"].fit_transform(X_pp)

    pipe["corr_filter"].fit(X_pp)

    return X_pp, pipe


def preprocess_transform(pipe, X):
    X_pp = pipe["imputer"].transform(X)
    X_pp = pipe["scaler"].transform(X_pp)
    X_pp = pipe["var_filter"].transform(X_pp)
    X_pp = pipe["corr_filter"].transform(X_pp)
    return X_pp


class CorrelationFilter:
    def __init__(self, threshold=0.95):
        self.threshold = threshold
        self.selected_indices_ = None

    def fit(self, X):
        corr_matrix = np.corrcoef(X, rowvar=False)
        n_features = corr_matrix.shape[0]
        keep = np.ones(n_features, dtype=bool)
        for i in range(n_features):
            if keep[i]:
                for j in range(i + 1, n_features):
                    if keep[j] and abs(corr_matrix[i, j]) > self.threshold:
                        keep[j] = False
        self.selected_indices_ = np.where(keep)[0]
        return self

    def transform(self, X):
        if self.selected_indices_ is None:
            raise RuntimeError("fit must be called before transform")
        return X[:, self.selected_indices_]

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)
