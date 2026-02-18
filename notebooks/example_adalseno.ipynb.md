CLA in Python 3
Original code in Python 2, together with the example dataset, is here: https://github.com/mdengler/cla

import CLA
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Markdown, display

# Python >= 3.9 or you might have issues with type-hints
Helper functions
def compute_return_risk(
    df: pd.DataFrame, mean: np.ndarray, covar: np.ndarray
) -> tuple[pd.Series, pd.Series]:
    """Compute Return and Risk (volatility) series for the CLW weights

    Args:
        df (pd.DataFrame): Dataframe with the weights
        mean (np.ndarray): Array of mean returns
        covar (np.ndarray): Array of covariances

    Returns:
        tuple[pd.Series, pd.Series]: series of returns and risk
    """
    p_ret = []
    risk = []
    for i in df.index:
        p_ret.append(np.dot(df.loc[i, :].values, mean)[0])
        risk.append(
            np.sqrt(np.dot(df.loc[i, :].values, np.dot(covar, df.loc[i, :].values)))
        )
    return pd.Series(p_ret, index=df.index, name="Return"), pd.Series(
        risk, index=df.index, name="Risk"
    )
def create_weight_table(
    cla: CLA, mean: np.ndarray, covar: np.ndarray, var_names: list
) -> pd.DataFrame:
    """Create the table with Return, Risk, Lambda and Weights

    Args:
        cla (CLA): The CLA object with the solution
        mean (np.ndarray): Array with the return means
        covar (np.ndarray): Array of covariances
        var_names (list): List of names for the columns

    Returns:
        pd.DataFrame: The weights table
    """
    weights = pd.DataFrame(
        np.hstack(cla.w).T, columns=var_names, index=np.arange(1, len(cla.w) + 1)
    )
    port_return, port_risk = compute_return_risk(weights, mean, covar)
    port_lambda = pd.Series(cla.l, index=weights.index, name="Lambda")
    return pd.concat([port_return, port_risk, port_lambda, weights], axis=1)
def display_results(ret_mean: np.ndarray, cla: CLA) -> None:
    """Plot the CLA results and dispaly the maximum Sharpe portfolio
    and the minimum variance one

    Args:
        ret_mean (np.ndarray): Array or return means
        cla (CLA): CLA object with the solution
    """
    plot_results()
    print()
    # 5) Get Maximum Sharpe ratio portfolio
    sr, w_sr = cla.getMaxSR()
    display(
        Markdown(
            f"### Portfolio volatility: {np.sqrt(np.dot(np.dot(w_sr.ravel(),cla.covar),w_sr.ravel())):.2%}, Sharpe ratio: {sr:.2f}"
        )
    )
    display(Markdown("### Weights (rounded to 4 decimal places):"))
    display(
        pd.Series(
            np.round(w_sr.ravel(), 4),
            name="sr_weights",
            index=np.arange(1, len(w_sr) + 1),
        )
    )
    print()
    # 6) Get Minimum Variance portfolio
    mv, w_mv = cla.getMinVar()
    mu_v = np.dot(w_mv.ravel(), ret_mean)
    sr_v = np.round(mu_v / mv, 2).ravel()[0]
    display(
        Markdown(
            f"### Portfolio minimum volatility: {mv.ravel()[0]:.2%}, Sharpe ratio: {sr_v:.2f}"
        )
    )
    display(Markdown("### Weights (rounded to 4 decimal places):"))
    display(
        pd.Series(
            np.round(w_mv.ravel(), 4),
            name="mv_weights",
            index=np.arange(1, len(w_sr) + 1),
        )
    )
    print()
    return
def plot_results() -> None:
    """Plots the results of CLA"""
    mu, sigma, weights = cla.efFrontier(100)
    mu = np.array(mu)
    sigma = np.array(sigma)
    x_low = max(sigma.min() - 0.05, 0.0)
    fig, ax = plt.subplots(1, 2, figsize=(20, 7))  # one row, one column, first plot
    ax[0].plot(sigma, mu, color="blue")
    ax[0].set_xlabel("Risk")
    ax[0].set_ylabel("Expected Excess Return", rotation=90)
    # ax[0].set_xticklabels(ax[0].get_xticks(), rotation='vertical')
    ax[0].set_xlim(x_low, 1.0)
    ax[0].set_title("CLA-derived Efficient Frontier")
    ax[1].plot(sigma, np.round(np.array(mu) / np.array(sigma), 2), color="blue")
    ax[1].set_xlabel("Risk")
    ax[1].set_ylabel("Sharpe ratio", rotation=90)
    # ax[1].set_xticklabels(ax[0].get_xticks(), rotation='vertical')
    ax[1].set_xlim(x_low, 1.0)
    ax[1].set_title("CLA-derived Sharpe Ratio function")
    plt.suptitle("CLA results", fontsize=16)
    plt.show()

    return
