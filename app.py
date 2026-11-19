from flask import Flask, render_template_string
from gold_calculator import calculate_gold
from database import create_database
import requests
import sqlite3
import json

app = Flask(__name__)

create_database()

@app.route("/")
def home():
    try:
        dollar_data = requests.get(
            "https://nerkhara.com/api/v1/latest/usd.json",
            timeout=15
        ).json()["item"]

        gold_data = requests.get(
            "https://xaus.com/api/v1/spot",
            timeout=15
        ).json()

        dollar_price = float(dollar_data["price"])
        ounce_price = float(gold_data["spot_usd_oz"])

        prices = calculate_gold(ounce_price, dollar_price)
        connection = sqlite3.connect("gold_history.db")
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO gold_prices
            (dollar_price, ounce_price, gold_18, gold_24)
            VALUES (?, ?, ?, ?)
        """, (
            dollar_price,
            ounce_price,
            prices["18_carat"],
            prices["24_carat"]
        ))

        connection.commit()

        cursor.execute("""
            SELECT created_at, gold_18
            FROM gold_prices
            WHERE created_at >= datetime('now', '-30 days')
            ORDER BY id ASC
        """)

        history = cursor.fetchall()
        connection.close()

    except Exception as e:
        return f"خطا در دریافت یا ذخیره قیمت‌ها: {e}"
    # ادامه کد قبلی render_template_string از اینجا قرار می‌گیرد

    return render_template_string("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IranGold | بازار طلا</title>
    <style>
        * {
            box-sizing: border-box;

        body {
            margin: 0;
            font-family: Tahoma, sans-serif;
            background: #263449;
            color: #f5f5f5;
        }

        header {
            padding: 25px 8%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #202e42;
            border-bottom: 1px solid #526078;
        }

        .logo {
            color: #F2CB70;
            font-size: 28px;
            font-weight: bold;
        }

        header span {
            color: #d5dce5;
            font-size: 13px;
        }

        .container {
            max-width: 1100px;
            margin: 50px auto;
            padding: 0 20px;
        }

        .welcome {
            text-align: center;
            margin-bottom: 40px;
        }

        .welcome h1 {
            color: #FFE5A3;
            font-size: 30px;
        }

        .welcome p {
            color: #c4cfdd;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .card {
            background: #35445A;
            padding: 28px;
            border-radius: 16px;
            border: 1px solid #596981;
            transition: 0.3s;
        }

        .card:hover {
            transform: translateY(-4px);
            border-color: #F2CB70;
        }

        .card h3 {
            color: #F2CB70;
            font-size: 17px;
        }

        .price {
            font-size: 25px;
            font-weight: bold;
            margin: 20px 0;
        }

        .unit {
            color: #c4cfdd;
            font-size: 13px;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: #c4cfdd;
            font-size: 12px;
        }

        @media (max-width: 600px) {
            .cards {
                grid-template-columns: 1fr;
            }

            header {
                padding: 20px;
            }

            .welcome h1 {
                font-size: 23px;
            }
        }
    </style>
</head>

<body>

<header>
    <div class="logo">IranGold ✦</div>
    <span>سامانه هوشمند بازار طلا</span>
</header>

<div class="container">

    <div class="welcome">
        <h1>به IranGold خوش آمدید</h1>
        <p>مرجع محاسبه و بررسی قیمت طلا در ایران</p>
    </div>

    <div class="cards">

        <div class="card">
            <h3>طلای ۱۸ عیار</h3>
            <div class="price">{{ "{:,}".format(prices["18_carat"]) }}</div>
            <div class="unit">قیمت هر گرم / تومان</div>
        </div>

        <div class="card">
            <h3>طلای ۲۴ عیار</h3>
            <div class="price">{{ "{:,}".format(prices["24_carat"]) }}</div>
            <div class="unit">قیمت هر گرم / تومان</div>
        </div>

        <div class="card">
            <h3>دلار آزاد</h3>
         <div class="price">{{ "{:,.0f}".format(dollar_price) }}</div>
            <div class="unit">قیمت هر دلار / تومان</div>
        </div>

        <div class="card">
            <h3>انس جهانی طلا</h3>
            <div class="price">{{ "{:,.2f}".format(ounce_price) }}</div>
            <div class="unit">XAU / USD</div>
        </div>

    </div>

</div>
<div style="background:#35445A; padding:20px; border-radius:12px; margin:25px 0;">
    <h2 style="color:#FFE5A3;">نمودار تغییرات طلای ۱۸ عیار</h2>
    <div style="margin-bottom:15px; display:flex; gap:10px; justify-content:center;">
    <button onclick="changeRange(1)">۲۴ ساعت</button>
    <button onclick="changeRange(7)">۷ روز</button>
    <button onclick="changeRange(30)">۳۰ روز</button>
</div>
    <div id="goldChart" style="width:100%; height:350px;"></div>
</div>

<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<script>
const history = {{ history | tojson }};

const dates = history.map(item => item[0]);
const prices = history.map(item => item[1]);

Plotly.newPlot("goldChart", [{
    x: dates,
    y: prices,
    type: "scatter",
    mode: "lines+markers",
    name: "طلای ۱۸ عیار"
}], {
    paper_bgcolor: "#35445A",
    plot_bgcolor: "#35445A",
    font: { color: "#FFFFFF" },
    xaxis: { title: "زمان" },
    yaxis: { title: "قیمت (تومان)" },
    autosize: true
}, {
    responsive: true
});
</script>

<footer>
    IranGold | اطلاعات قیمت پس از اتصال به منابع بازار نمایش داده می‌شوند.
</footer>

</body>
</html>
""", prices=prices, history=history, dollar_price=dollar_price, ounce_price=ounce_price)
if __name__ == "__main__":
    app.run(debug=True)
