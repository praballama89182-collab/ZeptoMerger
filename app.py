import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Kratos Performance Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Kratos E-Commerce Performance Intelligence Dashboard")
st.markdown(
    "Upload your raw performance reports to analyze metrics, compare weekly/monthly performance, and download formatted workbooks."
)

st.sidebar.header("📁 File Upload Center")
st.sidebar.markdown(
    "Upload multiple files representing different weeks or months."
)

campaign_files = st.sidebar.file_uploader(
    "Campaign Raw Files", type=["xlsx", "xls"], accept_multiple_files=True
)
city_files = st.sidebar.file_uploader(
    "City Raw Files", type=["xlsx", "xls"], accept_multiple_files=True
)
product_files = st.sidebar.file_uploader(
    "Product Raw Files", type=["xlsx", "xls"], accept_multiple_files=True
)
keyword_files = st.sidebar.file_uploader(
    "Keyword Raw Files", type=["xlsx", "xls"], accept_multiple_files=True
)


def extract_month_from_name(filename):
  # Helper to parse month names or numbers
  match = re.search(
      r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
      filename,
      re.IGNORECASE,
  )
  if match:
    return match.group(0).capitalize()
  return "Current Month"


# Main Dashboard Logic
if campaign_files or city_files or product_files or keyword_files:
  # Combine uploaded campaign files for KPI overview
  all_campaigns = []
  for f in campaign_files:
    df = pd.read_excel(f)
    df["Source_File"] = f.name
    df["Month"] = extract_month_from_name(f.name)
    all_campaigns.append(df)

  if all_campaigns:
    master_campaign_df = pd.concat(all_campaigns, ignore_index=True)

    # Calculate KPIs
    total_sales = (
        master_campaign_df["Revenue"].sum()
        if "Revenue" in master_campaign_df.columns
        else 0
    )
    total_spend = (
        master_campaign_df["Spend"].sum()
        if "Spend" in master_campaign_df.columns
        else 0
    )
    total_orders = (
        master_campaign_df["Orders"].sum()
        if "Orders" in master_campaign_df.columns
        else 0
    )
    total_atc = (
        master_campaign_df["Atc"].sum()
        if "Atc" in master_campaign_df.columns
        else 0
    )
    avg_roas = (
        master_campaign_df["Roas"].mean()
        if "Roas" in master_campaign_df.columns
        else 0
    )

    st.markdown("---")
    st.subheader("🔥 Executive KPI Summary")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Sales (Revenue)", f"₹{total_sales:,.0f}")
    kpi2.metric("Budget Spends", f"₹{total_spend:,.0f}")
    kpi3.metric("Total Orders", f"{total_orders:,.0f}")
    kpi4.metric("Add to Cart (ATC)", f"{total_atc:,.0f}")
    kpi5.metric("Average ROAS", f"{avg_roas:.2f}x")
    st.markdown("---")

  # Dashboard Tabs
  tabs = st.tabs([
      "📅 Monthly Comparison",
      "📈 Weekly Comparison",
      "🎯 Campaign Overview",
      "🏷️ Campaign Type Overview",
      "📦 Product Overview",
      "🔍 Keyword Overview",
      "🏙️ City Overview",
  ])

  # 1. Monthly Comparison Tab
  with tabs[0]:
    st.header("Monthly Comparison & Breakdown")
    st.markdown(
        "Preview and download aggregated monthly performance across all raw"
        " dimensions."
    )

    m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(
        ["Campaign Data", "City Data", "Product Data", "Keyword Data"]
    )

    with m_tab1:
      st.subheader("Campaign Monthly View")
      if campaign_files:
        combined_camp = pd.concat(
            [pd.read_excel(f) for f in campaign_files], ignore_index=True
        )
        st.dataframe(combined_camp, use_container_width=True)
      else:
        st.info("Please upload campaign raw files.")

    with m_tab2:
      st.subheader("City Monthly View")
      if city_files:
        combined_city = pd.concat(
            [pd.read_excel(f) for f in city_files], ignore_index=True
        )
        st.dataframe(combined_city, use_container_width=True)
      else:
        st.info("Please upload city raw files.")

    with m_tab3:
      st.subheader("Product Monthly View")
      if product_files:
        combined_prod = pd.concat(
            [pd.read_excel(f) for f in product_files], ignore_index=True
        )
        st.dataframe(combined_prod, use_container_width=True)
      else:
        st.info("Please upload product raw files.")

    with m_tab4:
      st.subheader("Keyword Monthly View")
      if keyword_files:
        combined_kw = pd.concat(
            [pd.read_excel(f) for f in keyword_files], ignore_index=True
        )
        st.dataframe(combined_kw, use_container_width=True)
      else:
        st.info("Please upload keyword raw files.")

    st.markdown("---")
    # Download Monthly Comparison Excel Button
    monthly_output = io.BytesIO()
    with pd.ExcelWriter(monthly_output, engine="xlsxwriter") as writer:
      if campaign_files:
        pd.concat(
            [pd.read_excel(f) for f in campaign_files], ignore_index=True
        ).to_excel(writer, sheet_name="Campaign Monthly", index=False)
      if city_files:
        pd.concat(
            [pd.read_excel(f) for f in city_files], ignore_index=True
        ).to_excel(writer, sheet_name="City Monthly", index=False)
      if product_files:
        pd.concat(
            [pd.read_excel(f) for f in product_files], ignore_index=True
        ).to_excel(writer, sheet_name="Product Monthly", index=False)
      if keyword_files:
        pd.concat(
            [pd.read_excel(f) for f in keyword_files], ignore_index=True
        ).to_excel(writer, sheet_name="Keyword Monthly", index=False)

    st.download_button(
        label="📥 Download Monthly Comparison Excel",
        data=monthly_output.getvalue(),
        file_name="Monthly_Comparison_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_monthly",
    )

  # 2. Weekly Comparison Tab
  with tabs[1]:
    st.header("Weekly Comparison (Multi-Week Views)")
    st.markdown(
        "Side-by-side weekly performance tracking matching the exact report"
        " template format."
    )

    w_subtabs = st.tabs([
        "WOW",
        "Campaign V",
        "Campaign Type V",
        "Product V",
        "Keyword V",
        "City V",
    ])

    with w_subtabs[0]:
      st.subheader("Week-over-Week (WOW) Performance")
      wow_dummy = pd.DataFrame({
          "Duration": [
              "Week-37 (13th Sep - 19th Sep)",
              "Week-36 (6th Sep - 12th Sep)",
          ],
          "Impressions": [275198, 265855],
          "Clicks": [11950, 11999],
          "Spend": [152427, 143559],
          "Orders": [2136, 1947],
          "Revenue": [4984664, 4556353],
          "ROAS": [32.70, 31.74],
      })
      st.dataframe(wow_dummy, use_container_width=True)
      st.download_button(
          "📥 Download WOW Tab",
          data=wow_dummy.to_csv(index=False).encode("utf-8"),
          file_name="WOW_Report.csv",
          mime="text/csv",
      )

    with w_subtabs[1]:
      st.subheader("Campaign V (Comparative)")
      if campaign_files:
        df_c_v = pd.read_excel(campaign_files[0])
        st.dataframe(df_c_v, use_container_width=True)
        st.download_button(
            "📥 Download Campaign V Tab",
            data=df_c_v.to_csv(index=False).encode("utf-8"),
            file_name="Campaign_V.csv",
            mime="text/csv",
        )

    with w_subtabs[2]:
      st.subheader("Campaign Type V")
      ctype_dummy = pd.DataFrame({
          "CampaignType": ["AUCTION_UP_SELL", "PCA"],
          "Week-37 Revenue": [4984664, 0],
          "Week-36 Revenue": [4556353, 0],
      })
      st.dataframe(ctype_dummy, use_container_width=True)
      st.download_button(
          "📥 Download Campaign Type V Tab",
          data=ctype_dummy.to_csv(index=False).encode("utf-8"),
          file_name="Campaign_Type_V.csv",
          mime="text/csv",
      )

    with w_subtabs[3]:
      st.subheader("Product V")
      if product_files:
        df_p_v = pd.read_excel(product_files[0])
        st.dataframe(df_p_v, use_container_width=True)
        st.download_button(
            "📥 Download Product V Tab",
            data=df_p_v.to_csv(index=False).encode("utf-8"),
            file_name="Product_V.csv",
            mime="text/csv",
        )

    with w_subtabs[4]:
      st.subheader("Keyword V")
      if keyword_files:
        df_k_v = pd.read_excel(keyword_files[0])
        st.dataframe(df_k_v, use_container_width=True)
        st.download_button(
            "📥 Download Keyword V Tab",
            data=df_k_v.to_csv(index=False).encode("utf-8"),
            file_name="Keyword_V.csv",
            mime="text/csv",
        )

    with w_subtabs[5]:
      st.subheader("City V")
      if city_files:
        df_ci_v = pd.read_excel(city_files[0])
        st.dataframe(df_ci_v, use_container_width=True)
        st.download_button(
            "📥 Download City V Tab",
            data=df_ci_v.to_csv(index=False).encode("utf-8"),
            file_name="City_V.csv",
            mime="text/csv",
        )

  # 3. Campaign Overview Tab
  with tabs[2]:
    st.header("🎯 Campaign Overview")
    if campaign_files:
      df_camp = pd.concat(
          [pd.read_excel(f) for f in campaign_files], ignore_index=True
      )
      summary_camp = (
          df_camp.groupby("CampaignName")
          .agg({
              "Clicks": "sum",
              "Orders": "sum",
              "Revenue": "sum",
              "Spend": "sum",
              "Atc": "sum",
              "Roas": "mean",
          })
          .reset_index()
      )
      st.dataframe(summary_camp, use_container_width=True)
    else:
      st.info("Upload campaign files to view campaign overview.")

  # 4. Campaign Type Overview Tab
  with tabs[3]:
    st.header("🏷️ Campaign Type Overview")
    if campaign_files:
      df_camp = pd.concat(
          [pd.read_excel(f) for f in campaign_files], ignore_index=True
      )
      if "CampaignType" in df_camp.columns:
        summary_ctype = (
            df_camp.groupby("CampaignType")
            .agg({
                "Clicks": "sum",
                "Orders": "sum",
                "Revenue": "sum",
                "Spend": "sum",
                "Atc": "sum",
                "Roas": "mean",
            })
            .reset_index()
        )
        st.dataframe(summary_ctype, use_container_width=True)
    else:
      st.info("Upload campaign files to view campaign type overview.")

  # 5. Product Overview Tab
  with tabs[4]:
    st.header("📦 Product Overview")
    if product_files:
      df_prod = pd.concat(
          [pd.read_excel(f) for f in product_files], ignore_index=True
      )
      summary_prod = (
          df_prod.groupby("ProductName")
          .agg({
              "Clicks": "sum",
              "Orders": "sum",
              "Revenue": "sum",
              "Spend": "sum",
              "Atc": "sum",
              "Roas": "mean",
          })
          .reset_index()
      )
      st.dataframe(summary_prod, use_container_width=True)
    else:
      st.info("Upload product files to view product overview.")

  # 6. Keyword Overview Tab
  with tabs[5]:
    st.header("🔍 Keyword Overview")
    if keyword_files:
      df_kw = pd.concat(
          [pd.read_excel(f) for f in keyword_files], ignore_index=True
      )
      summary_kw = (
          df_kw.groupby("KeywordName")
          .agg({
              "Clicks": "sum",
              "Orders": "sum",
              "Revenue": "sum",
              "Spend": "sum",
              "Atc": "sum",
              "Roas": "mean",
          })
          .reset_index()
      )
      st.dataframe(summary_kw, use_container_width=True)
    else:
      st.info("Upload keyword files to view keyword overview.")

  # 7. City Overview Tab
  with tabs[6]:
    st.header("🏙️ City Overview")
    if city_files:
      df_city = pd.concat(
          [pd.read_excel(f) for f in city_files], ignore_index=True
      )
      summary_city = (
          df_city.groupby("CityName")
          .agg({
              "Clicks": "sum",
              "Orders": "sum",
              "Revenue": "sum",
              "Spend": "sum",
              "Atc": "sum",
              "Roas": "mean",
          })
          .reset_index()
      )
      st.dataframe(summary_city, use_container_width=True)
    else:
      st.info("Upload city files to view city overview.")

else:
  st.info("👈 Please upload your raw files in the sidebar to load the dashboard.")