Import dataset
df = pd.read_csv("CLA_Data.csv")
df
<style scoped> .dataframe tbody tr th:only-of-type { vertical-align: middle; }
.dataframe tbody tr th {
    vertical-align: top;
}

.dataframe thead th {
    text-align: right;
}
</style>
X1	X2	X3	X4	X5	X6	X7	X8	X9	X10
0	1.175000	1.190000	0.396000	1.120000	0.346000	0.679000	0.089000	0.730000	0.481000	1.080000
1	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000
2	1.000000	1.000000	1.000000	1.000000	1.000000	1.000000	1.000000	1.000000	1.000000	1.000000
3	0.407552	0.031758	0.051839	0.056639	0.033023	0.008278	0.021659	0.013324	0.034348	0.022499
4	0.031758	0.906305	0.031364	0.026873	0.019172	0.009344	0.024950	0.007610	0.028749	0.013369
5	0.051839	0.031364	0.194909	0.044085	0.030068	0.013227	0.035260	0.011549	0.042756	0.020573
6	0.056639	0.026873	0.044085	0.195285	0.027773	0.005267	0.013758	0.007809	0.029142	0.016404
7	0.033023	0.019172	0.030068	0.027773	0.340591	0.007771	0.020678	0.007364	0.025427	0.012841
8	0.008278	0.009344	0.013227	0.005267	0.007771	0.159839	0.021056	0.005187	0.017237	0.007238
9	0.021659	0.024950	0.035260	0.013758	0.020678	0.021056	0.680567	0.013779	0.046270	0.019261
10	0.013324	0.007610	0.011549	0.007809	0.007364	0.005187	0.013779	0.955269	0.010655	0.007610
11	0.034348	0.028749	0.042756	0.029142	0.025427	0.017237	0.046270	0.010655	0.316816	0.018543
12	0.022499	0.013369	0.020573	0.016404	0.012841	0.007238	0.019261	0.007610	0.018543	0.110793
Create variables
var_names = df.columns.to_list()
var_names
['X1', 'X2', 'X3', 'X4', 'X5', 'X6', 'X7', 'X8', 'X9', 'X10']
mean = df.iloc[0, :].values.reshape(-1, 1)

lB = df.iloc[1, :].values.reshape(-1, 1)
uB = df.iloc[2, :].values.reshape(-1, 1)

covar = df.iloc[3:, :].values
Compute CLA
# 3) Invoke object
cla = CLA.CLA(mean, covar, lB, uB)
cla.solve()
Display results
weight_df = create_weight_table(cla, mean, covar, var_names)
weight_df.style.format("{:.3f}")
<style type="text/css"> </style>
 	Return	Risk	Lambda	X1	X2	X3	X4	X5	X6	X7	X8	X9	X10
1	1.190	0.952	58.303	0.000	1.000	0.000	0.000	0.000	0.000	0.000	0.000	0.000	0.000
2	1.180	0.546	4.174	0.649	0.351	0.000	-0.000	0.000	0.000	0.000	0.000	0.000	0.000
3	1.160	0.417	1.946	0.434	0.231	0.000	0.335	0.000	0.000	0.000	0.000	0.000	-0.000
4	1.111	0.267	0.165	0.127	0.072	0.000	0.281	0.000	0.000	0.000	-0.000	0.000	0.520
5	1.108	0.265	0.147	0.123	0.070	0.000	0.279	0.000	0.000	0.000	0.006	0.000	0.521
6	1.022	0.230	0.056	0.087	0.050	0.000	0.224	0.000	0.174	0.000	0.030	0.000	0.435
7	1.015	0.228	0.052	0.085	0.049	0.000	0.220	-0.000	0.180	0.000	0.031	0.006	0.429
8	0.973	0.220	0.037	0.074	0.044	0.000	0.199	0.026	0.198	0.000	0.033	0.028	0.398
9	0.950	0.216	0.031	0.068	0.041	0.015	0.188	0.034	0.202	0.000	0.034	0.034	0.383
10	0.803	0.205	0.000	0.037	0.027	0.095	0.126	0.077	0.219	0.030	0.036	0.061	0.292
display_results(mean, cla)
￼

Portfolio volatility: 22.74%, Sharpe ratio: 4.45
Weights (rounded to 4 decimal places):
1     0.0840
2     0.0489
3     0.0000
4     0.2183
5     0.0017
6     0.1812
7     0.0000
8     0.0312
9     0.0079
10    0.4269
Name: sr_weights, dtype: float64
Portfolio minimum volatility: 20.52%, Sharpe ratio: 3.91
Weights (rounded to 4 decimal places):
1     0.0370
2     0.0269
3     0.0949
4     0.1258
5     0.0767
6     0.2194
7     0.0300
8     0.0360
9     0.0613
10    0.2920
Name: mv_weights, dtype: float64
Thank you very much for your repo.

Kind regards,
Andrea Dalseno

￼
Create sub-issue
￼
￼
￼
👍
Unreact with 👍2
