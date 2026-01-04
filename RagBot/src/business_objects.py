LOGISTICS_MODIFIED = """
logistics_partaltunit:
  title: "واحد فرعی کالا"
  context: "logistics"
  parameters: null
  attributes:
    string_type:
      title: "عنوان واحد فرعی کالا"
      major_unit_title: "واحد سنجش اصلی"
    float64_type:
      coeff: "ضریب"
  relations: null


logistics_storagetype:
  title: "نوع انبار"
  context: "logistics"
  parameters:
    logistics_storagetype_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد نوع انبار"
      title: "عنوان نوع انبار"
      company_title: "شرکت"
  relations: null


logistics_units:
  title: "واحد سنجش (Unit of Measure)"
  context: "logistics"
  parameters: null
  attributes:
    string_type:
      title: "عنوان واحد سنجش"
    int64_type:
      dimension: "بعد"
  relations: null


logistics_store:
  title: "انبار"
  context: "logistics"
  parameters:
    logistics_store_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد انبار"
      title: "عنوان انبار"
      storage_type_title: "عنوان نوع انبار"
      state: "استان"
      company_title: "شرکت"
  relations:
    - name: "logistics_plants"
      title: "مرکز نگهداری"
      foreign_key: "plant_id"
      references: "logistics_plants.id"


logistics_partaccountcategory:
  title: "طبقه حساب کالا"
  context: "logistics"
  parameters:
    logistics_partaccountcategory_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد طبقه حساب کالا"
      title: "عنوان طبقه حساب کالا"
      pricing_method: "روش قیمت گذاری"
      company_title: "شرکت"
  relations: null


logistics_plants:
  title: "مرکز نگهداری"
  context: "logistics"
  parameters:
    logistics_plants_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد مرکز نگهداری"
      title: "عنوان مرکز نگهداری"
      branch_title: "عنوان شعبه"
      state: "استان"
      company_title: "شرکت"
  relations: null


logistics_invvoucher:
  title: "سند انبار"
  context: "logistics"
  parameters:
    logistics_invvoucher_p1:
      description: "از تاریخ سند انبار"
      type: "Date"
    logistics_invvoucher_p2:
      description: "تا تاریخ سند انبار"
      type: "Date"
    logistics_invvoucher_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date: "تاریخ سند"
      production_date: "تاریخ تولید"
      waybill_date: "تاریخ بارنامه"
    string_type:
      number: "شماره سند"
      description: "شرح سربرگ"
      sl_title: "معین"
      state: "وضعیت"
      fy_title: "دوره مالی"
      extra_field1: "فیلد اضافه 1"
      extra_field2: "فیلد اضافه 2"
      extra_field3: "فیلد اضافه 3"
      extra_field4: "فیلد اضافه 4"
      extra_field5: "فیلد اضافه 5"
      supplier_title: "تامین کننده"
      contractor_title: "پیمانکار"
      cost_center_title: "مرکز هزینه"
      project_title: "پروژه"
      customer_title: "مشتری"
      carrier_title: "موسسه حمل"
      consignment_party_title: "طرف حساب امانی"
      employee_title: "کارمند"
      sales_person_title: "کارمند فروش"
      purchase_order_no: "شماره سفارش خرید"
      purchase_invoice_no: "شماره فاکتور خرید"
      deliver_to: "تحویل گیرنده"
      cottage_no: "شماره کوتاژ"
      customs_green_sheet: "شماره برگ سبز"
      asn_no: "ASN NO"
      sales_order_no: "شماره سفارش فروش"
      sales_invoice_no: "شماره فاکتور خرید"
      sale_organization: "مرکز فروش"
      shopping_store: "فروشگاه"
      delivery_person: "تحویل دهنده"
      weighbridge_no: "شماره برگه باسکول"
      production_order_no: "شماره دستور تولید"
      production_plan_no: "شماره سفارش تولید"
      production_operation_no: "شماره عملیات تولید"
      production_shift: "شیفت تولید"
      qc_inspection_no: "شماره بازرسی کیفیت"
      qc_check_list_no: "شماره چک لیست"
      qc_lab_no: "شماره آزمایشگاه"
      conditional_approval: "تایید ارفاقی"
      inspection_result: "نتیجه بازرسی"
      coa_no: "شماره COA"
      transporter_name: "نام راننده"
      vehicle_no: "نام خودرو"
      license_plate_no: "شماره پلاک"
      waybill_no: "شماره بارنامه"
      transporter_phone_no: "تلفن راننده"
      company_title: "شرکت"
  relations:
    - name: "logistics_voucherspecification"
      title: "الگوی سند انبار"
      foreign_key: "voucher_specification_id"
      references: "logistics_voucherspecification.id"
    - name: "logistics_store"
      title: "انبار"
      foreign_key: "store_id"
      references: "logistics_store.id"
    - name: "logistics_counterstore"
      title: "انبار مقابل"
      foreign_key: "counter_part_store_id"
      references: "logistics_store.id"


logistics_parts:
  title: "کالا"
  context: "logistics"
  parameters:
    logistics_parts_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد کالا"
      title: "عنوان کالا"
      major_unit_title: "واحد سنجش اصلی"
      secondary_unit_title: "واحد سنجش دوم"
      part_account_category_title: "طبقه حساب کالا"
      part_type: "نوع کالا"
      part_usage: "نوع کارکرد کالا"
      company_title: "شرکت"
  relations:
    - name: "logistics_partaltunit"
      title: "واحد فرعی کالا"
      foreign_key: "id"
      references: "logistics_partaltunit.part_id"
    - name: "logistics_partstoragetype"
      title: "نوع انبار کالا"
      foreign_key: "id"
      references: "logistics_partstoragetype.part_id"


logistics_voucherspecification:
  title: "الگوی سند انبار"
  context: "logistics"
  parameters:
    logistics_voucherspecification_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد الگو"
      title: "عنوان الگو"
      voucher_type: "نوع سند"
      direction: "جهت سند"
      purchase_type: "نوع خرید"
      type_of_effect: "نوع تاثیر بر موجودی"
      counter_part_type: "نوع طرف مقابل"
      company_title: "شرکت"
  relations: null


logistics_invvoucheritem:
  title: "قلم سند انبار"
  context: "logistics"
  parameters:
    logistics_invvoucheritem_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    decimal_type:
      quantity: "مقدار"
      major_quantity: "مقدار به واحد اصلی"
      second_unit_quantity: "مقدار به واحد دوم"
      remained_major_quantity: "مانده استفاده نشده به واحد اصلی"
      remained_second_unit_quantity: "مانده استفاده نشده به واحد دوم"
    string_type:
      row_number: "شماره ردیف"
      sl_title: "معین"
      extra_field1: "فیلد اضافه 1"
      extra_field2: "فیلد اضافه 2"
      extra_field3: "فیلد اضافه 3"
      extra_field4: "فیلد اضافه 4"
      extra_field5: "فیلد اضافه 5"
      supplier_title: "تامین کننده"
      contractor_title: "پیمانکار"
      cost_center_title: "مرکز هزینه"
      project_title: "پروژه"
      customer_title: "مشتری"
      carrier_title: "موسسه حمل"
      consignment_party_title: "طرف حساب امانی"
      employee_title: "کارمند"
      sales_person_title: "کارمند فروش"
      purchase_order_no: "شماره سفارش خرید"
      purchase_invoice_no: "شماره فاکتور خرید"
      deliver_to: "تحویل گیرنده"
      cottage_no: "شماره کوتاژ"
      customs_green_sheet: "شماره برگ سبز"
      asn_no: "ASN NO"
      sales_order_no: "شماره سفارش فروش"
      sales_invoice_no: "شماره فاکتور خرید"
      sale_organization: "مرکز فروش"
      shopping_store: "فروشگاه"
      delivery_person: "تحویل دهنده"
      weighbridge_no: "شماره برگه باسکول"
      production_order_no: "شماره دستور تولید"
      production_plan_no: "شماره سفارش تولید"
      production_operation_no: "شماره عملیات تولید"
      production_shift: "شیفت تولید"
      qc_inspection_no: "شماره بازرسی کیفیت"
      qc_check_list_no: "شماره چک لیست"
      qc_lab_no: "شماره آزمایشگاه"
      conditional_approval: "تایید ارفاقی"
      inspection_result: "نتیجه بازرسی"
      coa_no: "شماره COA"
      transporter_name: "نام راننده"
      vehicle_no: "نام خودرو"
      license_plate_no: "شماره پلاک"
      waybill_no: "شماره بارنامه"
      transporter_phone_no: "تلفن راننده"
      company_title: "شرکت"
    date_type:
      production_date: "تاریخ تولید"
      waybill_date: "تاریخ بارنامه"
  relations:
    - name: "logistics_invvoucher"
      title: "سند انبار"
      foreign_key: "inventory_voucher_id"
      references: "logistics_invvoucher.id"
    - name: "logistics_part"
      title: "کالا"
      foreign_key: "part_id"
      references: "logistics_parts.id"
    - name: "logistics_unit"
      title: "واحد سنجش"
      foreign_key: "unit_id"
      references: "logistics_units.id"


logistics_invitemprice:
  title: "قلم قیمت"
  context: "logistics"
  parameters:
    logistics_invitemprice_p1:
      description: "حوزه قیمت‌گذاری"
      type: "Int64"
      source: "dataview"
    logistics_invitemprice_p2:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date: "تاریخ"
    decimal_type:
      fee: "فی"
      price: "مبلغ"
      major_fee: "فی به واحد اصلی"
      major_price: "مبلغ به واحد اصلی"
    string_type:
      price_type: "نوع قیمت"
      currency_title: "عنوان ارز"
      acc_voucher_number: "شماره سند حسابداری"
      company_title: "شرکت"
  relations:
    - name: "logistics_invvoucheritem"
      title: "قلم سند انبار"
      foreign_key: "inventory_voucher_item_id"
      references: "logistics_invvoucheritem.id"


logistics_invstockpricing:
  title: "گردش مبلغی"
  context: "logistics"
  parameters:
    logistics_invstockpricing_p1:
      description: "از تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invstockpricing_p2:
      description: "تا تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invstockpricing_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    decimal_type:
      fee: "فی"
      price: "مبلغ"
      price_in_functional_currency: "مبلغ به ارز عملیاتی"
      total_fee: "فی نهایی"
      total_price: "مبلغ نهایی"
      major_fee: "فی به واحد اصلی"
      major_unit_quantity: "مقدار واحد اصلی"
      quantity: "مقدار ثبت سند"
      second_unit_quantity: "مقدار واحد دوم"
    string_type:
      company_title: "عنوان شرکت"
      branch_title: "عنوان شعبه"
      plant_code: "کد مرکز نگهداری"
      plant_title: "عنوان مرکز نگهداری"
      store_code: "کد انبار"
      store_title: "عنوان انبار"
      storage_type: "نوع انبار"
      pricing_area_title: "عنوان حوزه قیمت گذاری"
      part_code: "کد کالا"
      part_title: "عنوان کالا"
      part_type: "نوع کالا"
      part_usage: "نوع کارکرد کالا"
      part_account_category: "طبقه حساب کالا"
      major_unit: "واحد اصلی"
      second_unit: "واحد دوم"
      inv_voucher_unit: "واحد ثبت سند"
      inventory_voucher_specification_title: "عنوان الگوی سند"
      inventory_voucher_type: "نوع سند"
      type_of_effect: "نوع تاثیر بر موجودی"
      counter_part_title: "طرف مقابل"
      inv_voucher_state: "وضعیت سند انبار"
      currency: "ارز"
      functional_currency: "ارز عملیاتی"
      itemprice_vouchering_state: "وضعیت سند حسابداری"
      item_pricing_state: "وضعیت قیمت گذاری"
      price_type: "نوع قیمت"
      acc_voucher_number: "شماره سند حسابداری"
  relations:
    - name: "logistics_invitemprice"
      title: "قلم قیمت"
      foreign_key: "inventory_voucher_item_price_id"
      references: "logistics_invitemprice.id"
    - name: "logistics_invitempricefactor"
      title: "جزییات مبلغی"
      foreign_key: "inventory_voucher_item_price_id"
      references: "logistics_invitempricefactor.inventory_voucher_item_price_id"


logistics_partstoragetype:
  title: "نوع انبار کالا"
  context: "logistics"
  parameters: null
  attributes: null
  relations:
    - name: "logistics_storagetype"
      title: "نوع انبار"
      foreign_key: "storage_type_id"
      references: "logistics_storagetype.id"


logistics_invitempricefactor:
  title: "جزییات مبلغی"
  context: "logistics"
  parameters:
    logistics_invitempricefactor_p1:
      description: "از تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invitempricefactor_p2:
      description: "تا تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invitempricefactor_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date_c: "تاریخ سند"
    decimal_type:
      td_in_functional_currency: "مالیات و عوارض"
      discount_in_functional_currency: "تخفیف"
      tf_in_functional_currency: "کرایه حمل"
      fee: "فی"
      major_fee: "فی به واحد اصلی"
      price: "مبلغ"
      price_in_reporting_currency1: "مبلغ به ارز گزارشگری1"
      price_in_reporting_currency2: "مبلغ به ارز گزارشگری2"
    string_type:
      transfer_fee_title: "ارز کرایه حمل"
      reporting1_currency: "ارز گزارشگری 1"
      reporting2_currency: "ارز گزارشگری 2"
      voucher_number: "شماره سند حسابداری"
      inv_voucher_number: "شماره سند انبار"
      company_title: "شرکت"
  relations: null
"""


