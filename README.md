\# UK Online Retail Intelligence



An end-to-end retail analytics portfolio project using Python, SQL,

machine learning, Power BI and Streamlit.



\## Project Objective



This project analyses UK online retail transactions to understand sales

performance, customer behaviour, product returns and future revenue.



\## Business Questions



\- Which products and markets generate the most revenue?

\- Who are the most valuable and loyal customers?

\- Which customers are at risk of becoming inactive?

\- Which products experience the highest cancellation value?

\- Can weekly retail revenue be forecast accurately?



\## Dataset



The project uses the UCI Online Retail dataset containing UK retail

transactions between December 2010 and December 2011.



After cleaning and duplicate removal, the sales dataset contains 524,878

valid transaction rows and 4,338 identified customers.



\## Technologies



\- Python

\- pandas and NumPy

\- SQL and SQLite

\- scikit-learn

\- statsmodels

\- Plotly

\- Power BI

\- Streamlit

\- Git and GitHub



\## Analysis



\### Sales Analysis



\- Revenue and order KPIs

\- Monthly and weekly trends

\- Country performance

\- Product performance

\- Returns and cancellations



\### Customer Segmentation



RFM analysis was used to classify customers into:



\- Champions

\- Loyal Customers

\- Potential Loyalists

\- New Customers

\- At Risk

\- Needs Attention

\- Lost Customers



K-Means clustering identified high-value engaged customers and

low-engagement or inactive customers.



\### Sales Forecasting



The following forecasting approaches were compared:



\- Naive baseline

\- Four-week moving average

\- Holt exponential smoothing

\- ARIMA



Holt achieved the best holdout performance:



\- MAE: £34,519

\- RMSE: £46,211

\- MAPE: 10.53%



\## Streamlit Application



The interactive application contains four pages:



1\. Executive Overview

2\. Customer Segmentation

3\. Products and Returns

4\. Sales Forecast



Run locally with:



```bash

python -m streamlit run Executive\_Overview.py

