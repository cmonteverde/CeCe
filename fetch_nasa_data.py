import requests
import pandas as pd
from datetime import datetime

def fetch_power_data(lat, lon, output_path):
    today = datetime.today().strftime("%Y%m%d")
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters=T2M,PRECTOT"
        f"&community=RE"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={today}&end={today}"
        f"&format=JSON"
    )

    response = requests.get(url)
    data = response.json()

    records = data['properties']['parameter']
    df = pd.DataFrame(records)
    df = df.transpose().reset_index().rename(columns={'index': 'date'})

    df.to_csv(output_path, index=False)
    print(f"✅ Saved NASA POWER data to: {output_path}")

# Example usage
if __name__ == "__main__":
    fetch_power_data(lat=32.7157, lon=-117.1611, output_path="daily_power_data.csv")