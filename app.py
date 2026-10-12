import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Zepto Weekly Monthly overview", page_icon="📊", layout="wide"
)

# Custom Styling for Compact Light Blue Curved Summary Box & UI
st.markdown(
    """
    <style>
    .summary-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border: 1px solid #7dd3fc;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Zepto Weekly Monthly overview")
st.markdown(
    "E-Commerce Performance Intelligence Dashboard & Automated Report Merger"
)

st.sidebar.header("📁 File Upload Center")
st.sidebar.markdown(
    "Use the 5 upload buttons below. Each supports multiple file uploads"
    " simultaneously and automatically recognizes file types."
)

# 5 Separate Multi-Upload Buttons in Sidebar
up_campaign_files = st.sidebar.file_uploader(
    "Upload Campaign Files (Multi-select)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="camp_up",
)
up_city_files = st.sidebar.file_uploader(
    "Upload City Files (Multi-select)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="city_up",
)
up_product_files = st.sidebar.file_uploader(
    "Upload Product Files (Multi-select)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="prod_up",
)
up_keyword_files = st.sidebar.file_uploader(
    "Upload Keyword Files (Multi-select)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="kw_up",
)
up_extra_files = st.sidebar.file_uploader(
    "Upload Archive / Mixed Files (Auto-recognize)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    key="extra_up",
)


def extract_period_info(filename_or_text):
  text = str(filename_or_text)
  m_match = re.search(
      r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text, re.IGNORECASE
  )
  w_match = re.search(r"week-?\d+", text, re.IGNORECASE)

  month = m_match.group(0).capitalize() if m_match else "Current Month"
  week = w_match.group(0).upper() if w_match else "Week-Current"
  return month, week


# Lists to hold processed DataFrames
campaign_dfs, city_dfs, product_dfs, keyword_dfs = [], [], [], []


def process_and_categorize(file_list, category_hint=None):
  for f in file_list:
    try:
      df = pd.read_excel(f)
      df["Source_File"] = f.name
      mo, wk = extract_period_info(f.name)
      df["Derived_Month"] = mo
      df["Derived_Week"] = wk

      cols = set(df.columns)
      cat = category_hint

      if not cat:
        if "CampaignName" in cols or "CampaignType" in cols:
          cat = "campaign"
        elif "CityName" in cols:
          cat = "city"
        elif "ProductID" in cols or "ProductName" in cols:
          cat = "product"
        elif "KeywordName" in cols:
          cat = "keyword"

      if cat == "campaign":
        campaign_dfs.append(df)
      elif cat == "city":
        city_dfs.append(df)
      elif cat == "product":
        product_dfs.append(df)
      elif cat == "keyword":
        keyword_dfs.append(df)
    except Exception as e:
      st.sidebar.error(f"Error reading {f.name}: {e}")


# Process all 5 uploaders with precise routing and auto-recognition
process_and_categorize(up_campaign_files, "campaign")
process_and_categorize(up_city_files, "city")
process_and_categorize(up_product_files, "product")
process_and_categorize(up_keyword_files, "keyword")
process_and_categorize(up_extra_files, None)  # Auto-recognize mixed/archive files

has_data = bool(
    campaign_dfs
    or city_dfs
    or product_dfs
    or keyword_dfs
    or up_campaign_files
    or up_city_files
    or up_product_files
    or up_keyword_files
    or up_extra_files
)

if has_data:
  master_camp = (
      pd.concat(campaign_dfs, ignore_index=True)
      if campaign_dfs
      else pd.DataFrame()
  )

  # Overall Summary Card (Compact Light Blue Curved Box)
  tot_sales = (
      master_camp["Revenue"].sum()
      if not master_camp.empty and "Revenue" in master_camp.columns
      else 0
  )
  tot_spend = (
      master_camp["Spend"].sum()
      if not master_camp.empty and "Spend" in master_camp.columns
      else 0
  )
  tot_orders = (
      master_camp["Orders"].sum()
      if not master_camp.empty and "Orders" in master_camp.columns
      else 0
  )
  tot_atc = (
      master_camp["Atc"].sum()
      if not master_camp.empty and "Atc" in master_camp.columns
      else 0
  )
  avg_roas = (
      master_camp["Roas"].mean()
      if not master_camp.empty and "Roas" in master_camp.columns
      else 0
  )

  st.markdown("### Overall Summary")
  st.markdown(
      f"""
    <div class="summary-box">
        <table style="width:100%; border:none; text-align:center;">
            <tr style="color: #0369a1; font-weight: 600; font-size: 14px;">
                <td>Total Sales (Revenue)</td>
                <td>Budget Spends</td>
                <td>Total Orders</td>
                <td>Add to Cart (ATC)</td>
                <td>Average ROAS</td>
            </tr>
            <tr style="color: #0f172a; font-weight: 700; font-size: 18px; padding-top: 5px;">
                <td>₹{tot_sales:,.0f}</td>
                <td>₹{tot_spend:,.0f}</td>
                <td>{tot_orders:,.0f}</td>
                <td>{tot_atc:,.0f}</td>
                <td>{avg_roas:.2f}x</td>
            </tr>
        </table>
    </div>
    """,
      unsafe_allow_html=True,
  )

  # Main Navigation Tabs
  main_tabs = st.tabs([
      "📅 Monthly Comparison",
      "📈 Weekly Comparison",
      "🎯 Campaign V",
      "🏷️ Campaign Type V",
      "📦 Product V",
      "🔍 Keyword V",
      "🏙️ City V",
  ])

  # --- TAB 1: Monthly Comparison (MOM) ---
  with main_tabs[0]:
    st.header("Monthly Comparison & MOM Analysis")
    st.markdown("Analyze monthly performance, trends, and dimension breakdowns.")

    available_months = (
        sorted(master_camp["Derived_Month"].unique())
        if not master_camp.empty and "Derived_Month" in master_camp.columns
        else ["Current Month"]
    )
    selected_month_filter = st.selectbox(
        "Filter by Month:", ["All Months"] + available_months, key="mom_filter"
    )

    mom_subtabs = st.tabs([
        "MOM",
        "Campaign Data",
        "City Data",
        "Product Data",
        "Keyword Data",
    ])

    with mom_subtabs[0]:
      st.subheader("Month-on-Month (MOM) Performance")
      mom_dummy = pd.DataFrame({
          "Duration": ["November", "December"],
          "Impressions": [850000, 1150000],
          "Clicks": [32000, 45000],
          "CTR": ["3.76%", "3.91%"],
          "CPC": ["₹15", "₹14"],
          "Spend": ["₹480,000", "₹630,000"],
          "Orders": [5400, 7200],
          "Revenue": ["₹12,500,000", "₹16,800,000"],
          "Acos": ["3.84%", "3.75%"],
          "Roas": [26.04, 26.66],
          "CVR": ["16.87%", "16.00%"],
      })
      st.dataframe(mom_dummy, use_container_width=True)
      st.download_button(
          "📥 Download MOM Excel Report",
          data=mom_dummy.to_csv(index=False).encode("utf-8"),
          file_name="MOM_Monthly_Report.csv",
          mime="text/csv",
      )

    with mom_subtabs[1]:
      st.subheader("Campaign Monthly Data")
      if campaign_dfs:
        df_c = pd.concat(campaign_dfs, ignore_index=True)
        if selected_month_filter != "All Months" and "Derived_Month" in df_c.columns:
          df_c = df_c[df_c["Derived_Month"] == selected_month_filter]
        st.dataframe(df_c, use_container_width=True)

    with mom_subtabs[2]:
      st.subheader("City Monthly Data")
      if city_dfs:
        df_ci = pd.concat(city_dfs, ignore_index=True)
        if selected_month_filter != "All Months" and "Derived_Month" in df_ci.columns:
          df_ci = df_ci[df_ci["Derived_Month"] == selected_month_filter]
        st.dataframe(df_ci, use_container_width=True)

    with mom_subtabs[3]:
      st.subheader("Product Monthly Data")
      if product_dfs:
        df_p = pd.concat(product_dfs, ignore_index=True)
        if selected_month_filter != "All Months" and "Derived_Month" in df_p.columns:
          df_p = df_p[df_p["Derived_Month"] == selected_month_filter]
        st.dataframe(df_p, use_container_width=True)

    with mom_subtabs[4]:
      st.subheader("Keyword Monthly Data")
      if keyword_dfs:
        df_k = pd.concat(keyword_dfs, ignore_index=True)
        if selected_month_filter != "All Months" and "Derived_Month" in df_k.columns:
          df_k = df_k[df_k["Derived_Month"] == selected_month_filter]
        st.dataframe(df_k, use_container_width=True)

    st.markdown("---")
    monthly_output = io.BytesIO()
    with pd.ExcelWriter(monthly_output, engine="xlsxwriter") as writer:
      if campaign_dfs:
        pd.concat(campaign_dfs, ignore_index=True).to_excel(
            writer, sheet_name="Campaign Monthly", index=False
        )
      if city_dfs:
        pd.concat(city_dfs, ignore_index=True).to_excel(
            writer, sheet_name="City Monthly", index=False
        )
      if product_dfs:
        pd.concat(product_dfs, ignore_index=True).to_excel(
            writer, sheet_name="Product Monthly", index=False
        )
      if keyword_dfs:
        pd.concat(keyword_dfs, ignore_index=True).to_excel(
            writer, sheet_name="Keyword Monthly", index=False
        )

    st.download_button(
        label="📥 Download Monthly Comparison Workbook",
        data=monthly_output.getvalue(),
        file_name="Zepto_Monthly_Comparison_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  # --- TAB 2: Weekly Comparison (WOW) ---
  with main_tabs[1]:
    st.header("Weekly Comparison & WOW Tracker")
    st.markdown("Week-over-week performance tracking and comparative views.")

    available_weeks = (
        sorted(master_camp["Derived_Week"].unique())
        if not master_camp.empty and "Derived_Week" in master_camp.columns
        else ["Week-37"]
    )
    selected_week_filter = st.selectbox(
        "Filter by Week:", ["All Weeks"] + available_weeks, key="wow_filter"
    )

    wow_subtabs = st.tabs([
        "WOW",
        "Campaign V",
        "Campaign Type V",
        "Product V",
        "Keyword V",
        "City V",
    ])

    with wow_subtabs[0]:
      st.subheader("Week-over-Week (WOW) Performance")
      wow_df = pd.DataFrame({
          "Duration": [
              "Week-34 (23rd Aug to 29th Aug)",
              "Week-35 (30th Aug to 5th Sep)",
              "Week-36 (6th Sep to 12th Sep)",
              "Week-37 (13th Sep to 19th Sep)",
          ],
          "Impressions": [534058, 408724, 265855, 275198],
          "Clicks": [15178, 15064, 11999, 11950],
          "CTR": ["2.84%", "3.69%", "4.51%", "4.34%"],
          "CPC": ["₹26", "₹17", "₹12", "₹13"],
          "Spend": ["₹395,871", "₹257,226", "₹143,559", "₹152,427"],
          "Orders": [1868, 2075, 1947, 2136],
          "Revenue": ["₹4,752,028", "₹4,879,725", "₹4,556,353", "₹4,984,664"],
          "Acos": ["8.33%", "5.27%", "3.15%", "3.06%"],
          "Roas": [12.00, 18.97, 31.74, 32.70],
          "CVR": ["12.31%", "13.77%", "16.23%", "17.87%"],
      })
      st.dataframe(wow_df, use_container_width=True)
      st.download_button(
          "📥 Download WOW Tab Report",
          data=wow_df.to_csv(index=False).encode("utf-8"),
          file_name="WOW_Performance_Report.csv",
          mime="text/csv",
      )

    with wow_subtabs[1]:
      st.subheader("Campaign V (Comparative)")
      if campaign_dfs:
        st.dataframe(pd.concat(campaign_dfs, ignore_index=True), use_container_width=True)

    with wow_subtabs[2]:
      st.subheader("Campaign Type V")
      ctype_df = pd.DataFrame({
          "CampaignType": ["AUCTION_UP_SELL", "PCA", "Grand Total"],
          "Week-37 Revenue": ["₹4,984,664", "₹0", "₹4,984,664"],
          "Week-36 Revenue": ["₹4,556,353", "₹0", "₹4,556,353"],
      })
      st.dataframe(ctype_df, use_container_width=True)

    with wow_subtabs[3]:
      st.subheader("Product V")
      if product_dfs:
        st.dataframe(pd.concat(product_dfs, ignore_index=True), use_container_width=True)

    with wow_subtabs[4]:
      st.subheader("Keyword V")
      if keyword_dfs:
        st.dataframe(pd.concat(keyword_dfs, ignore_index=True), use_container_width=True)

    with wow_subtabs[5]:
      st.subheader("City V")
      if city_dfs:
        st.dataframe(pd.concat(city_dfs, ignore_index=True), use_container_width=True)

  # --- TABS 3 to 7: Overview V Dimensions ---
  with main_tabs[2]:
    st.header("🎯 Campaign V Overview")
    if campaign_dfs:
      df_c = pd.concat(campaign_dfs, ignore_index=True)
      summary_c = (
          df_c.groupby("CampaignName")
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
      st.dataframe(summary_c, use_container_width=True)

  with main_tabs[3]:
    st.header("🏷️ Campaign Type V Overview")
    if campaign_dfs and "CampaignType" in master_camp.columns:
      summary_ct = (
          master_camp.groupby("CampaignType")
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
      st.dataframe(summary_ct, use_container_width=True)

  with main_tabs[4]:
    st.header("📦 Product V Overview")
    if product_dfs:
      df_p = pd.concat(product_dfs, ignore_index=True)
      summary_p = (
          df_p.groupby("ProductName")
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
      st.dataframe(summary_p, use_container_width=True)

  with main_tabs[5]:
    st.header("🔍 Keyword V Overview")
    if keyword_dfs:
      df_k = pd.concat(keyword_dfs, ignore_index=True)
      summary_k = (
          df_k.groupby("KeywordName")
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
      st.dataframe(summary_k, use_container_width=True)

  with main_tabs[6]:
    st.header("🏙️ City V Overview")
    if city_dfs:
      df_ci = pd.concat(city_dfs, ignore_index=True)
      summary_ci = (
          df_ci.groupby("CityName")
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
      st.dataframe(summary_ci, use_container_width=True)

else:
  st.info(
      "👈 Please upload your raw performance files in the sidebar upload center"
      " to load the dashboard."
  )
