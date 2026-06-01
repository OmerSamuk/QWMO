import numpy as np


def summarize(scores):

    scores = np.asarray(scores)

    return {
        "best": float(np.min(scores)),
        "mean": float(np.mean(scores)),
        "std": float(np.std(scores)),
        "median": float(np.median(scores)),
        "iqr": float(
            np.percentile(scores, 75)
            - np.percentile(scores, 25)
        ),
    }


def print_summary(name, summary):

    print(
        f"{name:<15}"
        f"best={summary['best']:.3e}  "
        f"mean={summary['mean']:.3e}  "
        f"std={summary['std']:.3e}"
    )