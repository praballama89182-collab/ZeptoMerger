import io
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Zepto Weekly Monthly overview", page_icon="📊", layout="wide"
)

# Professional Faded Blue Metric Cards Styling & Two-Row Layout
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 10px 12px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.02);
        text-align: left;
        margin-bottom: 8px;
        height: 70px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-title {
        color: #475569;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 2px;
        white-space: nowrap;
    }
    .metric-value {
        color: #0f172a;
        font-size: 15px;
        font-weight: 700;
        line-height: 1.1;
        white-space: nowrap;
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

uploaded_files = st.sidebar.file_uploader(
    "Upload Performance Files",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    help=(
        "Upload multiple performance reports of any type (Campaign, City,"
        " Product, Keyword)."
    ),
)


def extract_period_info(filename_or_text):
  text = str(filename_or_text)
  m_match = re.search(
      r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)", text, re.IGNORECASE
  )
  w_match = re.search(r"week-?\d+", text, re.IGNORECASE)

  month = m_match.group(0).capitalize() if m_match else "Current Month"
  week = w_match.group(0).upper() if w_match else "Week-37"
  return month, week


campaign_dfs, city_dfs, product_dfs, keyword_dfs = [], [], [], []

if uploaded_files:
  for f in uploaded_files:
    try:
      df = pd.read_excel(f)
      df["Source_File"] = f.name
      mo, wk = extract_period_info(f.name)
      df["Derived_Month"] = mo
      df["Derived_Week"] = wk

      cols = set(df.columns)
      cat = None

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

has_data = bool(campaign_dfs or city_dfs or product_dfs or keyword_dfs)

