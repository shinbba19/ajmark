import streamlit as st
import pandas as pd
import altair as alt
import numpy as np



# --------------------------------------------------
# Sidebar Menu
# --------------------------------------------------
menu = ["Data Dashboard", "Financial Calculator"]
choice = st.sidebar.selectbox("Menu", menu)

# --------------------------------------------------
# 1) Data Dashboard
# --------------------------------------------------
if choice == "Data Dashboard":
    st.header("📊 Data Dashboard (สำรวจข้อมูลรวม)")

    # Load dataset
    df = pd.read_csv("Price per sqm_cleaned_data_selection2.csv")

    # Sidebar Filters
    st.sidebar.subheader("🔍 ตัวกรองข้อมูล")
    district_options = sorted(df["district_type"].unique())
    selected_district = st.sidebar.multiselect(
        "เลือกโซนทำเล (district_type)", district_options, default=district_options
    )
    age_min, age_max = int(df["bld_age"].min()), int(df["bld_age"].max())
    age_range = st.sidebar.slider("ช่วงอายุอาคาร (ปี)", age_min, age_max, (age_min, age_max))
    price_min, price_max = int(df["price_sqm"].min()), int(df["price_sqm"].max())
    price_range = st.sidebar.slider("ช่วงราคาต่อตร.ม.", price_min, price_max, (price_min, price_max))

    # Apply Filters
    filtered_df = df[
        (df["district_type"].isin(selected_district)) &
        (df["bld_age"].between(age_range[0], age_range[1])) &
        (df["price_sqm"].between(price_range[0], price_range[1]))
    ]

    # ---------------- KPI Summary ----------------
    st.subheader("📌 สรุปข้อมูล (KPI Overview)")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ราคาเฉลี่ย (฿/ตร.ม.)", f"{filtered_df['price_sqm'].mean():,.0f}")
    with col2:
        st.metric("ราคาสูงสุด (฿/ตร.ม.)", f"{filtered_df['price_sqm'].max():,.0f}")
    with col3:
        st.metric("ราคาต่ำสุด (฿/ตร.ม.)", f"{filtered_df['price_sqm'].min():,.0f}")
    with col4:
        st.metric("อายุอาคารเฉลี่ย (ปี)", f"{filtered_df['bld_age'].mean():.1f}")

    st.write("---")

    # ---------------- Filtered Data ----------------
    st.subheader("📋 ข้อมูลที่ถูกกรอง")
    st.write(f"จำนวนแถวที่เลือก: {len(filtered_df)}")
    st.dataframe(filtered_df.head(20))

    # Chart 1: Distribution of Price
    st.subheader("📈 การกระจายราคาต่อตร.ม.")
    chart1 = alt.Chart(filtered_df).mark_bar().encode(
        alt.X("price_sqm", bin=alt.Bin(maxbins=50), title="ราคาต่อตร.ม."),
        y='count()'
    )
    st.altair_chart(chart1, use_container_width=True)

    # Chart 2: Age vs Price
    st.subheader("🏗️ ความสัมพันธ์ระหว่างอายุอาคารกับราคา")
    chart2 = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.5).encode(
        x=alt.X("bld_age", title="อายุอาคาร (ปี)"),
        y=alt.Y("price_sqm", title="ราคาต่อตร.ม."),
        color="district_type:N",
        tooltip=["bld_age", "price_sqm", "district_type"]
    )
    st.altair_chart(chart2, use_container_width=True)

    # Chart 3: Distance to BTS vs Price
    st.subheader("🚉 ระยะทางจาก BTS กับราคาต่อตร.ม.")
    chart3 = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.6).encode(
        x=alt.X("Aver_trans", title="ระยะทางจาก BTS (กม.)"),
        y=alt.Y("price_sqm", title="ราคาต่อตร.ม."),
        color="district_type:N",
        tooltip=["Aver_trans", "price_sqm", "district_type", "bld_age"]
    )
    st.altair_chart(chart3, use_container_width=True)

    # Chart 4: District vs Average Price
    st.subheader("🏙️ ราคาเฉลี่ยตาม District")
    district_chart = filtered_df.groupby("district_type")["price_sqm"].mean().reset_index()
    chart4 = alt.Chart(district_chart).mark_bar().encode(
        x="district_type:N",
        y="price_sqm:Q"
    )
    st.altair_chart(chart4, use_container_width=True)

    # Chart 5: Facilities Impact (Pool)
    st.subheader("🏊 สิ่งอำนวยความสะดวกกับราคาเฉลี่ย (Pool)")
    facility_chart = filtered_df.groupby("Pool")["price_sqm"].mean().reset_index()
    chart5 = alt.Chart(facility_chart).mark_bar().encode(
        x="Pool:N",
        y="price_sqm:Q"
    )
    st.altair_chart(chart5, use_container_width=True)

# --------------------------------------------------
# 2) Financial Calculator
# --------------------------------------------------
elif choice == "Financial Calculator":
    st.header("💰 Financial Calculator (เครื่องคำนวณการเงิน)")

    # Inputs
    price = st.number_input("ราคาทรัพย์ (บาท)", min_value=500000, max_value=100000000, value=3000000, step=50000)
    down_payment_percent = st.slider("เงินดาวน์ (%)", 0, 100, 20)
    interest_rate = st.slider("ดอกเบี้ยต่อปี (%)", 0.0, 15.0, 5.0, step=0.1)
    loan_years = st.slider("ระยะเวลากู้ (ปี)", 1, 40, 20)

    # Calculations
    down_payment = price * (down_payment_percent / 100)
    loan_amount = price - down_payment
    monthly_rate = interest_rate / 100 / 12
    months = loan_years * 12

    if monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
    else:
        monthly_payment = loan_amount / months

    # Results
    st.subheader("📊 ผลการคำนวณ")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("เงินดาวน์", f"{down_payment:,.0f} ฿")
    with col2:
        st.metric("วงเงินกู้", f"{loan_amount:,.0f} ฿")
    with col3:
        st.metric("ค่างวดรายเดือน", f"{monthly_payment:,.0f} ฿")
