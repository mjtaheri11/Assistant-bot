
CRM_BO = """
## crm_campaignLead
- **Title**: سرنخ مرتبط با کمپین
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - firstname: نام سرنخ
    - lastname: نام خانوادگی سرنخ
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
- **Relations**: None

## crm_leadOpportunity
- **Title**: فرصت مرتبط با سرنخ
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - name: نام فرصت
    - close_date: تاریخ بستن فرصت
    - pipeline: روند فروش
    - stage: مرحله فروش
    - price: مبلغ
    - expected_price: مبلغ مورد انتظار
    - success_probability: احتمال موفقیت
- **Relations**: None

## crm_customer
- **Title**: مشتری
- **Context**: crm
- **Parameters**: 
  - crm_customer_p1: از تاریخ ایجاد (Date)
  - crm_customer_p2: تا تاریخ ایجاد (Date)
  - crm_customer_p3: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - fullname: نام کامل مشتری
    - customer_type: نوع طرف تجاری
    - rate: میزان جذابیت
    - national_id: کد/شناسه ملی
    - website: وب سایت
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
    - industry: صنعت
    - subindustry: زیرصنعت
    - code: کد مشتری
    - sales_customer_code: کد مشتری در زیرسیستم فروش
    - registration_number: شماره ثبت
    - description: توضیحات
    - tax_group_display: گروه مالیاتی
    - customer_owner_display: کاربر پیگیری کننده
    - customer_creator_display: کاربر ایجاد کننده
    - created_at: تاریخ ایجاد
    - customer_editor_display: آخرین کاربر ویرایش کننده
    - updated_at: آخرین تاریخ ویرایش
- **Relations**:
  - crm_customerPhone: شماره تماس‌های مشتری (foreign key: id to crm_customerPhone.customer_id)
  - crm_customerEmail: ایمیل‌های مشتری (foreign key: id to crm_customerEmail.customer_id)
  - crm_customerAddress: آدرس‌های مشتری (foreign key: id to crm_customerAddress.customer_id)
  - crm_customerOpportunity: فرصت مرتبط با مشتری (foreign key: id to crm_customerOpportunity.customer_id)
  - crm_customerContact: فرد مرتبط با مشتری (foreign key: id to crm_customerContact.customer_id)
  - crm_customerLead: سرنخ مرتبط با مشتری (foreign key: id to crm_customerLead.customer_id)
  - crm_customerCampaign: کمپین مرتبط با مشتری (foreign key: id to crm_customerCampaign.customer_id)
  - crm_customerGrouping: گروه‌های عضو مرتبط با مشتری (foreign key: id to crm_customerGrouping.customer_id)
  - crm_customerQuote: پیش فاکتورهای مرتبط با مشتری (foreign key: id to crm_customerQuote.customer_id)

## crm_quoteitem
- **Title**: قلم پیش فاکتور
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - unit_title: واحد سنجش
    - store_title: انبار
    - amount: مقدار
    - company_title: شرکت
    - fee: فی
    - description: توضیحات
    - deduction_price: جمع تخفیف
    - surcharges: جمع عوامل افزاینده
    - tax_price: مالیات بر ارزش افزوده
    - total_price: مبلغ ناخالص
    - net_price: مبلغ خالص
    - functional_deduction_price: جمع تخفیف به ارز عملیاتی
    - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
    - functional_tax_price: جمع مالیات بر ارزش افزوده به ارز عملیاتی
    - functional_total_price: مبلغ ناخالص به ارز عملیاتی
    - functional_net_price: مبلغ خالص به ارز عملیاتی
- **Relations**: None

## crm_campaignCustomer
- **Title**: مشتری مرتبط با کمپین
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - fullname: نام کامل مشتری
    - customer_type: نوع طرف تجاری
    - code: کد مشتری
    - sales_customer_code: کد مشتری در زیرسیستم فروش
- **Relations**: None

## crm_lead
- **Title**: سرنخ
- **Context**: crm
- **Parameters**: 
  - crm_lead_p1: از تاریخ ایجاد (Date)
  - crm_lead_p2: تا تاریخ ایجاد (Date)
  - crm_lead_p3: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - salutation: پیشوند
    - firstname: نام سرنخ
    - lastname: نام خانوادگی سرنخ
    - customer_name: نام مشتری
    - lead_owner_display: کاربر پیگیری کننده
    - lead_state: مرحله
    - lead_type: نوع طرف تجاری
    - national_code: شناسه/کد ملی مشتری
    - source: منبع
    - source_note: توضیحات منبع
    - rate: میزان جذابیت
    - primary_campaign: کمپین اصلی
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
    - industry: صنعت
    - subindustry: زیرصنعت
    - website: وب سایت
    - birthdate: تاریخ تولد
    - lead_product_grouping_display: دسته محصول مورد نیاز
    - lost_reason: دلیل از دست رفتن
    - description: توضیحات
    - convert_date: تاریخ تبدیل
    - lead_creator_display: کاربر ایجاد کننده
    - created_at: تاریخ ایجاد
    - lead_editor_display: آخرین کاربر ویرایش کننده
    - updated_at: آخرین تاریخ ویرایش
- **Relations**:
  - crm_leadPhone: شماره تماس‌های سرنخ (foreign key: id to crm_leadPhone.lead_id)
  - crm_leadEmail: ایمیل‌های سرنخ (foreign key: id to crm_leadEmail.lead_id)
  - crm_leadAddress: آدرس‌های سرنخ (foreign key: id to crm_leadAddress.lead_id)
  - crm_leadCampaign: کمپین‌های سرنخ (foreign key: id to crm_leadCampaign.lead_id)
  - crm_leadCustomer: مشتری مرتبط با سرنخ (foreign key: customer_id to crm_leadCustomer.id)
  - crm_leadContact: فرد مرتبط با سرنخ (foreign key: contact_id to crm_leadContact.id)
  - crm_leadOpportunity: فرصت مرتبط با سرنخ (foreign key: opportunity_id to crm_leadOpportunity.id)

## crm_contactCustomer
- **Title**: مشتری مرتبط با فرد
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - fullname: نام کامل مشتری
    - customer_type: نوع طرف تجاری
    - code: کد مشتری
    - sales_customer_code: کد مشتری در زیرسیستم فروش
- **Relations**: None

## crm_leadAddress
- **Title**: آدرس‌های سرنخ
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - address_c: آدرس
    - lead_division_display: منطقه جغرافیایی
    - country: کشور
    - province: استان
    - city: شهر
    - postal_code: کد پستی
    - tel: تلفن
    - fax: دورنگار
    - is_primary: اصلی
- **Relations**: None

## crm_leadCustomer
- **Title**: مشتری مرتبط با سرنخ
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - fullname: نام کامل مشتری
    - customer_type: نوع طرف تجاری
    - code: کد مشتری
    - sales_customer_code: کد مشتری در زیرسیستم فروش
- **Relations**: None

## crm_quoteopportunity
- **Title**: فرصت مرتبط با پیش فاکتور
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - company_title: شرکت
    - opportunity_title: نام فرصت
    - opportunity_close_date: تاریخ بستن
    - opportunity_pipeline: روند فروش
    - opportunity_stage: مرحله
    - opportunity_price: مبلغ
    - opportunity_expected_price: مبلغ مورد انتظار
    - opportunity_success_probability: احتمال موفقیت
- **Relations**: None

## crm_customerPhone
- **Title**: شماره تماس‌های مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - number_c: تلفن
    - code: پیش‌شماره
    - extension: شماره داخلی
    - is_primary: اصلی
- **Relations**: None

## crm_customerContact
- **Title**: فرد مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - first_name: نام فرد
    - last_name: نام خانوادگی فرد
    - title: سمت
- **Relations**: None

## crm_customerCampaign
- **Title**: کمپین مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - name: نام
    - start_date: تاریخ شروع
    - end_date: تاریخ پایان
    - campaign_parent_display: کمپین مادر
    - description: توضیحات
    - stage: مرحله
    - campaign_owner_display: کاربر پیگیری کننده
    - budget: بودجه
    - expected_income: درآمد مورد انتظار
    - actual_cost: هزینه واقعی
- **Relations**: None

## crm_customerGrouping
- **Title**: گروه‌های عضو مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - group_title: گروه
    - grouping_title: گروه‌بندی
- **Relations**: None

## crm_opportunityquote
- **Title**: پیش فاکتور مرتبط با فرصت
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - title: نام پیش فاکتور
    - date: تاریخ پیش فاکتور
    - number: شماره پیش فاکتور
    - total_price: مبلغ ناخالص
    - deductions: کسورات
    - additions: اضافات
    - net_price: مبلغ خالص
    - sales_area_title: حوزه فروش
    - sales_office_title: دفتر فروش
    - currency_title: ارز
    - owner_display_name: کاربر پیگیری کننده
    - created_at: تاریخ ایجاد
    - company_title: شرکت
- **Relations**: None

## crm_opportunity
- **Title**: فرصت
- **Context**: crm
- **Parameters**: 
  - crm_opportunity_p1: از تاریخ بستن فرصت (Date)
  - crm_opportunity_p2: تا تاریخ بستن فرصت (Date)
  - crm_opportunity_p3: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - name: نام فرصت
    - customer_title: نام مشتری
    - pipeline: روند فروش
    - stage: مرحله فروش
    - success_probability: احتمال موفقیت
    - close_date: تاریخ بستن فرصت
    - price: مبلغ
    - currency_title: ارز
    - expected_price: مبلغ مورد انتظار
    - created_by: کاربر ایجاد کننده
    - user_display_name: کاربر پیگیری کننده
    - updated_by: آخرین کاربر ویرایش کننده
    - campaign_name: کمپین
    - description: توضیحات
    - company_title: شرکت
- **Relations**:
  - crm_opportunityitem: قلم فرصت (foreign key: id to crm_opportunityitem.opportunity_id)
  - crm_opportunitycustomer: مشتری (foreign key: customer_id to crm_opportunitycustomer.id)
  - crm_opportunitylead: سرنخ (foreign key: id to crm_opportunitylead.opportunity_id)
  - crm_opportunityquote: پیش فاکتور (foreign key: id to crm_opportunityquote.related_opportunity_id)

## crm_quote
- **Title**: پیش فاکتور
- **Context**: crm
- **Parameters**: 
  - crm_quote_p1: از تاریخ (Date)
  - crm_quote_p2: تا تاریخ (Date)
  - crm_quote_p3: شرکت پیش فاکتور (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - company_title: شرکت
    - title: عنوان پیش فاکتور
    - fiscal_year_title: سال مالی
    - number: شماره پیش فاکتور
    - date: تاریخ
    - description: توضیحات
    - customer_name: مشتری
    - sales_area_title: حوزه فروش
    - branch_title: شعبه
    - sales_office_title: دفتر فروش
    - settlement_method_title: روش تسویه
    - related_opportunity_title: نام فرصت
    - currency_title: ارز
    - currency_rate_type_title: نوع نرخ ارز
    - functional_currency_rate: نرخ ارز عملیاتی
    - total_price: مبلغ ناخالص
    - net_price: مبلغ خالص
    - deductions: جمع کسور
    - surcharges: جمع عوامل افزاینده
    - tax_price: جمع مالیات
    - functional_total_price: مبلغ ناخالص به ارز عملیاتی
    - functional_net_price: مبلغ خالص به ارز عملیاتی
    - functional_deductions: جمع تخفیف به ارز عملیاتی
    - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
    - functional_tax_price: جمع مالیات به ارز عملیاتی
    - owner_name: کاربر پیگیری کننده
    - creator_name: کاربر ایجاد کننده
    - updater_name: کاربر ویرایش کننده
    - created_at: تاریخ ایجاد
    - updated_at: آخرین تاریخ تغییر
- **Relations**:
  - crm_quoteitem: قلم پیش فاکتور (foreign key: id to crm_quoteitem.quote_id)
  - crm_quoteinvoice: فاکتور مرتبط با پیش فاکتور (foreign key: id to crm_quoteinvoice.quote_id)
  - crm_quotecustomer: مشتری مرتبط با پیش فاکتور (foreign key: customer_id to crm_quotecustomer.id)
  - crm_quoteopportunity: فرصت مرتبط با پیش فاکتور (foreign key: id to crm_quoteopportunity.quote_id)

## crm_quoteinvoice
- **Title**: فاکتور مرتبط با پیش فاکتور
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - invoice_company_title: شرکت
    - invoice_fy_title: سال مالی
    - invoice_number: شماره فاکتور
    - invoice_date: تاریخ
    - invoice_description: توضیحات
    - invoice_customer_code: کد مشتری
    - invoice_customer_fullname: نام مشتری
    - sa2: حوزه فروش
    - invoice_so_title: دفتر فروش
    - invoice_sm_title: روش تسویه
    - invoice_cur_title: ارز
    - invoice_functional_currency_rate: نرخ ارز عملیاتی
    - invoice_total_price: مبلغ ناخالص
    - invoice_net_price: مبلغ خالص
    - invoice_deductions: جمع کسور
    - invoice_surcharges: جمع عوامل افزاینده
    - invoice_tax_total: جمع مالیات
    - invoice_functional_total_price: مبلغ ناخالص به ارز عملیاتی
    - invoice_functional_net_price: مبلغ خالص به ارز عملیاتی
    - invoice_functional_deductions: جمع تخفیف به ارز عملیاتی
    - invoice_functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
    - invoice_functional_tax_total: جمع مالیات به ارز عملیاتی
- **Relations**: None

## crm_quotecustomer
- **Title**: مشتری مرتبط با پیش فاکتور
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - company_title: شرکت
    - name: نام مشتری
    - code: کد مشتری
    - sales_customer_code: کد مشتری فروش
- **Relations**: None

## crm_customerrequest
- **Title**: درخواست مشتری
- **Context**: crm
- **Parameters**: 
  - crm_customerrequest_p1: از تاریخ ایجاد (Date)
  - crm_customerrequest_p2: تا تاریخ ایجاد (Date)
  - crm_customerrequest_p3: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - company_display: نام شرکت
    - submission_date: تاریخ درخواست
    - code: شماره درخواست
    - title: عنوان درخواست
    - description: شرح درخواست
    - parent_display: عطف به درخواست پیشین
    - origin: مسیر ورودی درخواست
    - priority: اولویت
    - created_by_display: کاربر ایجاد کننده
    - owner_display: کاربر پیگیری کننده
    - stage: وضعیت
    - solution: راهکار ارائه شده
    - product_display: نام محصول
    - branch_display: شعبه
- **Relations**:
  - crm_customerrequestcustomer: مشتری مرتبط با درخواست مشتری (foreign key: customer_id to crm_customerrequestcustomer.id)

## crm_contactPhone
- **Title**: شماره تماس‌های فرد
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - number_c: تلفن
    - code: پیش‌شماره
    - extension: شماره داخلی
    - is_primary: اصلی
- **Relations**: None

## crm_opportunitylead
- **Title**: سرنخ مرتبط با فرصت
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - firstname: نام سرنخ
    - lastname: نام خانوادگی
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
    - company_title: شرکت
- **Relations**: None

## crm_campaign
- **Title**: کمپین
- **Context**: crm
- **Parameters**: 
  - crm_campaign_p1: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - name: نام
    - cmp_title: شرکت
    - start_date: تاریخ شروع
    - end_date: تاریخ پایان
    - campaign_parent_display: کمپین مادر
    - description: توضیحات
    - status: وضعیت
    - stage: مرحله
    - campaign_owner_display: کاربر پیگیری کننده
    - campaign_creator_display: کاربر ایجاد کننده
    - campaign_editor_display: آخرین کاربر ویرایش کننده
    - created_at: تاریخ ایجاد
    - updated_at: آخرین تاریخ ویرایش
    - budget: بودجه
    - expected_income: درآمد مورد انتظار
    - actual_cost: هزینه واقعی
- **Relations**:
  - crm_campaignCustomer: مشتری مرتبط با کمپین (foreign key: id to crm_campaignCustomer.campaign_id)
  - crm_campaignContact: فرد مرتبط با کمپین (foreign key: id to crm_campaignContact.campaign_id)
  - crm_campaignLead: سرنخ مرتبط با کمپین (foreign key: id to crm_campaignLead.campaign_id)
  - crm_campaignOpportunity: فرصت مرتبط با کمپین (foreign key: id to crm_campaignOpportunity.campaign_id)

## crm_customerAddress
- **Title**: آدرس‌های مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - address_c: آدرس
    - customer_division_display: منطقه جغرافیایی
    - country: کشور
    - province: استان
    - city: شهر
    - postal_code: کد پستی
    - tel: تلفن
    - fax: دورنگار
    - is_primary: اصلی
- **Relations**: None

## crm_leadPhone
- **Title**: شماره تماس‌های سرنخ
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - number_c: تلفن
    - code: پیش‌شماره
    - extension: شماره داخلی
    - is_primary: اصلی
- **Relations**: None

## crm_leadEmail
- **Title**: ایمیل‌های سرنخ
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - email: ایمیل
    - is_primary: اصلی
- **Relations**: None

## crm_customerEmail
- **Title**: ایمیل‌های مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - email: ایمیل
    - is_primary: اصلی
- **Relations**: None

## crm_contact
- **Title**: افراد
- **Context**: crm
- **Parameters**: 
  - crm_contact_p1: شرکت (Int64Array - multiselect from companies dataview)
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - salutation: پیشوند
    - first_name: نام فرد
    - last_name: نام خانوادگی فرد
    - title: سمت
    - primary_customer_display: مشتری اصلی
    - birthdate: تاریخ تولد
    - contact_owner_display: کاربر پیگیری کننده
    - contact_creator_display: کاربر ایجاد کننده
    - created_at: تاریخ ایجاد
    - contact_editor_display: آخرین کاربر ویرایش کننده
    - updated_at: آخرین تاریخ ویرایش
- **Relations**:
  - crm_contactPhone: شماره تماس‌های فرد (foreign key: id to crm_contactPhone.contact_id)
  - crm_contactEmail: ایمیل‌های فرد (foreign key: id to crm_contactEmail.contact_id)
  - crm_contactAddress: آدرس‌های فرد (foreign key: id to crm_contactAddress.contact_id)
  - crm_contactCustomer: مشتری مرتبط با فرد (foreign key: id to crm_contactCustomer.contact_id)
  - crm_contactCampaign: کمپین مرتبط با فرد (foreign key: id to crm_contactCampaign.contact_id)

## crm_contactAddress
- **Title**: آدرس‌های فرد
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - title: عنوان
    - address_c: آدرس
    - contact_division_display: منطقه جغرافیایی
    - country: کشور
    - province: استان
    - city: شهر
    - postal_code: کد پستی
    - tel: تلفن
    - fax: دورنگار
    - is_primary: اصلی
- **Relations**: None

## crm_campaignContact
- **Title**: فرد مرتبط با کمپین
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - first_name: نام فرد
    - last_name: نام خانوادگی فرد
    - title: سمت
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
- **Relations**: None

## crm_customerOpportunity
- **Title**: فرصت مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - name: نام فرصت
    - close_date: تاریخ بستن فرصت
    - pipeline: روند فروش
    - stage: مرحله فروش
    - price: مبلغ
    - expected_price: مبلغ مورد انتظار
    - success_probability: احتمال موفقیت
- **Relations**: None

## crm_customerLead
- **Title**: سرنخ مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - firstname: نام سرنخ
    - lastname: نام خانوادگی سرنخ
    - primary_phone: شماره تماس اصلی
    - primary_email: ایمیل اصلی
    - primary_address: آدرس اصلی
- **Relations**: None

## crm_contactCampaign
- **Title**: کمپین مرتبط با فرد
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - cmp_title: شرکت
    - name: نام
    - start_date: تاریخ شروع
    - end_date: تاریخ پایان
    - campaign_parent_display: کمپین مادر
    - description: توضیحات
    - stage: مرحله
    - campaign_owner_display: کاربر پیگیری کننده
    - budget: بودجه
    - expected_income: درآمد مورد انتظار
    - actual_cost: هزینه واقعی
- **Relations**: None

## crm_opportunityitem
- **Title**: قلم فرصت
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - product_title: نام محصول
    - unit_title: واحد سنجش
    - amount: مقدار
    - fee: فی
    - price: مبلغ ناخالص
    - deduction_price: کسورات
    - price_after_deduction: مبلغ بعد از کسر کسورات
    - addition_price: اضافات
    - net_price: مبلغ خالص
    - company_title: شرکت
- **Relations**: None

## crm_customerQuote
- **Title**: پیش فاکتورهای مرتبط با مشتری
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - company_title: شرکت
    - title: عنوان پیش فاکتور
    - date: تاریخ
    - number: شماره پیش فاکتور
    - total_price: مبلغ ناخالص
    - net_price: مبلغ خالص
    - deductions: جمع کسور
    - surcharges: جمع عوامل افزاینده
    - sales_area_title: حوزه فروش
    - sales_office_title: دفتر فروش
    - currency_title: ارز
    - owner_name: کاربر پیگیری کننده
    - created_at: تاریخ ایجاد
- **Relations**: None

## crm_opportunitycustomer
- **Title**: مشتری مرتبط با فرصت
- **Context**: crm
- **Parameters**: None
- **Attributes**:
  - **String Type**:
    - customer_title: نام مشتری
    - code: کد مشتری
    - company_title: شرکت
- **Relations**: None

"""