CRM_BO = """

crm_campaignLead:
  title: "سرنخ مرتبط با کمپین"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      firstname: "نام سرنخ"
      lastname: "نام خانوادگی سرنخ"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
  relations: null


crm_leadOpportunity:
  title: "فرصت مرتبط با سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام فرصت"
      close_date: "تاریخ بستن فرصت"
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
  relations: null


crm_customer:
  title: "مشتری"
  context: "crm"
  parameters:
    crm_customer_p1:
      description: "از تاریخ ایجاد"
      type: "Date"
    crm_customer_p2:
      description: "تا تاریخ ایجاد"
      type: "Date"
    crm_customer_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      cmp_title: "شرکت"
      fullname: "نام کامل مشتری"
      customer_type: "نوع طرف تجاری"
      rate: "میزان جذابیت"
      national_id: "کد/شناسه ملی"
      website: "وب سایت"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
      industry: "صنعت"
      subindustry: "زیرصنعت"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری در زیرسیستم فروش"
      registration_number: "شماره ثبت"
      description: "توضیحات"
      tax_group_display: "گروه مالیاتی"
      customer_owner_display: "کاربر پیگیری کننده"
      customer_creator_display: "کاربر ایجاد کننده"
      created_at: "تاریخ ایجاد"
      customer_editor_display: "آخرین کاربر ویرایش کننده"
      updated_at: "آخرین تاریخ ویرایش"
  relations:
    - name: "crm_customerPhone"
      title: "شماره تماس‌های مشتری"
      foreign_key: "id"
      references: "crm_customerPhone.customer_id"
    - name: "crm_customerEmail"
      title: "ایمیل‌های مشتری"
      foreign_key: "id"
      references: "crm_customerEmail.customer_id"
    - name: "crm_customerAddress"
      title: "آدرس‌های مشتری"
      foreign_key: "id"
      references: "crm_customerAddress.customer_id"
    - name: "crm_customerOpportunity"
      title: "فرصت مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerOpportunity.customer_id"
    - name: "crm_customerContact"
      title: "فرد مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerContact.customer_id"
    - name: "crm_customerLead"
      title: "سرنخ مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerLead.customer_id"
    - name: "crm_customerCampaign"
      title: "کمپین مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerCampaign.customer_id"
    - name: "crm_customerGrouping"
      title: "گروه‌های عضو مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerGrouping.customer_id"
    - name: "crm_customerQuote"
      title: "پیش فاکتورهای مرتبط با مشتری"
      foreign_key: "id"
      references: "crm_customerQuote.customer_id"


crm_quoteitem:
  title: "قلم پیش فاکتور"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      unit_title: "واحد سنجش"
      store_title: "انبار"
      amount: "مقدار"
      company_title: "شرکت"
      fee: "فی"
      description: "توضیحات"
      deduction_price: "جمع تخفیف"
      surcharges: "جمع عوامل افزاینده"
      tax_price: "مالیات بر ارزش افزوده"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      functional_deduction_price: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_price: "جمع مالیات بر ارزش افزوده به ارز عملیاتی"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
  relations: null


crm_campaignCustomer:
  title: "مشتری مرتبط با کمپین"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      fullname: "نام کامل مشتری"
      customer_type: "نوع طرف تجاری"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری در زیرسیستم فروش"
  relations: null


crm_lead:
  title: "سرنخ"
  context: "crm"
  parameters:
    crm_lead_p1:
      description: "از تاریخ ایجاد"
      type: "Date"
    crm_lead_p2:
      description: "تا تاریخ ایجاد"
      type: "Date"
    crm_lead_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      cmp_title: "شرکت"
      salutation: "پیشوند"
      firstname: "نام سرنخ"
      lastname: "نام خانوادگی سرنخ"
      customer_name: "نام مشتری"
      lead_owner_display: "کاربر پیگیری کننده"
      lead_state: "مرحله"
      lead_type: "نوع طرف تجاری"
      national_code: "شناسه/کد ملی مشتری"
      source: "منبع"
      source_note: "توضیحات منبع"
      rate: "میزان جذابیت"
      primary_campaign: "کمپین اصلی"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
      industry: "صنعت"
      subindustry: "زیرصنعت"
      website: "وب سایت"
      birthdate: "تاریخ تولد"
      lead_product_grouping_display: "دسته محصول مورد نیاز"
      lost_reason: "دلیل از دست رفتن"
      description: "توضیحات"
      convert_date: "تاریخ تبدیل"
      lead_creator_display: "کاربر ایجاد کننده"
      created_at: "تاریخ ایجاد"
      lead_editor_display: "آخرین کاربر ویرایش کننده"
      updated_at: "آخرین تاریخ ویرایش"
  relations:
    - name: "crm_leadPhone"
      title: "شماره تماس‌های سرنخ"
      foreign_key: "id"
      references: "crm_leadPhone.lead_id"
    - name: "crm_leadEmail"
      title: "ایمیل‌های سرنخ"
      foreign_key: "id"
      references: "crm_leadEmail.lead_id"
    - name: "crm_leadAddress"
      title: "آدرس‌های سرنخ"
      foreign_key: "id"
      references: "crm_leadAddress.lead_id"
    - name: "crm_leadCampaign"
      title: "کمپین‌های سرنخ"
      foreign_key: "id"
      references: "crm_leadCampaign.lead_id"
    - name: "crm_leadCustomer"
      title: "مشتری مرتبط با سرنخ"
      foreign_key: "customer_id"
      references: "crm_leadCustomer.id"
    - name: "crm_leadContact"
      title: "فرد مرتبط با سرنخ"
      foreign_key: "contact_id"
      references: "crm_leadContact.id"
    - name: "crm_leadOpportunity"
      title: "فرصت مرتبط با سرنخ"
      foreign_key: "opportunity_id"
      references: "crm_leadOpportunity.id"


crm_contactCustomer:
  title: "مشتری مرتبط با فرد"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      fullname: "نام کامل مشتری"
      customer_type: "نوع طرف تجاری"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری در زیرسیستم فروش"
  relations: null


crm_leadAddress:
  title: "آدرس‌های سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      address_c: "آدرس"
      lead_division_display: "منطقه جغرافیایی"
      country: "کشور"
      province: "استان"
      city: "شهر"
      postal_code: "کد پستی"
      tel: "تلفن"
      fax: "دورنگار"
      is_primary: "اصلی"
  relations: null


crm_leadCustomer:
  title: "مشتری مرتبط با سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      fullname: "نام کامل مشتری"
      customer_type: "نوع طرف تجاری"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری در زیرسیستم فروش"
  relations: null


crm_quoteopportunity:
  title: "فرصت مرتبط با پیش فاکتور"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      company_title: "شرکت"
      opportunity_title: "نام فرصت"
      opportunity_close_date: "تاریخ بستن"
      opportunity_pipeline: "روند فروش"
      opportunity_stage: "مرحله"
      opportunity_price: "مبلغ"
      opportunity_expected_price: "مبلغ مورد انتظار"
      opportunity_success_probability: "احتمال موفقیت"
  relations: null


crm_customerPhone:
  title: "شماره تماس‌های مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      number_c: "تلفن"
      code: "پیش‌شماره"
      extension: "شماره داخلی"
      is_primary: "اصلی"
  relations: null


crm_customerContact:
  title: "فرد مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      first_name: "نام فرد"
      last_name: "نام خانوادگی فرد"
      title: "سمت"
  relations: null


crm_customerCampaign:
  title: "کمپین مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام"
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
  relations: null


crm_customerGrouping:
  title: "گروه‌های عضو مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      group_title: "گروه"
      grouping_title: "گروه‌بندی"
  relations: null


crm_opportunityquote:
  title: "پیش فاکتور مرتبط با فرصت"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      title: "نام پیش فاکتور"
      date: "تاریخ پیش فاکتور"
      number: "شماره پیش فاکتور"
      total_price: "مبلغ ناخالص"
      deductions: "کسورات"
      additions: "اضافات"
      net_price: "مبلغ خالص"
      sales_area_title: "حوزه فروش"
      sales_office_title: "دفتر فروش"
      currency_title: "ارز"
      owner_display_name: "کاربر پیگیری کننده"
      created_at: "تاریخ ایجاد"
      company_title: "شرکت"
  relations: null


crm_opportunity:
  title: "فرصت"
  context: "crm"
  parameters:
    crm_opportunity_p1:
      description: "از تاریخ بستن فرصت"
      type: "Date"
    crm_opportunity_p2:
      description: "تا تاریخ بستن فرصت"
      type: "Date"
    crm_opportunity_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      name: "نام فرصت"
      customer_title: "نام مشتری"
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      success_probability: "احتمال موفقیت"
      close_date: "تاریخ بستن فرصت"
      price: "مبلغ"
      currency_title: "ارز"
      expected_price: "مبلغ مورد انتظار"
      created_by: "کاربر ایجاد کننده"
      user_display_name: "کاربر پیگیری کننده"
      updated_by: "آخرین کاربر ویرایش کننده"
      campaign_name: "کمپین"
      description: "توضیحات"
      company_title: "شرکت"
  relations:
    - name: "crm_opportunityitem"
      title: "قلم فرصت"
      foreign_key: "id"
      references: "crm_opportunityitem.opportunity_id"
    - name: "crm_opportunitycustomer"
      title: "مشتری"
      foreign_key: "customer_id"
      references: "crm_opportunitycustomer.id"
    - name: "crm_opportunitylead"
      title: "سرنخ"
      foreign_key: "id"
      references: "crm_opportunitylead.opportunity_id"
    - name: "crm_opportunityquote"
      title: "پیش فاکتور"
      foreign_key: "id"
      references: "crm_opportunityquote.related_opportunity_id"


crm_quote:
  title: "پیش فاکتور"
  context: "crm"
  parameters:
    crm_quote_p1:
      description: "از تاریخ"
      type: "Date"
    crm_quote_p2:
      description: "تا تاریخ"
      type: "Date"
    crm_quote_p3:
      description: "شرکت پیش فاکتور"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      company_title: "شرکت"
      title: "عنوان پیش فاکتور"
      fiscal_year_title: "سال مالی"
      number: "شماره پیش فاکتور"
      date: "تاریخ"
      description: "توضیحات"
      customer_name: "مشتری"
      sales_area_title: "حوزه فروش"
      branch_title: "شعبه"
      sales_office_title: "دفتر فروش"
      settlement_method_title: "روش تسویه"
      related_opportunity_title: "نام فرصت"
      currency_title: "ارز"
      currency_rate_type_title: "نوع نرخ ارز"
      functional_currency_rate: "نرخ ارز عملیاتی"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deductions: "جمع کسور"
      surcharges: "جمع عوامل افزاینده"
      tax_price: "جمع مالیات"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
      functional_deductions: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_price: "جمع مالیات به ارز عملیاتی"
      owner_name: "کاربر پیگیری کننده"
      creator_name: "کاربر ایجاد کننده"
      updater_name: "کاربر ویرایش کننده"
      created_at: "تاریخ ایجاد"
      updated_at: "آخرین تاریخ تغییر"
  relations:
    - name: "crm_quoteitem"
      title: "قلم پیش فاکتور"
      foreign_key: "id"
      references: "crm_quoteitem.quote_id"
    - name: "crm_quoteinvoice"
      title: "فاکتور مرتبط با پیش فاکتور"
      foreign_key: "id"
      references: "crm_quoteinvoice.quote_id"
    - name: "crm_quotecustomer"
      title: "مشتری مرتبط با پیش فاکتور"
      foreign_key: "customer_id"
      references: "crm_quotecustomer.id"
    - name: "crm_quoteopportunity"
      title: "فرصت مرتبط با پیش فاکتور"
      foreign_key: "id"
      references: "crm_quoteopportunity.quote_id"


crm_quoteinvoice:
  title: "فاکتور مرتبط با پیش فاکتور"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      invoice_company_title: "شرکت"
      invoice_fy_title: "سال مالی"
      invoice_number: "شماره فاکتور"
      invoice_date: "تاریخ"
      invoice_description: "توضیحات"
      invoice_customer_code: "کد مشتری"
      invoice_customer_fullname: "نام مشتری"
      sa2: "حوزه فروش"
      invoice_so_title: "دفتر فروش"
      invoice_sm_title: "روش تسویه"
      invoice_cur_title: "ارز"
      invoice_functional_currency_rate: "نرخ ارز عملیاتی"
      invoice_total_price: "مبلغ ناخالص"
      invoice_net_price: "مبلغ خالص"
      invoice_deductions: "جمع کسور"
      invoice_surcharges: "جمع عوامل افزاینده"
      invoice_tax_total: "جمع مالیات"
      invoice_functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      invoice_functional_net_price: "مبلغ خالص به ارز عملیاتی"
      invoice_functional_deductions: "جمع تخفیف به ارز عملیاتی"
      invoice_functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      invoice_functional_tax_total: "جمع مالیات به ارز عملیاتی"
  relations: null


crm_quotecustomer:
  title: "مشتری مرتبط با پیش فاکتور"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      company_title: "شرکت"
      name: "نام مشتری"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری فروش"
  relations: null


crm_customerrequest:
  title: "درخواست مشتری"
  context: "crm"
  parameters:
    crm_customerrequest_p1:
      description: "از تاریخ ایجاد"
      type: "Date"
    crm_customerrequest_p2:
      description: "تا تاریخ ایجاد"
      type: "Date"
    crm_customerrequest_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      company_display: "نام شرکت"
      submission_date: "تاریخ درخواست"
      code: "شماره درخواست"
      title: "عنوان درخواست"
      description: "شرح درخواست"
      parent_display: "عطف به درخواست پیشین"
      origin: "مسیر ورودی درخواست"
      priority: "اولویت"
      created_by_display: "کاربر ایجاد کننده"
      owner_display: "کاربر پیگیری کننده"
      stage: "وضعیت"
      solution: "راهکار ارائه شده"
      product_display: "نام محصول"
      branch_display: "شعبه"
  relations:
    - name: "crm_customerrequestcustomer"
      title: "مشتری مرتبط با درخواست مشتری"
      foreign_key: "customer_id"
      references: "crm_customerrequestcustomer.id"


crm_contactPhone:
  title: "شماره تماس‌های فرد"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      number_c: "تلفن"
      code: "پیش‌شماره"
      extension: "شماره داخلی"
      is_primary: "اصلی"
  relations: null


crm_opportunitylead:
  title: "سرنخ مرتبط با فرصت"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      firstname: "نام سرنخ"
      lastname: "نام خانوادگی"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
      company_title: "شرکت"
  relations: null


crm_campaign:
  title: "کمپین"
  context: "crm"
  parameters:
    crm_campaign_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      name: "نام"
      cmp_title: "شرکت"
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      status: "وضعیت"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      campaign_creator_display: "کاربر ایجاد کننده"
      campaign_editor_display: "آخرین کاربر ویرایش کننده"
      created_at: "تاریخ ایجاد"
      updated_at: "آخرین تاریخ ویرایش"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
  relations:
    - name: "crm_campaignCustomer"
      title: "مشتری مرتبط با کمپین"
      foreign_key: "id"
      references: "crm_campaignCustomer.campaign_id"
    - name: "crm_campaignContact"
      title: "فرد مرتبط با کمپین"
      foreign_key: "id"
      references: "crm_campaignContact.campaign_id"
    - name: "crm_campaignLead"
      title: "سرنخ مرتبط با کمپین"
      foreign_key: "id"
      references: "crm_campaignLead.campaign_id"
    - name: "crm_campaignOpportunity"
      title: "فرصت مرتبط با کمپین"
      foreign_key: "id"
      references: "crm_campaignOpportunity.campaign_id"


crm_customerAddress:
  title: "آدرس‌های مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      address_c: "آدرس"
      customer_division_display: "منطقه جغرافیایی"
      country: "کشور"
      province: "استان"
      city: "شهر"
      postal_code: "کد پستی"
      tel: "تلفن"
      fax: "دورنگار"
      is_primary: "اصلی"
  relations: null


crm_leadPhone:
  title: "شماره تماس‌های سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      number_c: "تلفن"
      code: "پیش‌شماره"
      extension: "شماره داخلی"
      is_primary: "اصلی"
  relations: null


crm_leadEmail:
  title: "ایمیل‌های سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      email: "ایمیل"
      is_primary: "اصلی"
  relations: null


crm_customerEmail:
  title: "ایمیل‌های مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      email: "ایمیل"
      is_primary: "اصلی"
  relations: null


crm_contact:
  title: "افراد"
  context: "crm"
  parameters:
    crm_contact_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      cmp_title: "شرکت"
      salutation: "پیشوند"
      first_name: "نام فرد"
      last_name: "نام خانوادگی فرد"
      title: "سمت"
      primary_customer_display: "مشتری اصلی"
      birthdate: "تاریخ تولد"
      contact_owner_display: "کاربر پیگیری کننده"
      contact_creator_display: "کاربر ایجاد کننده"
      created_at: "تاریخ ایجاد"
      contact_editor_display: "آخرین کاربر ویرایش کننده"
      updated_at: "آخرین تاریخ ویرایش"
  relations:
    - name: "crm_contactPhone"
      title: "شماره تماس‌های فرد"
      foreign_key: "id"
      references: "crm_contactPhone.contact_id"
    - name: "crm_contactEmail"
      title: "ایمیل‌های فرد"
      foreign_key: "id"
      references: "crm_contactEmail.contact_id"
    - name: "crm_contactAddress"
      title: "آدرس‌های فرد"
      foreign_key: "id"
      references: "crm_contactAddress.contact_id"
    - name: "crm_contactCustomer"
      title: "مشتری مرتبط با فرد"
      foreign_key: "id"
      references: "crm_contactCustomer.contact_id"
    - name: "crm_contactCampaign"
      title: "کمپین مرتبط با فرد"
      foreign_key: "id"
      references: "crm_contactCampaign.contact_id"


crm_contactAddress:
  title: "آدرس‌های فرد"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      address_c: "آدرس"
      contact_division_display: "منطقه جغرافیایی"
      country: "کشور"
      province: "استان"
      city: "شهر"
      postal_code: "کد پستی"
      tel: "تلفن"
      fax: "دورنگار"
      is_primary: "اصلی"
  relations: null


crm_campaignContact:
  title: "فرد مرتبط با کمپین"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      first_name: "نام فرد"
      last_name: "نام خانوادگی فرد"
      title: "سمت"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
  relations: null


crm_customerOpportunity:
  title: "فرصت مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام فرصت"
      close_date: "تاریخ بستن فرصت"
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
  relations: null


crm_customerLead:
  title: "سرنخ مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      firstname: "نام سرنخ"
      lastname: "نام خانوادگی سرنخ"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
  relations: null


crm_contactCampaign:
  title: "کمپین مرتبط با فرد"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام"
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
  relations: null


crm_opportunityitem:
  title: "قلم فرصت"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      product_title: "نام محصول"
      unit_title: "واحد سنجش"
      amount: "مقدار"
      fee: "فی"
      price: "مبلغ ناخالص"
      deduction_price: "کسورات"
      price_after_deduction: "مبلغ بعد از کسر کسورات"
      addition_price: "اضافات"
      net_price: "مبلغ خالص"
      company_title: "شرکت"
  relations: null


crm_customerQuote:
  title: "پیش فاکتورهای مرتبط با مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      company_title: "شرکت"
      title: "عنوان پیش فاکتور"
      date: "تاریخ"
      number: "شماره پیش فاکتور"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deductions: "جمع کسور"
      surcharges: "جمع عوامل افزاینده"
      sales_area_title: "حوزه فروش"
      sales_office_title: "دفتر فروش"
      currency_title: "ارز"
      owner_name: "کاربر پیگیری کننده"
      created_at: "تاریخ ایجاد"
  relations: null


crm_opportunitycustomer:
  title: "مشتری مرتبط با فرصت"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      customer_title: "نام مشتری"
      code: "کد مشتری"
      company_title: "شرکت"
  relations: null


crm_contactEmail:
  title: "ایمیل‌های فرد"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      title: "عنوان"
      email: "ایمیل"
      is_primary: "اصلی"
  relations: null


crm_campaignOpportunity:
  title: "فرصت مرتبط با کمپین"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام فرصت"
      close_date: "تاریخ بستن فرصت"
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
  relations: null


crm_leadCampaign:
  title: "کمپین‌های سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام"
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
  relations: null


crm_leadContact:
  title: "فرد مرتبط با سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      first_name: "نام فرد"
      last_name: "نام خانوادگی فرد"
      title: "سمت"
      primary_phone: "شماره تماس اصلی"
      primary_email: "ایمیل اصلی"
      primary_address: "آدرس اصلی"
  relations: null


crm_customerrequestcustomer:
  title: "مشتری مرتبط با درخواست مشتری"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      company_title: "شرکت"
      fullname: "نام کامل مشتری"
      customer_type: "نوع طرف تجاری"
      code: "کد مشتری"
      sales_customer_code: "کد مشتری در زیرسیستم فروش"
  relations: null
"""

TREASURY_BO = """
treasury_cheque
  title: "چک پرداختی"
  context: "treasury"
  parameters: 
    treasury_cheque_p1:
      description: "شناسه قلم"
      type: "Int64Array"
  attributes:
    string_type:
      id: "قلم سند پرداخت"
      due_date: "تاریخ سررسید"
      full_name: "نام دریافت کننده"
      national_id: "کد/شناسه ملی"
    decimal_type:
      amount: "مبلغ"
  relations: null
"""