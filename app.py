import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Zepto Reports Merger",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Zepto Reports Merger & Intelligence Dashboard")
st.markdown(
    "Upload any combination of raw performance reports below. The app will"
    " automatically identify their type and process them!"
)

st.sidebar.header("📁 File Upload Center")
uploaded_files = st.sidebar.file_uploader(
    "Upload All Raw Files (Campaign, City, Product, Keyword)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
)


def classify_and_split_files(files):
  campaign_dfs, city_dfs, product_dfs, keyword_dfs = [], [], [], []

  for f in files:
    try:
      df = pd.read_excel(f)
      cols = set(df.columns)

      # Signature column checks
      if "CampaignName" in cols or "CampaignType" in cols:
        df["Source_File"] = f.name
        campaign_dfs.append(df)
      elif "CityName" in cols:
        df["Source_File"] = f.name
        city_dfs.append(df)
      elif "ProductID" in cols or "ProductName" in cols:
        df["Source_File"] = f.name
        product_dfs.append(df)
      elif "KeywordName" in cols:
        df["Source_File"] = f.name
        keyword_dfs.append(df)
    except Exception as e:
      st.error(f"Error reading {f.name}: {e}")

  return campaign_dfs, city_dfs, product_dfs, keyword_dfs


def extract_month_from_name(filename):
  match = re.search(
      r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
      filename,
      re.IGNORECASE,
  )
  if match:
    return match.group(0).capitalize()
  return "Current Month"


# Main Dashboard Logic
if uploaded_files:
  campaign_list, city_list, product_list, keyword_list = (
      classify_and_split_files(uploaded_files)
  )

  st.sidebar.success(
      f"Identified: {len(campaign_list)} Campaign, {len(city_list)} City,"
      f" {len(product_list)} Product, {len(keyword_list)} Keyword files."
  )

  # Executive KPI Summary
  if campaign_list:
    master_campaign_df = pd.concat(campaign_list, ignore_index=True)
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
        "Preview and download aggregated monthly performance across all"
        " dimensions."
    )

    m_tab1, m_tab2, m_tab3, m_tab4 = st.tabs(
        ["Campaign Data", "City Data", "Product Data", "Keyword Data"]
    )

    with m_tab1:
      st.subheader("Campaign Monthly View")
      if campaign_list:
        st.dataframe(
            pd.concat(campaign_list, ignore_index=True), use_container_width=True
        )
      else:
        st.info("No campaign files detected.")

    with m_tab2:
      st.subheader("City Monthly View")
      if city_list:
        st.dataframe(
            pd.concat(city_list, ignore_index=True), use_container_width=True
        )
      else:
        st.info("No city files detected.")

    with m_tab3:
      st.subheader("Product Monthly View")
      if product_list:
        st.dataframe(
            pd.concat(product_list, ignore_index=True), use_container_width=True
        )
      else:
        st.info("No product files detected.")

    with m_tab4:
      st.subheader("Keyword Monthly View")
      if keyword_list:
        st.dataframe(
            pd.concat(keyword_list, ignore_index=True), use_container_width=True
        )
      else:
        st.info("No keyword files detected.")

    st.markdown("---")
    monthly_output = io.BytesIO()
    with pd.ExcelWriter(monthly_output, engine="xlsxwriter") as writer:
      if campaign_list:
        pd.concat(campaign_list, ignore_index=True).to_excel(
            writer, sheet_name="Campaign Monthly", index=False
        )
      if city_list:
        pd.concat(city_list, ignore_index=True).to_excel(
            writer, sheet_name="City Monthly", index=False
        )
      if product_list:
        pd.concat(product_list, ignore_index=True).to_excel(
            writer, sheet_name="Product Monthly", index=False
        )
      if keyword_list:
        pd.concat(keyword_list, ignore_index=True).to_excel(
            writer, sheet_name="Keyword Monthly", index=False
        )

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
      st.subheader("Campaign V")
      if campaign_list:
        df_c_v = campaign_list[0]
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
      if product_list:
        df_p_v = product_list[0]
        st.dataframe(df_p_v, use_container_width=True)
        st.download_button(
            "📥 Download Product V Tab",
            data=df_p_v.to_csv(index=False).encode("utf-8"),
            file_name="Product_V.csv",
            mime="text/csv",
        )

    with w_subtabs[4]:
      st.subheader("Keyword V")
      if keyword_list:
        df_k_v = keyword_list[0]
        st.dataframe(df_k_v, use_container_width=True)
        st.download_button(
            "📥 Download Keyword V Tab",
            data=df_k_v.to_csv(index=False).encode("utf-8"),
            file_name="Keyword_V.csv",
            mime="text/csv",
        )

    with w_subtabs[5]:
      st.subheader("City V")
      if city_list:
        df_ci_v = city_list[0]
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
    if campaign_list:
      df_camp = pd.concat(campaign_list, ignore_index=True)
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
      st.info("Upload campaign files to view overview.")

  # 4. Campaign Type Overview Tab
  with tabs[3]:
    st.header("🏷️ Campaign Type Overview")
    if campaign_list:
      df_camp = pd.concat(campaign_list, ignore_index=True)
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
      st.info("Upload campaign files to view overview.")

  # 5. Product Overview Tab
  with tabs[4]:
    st.header("📦 Product Overview")
    if product_list:
      df_prod = pd.concat(product_list, ignore_index=True)
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
      st.info("Upload product files to view overview.")

  # 6. Keyword Overview Tab
  with tabs[5]:
    st.header("🔍 Keyword Overview")
    if keyword_list:
      df_kw = pd.concat(keyword_list, ignore_index=True)
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
      st.info("Upload keyword files to view overview.")

  # 7. City Overview Tab
  with tabs[6]:
    st.header("🏙️ City Overview")
    if city_list:
      df_city = pd.concat(city_list, ignore_index=True)
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
      st.info("Upload city files to view overview.")

else:
  st.info(
      "👈 Please upload your raw performance files in the sidebar to start."
  )