LOGISTICS_SALES_MODIFIED = """
logistics_partaltunit:
  title: "واحد فرعی کالا"
  context: "logistics"
  parameters: null
  attributes:
    string_type:
      title: "عنوان واحد فرعی کالا"
      major_unit_title: "واحد سنجش اصلی"
    float64_type:
      coeff: "ضریب"
  relations: null


logistics_storagetype:
  title: "نوع انبار"
  context: "logistics"
  parameters:
    logistics_storagetype_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد نوع انبار"
      title: "عنوان نوع انبار"
      company_title: "شرکت"
  relations: null


logistics_units:
  title: "واحد سنجش (Unit of Measure)"
  context: "logistics"
  parameters: null
  attributes:
    string_type:
      title: "عنوان واحد سنجش"
    int64_type:
      dimension: "بعد"
  relations: null


logistics_store:
  title: "انبار"
  context: "logistics"
  parameters:
    logistics_store_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد انبار"
      title: "عنوان انبار"
      storage_type_title: "عنوان نوع انبار"
      state: "استان"
      company_title: "شرکت"
  relations:
    - name: "logistics_plants"
      title: "مرکز نگهداری"
      foreign_key: "plant_id"
      references: "logistics_plants.id"


logistics_partaccountcategory:
  title: "طبقه حساب کالا"
  context: "logistics"
  parameters:
    logistics_partaccountcategory_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد طبقه حساب کالا"
      title: "عنوان طبقه حساب کالا"
      pricing_method: "روش قیمت گذاری"
      company_title: "شرکت"
  relations: null


logistics_plants:
  title: "مرکز نگهداری"
  context: "logistics"
  parameters:
    logistics_plants_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد مرکز نگهداری"
      title: "عنوان مرکز نگهداری"
      branch_title: "عنوان شعبه"
      state: "استان"
      company_title: "شرکت"
  relations: null


logistics_invvoucher:
  title: "سند انبار"
  context: "logistics"
  parameters:
    logistics_invvoucher_p1:
      description: "از تاریخ سند انبار"
      type: "Date"
    logistics_invvoucher_p2:
      description: "تا تاریخ سند انبار"
      type: "Date"
    logistics_invvoucher_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date: "تاریخ سند"
      production_date: "تاریخ تولید"
      waybill_date: "تاریخ بارنامه"
    string_type:
      number: "شماره سند"
      description: "شرح سربرگ"
      sl_title: "معین"
      state: "وضعیت"
      fy_title: "دوره مالی"
      extra_field1: "فیلد اضافه 1"
      extra_field2: "فیلد اضافه 2"
      extra_field3: "فیلد اضافه 3"
      extra_field4: "فیلد اضافه 4"
      extra_field5: "فیلد اضافه 5"
      supplier_title: "تامین کننده"
      contractor_title: "پیمانکار"
      cost_center_title: "مرکز هزینه"
      project_title: "پروژه"
      customer_title: "مشتری"
      carrier_title: "موسسه حمل"
      consignment_party_title: "طرف حساب امانی"
      employee_title: "کارمند"
      sales_person_title: "کارمند فروش"
      purchase_order_no: "شماره سفارش خرید"
      purchase_invoice_no: "شماره فاکتور خرید"
      deliver_to: "تحویل گیرنده"
      cottage_no: "شماره کوتاژ"
      customs_green_sheet: "شماره برگ سبز"
      asn_no: "ASN NO"
      sales_order_no: "شماره سفارش فروش"
      sales_invoice_no: "شماره فاکتور خرید"
      sale_organization: "مرکز فروش"
      shopping_store: "فروشگاه"
      delivery_person: "تحویل دهنده"
      weighbridge_no: "شماره برگه باسکول"
      production_order_no: "شماره دستور تولید"
      production_plan_no: "شماره سفارش تولید"
      production_operation_no: "شماره عملیات تولید"
      production_shift: "شیفت تولید"
      qc_inspection_no: "شماره بازرسی کیفیت"
      qc_check_list_no: "شماره چک لیست"
      qc_lab_no: "شماره آزمایشگاه"
      conditional_approval: "تایید ارفاقی"
      inspection_result: "نتیجه بازرسی"
      coa_no: "شماره COA"
      transporter_name: "نام راننده"
      vehicle_no: "نام خودرو"
      license_plate_no: "شماره پلاک"
      waybill_no: "شماره بارنامه"
      transporter_phone_no: "تلفن راننده"
      company_title: "شرکت"
  relations:
    - name: "logistics_voucherspecification"
      title: "الگوی سند انبار"
      foreign_key: "voucher_specification_id"
      references: "logistics_voucherspecification.id"
    - name: "logistics_store"
      title: "انبار"
      foreign_key: "store_id"
      references: "logistics_store.id"
    - name: "logistics_counterstore"
      title: "انبار مقابل"
      foreign_key: "counter_part_store_id"
      references: "logistics_store.id"


logistics_parts:
  title: "کالا"
  context: "logistics"
  parameters:
    logistics_parts_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد کالا"
      title: "عنوان کالا"
      major_unit_title: "واحد سنجش اصلی"
      secondary_unit_title: "واحد سنجش دوم"
      part_account_category_title: "طبقه حساب کالا"
      part_type: "نوع کالا"
      part_usage: "نوع کارکرد کالا"
      company_title: "شرکت"
  relations:
    - name: "logistics_partaltunit"
      title: "واحد فرعی کالا"
      foreign_key: "id"
      references: "logistics_partaltunit.part_id"
    - name: "logistics_partstoragetype"
      title: "نوع انبار کالا"
      foreign_key: "id"
      references: "logistics_partstoragetype.part_id"


logistics_voucherspecification:
  title: "الگوی سند انبار"
  context: "logistics"
  parameters:
    logistics_voucherspecification_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      code: "کد الگو"
      title: "عنوان الگو"
      voucher_type: "نوع سند"
      direction: "جهت سند"
      purchase_type: "نوع خرید"
      type_of_effect: "نوع تاثیر بر موجودی"
      counter_part_type: "نوع طرف مقابل"
      company_title: "شرکت"
  relations: null


logistics_invvoucheritem:
  title: "قلم سند انبار"
  context: "logistics"
  parameters:
    logistics_invvoucheritem_p1:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    decimal_type:
      quantity: "مقدار"
      major_quantity: "مقدار به واحد اصلی"
      second_unit_quantity: "مقدار به واحد دوم"
      remained_major_quantity: "مانده استفاده نشده به واحد اصلی"
      remained_second_unit_quantity: "مانده استفاده نشده به واحد دوم"
    string_type:
      row_number: "شماره ردیف"
      sl_title: "معین"
      extra_field1: "فیلد اضافه 1"
      extra_field2: "فیلد اضافه 2"
      extra_field3: "فیلد اضافه 3"
      extra_field4: "فیلد اضافه 4"
      extra_field5: "فیلد اضافه 5"
      supplier_title: "تامین کننده"
      contractor_title: "پیمانکار"
      cost_center_title: "مرکز هزینه"
      project_title: "پروژه"
      customer_title: "مشتری"
      carrier_title: "موسسه حمل"
      consignment_party_title: "طرف حساب امانی"
      employee_title: "کارمند"
      sales_person_title: "کارمند فروش"
      purchase_order_no: "شماره سفارش خرید"
      purchase_invoice_no: "شماره فاکتور خرید"
      deliver_to: "تحویل گیرنده"
      cottage_no: "شماره کوتاژ"
      customs_green_sheet: "شماره برگ سبز"
      asn_no: "ASN NO"
      sales_order_no: "شماره سفارش فروش"
      sales_invoice_no: "شماره فاکتور خرید"
      sale_organization: "مرکز فروش"
      shopping_store: "فروشگاه"
      delivery_person: "تحویل دهنده"
      weighbridge_no: "شماره برگه باسکول"
      production_order_no: "شماره دستور تولید"
      production_plan_no: "شماره سفارش تولید"
      production_operation_no: "شماره عملیات تولید"
      production_shift: "شیفت تولید"
      qc_inspection_no: "شماره بازرسی کیفیت"
      qc_check_list_no: "شماره چک لیست"
      qc_lab_no: "شماره آزمایشگاه"
      conditional_approval: "تایید ارفاقی"
      inspection_result: "نتیجه بازرسی"
      coa_no: "شماره COA"
      transporter_name: "نام راننده"
      vehicle_no: "نام خودرو"
      license_plate_no: "شماره پلاک"
      waybill_no: "شماره بارنامه"
      transporter_phone_no: "تلفن راننده"
      company_title: "شرکت"
    date_type:
      production_date: "تاریخ تولید"
      waybill_date: "تاریخ بارنامه"
  relations:
    - name: "logistics_invvoucher"
      title: "سند انبار"
      foreign_key: "inventory_voucher_id"
      references: "logistics_invvoucher.id"
    - name: "logistics_part"
      title: "کالا"
      foreign_key: "part_id"
      references: "logistics_parts.id"
    - name: "logistics_unit"
      title: "واحد سنجش"
      foreign_key: "unit_id"
      references: "logistics_units.id"


logistics_invitemprice:
  title: "قلم قیمت"
  context: "logistics"
  parameters:
    logistics_invitemprice_p1:
      description: "حوزه قیمت‌گذاری"
      type: "Int64"
      source: "dataview"
    logistics_invitemprice_p2:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date: "تاریخ"
    decimal_type:
      fee: "فی"
      price: "مبلغ"
      major_fee: "فی به واحد اصلی"
      major_price: "مبلغ به واحد اصلی"
    string_type:
      price_type: "نوع قیمت"
      currency_title: "عنوان ارز"
      acc_voucher_number: "شماره سند حسابداری"
      company_title: "شرکت"
  relations:
    - name: "logistics_invvoucheritem"
      title: "قلم سند انبار"
      foreign_key: "inventory_voucher_item_id"
      references: "logistics_invvoucheritem.id"


logistics_invstockpricing:
  title: "گردش مبلغی"
  context: "logistics"
  parameters:
    logistics_invstockpricing_p1:
      description: "از تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invstockpricing_p2:
      description: "تا تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invstockpricing_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    decimal_type:
      fee: "فی"
      price: "مبلغ"
      price_in_functional_currency: "مبلغ به ارز عملیاتی"
      total_fee: "فی نهایی"
      total_price: "مبلغ نهایی"
      major_fee: "فی به واحد اصلی"
      major_unit_quantity: "مقدار واحد اصلی"
      quantity: "مقدار ثبت سند"
      second_unit_quantity: "مقدار واحد دوم"
    string_type:
      company_title: "عنوان شرکت"
      branch_title: "عنوان شعبه"
      plant_code: "کد مرکز نگهداری"
      plant_title: "عنوان مرکز نگهداری"
      store_code: "کد انبار"
      store_title: "عنوان انبار"
      storage_type: "نوع انبار"
      pricing_area_title: "عنوان حوزه قیمت گذاری"
      part_code: "کد کالا"
      part_title: "عنوان کالا"
      part_type: "نوع کالا"
      part_usage: "نوع کارکرد کالا"
      part_account_category: "طبقه حساب کالا"
      major_unit: "واحد اصلی"
      second_unit: "واحد دوم"
      inv_voucher_unit: "واحد ثبت سند"
      inventory_voucher_specification_title: "عنوان الگوی سند"
      inventory_voucher_type: "نوع سند"
      type_of_effect: "نوع تاثیر بر موجودی"
      counter_part_title: "طرف مقابل"
      inv_voucher_state: "وضعیت سند انبار"
      currency: "ارز"
      functional_currency: "ارز عملیاتی"
      itemprice_vouchering_state: "وضعیت سند حسابداری"
      item_pricing_state: "وضعیت قیمت گذاری"
      price_type: "نوع قیمت"
      acc_voucher_number: "شماره سند حسابداری"
  relations:
    - name: "logistics_invitemprice"
      title: "قلم قیمت"
      foreign_key: "inventory_voucher_item_price_id"
      references: "logistics_invitemprice.id"
    - name: "logistics_invitempricefactor"
      title: "جزییات مبلغی"
      foreign_key: "inventory_voucher_item_price_id"
      references: "logistics_invitempricefactor.inventory_voucher_item_price_id"


logistics_partstoragetype:
  title: "نوع انبار کالا"
  context: "logistics"
  parameters: null
  attributes: null
  relations:
    - name: "logistics_storagetype"
      title: "نوع انبار"
      foreign_key: "storage_type_id"
      references: "logistics_storagetype.id"


logistics_invitempricefactor:
  title: "جزییات مبلغی"
  context: "logistics"
  parameters:
    logistics_invitempricefactor_p1:
      description: "از تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invitempricefactor_p2:
      description: "تا تاریخ قیمت سند انبار"
      type: "Date"
    logistics_invitempricefactor_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    date_type:
      date_c: "تاریخ سند"
    decimal_type:
      td_in_functional_currency: "مالیات و عوارض"
      discount_in_functional_currency: "تخفیف"
      tf_in_functional_currency: "کرایه حمل"
      fee: "فی"
      major_fee: "فی به واحد اصلی"
      price: "مبلغ"
      price_in_reporting_currency1: "مبلغ به ارز گزارشگری1"
      price_in_reporting_currency2: "مبلغ به ارز گزارشگری2"
    string_type:
      transfer_fee_title: "ارز کرایه حمل"
      reporting1_currency: "ارز گزارشگری 1"
      reporting2_currency: "ارز گزارشگری 2"
      voucher_number: "شماره سند حسابداری"
      inv_voucher_number: "شماره سند انبار"
      company_title: "شرکت"
  relations: null


sales_pricelistitem:
  title: "قلم لیست قیمت"
  context: "sales"
  parameters:
    sales_pricelistitem_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
    sales_pricelistitem_p4:
      description: "ارز"
      type: "Int64Array"
      source: "currencies dataview"
      selection: "multiselect"
  attributes:
    decimal_type:
      plip_fee: "فی"
      pli_max_decrease_fee_percent: "حداکثر درصد کاهش"
      pli_max_increase_fee_percent: "حداکثر درصد افزایش"
    string_type:
      product_title: "عنوان کالا/خدمت"
      unit_title: "عنوان واحد سنجش"
      cmp_title: "شرکت"
    boolean_type:
      pli_is_price_changeable: "امکان تغییر در اسناد"
    date_type:
      plip_validity_start_date: "تاریخ شروع اعتبار بازه"
      plip_validity_end_date: "تاریخ پایان اعتبار بازه"
    int64_type: {}
  relations:
    - name: "sales_pricelistheader"
      title: "لیست قیمت"
      foreign_key: "pl_id"
      references: "sales_pricelistheader.id"
    - name: "sales_plparameters"
      title: "پارامتر های لیست قیمت"
      foreign_key: "pl_id"
      references: "sales_plparameters.pl_id"


sales_channel:
  title: "کانال فروش"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان کانال فروش"
      cmp_title: "شرکت"
      code: "کد کانال فروش"
  relations: null


sales_salesarea:
  title: "حوزه فروش"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان حوزه فروش"
      code: "کد حوزه فروش"
      cmp_title: "شرکت"
  relations: null


sales_division:
  title: "بخش فروش"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان بخش فروش"
      code: "کد بخش فروش"
      cmp_title: "شرکت"
  relations: null


sales_organization:
  title: "سازمان فروش"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان سازمان فروش"
      code: "کد سازمان فروش"
      cmp_title: "شرکت"
  relations: null


sales_settlementmethod:
  title: "روش تسویه"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان روش تسویه"
      cmp_title: "شرکت"
  relations: null


sales_customergroup:
  title: "گروه بندی مشتری"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان گروه مشتری"
      code: "کد گروه مشتری"
      grouping_title: "عنوان گروه بندی مشتری"
      cmp_title: "شرکت"
  relations: null


sales_pricelistheader:
  title: "لیست قیمت"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان لیست قیمت"
      currency_title: "عنوان ارز"
      state: "وضعیت"
      cmp_title: "شرکت"
    date_type:
      pl_validity_start_date: "تاریخ شروع اعتبار"
      pl_validity_end_date: "تاریخ پایان اعتبار"
  relations: null


sales_office:
  title: "دفتر فروش"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      title: "عنوان دفتر فروش"
      code: "کد دفتر فروش"
      cmp_title: "شرکت"
  relations: null


sales_plparameters:
  title: "پارامتر های لیست قیمت"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
  relations:
    - name: "sales_office"
      title: "دفتر فروش"
      foreign_key: "sales_office_id"
      references: "sales_office.id"
    - name: "customergroup"
      title: "گروه مشتری"
      foreign_key: "customer_group_id"
      references: "sales_customergroup.customer_group_id"
    - name: "sales_settlementmethod"
      title: "روش تسویه"
      foreign_key: "settlement_method_id"
      references: "sales_settlementmethod.id"
    - name: "sales_organization"
      title: "سازمان فروش"
      foreign_key: "sales_organization_id"
      references: "sales_organization.id"
    - name: "sales_division"
      title: "بخش فروش"
      foreign_key: "sales_division_id"
      references: "sales_division.id"
    - name: "sales_salesarea"
      title: "حوزه فروش"
      foreign_key: "sales_area_id"
      references: "sales_salesarea.id"
    - name: "sales_channel"
      title: "کانال فروش"
      foreign_key: "sales_channel_id"
      references: "sales_channel.id"


sales_returninvoice:
  title: "فاکتور برگشتی"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      afy_title: "سال مالی"
      cmp_title: "شرکت"
      number_c: "شماره فاکتور برگشتی"
      invoice_state: "وضعیت"
      description_c: "توضیحات"
      cu_code: "کد مشتری"
      cu_full_name: "نام و نام خانوادگی مشتری"
      sa_title: "حوزه فروش"
      so_title: "دفتر فروش"
      cur_title: "ارز"
    date_type:
      date_c: "تاریخ فاکتور برگشتی"
    decimal_type:
      functional_currency_rate: "نرخ ارز عملیاتی"
      first_reporting_currency_rate: "نرخ ارز گزارشگری اول"
      second_reporting_currency_rate: "نرخ ارز گزارشگری دوم"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deductions: "جمع تخفیف"
      surcharges: "جمع عوامل افزاینده"
      tax_total: "جمع مالیات"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
      functional_deductions: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_total: "جمع مالیات به ارز عملیاتی"
      first_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری اول"
      first_reporting_net_price: "مبلغ خالص به ارز گزارشگری اول"
      first_reporting_deductions: "جمع تخفیف به ارز گزارشگری اول"
      first_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری اول"
      first_reporting_tax_total: "جمع مالیات به ارز گزارشگری اول"
      second_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری دوم"
      second_reporting_net_price: "مبلغ خالص به ارز گزارشگری دوم"
      second_reporting_deductions: "جمع تخفیف به ارز گزارشگری دوم"
      second_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری دوم"
      second_reporting_tax_total: "جمع مالیات به ارز گزارشگری دوم"
  relations:
    - name: "sales_invoicecustomergroup"
      title: "گروه مشتری"
      foreign_key: "customer_id"
      references: "sales_invoicecustomergroup.customer_id"


sales_rinvoiceitem:
  title: "قلم فاکتور برگشتی"
  context: "sales"
  parameters:
    sales_rinvoiceitem_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      cmp_title: "شرکت"
      base_type_invoice: "نوع مبنا"
      base_invoice_number: "شماره سند مبنا"
      unit_title: "واحد سنجش"
      description_c: "توضیحات"
      store_title: "انبار"
    decimal_type:
      amount: "مقدار"
      fee: "فی"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deduction_price: "جمع تخفیف"
      surcharges: "جمع عوامل افزاینده"
      tax_total: "مالیات بر ارزش افزوده"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
      functional_deduction_price: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_total: "جمع مالیات به ارز عملیاتی"
      first_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری اول"
      first_reporting_net_price: "مبلغ خالص به ارز گزارشگری اول"
      first_reporting_deduction_price: "جمع تخفیف به ارز گزارشگری اول"
      first_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری اول"
      first_reporting_tax_total: "جمع مالیات به ارز گزارشگری اول"
      second_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری دوم"
      second_reporting_net_price: "مبلغ خالص به ارز گزارشگری دوم"
      second_reporting_deduction_price: "جمع تخفیف به ارز گزارشگری دوم"
      second_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری دوم"
      second_reporting_tax_total: "جمع مالیات به ارز گزارشگری دوم"
  relations:
    - name: "sales_product"
      title: "کالا/خدمت"
      foreign_key: "gnr_product_id"
      references: "sales_product.id"
    - name: "sales_productgroup"
      title: "گروه کالا/خدمت"
      foreign_key: "gnr_product_id"
      references: "sales_productgroup.product_id"
    - name: "logistics_invvoucheritem"
      title: "قلم سند انبار"
      foreign_key: "voucher_item_id"
      references: "logistics_invvoucheritem.id"
    - name: "sales_invoiceitem"
      title: "قلم فاکتور مبنا"
      foreign_key: "base_item_id"
      references: "sales_invoiceitem.id"
    - name: "sales_returninvoice"
      title: "فاکتور برگشتی"
      foreign_key: "return_invoice_id"
      references: "sales_returninvoice.id"


sales_invoice:
  title: "فاکتور"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      afy_title: "سال مالی"
      number_c: "شماره فاکتور"
      description_c: "توضیحات"
      cu_code: "کد مشتری"
      cu_full_name: "نام و نام خانوادگی مشتری"
      sa_title: "حوزه فروش"
      so_title: "دفتر فروش"
      sm_title: "روش تسویه"
      pay_full_name: "نام و نام خانوادگی پرداخت کننده"
      invoice_state: "وضعیت"
      payer_code: "کد پرداخت کننده"
      rec_full_name: "نام و نام خانوادگی تحویل گیرنده"
      receiver_code: "کد تحویل گیرنده"
      cur_title: "ارز"
    date_type:
      date_c: "تاریخ فاکتور"
    decimal_type:
      functional_currency_rate: "نرخ ارز عملیاتی"
      first_reporting_currency_rate: "نرخ ارز گزارشگری اول"
      second_reporting_currency_rate: "نرخ ارز گزارشگری دوم"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deductions: "جمع تخفیف"
      surcharges: "جمع عوامل افزاینده"
      tax_total: "جمع مالیات"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
      functional_deductions: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_total: "جمع مالیات به ارز عملیاتی"
      first_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری اول"
      first_reporting_net_price: "مبلغ خالص به ارز گزارشگری اول"
      first_reporting_deductions: "جمع تخفیف به ارز گزارشگری اول"
      first_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری اول"
      first_reporting_tax_total: "جمع مالیات به ارز گزارشگری اول"
      second_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری دوم"
      second_reporting_net_price: "مبلغ خالص به ارز گزارشگری دوم"
      second_reporting_deductions: "جمع تخفیف به ارز گزارشگری دوم"
      second_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری دوم"
      second_reporting_tax_total: "جمع مالیات به ارز گزارشگری دوم"
  relations:
    - name: "sales_invoicecustomergroup"
      title: "گروه مشتری"
      foreign_key: "customer_id"
      references: "sales_invoicecustomergroup.customer_id"


sales_invoiceitem:
  title: "قلم فاکتور"
  context: "sales"
  parameters:
    sales_invoiceitem_p3:
      description: "شرکت"
      type: "Int64Array"
      source: "companies dataview"
      selection: "multiselect"
  attributes:
    string_type:
      unit_title: "واحد سنجش"
      cmp_title: "شرکت"
      description_c: "توضیحات"
      store_title: "انبار"
    decimal_type:
      amount: "مقدار"
      fee: "فی"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deduction_price: "جمع تخفیف"
      surcharges: "جمع عوامل افزاینده"
      tax_total: "مالیات بر ارزش افزوده"
      functional_total_price: "مبلغ ناخالص به ارز عملیاتی"
      functional_net_price: "مبلغ خالص به ارز عملیاتی"
      functional_deduction_price: "جمع تخفیف به ارز عملیاتی"
      functional_surcharges: "جمع عوامل افزاینده به ارز عملیاتی"
      functional_tax_total: "جمع مالیات به ارز عملیاتی"
      first_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری اول"
      first_reporting_net_price: "مبلغ خالص به ارز گزارشگری اول"
      first_reporting_deduction_price: "جمع تخفیف به ارز گزارشگری اول"
      first_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری اول"
      first_reporting_tax_total: "جمع مالیات به ارز گزارشگری اول"
      second_reporting_total_price: "جمع مبلغ ناخالص به ارز گزارشگری دوم"
      second_reporting_net_price: "مبلغ خالص به ارز گزارشگری دوم"
      second_reporting_deduction_price: "جمع تخفیف به ارز گزارشگری دوم"
      second_reporting_surcharges: "جمع عوامل افزاینده به ارز گزارشگری دوم"
      second_reporting_tax_total: "جمع مالیات به ارز گزارشگری دوم"
  relations:
    - name: "sales_product"
      title: "کالا/خدمت"
      foreign_key: "gnr_product_id"
      references: "sales_product.id"
    - name: "sales_productgroup"
      title: "گروه کالا/خدمت"
      foreign_key: "gnr_product_id"
      references: "productgroup.product_id"
    - name: "logistics_invvoucheritem"
      title: "قلم سند انبار"
      foreign_key: "voucher_item_id"
      references: "logistics_invvoucheritem.id"
    - name: "sales_invoice"
      title: "فاکتور"
      foreign_key: "invoice_id"
      references: "sales_invoice.id"


sales_productgroup:
  title: "گروه بندی کالا/خدمت"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      code: "کد گروه کالا/خدمت"
      group_title: "عنوان گروه کالا/خدمت"
      grouping_title: "عنوان گروهبندی کالا/خدمت"
      cmp_title: "شرکت"
  relations: null


sales_invoicecustomergroup:
  title: "اعضای گروه بندی مشتری"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      group_title: "عنوان گروه مشتری"
      code: "کد گروه مشتری"
      title: "عنوان گروه بندی مشتری"
      cmp_title: "شرکت"
  relations: null


sales_product:
  title: "کالا/خدمت"
  context: "sales"
  parameters: null
  attributes:
    string_type:
      code: "کد کالا/خدمت"
      major_unit_title: "واحد سنجش اصلی"
      secondary_unit_title: "واحد سنجش دوم"
      cmp_title: "شرکت"
      title: "عنوان کالا/خدمت"
  relations: null
"""


