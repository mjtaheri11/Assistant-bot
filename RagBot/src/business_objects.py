LOGISTICS_SALES_MODIFIED = """
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


    ## sales_pricelistitem 
    - **Title**: قلم لیست قیمت
    - **Context**: sales
    - **Parameters**:
      - sales_pricelistitem_p3: شرکت (Int64Array - multiselect from companies dataview)
      - sales_pricelistitem_p4: ارز (Int64Array - multiselect from currencies dataview)
    - **Attributes**:
      - **Decimal Type**:
        - plip_fee: فی
        - pli_max_decrease_fee_percent: حداکثر درصد کاهش 
        - pli_max_increase_fee_percent: حداکثر درصد افزایش 
      - **String Type**:
        - product_title: عنوان کالا/خدمت 
        - unit_title: عنوان واحد سنجش 
        - cmp_title: شرکت
      - **Boolean Type**:
        - pli_is_price_changeable: امکان تغییر در اسناد 
      - **Date Type**:
        - plip_validity_start_date: تاریخ شروع اعتبار بازه 
        - plip_validity_end_date: تاریخ پایان اعتبار بازه 
      - **Int64 Type**:
    - **Relations**:
      - sales_pricelistheader: لیست قیمت (foreign key pl_id to sales_pricelistheader.id)
      - sales_plparameters: پارامتر های لیست قیمت (foreign key pl_id to sales_plparameters.pl_id)


    ## sales_channel 
    - **Title**: کانال فروش
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان کانال فروش
        - cmp_title: شرکت
        - code: کد کانال فروش
    - **Relations**: None

    ## sales_salesarea 
    - **Title**: حوزه فروش
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان حوزه فروش
        - code: کد حوزه فروش
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_division 
    - **Title**: بخش فروش
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان بخش فروش
        - code: کد بخش فروش
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_organization 
    - **Title**: سازمان فروش
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان سازمان فروش
        - code: کد سازمان فروش
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_settlementmethod 
    - **Title**: روش تسویه
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان روش تسویه
        - cmp_title: شرکت
    - **Relations**: None

    ## sales_customergroup 
    - **Title**: گروه بندی مشتری
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان گروه مشتری
        - code: کد گروه مشتری
        - grouping_title: عنوان گروه بندی مشتری
        - cmp_title: شرکت


    ## sales_pricelistheader 
    - **Title**: لیست قیمت
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان لیست قیمت 
        - currency_title: عنوان ارز
        - state: وضعیت 
        - cmp_title: شرکت 
      - **Date Type**:
        - pl_validity_start_date: تاریخ شروع اعتبار 
        - pl_validity_end_date: تاریخ پایان اعتبار 
    - **Relations**: None


    ## sales_office 
    - **Title**: دفتر فروش
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - title: عنوان دفتر فروش
        - code: کد دفتر فروش
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_plparameters 
    - **Title**: پارامتر های لیست قیمت
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - cmp_title: شرکت (all Str)
    - **Relations**:
      - sales_office: دفتر فروش (foreign key sales_office_id to sales_office.id)
      - customergroup: گروه مشتری (foreign key customer_group_id to sales_customergroup.customer_group_id)
      - sales_settlementmethod: روش تسویه (foreign key settlement_method_id to sales_settlementmethod.id)
      - sales_organization: سازمان فروش (foreign key sales_organization_id to sales_organization.id)
      - sales_division: بخش فروش (foreign key sales_division_id to sales_division.id)
      - sales_salesarea: حوزه فروش (foreign key sales_area_id to sales_salesarea.id)
      - sales_channel: کانال فروش (foreign key sales_channel_id to sales_channel.id)


    ## sales_returninvoice
    - **Title**: فاکتور برگشتی
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - afy_title: سال مالی
        - cmp_title: شرکت
        - number_c: شماره فاکتور برگشتی
        - invoice_state: وضعیت
        - description_c: توضیحات
        - cu_code: کد مشتری
        - cu_full_name: نام و نام خانوادگی مشتری
        - sa_title: حوزه فروش
        - so_title: دفتر فروش
        - cur_title: ارز
      - **Date Type**:
        - date_c: تاریخ فاکتور برگشتی
      - **Decimal Type**:
        - functional_currency_rate: نرخ ارز عملیاتی
        - first_reporting_currency_rate: نرخ ارز گزارشگری اول
        - second_reporting_currency_rate: نرخ ارز گزارشگری دوم
        - total_price: مبلغ ناخالص
        - net_price: مبلغ خالص
        - deductions: جمع تخفیف
        - surcharges: جمع عوامل افزاینده
        - tax_total: جمع مالیات
        - functional_total_price: مبلغ ناخالص به ارز عملیاتی
        - functional_net_price: مبلغ خالص به ارز عملیاتی
        - functional_deductions: جمع تخفیف به ارز عملیاتی
        - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
        - functional_tax_total: جمع مالیات به ارز عملیاتی
        - first_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری اول
        - first_reporting_net_price: مبلغ خالص به ارز گزارشگری اول
        - first_reporting_deductions: جمع تخفیف به ارز گزارشگری اول
        - first_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری اول
        - first_reporting_tax_total: جمع مالیات به ارز گزارشگری اول
        - second_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری دوم
        - second_reporting_net_price: مبلغ خالص به ارز گزارشگری دوم
        - second_reporting_deductions: جمع تخفیف به ارز گزارشگری دوم
        - second_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری دوم
        - second_reporting_tax_total: جمع مالیات به ارز گزارشگری دوم
    - **Relations**:
      - sales_invoicecustomergroup: گروه مشتری (foreign key customer_id to sales_invoicecustomergroup.customer_id)


    ## sales_rinvoiceitem 
    - **Title**: قلم فاکتور برگشتی
    - **Context**: sales
    - **Parameters**:
      - sales_rinvoiceitem_p3: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - cmp_title: شرکت
        - base_type_invoice: نوع مبنا
        - base_invoice_number: شماره سند مبنا
        - unit_title: واحد سنجش
        - description_c: توضیحات
        - store_title: انبار
      - **Decimal Type**:
        - amount: مقدار
        - fee: فی
        - total_price: مبلغ ناخالص
        - net_price: مبلغ خالص
        - deduction_price: جمع تخفیف
        - surcharges: جمع عوامل افزاینده
        - tax_total: مالیات بر ارزش افزوده
        - functional_total_price: مبلغ ناخالص به ارز عملیاتی
        - functional_net_price: مبلغ خالص به ارز عملیاتی
        - functional_deduction_price: جمع تخفیف به ارز عملیاتی
        - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
        - functional_tax_total: جمع مالیات به ارز عملیاتی
        - first_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری اول
        - first_reporting_net_price: مبلغ خالص به ارز گزارشگری اول
        - first_reporting_deduction_price: جمع تخفیف به ارز گزارشگری اول
        - first_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری اول
        - first_reporting_tax_total: جمع مالیات به ارز گزارشگری اول
        - second_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری دوم
        - second_reporting_net_price: مبلغ خالص به ارز گزارشگری دوم
        - second_reporting_deduction_price: جمع تخفیف به ارز گزارشگری دوم
        - second_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری دوم
        - second_reporting_tax_total: جمع مالیات به ارز گزارشگری دوم
    - **Relations**:
      - sales_product: کالا/خدمت (foreign key gnr_product_id to sales_product.id)
      - sales_productgroup: گروه کالا/خدمت (foreign key gnr_product_id to sales_productgroup.product_id)
      - logistics_invvoucheritem: قلم سند انبار (foreign key voucher_item_id to logistics_invvoucheritem.id)
      - sales_invoiceitem: قلم فاکتور مبنا (foreign key base_item_id to sales_invoiceitem.id)
      - sales_returninvoice: فاکتور برگشتی (foreign key return_invoice_id to sales_returninvoice.id)


    ## sales_invoice
    - **Title**: فاکتور
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - cmp_title: شرکت
        - afy_title: سال مالی
        - number_c: شماره فاکتور
        - description_c: توضیحات
        - cu_code: کد مشتری
        - cu_full_name: نام و نام خانوادگی مشتری
        - sa_title: حوزه فروش
        - so_title: دفتر فروش
        - sm_title: روش تسویه
        - pay_full_name: نام و نام خانوادگی پرداخت کننده
        - invoice_state: وضعیت
        - payer_code: کد پرداخت کننده
        - rec_full_name: نام و نام خانوادگی تحویل گیرنده
        - receiver_code: کد تحویل گیرنده
        - cur_title: ارز
      - **Date Type**:
        - date_c: تاریخ فاکتور
      - **Decimal Type**:
        - functional_currency_rate: نرخ ارز عملیاتی
        - first_reporting_currency_rate: نرخ ارز گزارشگری اول
        - second_reporting_currency_rate: نرخ ارز گزارشگری دوم
        - total_price: مبلغ ناخالص
        - net_price: مبلغ خالص
        - deductions: جمع تخفیف
        - surcharges: جمع عوامل افزاینده
        - tax_total: جمع مالیات
        - functional_total_price: مبلغ ناخالص به ارز عملیاتی
        - functional_net_price: مبلغ خالص به ارز عملیاتی
        - functional_deductions: جمع تخفیف به ارز عملیاتی
        - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
        - functional_tax_total: جمع مالیات به ارز عملیاتی
        - first_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری اول
        - first_reporting_net_price: مبلغ خالص به ارز گزارشگری اول
        - first_reporting_deductions: جمع تخفیف به ارز گزارشگری اول
        - first_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری اول
        - first_reporting_tax_total: جمع مالیات به ارز گزارشگری اول
        - second_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری دوم
        - second_reporting_net_price: مبلغ خالص به ارز گزارشگری دوم
        - second_reporting_deductions: جمع تخفیف به ارز گزارشگری دوم
        - second_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری دوم
        - second_reporting_tax_total: جمع مالیات به ارز گزارشگری دوم
    - **Relations**:
      - sales_invoicecustomergroup: گروه مشتری (foreign key customer_id to sales_invoicecustomergroup.customer_id)


    ## sales_invoiceitem:
    - **Title**: قلم فاکتور
    - **Context**: sales
    - **Parameters**:
      - sales_invoiceitem_p3: شرکت (Int64Array - multiselect from companies dataview)
    - **Attributes**:
      - **String Type**:
        - unit_title: واحد سنجش
        - cmp_title: شرکت
        - description_c: توضیحات
        - store_title: انبار
      - **Decimal Type**:
        - amount: مقدار
        - fee: فی
        - total_price: مبلغ ناخالص
        - net_price: مبلغ خالص
        - deduction_price: جمع تخفیف
        - surcharges: جمع عوامل افزاینده
        - tax_total: مالیات بر ارزش افزوده
        - functional_total_price: مبلغ ناخالص به ارز عملیاتی
        - functional_net_price: مبلغ خالص به ارز عملیاتی
        - functional_deduction_price: جمع تخفیف به ارز عملیاتی
        - functional_surcharges: جمع عوامل افزاینده به ارز عملیاتی
        - functional_tax_total: جمع مالیات به ارز عملیاتی
        - first_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری اول
        - first_reporting_net_price: مبلغ خالص به ارز گزارشگری اول
        - first_reporting_deduction_price: جمع تخفیف به ارز گزارشگری اول
        - first_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری اول
        - first_reporting_tax_total: جمع مالیات به ارز گزارشگری اول
        - second_reporting_total_price: جمع مبلغ ناخالص به ارز گزارشگری دوم
        - second_reporting_net_price: مبلغ خالص به ارز گزارشگری دوم
        - second_reporting_deduction_price: جمع تخفیف به ارز گزارشگری دوم
        - second_reporting_surcharges: جمع عوامل افزاینده به ارز گزارشگری دوم
        - second_reporting_tax_total: جمع مالیات به ارز گزارشگری دوم
    - **Relations**:
      - sales_product: کالا/خدمت (foreign key gnr_product_id to sales_product.id)
      - sales_productgroup: گروه کالا/خدمت (foreign key gnr_product_id to productgroup.product_id)
      - logistics_invvoucheritem: قلم سند انبار (foreign key voucher_item_id to logistics_invvoucheritem.id)
      - sales_invoice: فاکتور (foreign key invoice_id to sales_invoice.id)


    ## sales_productgroup 
    - **Title**: گروه بندی کالا/خدمت
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - code: کد گروه کالا/خدمت
        - group_title: عنوان گروه کالا/خدمت
        - grouping_title: عنوان گروهبندی کالا/خدمت
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_invoicecustomergroup 
    - **Title**: اعضای گروه بندی مشتری
    - **Context**: sales
    - **Parameters**: None
    - **Attributes**:
      - **String Type**:
        - group_title: عنوان گروه مشتری
        - code: کد گروه مشتری
        - title: عنوان گروه بندی مشتری
        - cmp_title: شرکت
    - **Relations**: None


    ## sales_product 
    - **Title**: کالا/خدمت
    - **Context**: sales
    - **Parameters**: None
    - **Attributes **:
      - **String Type**:
        - code: کد کالا/خدمت
        - major_unit_title: واحد سنجش اصلی
        - secondary_unit_title: واحد سنجش دوم
        - cmp_title: شرکت
        - title: عنوان کالا/خدمت
    - **Relations**: None
"""


