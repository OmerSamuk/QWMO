import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score


class FitnessEvaluator:
    """Radiomics fitness evaluator: mean inner AUC via CV + sparsity penalty.

    Charter §16: fitness = (1 - mean_inner_AUC) + lambda * selected_feature_ratio
    Charter §17: solver = liblinear, max_iter = 5000
    """

    def __init__(self, X, y, n_splits=3, random_state=42, sparsity_lambda=0.01):
        self.X = np.asarray(X)
        self.y = np.asarray(y)
        self.n_splits = n_splits
        self.random_state = random_state
        self.sparsity_lambda = sparsity_lambda
        self.n_total = X.shape[1]

    def __call__(self, mask):
        selected_features = np.where(mask == 1)[0]
        n_selected = len(selected_features)
        if n_selected == 0:
            return 1.0
        selected_feature_ratio = n_selected / self.n_total
        X_sub = self.X[:, selected_features]

        skf = StratifiedKFold(
            n_splits=self.n_splits,
            shuffle=True,
            random_state=self.random_state,
        )

        aucs = []
        for train_idx, val_idx in skf.split(X_sub, self.y):
            X_train, X_val = X_sub[train_idx], X_sub[val_idx]
            y_train, y_val = self.y[train_idx], self.y[val_idx]

            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            X_val = scaler.transform(X_val)

            clf = LogisticRegression(
                solver='liblinear', max_iter=5000, random_state=self.random_state
            )
            clf.fit(X_train, y_train)

            y_prob = clf.predict_proba(X_val)[:, 1]
            try:
                auc = roc_auc_score(y_val, y_prob)
            except ValueError:
                auc = 0.5
            aucs.append(auc)

        mean_auc = float(np.mean(aucs))
        error = 1.0 - mean_auc
        return error + self.sparsity_lambda * selected_feature_ratio