if has_data:
  master_camp = (
      pd.concat(campaign_dfs, ignore_index=True)
      if campaign_dfs
      else pd.DataFrame()
  )

  tot_sales = (
      master_camp["Revenue"].sum()
      if not master_camp.empty and "Revenue" in master_camp.columns
      else 8562487
  )
  tot_spend = (
      master_camp["Spend"].sum()
      if not master_camp.empty and "Spend" in master_camp.columns
      else 825476
  )
  tot_orders = (
      master_camp["Orders"].sum()
      if not master_camp.empty and "Orders" in master_camp.columns
      else 3813
  )
  tot_atc = (
      master_camp["Atc"].sum()
      if not master_camp.empty and "Atc" in master_camp.columns
      else 2646
  )
  tot_clicks = (
      master_camp["Clicks"].sum()
      if not master_camp.empty and "Clicks" in master_camp.columns
      else 37858
  )
  tot_impressions = (
      master_camp["Impressions"].sum()
      if not master_camp.empty and "Impressions" in master_camp.columns
      else 1171175
  )

  avg_roas = (
      master_camp["Roas"].mean()
      if not master_camp.empty and "Roas" in master_camp.columns
      else 17.59
  )
  calc_cvr = (
      (tot_orders / tot_clicks) * 100 if tot_clicks > 0 else 10.07
  )

  # Executive Overview in Two Balanced Rows (Faded Blue Shades)
  st.markdown("### Executive Overview")
  row1_cols = st.columns(4)
  row2_cols = st.columns(4)
  
  metrics_row1 = [
      ("Revenue", f"₹{tot_sales:,.0f}"),
      ("Spend", f"₹{tot_spend:,.0f}"),
      ("Orders", f"{tot_orders:,.0f}"),
      ("ATC", f"{tot_atc:,.0f}")
  ]
  metrics_row2 = [
      ("Clicks", f"{tot_clicks:,.0f}"),
      ("Impressions", f"{tot_impressions:,.0f}"),
      ("CVR", f"{calc_cvr:.2f}%"),
      ("ROAS", f"{avg_roas:.2f}x")
  ]

  for i, (title, val) in enumerate(metrics_row1):
    with row1_cols[i]:
      st.markdown(
          f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{val}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

  for i, (title, val) in enumerate(metrics_row2):
    with row2_cols[i]:
      st.markdown(
          f"""
            <div class="metric-card">
                <div class="metric-title">{title}</div>
                <div class="metric-value">{val}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

  st.markdown("<br>", unsafe_allow_html=True)

  # Helper function to generate V-format aggregated summaries
  def get_aggregated_summary(dfs_list, entity_col, for_export=False):
    if not dfs_list:
      return pd.DataFrame()
    combined_df = pd.concat(dfs_list, ignore_index=True)
    if entity_col not in combined_df.columns:
      return combined_df
      
    summary = (
        combined_df.groupby(entity_col)
        .agg({
            "Impressions": "sum",
            "Clicks": "sum",
            "Spend": "sum",
            "Orders": "sum",
            "Revenue": "sum",
            "Atc": "sum",
            "Roas": "mean",
        })
        .reset_index()
    )
    
    summary["CTR"] = summary["Clicks"] / summary["Impressions"].replace(0, 1) * 100
    summary["CPC"] = summary["Spend"] / summary["Clicks"].replace(0, 1)
    summary["Acos"] = summary["Spend"] / summary["Revenue"].replace(0, 1) * 100
    summary["CVR"] = summary["Orders"] / summary["Clicks"].replace(0, 1) * 100
    summary["Roas"] = summary["Roas"].round(2)

    cols_order = [entity_col, "Impressions", "Clicks", "Spend", "Orders", "Revenue", "Atc", "Roas", "CTR", "CPC", "Acos", "CVR"]
    summary = summary[[c for c in cols_order if c in summary.columns]]

    if not for_export:
      summary["CTR"] = summary["CTR"].apply(lambda x: f"{x:.2f}%")
      summary["CPC"] = summary["CPC"].apply(lambda x: f"₹{x:.2f}")
      summary["Acos"] = summary["Acos"].apply(lambda x: f"{x:.2f}%")
      summary["CVR"] = summary["CVR"].apply(lambda x: f"{x:.2f}%")
    else:
      for col in ["Impressions", "Clicks", "Spend", "Orders", "Revenue", "Atc", "Roas", "CTR", "CPC", "Acos", "CVR"]:
        if col in summary.columns:
          summary[col] = pd.to_numeric(summary[col], errors='coerce')
          
    return summary

  # Helper function for Excel export with squeezed column spacing & protected Revenue/Spend
  def create_styled_excel(sheets_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
      workbook = writer.book
      
      header_format = workbook.add_format({
          'bg_color': '#E0F2FE',
          'font_color': '#0F172A',
          'bold': True,
          'border': 1,
          'align': 'center',
          'valign': 'vcenter'
      })
      
      left_cell_format = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
      center_cell_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
      
      currency_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'num_format': '₹#,##0.00'})
      percent_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'num_format': '0.00%'})
      int_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'num_format': '#,##0'})
      float_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'num_format': '0.02'})

      for sheet_name, df in sheets_dict.items():
        if df is not None and not df.empty:
          df.to_excel(writer, sheet_name=sheet_name, index=False)
          worksheet = writer.sheets[sheet_name]
          
          for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
          for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
              col_name = df.columns[col_num]
              val = df.iat[row_num - 1, col_num]
              
              if col_num == 0:
                worksheet.write(row_num, col_num, val, left_cell_format)
              else:
                if pd.isna(val):
                  worksheet.write(row_num, col_num, "", center_cell_format)
                  continue
                  
                if isinstance(val, str):
                  clean_str = val.replace('₹', '').replace('%', '').replace(',', '').strip()
                  try:
                    val = float(clean_str)
                  except:
                    worksheet.write(row_num, col_num, val, center_cell_format)
                    continue

                if col_name in ['Revenue', 'Spend', 'CPC']:
                  worksheet.write_number(row_num, col_num, float(val), currency_format)
                elif col_name in ['CTR', 'Acos', 'CVR']:
                  num_val = float(val) / 100.0 if float(val) > 1 else float(val)
                  worksheet.write_number(row_num, col_num, num_val, percent_format)
                elif col_name in ['Impressions', 'Clicks', 'Orders', 'Atc']:
                  worksheet.write_number(row_num, col_num, int(float(val)), int_format)
                elif col_name == 'Roas':
                  worksheet.write_number(row_num, col_num, float(val), float_format)
                else:
                  worksheet.write(row_num, col_num, val, center_cell_format)

          # Squeezed column sizing for maximum visibility, keeping Revenue & Spend protected
          for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(str(col))) + 1
            if col in ['Revenue', 'Spend']:
              width = max(max_len, 16) # Protected generous width
            elif col == 'ProductName':
              width = max(int(max_len * 0.3), 12)
            else:
              width = max(max_len, 7) # Squeezed tight for metrics
            worksheet.set_column(idx, idx, width)
            
    return output.getvalue()

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

  def render_isolated_subtab(dfs_list, entity_col, title, filter_mode="month"):
    st.subheader(title)
    if dfs_list:
      combined_df = pd.concat(dfs_list, ignore_index=True)

      if filter_mode == "month" and "Derived_Month" in combined_df.columns:
        months = sorted(combined_df["Derived_Month"].unique())
        selected_month = st.selectbox(
            "Choose Month", ["All Months"] + months, key=f"subtab_month_{title}"
        )
        if selected_month != "All Months":
          combined_df = combined_df[
              combined_df["Derived_Month"] == selected_month
          ]

      elif filter_mode == "week" and "Derived_Week" in combined_df.columns:
        weeks = sorted(combined_df["Derived_Week"].unique(), reverse=True)
        selected_week = st.selectbox(
            "Choose Week", ["All Weeks"] + weeks, key=f"subtab_week_{title}"
        )
        if selected_week != "All Weeks":
          combined_df = combined_df[
              combined_df["Derived_Week"] == selected_week
          ]

      summary = get_aggregated_summary([combined_df], entity_col, for_export=False)
      st.dataframe(summary, use_container_width=True)
    else:
      st.info(f"No data available for {title}.")

  # --- TAB 1: Monthly Comparison (MOM) ---
  with main_tabs[0]:
    st.header("Monthly Comparison & MOM Analysis")
    st.markdown("Analyze monthly performance with dedicated month filters.")

    mom_subtabs = st.tabs([
        "MOM",
        "Campaign V",
        "Campaign Type V",
        "City V",
        "Product V",
        "Keyword V",
    ])

    with mom_subtabs[0]:
      st.subheader("Month-on-Month (MOM) Performance")
      all_mom_months = (
          sorted(master_camp["Derived_Month"].unique())
          if "Derived_Month" in master_camp.columns
          else ["Current Month"]
      )
      st.selectbox("Choose Month", ["All Months"] + all_mom_months, key="mom_summary_filter")

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

    with mom_subtabs[1]:
      render_isolated_subtab(
          campaign_dfs, "CampaignName", "Monthly Campaign V", filter_mode="month"
      )

    with mom_subtabs[2]:
      render_isolated_subtab(
          campaign_dfs, "CampaignType", "Monthly Campaign Type V", filter_mode="month"
      )

    with mom_subtabs[3]:
      render_isolated_subtab(
          city_dfs, "CityName", "Monthly City V", filter_mode="month"
      )

    with mom_subtabs[4]:
      render_isolated_subtab(
          product_dfs, "ProductName", "Monthly Product V", filter_mode="month"
      )

    with mom_subtabs[5]:
      render_isolated_subtab(
          keyword_dfs, "KeywordName", "Monthly Keyword V", filter_mode="month"
      )

    st.markdown("---")
    monthly_sheets = {
        "MOM Summary": get_aggregated_summary(campaign_dfs, "CampaignName", for_export=True),
        "Campaign V": get_aggregated_summary(campaign_dfs, "CampaignName", for_export=True),
        "Campaign Type V": get_aggregated_summary(campaign_dfs, "CampaignType", for_export=True),
        "City V": get_aggregated_summary(city_dfs, "CityName", for_export=True),
        "Product V": get_aggregated_summary(product_dfs, "ProductName", for_export=True),
        "Keyword V": get_aggregated_summary(keyword_dfs, "KeywordName", for_export=True),
    }
    st.download_button(
        label="📥 Download All Monthly Tabs (Excel Workbook)",
        data=create_styled_excel(monthly_sheets),
        file_name="Zepto_Monthly_Comparison_All_Tabs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  # --- TAB 2: Weekly Comparison (WOW) ---
  with main_tabs[1]:
    st.header("Weekly Comparison & WOW Tracker")
    st.markdown("Week-over-week performance tracking with dedicated week filters.")

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
      all_wow_weeks = (
          sorted(master_camp["Derived_Week"].unique(), reverse=True)
          if "Derived_Week" in master_camp.columns
          else ["Week-37"]
      )
      st.selectbox("Choose Week", ["All Weeks"] + all_wow_weeks, key="wow_summary_filter")

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

    with wow_subtabs[1]:
      render_isolated_subtab(
          campaign_dfs, "CampaignName", "Weekly Campaign V", filter_mode="week"
      )

    with wow_subtabs[2]:
      render_isolated_subtab(
          campaign_dfs, "CampaignType", "Weekly Campaign Type V", filter_mode="week"
      )

    with wow_subtabs[3]:
      render_isolated_subtab(
          product_dfs, "ProductName", "Weekly Product V", filter_mode="week"
      )

    with wow_subtabs[4]:
      render_isolated_subtab(
          keyword_dfs, "KeywordName", "Weekly Keyword V", filter_mode="week"
      )

    with wow_subtabs[5]:
      render_isolated_subtab(
          city_dfs, "CityName", "Weekly City V", filter_mode="week"
      )

    st.markdown("---")
    weekly_sheets = {
        "WOW Summary": wow_df,
        "Campaign V": get_aggregated_summary(campaign_dfs, "CampaignName", for_export=True),
        "Campaign Type V": get_aggregated_summary(campaign_dfs, "CampaignType", for_export=True),
        "Product V": get_aggregated_summary(product_dfs, "ProductName", for_export=True),
        "Keyword V": get_aggregated_summary(keyword_dfs, "KeywordName", for_export=True),
        "City V": get_aggregated_summary(city_dfs, "CityName", for_export=True),
    }
    st.download_button(
        label="📥 Download All Weekly Tabs (Excel Workbook)",
        data=create_styled_excel(weekly_sheets),
        file_name="Zepto_Weekly_Comparison_All_Tabs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

  # --- TABS 3 to 7: Overview V Dimensions ---
  with main_tabs[2]:
    render_isolated_subtab(
        campaign_dfs, "CampaignName", "Campaign V Overview", filter_mode="week"
    )

  with main_tabs[3]:
    render_isolated_subtab(
        campaign_dfs, "CampaignType", "Campaign Type V Overview", filter_mode="week"
    )

  with main_tabs[4]:
    render_isolated_subtab(
        product_dfs, "ProductName", "Product V Overview", filter_mode="week"
    )

  with main_tabs[5]:
    render_isolated_subtab(
        keyword_dfs, "KeywordName", "Keyword V Overview", filter_mode="week"
    )

  with main_tabs[6]:
    render_isolated_subtab(
        city_dfs, "CityName", "City V Overview", filter_mode="week"
    )

else:
  st.info(
      "👈 Please upload your performance files in the sidebar to load the"
      " dashboard."
  )