FINANCIAL_BO_MODIFIED = """
    ## financial_vouchers:
    - Title: اقلام سند حسابداری
    - Context: financial
    - **Parameters**:
      - financial_vouchers_p1: شرکت (Int64 - from dataview)
      - financial_vouchers_p2: دفتر (Int64 - from dataview)
      - financial_vouchers_p3: تاریخ شروع (Date)
      - financial_vouchers_p4: تاریخ پایان (Date)
      - financial_vouchers_p5: نوع سند (Int64Array - multiselect from dataview)
      - financial_vouchers_p6: وضعیت سند (Int64 - enum: financial_vouchers_finenum01)
    - **Attributes**:
      - **Date Type**:
        - voucher_date: تاریخ سند
        - follow_up_date: تاریخ پیگیری
      - **Decimal Type**:
        - debit: گردش بدهکار ارز عملیاتی
        - credit: گردش بستانکار ارز عملیاتی
        - debit_million: کسر میلیون گردش بدهکار ارز عملیاتی
        - credit_million: کسر میلیون گردش بستانکار ارز عملیاتی
        - currency_debit: گردش بدهکار ارز سند
        - currency_credit: گردش بستانکار ارز سند
        - functional_currency_exchange_rate: نرخ تبدیل ارز عملیاتی
        - base_currency_debit: گردش بدهکار ارز مبنا
        - base_currency_credit: گردش بستانکار ارز مبنا
        - base_currency_exchange_rate: نرخ تبدیل ارز مبنا
        - first_reporting_currency_debit: گردش بدهکار ارز گزارشگری اول
        - first_reporting_currency_credit: گردش بستانکار ارز گزارشگری اول
        - first_reporting_currency_exchange_rate: نرخ تبدیل ارز گزارشگری اول
        - second_reporting_currency_debit: گردش بدهکار ارز گزارشگری دوم
        - second_reporting_currency_credit: گردش بستانکار ارز گزارشگری دوم
        - second_reporting_currency_exchange_rate: نرخ تبدیل ارز گزارشگری دوم
        - quantity: مقدار
      - **String Type**:
        - header_branch_code: کد شعبه
        - header_branch_title: عنوان شعبه
        - voucher_number: شماره سند
        - sequence_number: شماره عطف
        - daily_number: شماره روزانه
        - auxiliary_number: شماره فرعی
        - voucher_type_title: نوع سند
        - voucher_state: وضعیت سند
        - voucher_explanation: شرح سند
        - creator_name: صادر کننده
        - reviewer_name: بررسی کننده
        - ag_code: کد گروه حساب
        - ag_title: عنوان گروه حساب
        - gl_code: کد حساب کل
        - gl_title: عنوان حساب کل
        - row_number: شماره ردیف
        - sl_code: کد حساب معین
        - sl_title: عنوان حساب معین
        - dl_code: کد تفصیل
        - dl_title: عنوان تفصیل
        - business_party_dl_code: کد طرف تجاری
        - business_party_dl_title: عنوان طرف تجاری
        - business_party_role: نقش طرف تجاری
        - cost_center_dl_code: کد مرکز هزینه
        - cost_center_dl_title: عنوان مرکز هزینه
        - project_dl_code: کد پروژه
        - project_dl_title: عنوان پروژه
        - pricing_area_dl_code: کد حوزه قیمت گذاری
        - pricing_area_dl_title: عنوان حوزه قیمت گذاری
        - part_dl_code: کد کالا
        - part_dl_title: عنوان کالا
        - other_party_dl_code: کد سایر اشخاص
        - other_party_dl_title: عنوان سایر اشخاص
        - other_party_role: نقش سایر اشخاص
        - branch_dl_code: کد تفصیل شعبه
        - branch_dl_title: عنوان تفصیل شعبه
        - bank_account_dl_code: کد حساب بانکی
        - bank_account_dl_title: عنوان حساب بانکی
        - voucher_currency_title: ارز سند
        - currency_rate_type_title: نوع نرخ ارز
        - base_currency_title: ارز مبنا
        - voucher_item_explanation: شرح قلم سندحسابداری
        - follow_up_number: شماره پیگیری
    - **Relations**: None
    """