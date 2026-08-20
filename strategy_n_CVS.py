import pandas as pd
import numpy as np

def calculate_cvs_and_strategy(df: pd.DataFrame, weight_price: float = 0.6, weight_sentiment: float = 0.4) -> pd.DataFrame:
    """
    Calculates the Competitive Vulnerability Score (CVS) using Z-scores 
    and maps the result to a strategic positioning tactic.
    """
    # 1. Normalize variables using Z-scores
    df['z_price'] = (df['standard_order_fee'] - df['standard_order_fee'].mean()) / df['standard_order_fee'].std()
    df['z_sentiment'] = (df['sentiment_score'] - df['sentiment_score'].mean()) / df['sentiment_score'].std()
    
    # Fill any NaNs (e.g., if standard deviation is 0) with 0
    df = df.fillna(0)
    
    # 2. Calculate the weighted CVS
    # Note: High price adds to vulnerability; high sentiment reduces it.
    df['cvs'] = (weight_price * df['z_price']) - (weight_sentiment * df['z_sentiment'])
    
    # 3. Define strategic heuristic rules based on CVS and quadrant
    def assign_tactic(row):
        if row['cvs'] > 1.0:
            return "Aggressive Acquisition: Target with cost-leadership marketing."
        elif row['cvs'] < -1.0:
            return "Avoid Direct Competition: Differentiate via niche features."
        elif row['z_price'] < 0 and row['z_sentiment'] < 0:
            return "Brand Rehabilitation: Invest in UX/UI and customer service."
        elif row['z_price'] > 0 and row['z_sentiment'] > 0:
            return "Premium Justification: Maintain high touch service to defend margins."
        else:
            return "Monitor: Market position is at equilibrium."
            
    df['recommended_tactic'] = df.apply(assign_tactic, axis=1)
    
    return df.sort_values(by='cvs', ascending=False)

# Example usage (assuming df_merged contains your scraped and NLP data)
# df_strategy = calculate_cvs_and_strategy(df_merged)
# print(df_strategy[['broker_name', 'cvs', 'recommended_tactic']])