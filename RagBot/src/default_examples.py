DEFAULT_EXAMPLES = """
Example 1 - Last Week (Calendar):
Query: مجموع فروش هفته گذشته
Analysis: "هفته گذشته" = calendar week = {last_week_saturday} to {last_week_friday}
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2", "parameters": {{"1": "{last_week_saturday}", "2": "{last_week_friday}"}}}}

Example 2 - Two Weeks (Rolling):
Query: مجموع فروش دو هفته گذشته
Analysis: "دو هفته گذشته" = rolling 14 days = {two_weeks_ago} to {today_date}
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2", "parameters": {{"1": "{two_weeks_ago}", "2": "{today_date}"}}}}

Example 3 - Three Weeks:
Query: گزارش فروش در سه هفته اخیر
Analysis: "سه هفته اخیر" = rolling 21 days = {three_weeks_ago} to {today_date}
{{"SQL": "SELECT sinv.date AS sinv_date, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{three_weeks_ago}", "2": "{today_date}"}}}}

Example 4 - One Week Rolling vs Calendar:
Query: فروش یک هفته اخیر
Analysis: "یک هفته اخیر" = rolling 7 days (NOT calendar week) = {one_week_ago} to {today_date}
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2", "parameters": {{"1": "{one_week_ago}", "2": "{today_date}"}}}}

Example 5 - This Week:
Query: فروش این هفته چقدر بوده؟
Analysis: "این هفته" = calendar week = {this_week_saturday} to {this_week_friday}
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2", "parameters": {{"1": "{this_week_saturday}", "2": "{this_week_friday}"}}}}

Example 6 - Last Week with Range:
Query: چند تا سند انبار از شنبه هفته پیش تا آخر هفته ثبت شده؟
Analysis: شنبه هفته پیش = {last_week_saturday}, آخر هفته (of last week) = {last_week_friday}
{{"SQL": "SELECT COUNT(liv.id) AS liv_id_count FROM logistics_invvoucher AS liv WHERE liv.date >= $1 AND liv.date <= $2 AND liv.state = $3", "parameters": {{"1": "{last_week_saturday}", "2": "{last_week_friday}", "3": "ثبت شده"}}}}

Example 7 - Specific Day Last Week:
Query: فروش سه‌شنبه هفته پیش
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date = $1", "parameters": {{"1": "{last_week_tuesday}"}}}}

Example 8 - Three Months:
Query: گزارش فروش سه ماه گذشته
Analysis: "سه ماه گذشته" = {three_months_ago} to {today_date}
{{"SQL": "SELECT sinv.date AS sinv_date, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{three_months_ago}", "2": "{today_date}"}}}}

Example 9 - Six Months:
Query: عملکرد فروش شش ماه اخیر
Analysis: "شش ماه اخیر" = {six_months_ago} to {today_date}
{{"SQL": "SELECT sinv.date AS sinv_date, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{six_months_ago}", "2": "{today_date}"}}}}

Example 10 - Date and Text Search:
Query: حداقل مصرف پروژه روزانه گریس از ابتدای سال چقدر بوده؟
{{"SQL": "SELECT MIN(A.lii_major_quantity_sum) AS A_lii_major_quantity_sum_min FROM (SELECT SUM(lii.major_quantity) AS lii_major_quantity_sum, liv.date AS liv_date FROM logistics_invvoucheritem AS lii JOIN logistics_invvoucher AS liv ON liv.id = lii.inventory_voucher_id JOIN logistics_voucherspecification AS lvs ON lvs.id = liv.voucher_specification_id JOIN logistics_parts AS lp ON lp.id = lii.part_id WHERE liv.date >= $1 AND lp.title = $2 AND lvs.title = $3 AND liv.state IN ($4, $5) GROUP BY liv.date) AS A", "parameters": {{"1": "{persian_year_start}", "2": "گریس", "3": "مصرف پروژه", "4": "تایید شده", "5": "ثبت شده"}}}}

Example 11 - Non-SELECT (Return Null):
Query: جدول جدیدی برای محصولات ایجاد کن
{{"SQL": null, "parameters": {{}}}}

Example 12 - Data Modification (Return Null):
Query: قیمت محصول شماره 123 را به 5000 تومان تغییر بده
{{"SQL": null, "parameters": {{}}}}

Example 13 - Numeric Parameter:
Query: اقلام فاکتور با مبلغ خالص بالای 1000000 را نمایش دهید
{{"SQL": "SELECT si.amount AS si_amount, si.fee AS si_fee, si.net_price AS si_net_price, si.unit_title AS si_unit_title, si.description_c AS si_description_c FROM sales_invoiceitem AS si WHERE si.net_price > $1", "parameters": {{"1": "1000000"}}}}

Example 14 - Today vs Yesterday:
Query: فروش امروز نسبت به دیروز چقدر تغییر کرده؟
{{"SQL": "SELECT (SELECT SUM(si.net_price) FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date = $1) - (SELECT SUM(si.net_price) FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date = $2) AS sales_difference", "parameters": {{"1": "{today_date}", "2": "{yesterday_date}"}}}}

Example 15 - Previous Year:
Query: مجموع فروش سال قبل چقدر بوده؟
{{"SQL": "SELECT SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2", "parameters": {{"1": "{prev_persian_year_start}", "2": "{prev_persian_year_end}"}}}}

Example 16 - Last Month:
Query: گزارش فروش ماه گذشته
{{"SQL": "SELECT sinv.date AS sinv_date, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{last_month_date}", "2": "{today_date}"}}}}

Example 17 - Two Months:
Query: آمار فروش دو ماه اخیر
Analysis: "دو ماه اخیر" = {two_months_ago} to {today_date}
{{"SQL": "SELECT sinv.date AS sinv_date, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{two_months_ago}", "2": "{today_date}"}}}}

Example 18 - No Parameters:
Query: میانگین و حداکثر مبلغ فاکتورها
{{"SQL": "SELECT AVG(si.net_price) AS si_net_price_avg, MAX(si.net_price) AS si_net_price_max FROM sales_invoiceitem AS si", "parameters": {{}}}}

Example 19 - Companies with Two Weeks:
Query: مقایسه فروش شرکت‌های شفا و تهران دارو در دو هفته گذشته
Analysis: "دو هفته گذشته" = {two_weeks_ago} to {today_date}
{{"SQL": "SELECT sinv.cmp_title AS sinv_cmp_title, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 AND (sinv.cmp_title = $3 OR sinv.cmp_title = $4) GROUP BY sinv.cmp_title", "parameters": {{"1": "{two_weeks_ago}", "2": "{today_date}", "3": "شفا", "4": "تهران دارو"}}}}

Example 20 - Ten Days:
Query: آمار ده روز گذشته
Analysis: "ده روز گذشته" = {ten_days_ago} to {today_date}
{{"SQL": "SELECT sinv.date AS sinv_date, COUNT(sinv.id) AS sinv_id_count, SUM(si.net_price) AS si_net_price_sum FROM sales_invoiceitem AS si JOIN sales_invoice AS sinv ON si.invoice_id = sinv.id WHERE sinv.date >= $1 AND sinv.date <= $2 GROUP BY sinv.date ORDER BY sinv.date", "parameters": {{"1": "{ten_days_ago}", "2": "{today_date}"}}}}
"""