FINANCIAL_BO_MODIFIED = """
financial_vouchers:
  title: "اقلام سند حسابداری"
  context: "financial"
  parameters:
    financial_vouchers_p1:
      description: "شرکت"
      type: "Int64"
      source: "dataview"
    financial_vouchers_p2:
      description: "دفتر"
      type: "Int64"
      source: "dataview"
    financial_vouchers_p3:
      description: "تاریخ شروع"
      type: "Date"
    financial_vouchers_p4:
      description: "تاریخ پایان"
      type: "Date"
    financial_vouchers_p5:
      description: "نوع سند"
      type: "Int64Array"
      source: "dataview"
      selection: "multiselect"
    financial_vouchers_p6:
      description: "وضعیت سند"
      type: "Int64"
      source: "enum"
      enum_name: "financial_vouchers_finenum01"
  attributes:
    date_type:
      voucher_date: "تاریخ سند"
      follow_up_date: "تاریخ پیگیری"
    decimal_type:
      debit: "گردش بدهکار ارز عملیاتی"
      credit: "گردش بستانکار ارز عملیاتی"
      debit_million: "کسر میلیون گردش بدهکار ارز عملیاتی"
      credit_million: "کسر میلیون گردش بستانکار ارز عملیاتی"
      currency_debit: "گردش بدهکار ارز سند"
      currency_credit: "گردش بستانکار ارز سند"
      functional_currency_exchange_rate: "نرخ تبدیل ارز عملیاتی"
      base_currency_debit: "گردش بدهکار ارز مبنا"
      base_currency_credit: "گردش بستانکار ارز مبنا"
      base_currency_exchange_rate: "نرخ تبدیل ارز مبنا"
      first_reporting_currency_debit: "گردش بدهکار ارز گزارشگری اول"
      first_reporting_currency_credit: "گردش بستانکار ارز گزارشگری اول"
      first_reporting_currency_exchange_rate: "نرخ تبدیل ارز گزارشگری اول"
      second_reporting_currency_debit: "گردش بدهکار ارز گزارشگری دوم"
      second_reporting_currency_credit: "گردش بستانکار ارز گزارشگری دوم"
      second_reporting_currency_exchange_rate: "نرخ تبدیل ارز گزارشگری دوم"
      quantity: "مقدار"
    string_type:
      header_branch_code: "کد شعبه"
      header_branch_title: "عنوان شعبه"
      voucher_number: "شماره سند"
      sequence_number: "شماره عطف"
      daily_number: "شماره روزانه"
      auxiliary_number: "شماره فرعی"
      voucher_type_title: "نوع سند"
      voucher_state: "وضعیت سند"
      voucher_explanation: "شرح سند"
      creator_name: "صادر کننده"
      reviewer_name: "بررسی کننده"
      ag_code: "کد گروه حساب"
      ag_title: "عنوان گروه حساب"
      gl_code: "کد حساب کل"
      gl_title: "عنوان حساب کل"
      row_number: "شماره ردیف"
      sl_code: "کد حساب معین"
      sl_title: "عنوان حساب معین"
      dl_code: "کد تفصیل"
      dl_title: "عنوان تفصیل"
      business_party_dl_code: "کد طرف تجاری"
      business_party_dl_title: "عنوان طرف تجاری"
      business_party_role: "نقش طرف تجاری"
      cost_center_dl_code: "کد مرکز هزینه"
      cost_center_dl_title: "عنوان مرکز هزینه"
      project_dl_code: "کد پروژه"
      project_dl_title: "عنوان پروژه"
      pricing_area_dl_code: "کد حوزه قیمت گذاری"
      pricing_area_dl_title: "عنوان حوزه قیمت گذاری"
      part_dl_code: "کد کالا"
      part_dl_title: "عنوان کالا"
      other_party_dl_code: "کد سایر اشخاص"
      other_party_dl_title: "عنوان سایر اشخاص"
      other_party_role: "نقش سایر اشخاص"
      branch_dl_code: "کد تفصیل شعبه"
      branch_dl_title: "عنوان تفصیل شعبه"
      bank_account_dl_code: "کد حساب بانکی"
      bank_account_dl_title: "عنوان حساب بانکی"
      voucher_currency_title: "ارز سند"
      currency_rate_type_title: "نوع نرخ ارز"
      base_currency_title: "ارز مبنا"
      voucher_item_explanation: "شرح قلم سندحسابداری"
      follow_up_number: "شماره پیگیری"
  relations: null
    """

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
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
    date_type:
      close_date: "تاریخ بستن فرصت"
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
      customer_editor_display: "آخرین کاربر ویرایش کننده"
    date_type:
      created_at: "تاریخ ایجاد"
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
  attributes:crm_campaign_campaignstatus
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
      lead_product_grouping_display: "دسته محصول مورد نیاز"
      lost_reason: "دلیل از دست رفتن"
      description: "توضیحات"
      lead_editor_display: "آخرین کاربر ویرایش کننده"
      lead_creator_display: "کاربر ایجاد کننده"
    date_type:
      convert_date: "تاریخ تبدیل"
      created_at: "تاریخ ایجاد"
      updated_at: "آخرین تاریخ ویرایش"
      birthdate: "تاریخ تولد"
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
      opportunity_pipeline: "روند فروش"
      opportunity_stage: "مرحله"
      opportunity_price: "مبلغ"
      opportunity_expected_price: "مبلغ مورد انتظار"
      opportunity_success_probability: "احتمال موفقیت"
    date_type:
      opportunity_close_date: "تاریخ بستن"
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
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
    date_type:
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
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
      number: "شماره پیش فاکتور"
      total_price: "مبلغ ناخالص"
      deductions: "کسورات"
      additions: "اضافات"
      net_price: "مبلغ خالص"
      sales_area_title: "حوزه فروش"
      sales_office_title: "دفتر فروش"
      currency_title: "ارز"
      owner_display_name: "کاربر پیگیری کننده"
      company_title: "شرکت"
    date_type:
      created_at: "تاریخ ایجاد"
      date: "تاریخ پیش فاکتور"
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
      price: "مبلغ"
      currency_title: "ارز"
      expected_price: "مبلغ مورد انتظار"
      created_by: "کاربر ایجاد کننده"
      user_display_name: "کاربر پیگیری کننده"
      updated_by: "آخرین کاربر ویرایش کننده"
      campaign_name: "کمپین"
      description: "توضیحات"
      company_title: "شرکت"
    date_type:
      close_date: "تاریخ بستن فرصت"
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
    date_type:
      date: "تاریخ"
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
    date_type:
      invoice_date: "تاریخ"
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
    date_type:
      submission_date: "تاریخ درخواست"
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
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      status: "وضعیت"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      campaign_creator_display: "کاربر ایجاد کننده"
      campaign_editor_display: "آخرین کاربر ویرایش کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
    date_type:
      created_at: "تاریخ ایجاد"
      updated_at: "آخرین تاریخ ویرایش"
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
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
      contact_owner_display: "کاربر پیگیری کننده"
      contact_creator_display: "کاربر ایجاد کننده"
      contact_editor_display: "آخرین کاربر ویرایش کننده"
    date_type:
      created_at: "تاریخ ایجاد"
      birthdate: "تاریخ تولد"
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
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
    date_type:
      close_date: "تاریخ بستن فرصت"
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
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
    date_type:
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
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
      number: "شماره پیش فاکتور"
      total_price: "مبلغ ناخالص"
      net_price: "مبلغ خالص"
      deductions: "جمع کسور"
      surcharges: "جمع عوامل افزاینده"
      sales_area_title: "حوزه فروش"
      sales_office_title: "دفتر فروش"
      currency_title: "ارز"
      owner_name: "کاربر پیگیری کننده"
    date_type:
      date: "تاریخ"
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
      pipeline: "روند فروش"
      stage: "مرحله فروش"
      price: "مبلغ"
      expected_price: "مبلغ مورد انتظار"
      success_probability: "احتمال موفقیت"
    date_type:
      close_date: "تاریخ بستن فرصت"
  relations: null


crm_leadCampaign:
  title: "کمپین‌های سرنخ"
  context: "crm"
  parameters: null
  attributes:
    string_type:
      cmp_title: "شرکت"
      name: "نام"
      campaign_parent_display: "کمپین مادر"
      description: "توضیحات"
      stage: "مرحله"
      campaign_owner_display: "کاربر پیگیری کننده"
      budget: "بودجه"
      expected_income: "درآمد مورد انتظار"
      actual_cost: "هزینه واقعی"
    date_type:
      start_date: "تاریخ شروع"
      end_date: "تاریخ پایان"
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
treasury_cheque:
  title: "چک پرداختی"
  context: "treasury"
  parameters: 
    treasury_cheque_p1:
      description: "شناسه قلم"
      type: "Int64Array"
  attributes:
    string_type:
      id: "قلم سند پرداخت"
      full_name: "نام دریافت کننده"
      national_id: "کد/شناسه ملی"
    date_type:
      due_date: "تاریخ سررسید"
    decimal_type:
      amount: "مبلغ"
  relations: null
"""