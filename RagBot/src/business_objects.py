LOGISTICS_MODIFIED = """
    ## logistics_partaltunit
    - **Title**: واحد فرعی کالا 
    - **Context**: logistics
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان واحد فرعی کالا 
        - major_unit_title: واحد سنجش اصلی 
      - **Float64 Type**: 
        - coeff: ضریب 
    - **Relations**: None

        
    ## logistics_storagetype:
    - **Title**: نوع انبار
    - **Context**: logistics
    - **Parameters**:
      - logistics_storagetype_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - code: کد نوع انبار
        - title: عنوان نوع انبار
        - company_title: شرکت
    - **Relations**: None

    
    ## logistics_units
    - **Title**: واحد سنجش (Unit of Measure)
    - **Context**: logistics
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان واحد سنجش
      - Int64 Type:
        - dimension: بعد 
    - **Relations**: None


    ## logistics_store
    - **Title**: انبار
    - **Context**: logistics
    - **Parameters**:
      - logistics_store_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - code: کد انبار 
        - title: عنوان انبار 
        - storage_type_title: عنوان نوع انبار 
        - state: استان 
        - company_title: شرکت
    - **Relations**:
      - logistics_plants: مرکز نگهداری (foreign key: plant_id to logistics_plants.id)


    ## logistics_partaccountcategory
    - **Title**: طبقه حساب کالا 
    - **Context**: logistics
    - **Parameters**:
      - logistics_partaccountcategory_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**: 
        - code: کد طبقه حساب کالا 
        - title: عنوان طبقه حساب کالا 
        - pricing_method: روش قیمت گذاری 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_plants
    - **Title**: مرکز نگهداری 
    - **Context**: logistics
    - **Parameters**: 
      - logistics_plants_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - code: کد مرکز نگهداری 
        - title: عنوان مرکز نگهداری 
        - branch_title: عنوان شعبه 
        - state: استان 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_invvoucher
    - **Title**: سند انبار 
    - **Context**: logistics
    - **Parameters**:
      - logistics_invvoucher_p1: از تاریخ سند انبار (Date)
      - logistics_invvoucher_p2: تا تاریخ سند انبار (Date)
      - logistics_invvoucher_p3: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **Date Type**: 
        - date: تاریخ سند
        - production_date: تاریخ تولید
        - waybill_date: تاریخ بارنامه 
      - **String Type**: 
        - number: شماره سند 
        - description: شرح سربرگ 
        - sl_title: معین 
        - state: وضعیت 
        - fy_title: دوره مالی 
        - extra_field1: فیلد اضافه 1 
        - extra_field2: فیلد اضافه 2 
        - extra_field3: فیلد اضافه 3 
        - extra_field4: فیلد اضافه 4 
        - extra_field5: فیلد اضافه 5 
        - supplier_title: تامین کننده 
        - contractor_title: پیمانکار 
        - cost_center_title: مرکز هزینه 
        - project_title: پروژه 
        - customer_title: مشتری 
        - carrier_title: موسسه حمل 
        - consignment_party_title: طرف حساب امانی 
        - employee_title: کارمند 
        - sales_person_title: کارمند فروش 
        - purchase_order_no: شماره سفارش خرید 
        - purchase_invoice_no: شماره فاکتور خرید 
        - deliver_to: تحویل گیرنده 
        - cottage_no: شماره کوتاژ 
        - customs_green_sheet: شماره برگ سبز 
        - asn_no: ASN NO 
        - sales_order_no: شماره سفارش فروش 
        - sales_invoice_no: شماره فاکتور خرید 
        - sale_organization: مرکز فروش 
        - shopping_store: فروشگاه 
        - delivery_person: تحویل دهنده 
        - weighbridge_no: شماره برگه باسکول 
        - production_order_no: شماره دستور تولید 
        - production_plan_no: شماره سفارش تولید 
        - production_operation_no: شماره عملیات تولید 
        - production_shift: شیفت تولید 
        - qc_inspection_no: شماره بازرسی کیفیت 
        - qc_check_list_no: شماره چک لیست 
        - qc_lab_no: شماره آزمایشگاه 
        - conditional_approval: تایید ارفاقی 
        - inspection_result: نتیجه بازرسی 
        - coa_no: شماره COA 
        - transporter_name: نام راننده 
        - vehicle_no: نام خودرو 
        - license_plate_no: شماره پلاک 
        - waybill_no: شماره بارنامه 
        - transporter_phone_no: تلفن راننده 
        - company_title: شرکت 
    - **Relations**:
      - logistics_voucherspecification: الگوی سند انبار (foreign key: voucher_specification_id to logistics_voucherspecification.id)
      - logistics_store: انبار (foreign key: store_id to logistics_store.id)
      - logistics_counterstore: انبار مقابل (foreign key: counter_part_store_id to logistics_store.id)


    ## logistics_parts
    - **Title**: کالا 
    - **Context**: logistics
    - **Parameters**: 
      - logistics_parts_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - code: کد کالا 
        - title: عنوان کالا 
        - major_unit_title: واحد سنجش اصلی 
        - secondary_unit_title: واحد سنجش دوم 
        - part_account_category_title: طبقه حساب کالا 
        - part_type: نوع کالا 
        - part_usage: نوع کارکرد کالا 
        - company_title: شرکت 
    - **Relations**:
      - logistics_partaltunit: واحد فرعی کالا (foreign key: id to logistics_partaltunit.part_id)
      - logistics_partstoragetype: نوع انبار کالا (foreign key: id to logistics_partstoragetype.part_id)


    ## logistics_voucherspecification
    - **Title**: الگوی سند انبار
    - **Context**: logistics
    - **Parameters**: 
      - logistics_voucherspecification_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**: 
        - code: کد الگو 
        - title: عنوان الگو 
        - voucher_type: نوع سند 
        - direction: جهت سند 
        - purchase_type: نوع خرید 
        - type_of_effect: نوع تاثیر بر موجودی 
        - counter_part_type: نوع طرف مقابل 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_invvoucheritem
    - **Title**: قلم سند انبار 
    - **Context**: logistics
    - **Parameters**: 
      - logistics_invvoucheritem_p1: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **Decimal Type**: 
        - quantity: مقدار 
        - major_quantity: مقدار به واحد اصلی 
        - second_unit_quantity: مقدار به واحد دوم 
        - remained_major_quantity: مانده استفاده نشده به واحد اصلی 
        - remained_second_unit_quantity: مانده استفاده نشده به واحد دوم 
      - **String Type**:
        - row_number: شماره ردیف  
        - sl_title: معین 
        - extra_field1: فیلد اضافه 1 
        - extra_field2: فیلد اضافه 2 
        - extra_field3: فیلد اضافه 3 
        - extra_field4: فیلد اضافه 4 
        - extra_field5: فیلد اضافه 5 
        - supplier_title: تامین کننده 
        - contractor_title: پیمانکار 
        - cost_center_title: مرکز هزینه 
        - project_title: پروژه 
        - customer_title: مشتری 
        - carrier_title: موسسه حمل 
        - consignment_party_title: طرف حساب امانی 
        - employee_title: کارمند 
        - sales_person_title: کارمند فروش 
        - purchase_order_no: شماره سفارش خرید 
        - purchase_invoice_no: شماره فاکتور خرید 
        - deliver_to: تحویل گیرنده 
        - cottage_no: شماره کوتاژ 
        - customs_green_sheet: شماره برگ سبز 
        - asn_no: ASN NO 
        - sales_order_no: شماره سفارش فروش 
        - sales_invoice_no: شماره فاکتور خرید 
        - sale_organization: مرکز فروش 
        - shopping_store: فروشگاه 
        - delivery_person: تحویل دهنده 
        - weighbridge_no: شماره برگه باسکول 
        - production_order_no: شماره دستور تولید 
        - production_plan_no: شماره سفارش تولید 
        - production_operation_no: شماره عملیات تولید 
        - production_shift: شیفت تولید 
        - qc_inspection_no: شماره بازرسی کیفیت 
        - qc_check_list_no: شماره چک لیست 
        - qc_lab_no: شماره آزمایشگاه 
        - conditional_approval: تایید ارفاقی 
        - inspection_result: نتیجه بازرسی 
        - coa_no: شماره COA 
        - transporter_name: نام راننده 
        - vehicle_no: نام خودرو 
        - license_plate_no: شماره پلاک 
        - waybill_no: شماره بارنامه 
        - transporter_phone_no: تلفن راننده 
        - company_title: شرکت 
      - **Date Type**:
        - production_date: تاریخ تولید
        - waybill_date: تاریخ بارنامه  
    - **Relations**:
      - logistics_invvoucher: سند انبار (foreign key: inventory_voucher_id to logistics_invvoucher.id)
      - logistics_part: کالا (foreign key: part_id to logistics_parts.id)
      - logistics_unit: واحد سنجش (foreign key: unit_id to logistics_units.id)


    ## logistics_invitemprice
    - **Title**: قلم قیمت 
    - **Context**: logistics
    - **Parameters**: 
      - logistics_invitemprice_p1: حوزه قیمت‌گذاری (Int64 - from dataview)
      - logistics_invitemprice_p2: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **Date Type**: 
        - date: تاریخ 
      - **Decimal Type**: 
        - fee: فی 
        - price: مبلغ 
        - major_fee: فی به واحد اصلی 
        - major_price: مبلغ به واحد اصلی 
      - **String Type**:
        - price_type: نوع قیمت 
        - currency_title: عنوان ارز 
        - acc_voucher_number: شماره سند حسابداری 
        - company_title: شرکت 
    - **Relations**:
      - logistics_invvoucheritem: قلم سند انبار (foreign key: inventory_voucher_item_id to logistics_invvoucheritem.id)


    ## logistics_invstockpricing
    - **Title**: گردش مبلغی
    - **Context**: logistics
    - **Parameters**: 
      - logistics_invstockpricing_p1 (Date): از تاریخ قیمت سند انبار
      - logistics_invstockpricing_p2 (Date): تا تاریخ قیمت سند انبار
      - logistics_invstockpricing_p3: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **Decimal Type**: 
        - fee: فی 
        - price: مبلغ 
        - price_in_functional_currency: مبلغ به ارز عملیاتی 
        - total_fee: فی نهایی 
        - total_price: مبلغ نهایی 
        - major_fee: فی به واحد اصلی 
        - major_unit_quantity: مقدار واحد اصلی 
        - quantity: مقدار ثبت سند 
        - second_unit_quantity: مقدار واحد دوم 
      - **String Type**:
        - company_title: عنوان شرکت 
        - branch_title: عنوان شعبه 
        - plant_code: کد مرکز نگهداری 
        - plant_title: عنوان مرکز نگهداری 
        - store_code: کد انبار 
        - store_title: عنوان انبار 
        - storage_type: نوع انبار 
        - pricing_area_title: عنوان حوزه قیمت گذاری 
        - part_code: کد کالا 
        - part_title: عنوان کالا 
        - part_type: نوع کالا 
        - part_usage: نوع کارکرد کالا 
        - part_account_category: طبقه حساب کالا 
        - major_unit: واحد اصلی 
        - second_unit: واحد دوم 
        - inv_voucher_unit: واحد ثبت سند 
        - inventory_voucher_specification_title: عنوان الگوی سند 
        - inventory_voucher_type: نوع سند
        - type_of_effect: نوع تاثیر بر موجودی 
        - counter_part_title: طرف مقابل 
        - inv_voucher_state: وضعیت سند انبار 
        - currency: ارز 
        - functional_currency: ارز عملیاتی 
        - itemprice_vouchering_state: وضعیت سند حسابداری 
        - item_pricing_state: وضعیت قیمت گذاری 
        - price_type: نوع قیمت 
        - acc_voucher_number: شماره سند حسابداری 
    - **Relations**:
      - logistics_invitemprice: قلم قیمت (foreign key: inventory_voucher_item_price_id to logistics_invitemprice.id)
      - logistics_invitempricefactor: جزییات مبلغی (foreign key: inventory_voucher_item_price_id to logistics_invitempricefactor.inventory_voucher_item_price_id)


    ## logistics_storagetype
    - **Title**: نوع انبار 
    - **Context**: logistics
    - **Parameters**: 
      - logistics_storagetype_p1 (Int64Array_Dataview): شرکت
    - **Attributes**:
      - **Str Type**: 
        - code: کد نوع انبار 
        - title: عنوان نوع انبار 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_partstoragetype
    - **Title**: نوع انبار کالا 
    - **Context**: logistics
    - **Parameters**: None
    - **Attributes**: None
    - **Relations**:
      - logistics_storagetype: نوع انبار (foreign key: storage_type_id to logistics_storagetype.id)


    ## logistics_invitempricefactor
    - **Title**: جزییات مبلغی
    - **Context**: logistics
    - **Parameters**:
      - logistics_invitempricefactor_p1 (Date): از تاریخ قیمت سند انبار
      - logistics_invitempricefactor_p2 (Date): تا تاریخ قیمت سند انبار
      - logistics_invitempricefactor_p3: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **Date Type**:
        - date_c: تاریخ سند 
      - **Decimal Type**: 
        - td_in_functional_currency: مالیات و عوارض 
        - discount_in_functional_currency: تخفیف 
        - tf_in_functional_currency: کرایه حمل 
        - fee: فی 
        - major_fee: فی به واحد اصلی 
        - price: مبلغ 
        - price_in_reporting_currency1: مبلغ به ارز گزارشگری1 
        - price_in_reporting_currency2: مبلغ به ارز گزارشگری2 
      - **String Type**:
        - transfer_fee_title: ارز کرایه حمل
        - reporting1_currency: ارز گزارشگری 1
        - reporting2_currency: ارز گزارشگری 2
        - voucher_number: شماره سند حسابداری
        - inv_voucher_number: شماره سند انبار
        - company_title: شرکت
    - **Relations**: None

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
