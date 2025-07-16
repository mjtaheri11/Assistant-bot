# LOGISTICS_BO = """
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "voucherspecification"
#             },
#             "title": "الگوی سند انبار",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد الگو",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان الگو",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_type",
#                     "title": "نوع سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "direction",
#                     "title": "جهت سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "purchase_type",
#                     "title": "نوع خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "type_of_effect",
#                     "title": "نوع تاثیر بر موجودی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "counter_part_type",
#                     "title": "نوع طرف مقابل",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "store"
#             },
#             "title": "انبار",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد انبار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان انبار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "storage_type_title",
#                     "title": "عنوان نوع انبار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "state",
#                     "title": "استان",
#                 }
#             ],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "plants"
#                     },
#                     "name": "plants",
#                     "title": "مرکز نگهداری",
#                     "foreignKey": {
#                         "local": {
#                             "name": "plant_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Plant ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "invvoucher"
#             },
#             "title": "سند انبار",
#             "parameters": [
#                 {
#                     "type": "DateType",
#                     "name": "logistics_invvoucher_p1",
#                     "title": "از تاریخ سند انبار",
#                     "dataview": null,
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "logistics_invvoucher_p2",
#                     "title": "تا تاریخ سند انبار",
#                     "dataview": null,
#                 }
#             ],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "number",
#                     "title": "شماره سند",
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "date",
#                     "title": "تاریخ سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "description",
#                     "title": "شرح سربرگ",
#                     "canOrder": false,
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_title",
#                     "title": "معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "state",
#                     "title": "وضعیت",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "fy_title",
#                     "title": "دوره مالی",
#                     "canOrder": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field1",
#                     "title": "فیلد اضافه 1",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field2",
#                     "title": "فیلد اضافه 2",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field3",
#                     "title": "فیلد اضافه 3",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field4",
#                     "title": "فیلد اضافه 4",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field5",
#                     "title": "فیلد اضافه 5",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "supplier_title",
#                     "title": "تامین کننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "contractor_title",
#                     "title": "پیمانکار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_title",
#                     "title": "مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_title",
#                     "title": "پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "customer_title",
#                     "title": "مشتری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "carrier_title",
#                     "title": "موسسه حمل",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "consignment_party_title",
#                     "title": "طرف حساب امانی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "employee_title",
#                     "title": "کارمند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_person_title",
#                     "title": "کارمند فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "purchase_order_no",
#                     "title": "شماره سفارش خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "purchase_invoice_no",
#                     "title": "شماره فاکتور خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "deliver_to",
#                     "title": "تحویل گیرنده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cottage_no",
#                     "title": "شماره کوتاژ",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "customs_green_sheet",
#                     "title": "شماره برگ سبز",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "asn_no",
#                     "title": "ASN NO",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_order_no",
#                     "title": "شماره سفارش فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_invoice_no",
#                     "title": "شماره فاکتور خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sale_organization",
#                     "title": "مرکز فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "shopping_store",
#                     "title": "فروشگاه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "delivery_person",
#                     "title": "تحویل دهنده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "weighbridge_no",
#                     "title": "شماره برگه باسکول",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_order_no",
#                     "title": "شماره دستور تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_plan_no",
#                     "title": "شماره سفارش تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_operation_no",
#                     "title": "شماره عملیات تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_shift",
#                     "title": "شیفت تولید",
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "production_date",
#                     "title": "تاریخ تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_inspection_no",
#                     "title": "شماره بازرسی کیفیت",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_check_list_no",
#                     "title": "شماره چک لیست",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_lab_no",
#                     "title": "شماره آزمایشگاه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "conditional_approval",
#                     "title": "تایید ارفاقی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "inspection_result",
#                     "title": "نتیجه بازرسی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "coa_no",
#                     "title": "شماره COA",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "transporter_name",
#                     "title": "نام راننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "vehicle_no",
#                     "title": "نام خودرو",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "license_plate_no",
#                     "title": "شماره پلاک",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "waybill_no",
#                     "title": "شماره بارنامه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "waybill_date",
#                     "title": "تاریخ بارنامه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "transporter_phone_no",
#                     "title": "تلفن راننده",
#                 }
#             ],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "voucherspecification"
#                     },
#                     "name": "ivs",
#                     "title": "الگوی سند انبار",
#                     "foreignKey": {
#                         "local": {
#                             "name": "voucher_specification_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "شناسه الگوی سند انبار"
#                         }
#                     },
#                     "dataview": null
#                 },
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "store"
#                     },
#                     "name": "store",
#                     "title": "انبار",
#                     "foreignKey": {
#                         "local": {
#                             "name": "store_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "شناسه انبار"
#                         }
#                     },
#                     "dataview": null
#                 },
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "store"
#                     },
#                     "name": "counterstore",
#                     "title": "انبار مقابل",
#                     "foreignKey": {
#                         "local": {
#                             "name": "counter_part_store_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Counterpart Store ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "partaccountcategory"
#             },
#             "title": "طبقه حساب کالا",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد طبقه حساب کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان طبقه حساب کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "pricing_method",
#                     "title": "روش قیمت گذاری",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "invvoucheritem"
#             },
#             "title": "قلم سند انبار",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "DecimalType",
#                     "name": "quantity",
#                     "title": "مقدار",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "major_quantity",
#                     "title": "مقدار به واحد اصلی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_unit_quantity",
#                     "title": "مقدار به واحد دوم",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remained_major_quantity",
#                     "title": "مانده استفاده نشده به واحد اصلی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remained_second_unit_quantity",
#                     "title": "مانده استفاده نشده به واحد دوم",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "row_number",
#                     "title": "شماره ردیف",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_title",
#                     "title": "معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field1",
#                     "title": "فیلد اضافه 1",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field2",
#                     "title": "فیلد اضافه 2",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field3",
#                     "title": "فیلد اضافه 3",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field4",
#                     "title": "فیلد اضافه 4",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "extra_field5",
#                     "title": "فیلد اضافه 5",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "supplier_title",
#                     "title": "تامین کننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "contractor_title",
#                     "title": "پیمانکار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_title",
#                     "title": "مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_title",
#                     "title": "پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "customer_title",
#                     "title": "مشتری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "carrier_title",
#                     "title": "موسسه حمل",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "consignment_party_title",
#                     "title": "طرف حساب امانی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "employee_title",
#                     "title": "کارمند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_person_title",
#                     "title": "کارمند فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "purchase_order_no",
#                     "title": "شماره سفارش خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "purchase_invoice_no",
#                     "title": "شماره فاکتور خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "deliver_to",
#                     "title": "تحویل گیرنده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cottage_no",
#                     "title": "شماره کوتاژ",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "customs_green_sheet",
#                     "title": "شماره برگ سبز",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "asn_no",
#                     "title": "ASN NO",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_order_no",
#                     "title": "شماره سفارش فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sales_invoice_no",
#                     "title": "شماره فاکتور خرید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sale_organization",
#                     "title": "مرکز فروش",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "shopping_store",
#                     "title": "فروشگاه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "delivery_person",
#                     "title": "تحویل دهنده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "weighbridge_no",
#                     "title": "شماره برگه باسکول",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_order_no",
#                     "title": "شماره دستور تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_plan_no",
#                     "title": "شماره سفارش تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_operation_no",
#                     "title": "شماره عملیات تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_shift",
#                     "title": "شیفت تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "production_date",
#                     "title": "تاریخ تولید",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_inspection_no",
#                     "title": "شماره بازرسی کیفیت",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_check_list_no",
#                     "title": "شماره چک لیست",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "qc_lab_no",
#                     "title": "شماره آزمایشگاه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "conditional_approval",
#                     "title": "تایید ارفاقی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "inspection_result",
#                     "title": "نتیجه بازرسی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "coa_no",
#                     "title": "شماره COA",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "transporter_name",
#                     "title": "نام راننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "vehicle_no",
#                     "title": "نام خودرو",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "license_plate_no",
#                     "title": "شماره پلاک",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "waybill_no",
#                     "title": "شماره بارنامه",
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "waybill_date",
#                     "title": "تاریخ بارنامه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "transporter_phone_no",
#                     "title": "تلفن راننده",
#                 }
#             ],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "invvoucher"
#                     },
#                     "name": "iv",
#                     "title": "سند انبار",
#                     "foreignKey": {
#                         "local": {
#                             "name": "inventory_voucher_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Inventory Voucher ID"
#                         }
#                     },
#                     "dataview": null
#                 },
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "parts"
#                     },
#                     "name": "part",
#                     "title": "کالا",
#                     "foreignKey": {
#                         "local": {
#                             "name": "part_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Part ID"
#                         }
#                     },
#                     "dataview": null
#                 },
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "units"
#                     },
#                     "name": "unit",
#                     "title": "واحد سنجش",
#                     "foreignKey": {
#                         "local": {
#                             "name": "unit_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Unit ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "invitemprice"
#             },
#             "title": "قلم قیمت",
#             "parameters": [
#                 {
#                     "type": "Int64Type",
#                     "name": "logistics_invitemprice_p1",
#                     "title": "حوزه قیمت‌گذاری",
#                     "dataview": {
#                         "name": "item-price-pricing-areas",
#                         "key": "id",
#                         "title": "حوزه قیمت‌گذاری",
#                         "columns": [
#                             {
#                                 "key": "code",
#                                 "title": "کد"
#                             },
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": false,
#                         "displayField": "title"
#                     },
#                 }
#             ],
#             "columns": [
#                 {
#                     "type": "DecimalType",
#                     "name": "fee",
#                     "title": "فی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "price",
#                     "title": "مبلغ",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "major_fee",
#                     "title": "فی به واحد اصلی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "major_price",
#                     "title": "مبلغ به واحد اصلی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "date",
#                     "title": "تاریخ",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "price_type",
#                     "title": "نوع قیمت",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "currency_title",
#                     "title": "عنوان ارز",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "acc_voucher_number",
#                     "title": "شماره سند حسابداری",
#                 }
#             ],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "invvoucheritem"
#                     },
#                     "name": "ivi",
#                     "title": "قلم سند انبار",
#                     "foreignKey": {
#                         "local": {
#                             "name": "inventory_voucher_item_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Voucher Item ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "plants"
#             },
#             "title": "مرکز نگهداری",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد مرکز نگهداری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان مرکز نگهداری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "branch_title",
#                     "title": "عنوان شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "state",
#                     "title": "استان",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "storagetype"
#             },
#             "title": "نوع انبار",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد نوع انبار",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان نوع انبار",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "partstoragetype"
#             },
#             "title": "نوع انبار کالا",
#             "parameters": [],
#             "columns": [],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "storagetype"
#                     },
#                     "name": "storagetype",
#                     "title": "نوع انبار",
#                     "foreignKey": {
#                         "local": {
#                             "name": "storage_type_id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "id",
#                             "title": "Storage Type ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "units"
#             },
#             "title": "واحد سنجش",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان واحد سنجش",
#                 },
#                 {
#                     "type": "Int64Type",
#                     "name": "dimension",
#                     "title": "بعد",
#                     "canGroup": false,
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "partaltunit"
#             },
#             "title": "واحد فرعی کالا",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان واحد فرعی کالا",
#                 },
#                 {
#                     "type": "Float64Type",
#                     "name": "coeff",
#                     "title": "ضریب",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "major_unit_title",
#                     "title": "واحد سنجش اصلی",
#                     "canGroup": false,
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "parts"
#             },
#             "title": "کالا",
#             "parameters": [],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "code",
#                     "title": "کد کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "title",
#                     "title": "عنوان کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "major_unit_title",
#                     "title": "واحد سنجش اصلی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "secondary_unit_title",
#                     "title": "واحد سنجش دوم",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_account_category_title",
#                     "title": "طبقه حساب کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_type",
#                     "title": "نوع کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_usage",
#                     "title": "نوع کارکرد کالا",
#                 }
#             ],
#             "relations": [
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "partaltunit"
#                     },
#                     "name": "altunit",
#                     "title": "واحد فرعی کالا",
#                     "foreignKey": {
#                         "local": {
#                             "name": "id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "part_id",
#                             "title": "Part ID"
#                         }
#                     },
#                     "dataview": null
#                 },
#                 {
#                     "businessObjectId": {
#                         "contextName": "logistics",
#                         "name": "partstoragetype"
#                     },
#                     "name": "storagetype",
#                     "title": "نوع انبار کالا",
#                     "foreignKey": {
#                         "local": {
#                             "name": "id",
#                             "title": "شناسه"
#                         },
#                         "referenced": {
#                             "name": "part_id",
#                             "title": "Storage Type ID"
#                         }
#                     },
#                     "dataview": null
#                 }
#             ],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "logistics",
#                 "name": "storeinventory"
#             },
#             "title": "گزارش مبلغی انبار ",
#             "parameters": [
#                 {
#                     "type": "Int64Type",
#                     "name": "logistics_storeinventory_p1",
#                     "title": "انبار ",
#                     "dataview": {
#                         "name": "store-inventory-amount-stores",
#                         "key": "id",
#                         "title": "انبار ",
#                         "columns": [
#                             {
#                                 "key": "code",
#                                 "title": "کد"
#                             },
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": false,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "logistics_storeinventory_p2",
#                     "title": "تا تاریخ",
#                     "dataview": null,
#                 }
#             ],
#             "columns": [
#                 {
#                     "type": "Int64Type",
#                     "name": "part_id",
#                     "title": "شناسه کالا",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_title",
#                     "title": "عنوان کالا",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_code",
#                     "title": "کد کالا",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "store_title",
#                     "title": "عنوان انبار",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "store_code",
#                     "title": "کد انبار",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "unit_title",
#                     "title": "واحد سنجش اصلی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "fee",
#                     "title": "فی",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "Int64Type",
#                     "name": "remaining",
#                     "title": "موجودی کالا",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "total_amount",
#                     "title": "موجودی مبلغی کالا",
#                     "canGroup": false,
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "last_pricing_date",
#                     "title": "تاریخ آخرین قیمت گذاری",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
# """

LOGISTICS_BO = """
    partaccountcategory:
    - Title: طبقه حساب کالا
    - Context: logistics
    - Attributes (all Str):
      - code: کد طبقه حساب کالا
      - title: عنوان طبقه حساب کالا
      - pricing_method: روش قیمت گذاری [ENUM: "میانگین", "شناسایی ویژه", "فایفو"]
    - Relations: None


    units:
    - Title: واحد سنجش
    - Context: logistics
    - Attributes:
      - Str: 
        - title: عنوان واحد سنجش
      - Int64: 
        - dimension: بعد
    - Relations: None


    storeinventory:
    - Title: گزارش مبلغی انبار
    - Context: logistics
    - Parameters:
      - logistics_storeinventory_p1 (Int64): انبار
      - logistics_storeinventory_p2 (Date): تا تاریخ
    - Attributes:
      - Int64:
        - part_id: شناسه کالا
        - remaining: موجودی کالا
      - Dec:
        - fee: فی
        - total_amount: موجودی مبلغی کالا
      - Date:
        - last_pricing_date: تاریخ آخرین قیمت گذاری
      - All other attributes are Str:
        - part_title: عنوان کالا
        - part_code: کد کالا
        - store_title: عنوان انبار
        - store_code: کد انبار
        - unit_title: واحد سنجش اصلی
    - Relations: None


    invitemprice:
    - Title: قلم قیمت
    - Context: logistics
    - Parameters:
      - logistics_invitemprice_p1 (Int64): حوزه قیمت‌گذاری
    - Attributes:
      - Decimal type:
        - fee: فی
        - price: مبلغ
        - major_fee: فی به واحد اصلی
        - major_price: مبلغ به واحد اصلی
      - Date Type:
        - date: تاریخ
      - All other attributes are Str
        - price_type: نوع قیمت [ENUM: "براوردی", "واقعی", "براوردی به واقعی", "اصلاح بها", "تعدیل"]
        - currency_title: عنوان ارز
        - acc_voucher_number: شماره سند حسابداری
    - Relations:
      - invvoucheritem: قلم سند انبار (foreign key inventory_voucher_item_id to invvoucheritem.id)


    plants:
    - Title: مرکز نگهداری
    - Context: logistics
    - Attributes (all Str):
      - code: کد مرکز نگهداری
      - title: عنوان مرکز نگهداری
      - branch_title: عنوان شعبه
      - state: وضعیت [ENUM: "فعال", "غیرفعال"]
    - Relations: None


    storagetype:
    - Title: نوع انبار
    - Context: logistics
    - Attributes (all Str):
      - code: کد نوع انبار
      - title: عنوان نوع انبار
    - Relations: None


    parts:
    - Title: کالا
    - Context: logistics
    - Attributes (all Str):
      - code: کد کالا
      - title: عنوان کالا
      - major_unit_title: واحد سنجش اصلی
      - secondary_unit_title: واحد سنجش دوم
      - part_account_category_title: طبقه حساب کالا
      - part_type: نوع کالا
      - part_usage: نوع کارکرد کالا (موجود، قابل فروش و ...)
    - Relations:
      - partaltunit: واحد فرعی کالا (foreign key id to partaltunit.part_id)
      - storagetype: نوع انبار کالا (foreign key id to partstoragetype.part_id)


    partstoragetype:
    - Title: نوع انبار کالا
    - Context: logistics
    - Attributes: None
    - Relations:
      - storagetype: نوع انبار (foreign key storage_type_id to storagetype.id)


    partaltunit:
    - Title: واحد فرعی کالا
    - Context: logistics
    - Attributes:
      - Str:
        - title: عنوان واحد فرعی کالا
        - major_unit_title: واحد سنجش اصلی
      - Float64: coeff: ضریب
    - Relations: None
    

    voucherspecification:
    - Title: الگوی سند انبار
    - Context: logistics
    - Attributes (all Str):
      - code: کد الگو
      - title: عنوان الگو
      - voucher_type: نوع سند (Examples: "مصرف", "تحویل دارایی ثابت", "انتقال بین انبار", "خرید", "ضایعات", "امانی ", ...)
      - direction: جهت سند [ENUM: "ورودی", "خروجی"]
      - purchase_type: نوع خرید [ENUM: "داخلی", "خارجی"]
      - type_of_effect: نوع تاثیر بر موجودی [ENUM: "ضایعات", "موقت", "دائم"]
      - counter_part_type: نوع طرف مقابل
    - Relations: None


    store:
    - Title: انبار
    - Context: logistics
    - Attributes (all Str):
      - code: کد انبار
      - title: عنوان انبار
      - storage_type_title: عنوان نوع انبار
      - state: وضعیت [ENUM: "غیر فعال", "فعال", "ثبت اولیه"]
    - Relations:
      - plants: مرکز نگهداری (foreign key plant_id to plants.id)

    
    invvoucheritem:
    - Title: قلم سند انبار
    - Context: logistics
    - Attributes:
      - Decimal type:
        - quantity: مقدار
        - major_quantity: مقدار به واحد اصلی
        - second_unit_quantity: مقدار به واحد دوم
        - remained_major_quantity: مانده استفاده نشده به واحد اصلی
        - remained_second_unit_quantity: مانده استفاده نشده به واحد دوم
      - Date Type:
        - waybill_date: تاریخ بارنامه
      - All other attributes are Str:
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
        - production_date: تاریخ تولید
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
    - Relations:
      - invvoucher: سند انبار (foreign key inventory_voucher_id to invvoucher.id)
      - parts: کالا (foreign key part_id to parts.id)
      - units: واحد سنجش (foreign key unit_id to units.id)


    invvoucher:
    - Title: سند انبار
    - Context: logistics
    - Parameters:
      - logistics_invvoucher_p1 (Date): از تاریخ سند انبار
      - logistics_invvoucher_p2 (Date): تا تاریخ سند انبار
    - Attributes:
      - Date Type:
        - date: تاریخ سند
        - production_date: تاریخ تولید
        - waybill_date: تاریخ بارنامه
      - All other attributes are Str:
        - number: شماره سند
        - description: شرح سربرگ
        - sl_title: معین
        - state: وضعیت [ENUM: 'ثبت شده', 'باطل شده', 'تایید شده']
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
    - Relations:
      - voucherspecification: الگوی سند انبار (foreign key voucher_specification_id to voucherspecification.id)
      - store: انبار (foreign key store_id to store.id)
    """


    # voucherssummary:
    # - Title: گردش و مانده حساب ها
    # - Context: financial
    # - Parameters:
    #   - financial_voucherssummary_p1 (Int64): دفتر
    #   - financial_voucherssummary_p3 (Int64Array): نوع سند
    #   - financial_voucherssummary_p4 (Int64Array): وضعیت سند
    #   - financial_voucherssummary_p5 (Date): تاریخ شروع
    #   - financial_voucherssummary_p6 (Date): تاریخ پایان
    #   - financial_voucherssummary_p7 (Int64Array): نوع حساب
    #   - financial_voucherssummary_p8 (Bool): وضعیت معین
    # - Attributes:1
    #   - Dec Type:
    #     - debit: گردش بدهکار ارز عملیاتی
    #     - credit: گردش بستانکار ارز عملیاتی
    #     - currency_debit: گردش بدهکار ارز سند
    #     - currency_credit: گردش بستانکار ارز سند
    #     - remaining_currency_debit: مانده بدهکار ارز سند
    #     - remaining_currency_credit: مانده بستانکار ارز سند
    #     - remaining_currency: مانده ارز سند
    #     - base_currency_debit: گردش بدهکار ارز مبنا
    #     - base_currency_credit: گردش بستانکار ارز مبنا
    #     - remaining_base_currency_debit: مانده بدهکار ارز مبنا
    #     - remaining_base_currency_credit: مانده بستانکار ارز مبنا
    #     - remaining_base_currency: مانده ارز مبنا
    #     - first_reporting_currency_debit: گردش بدهکار ارز گزارشگری اول
    #     - first_reporting_currency_credit: گردش بستانکار ارز گزارشگری اول
    #     - remaining_first_reporting_currency_debit: مانده بدهکار ارز گزارشگری اول
    #     - remaining_first_reporting_currency_credit: مانده بستانکار ارز گزارشگری اول
    #     - remaining_first_reporting_currency: مانده ارز گزارشگری اول
    #     - second_reporting_currency_debit: گردش بدهکار ارز گزارشگری دوم
    #     - second_reporting_currency_credit: گردش بستانکار ارز گزارشگری دوم
    #     - remaining_second_reporting_currency_debit: مانده بدهکار ارز گزارشگری دوم
    #     - remaining_second_reporting_currency_credit: مانده بستانکار ارز گزارشگری دوم
    #     - remaining_second_reporting_currency: مانده ارز گزارشگری دوم
    #     - quantity_credit: گردش بستانکار مقدار
    #     - quantity_remaining: مانده مقدار
    #   - All other attributes are Str:
    #     - header_branch_code: کد شعبه
    #     - header_branch_title: عنوان شعبه
    #     - account_group_code: کد گروه حساب
    #     - account_group_title: عنوان گروه حساب
    #     - gl_code: کد حساب کل
    #     - gl_title: عنوان حساب کل
    #     - sl_code: کد حساب معین
    #     - sl_title: عنوان حساب معین
    #     - business_party_dl_code: کد طرف تجاری
    #     - business_party_dl_title: عنوان طرف تجاری
    #     - business_party_role: نقش طرف تجاری
    #     - cost_center_dl_code: کد مرکز هزینه
    #     - cost_center_dl_title: عنوان مرکز هزینه
    #     - project_dl_code: کد پروژه
    #     - project_dl_title: عنوان پروژه
    #     - pricing_area_dl_code: کد حوزه قیمت گذاری
    #     - pricing_area_dl_title: عنوان حوزه قیمت گذاری
    #     - part_dl_code: کد کالا
    #     - part_dl_title: عنوان کالا
    #     - other_party_dl_code: کد سایر اشخاص
    #     - other_party_dl_title: عنوان سایر اشخاص
    #     - other_party_role: نقش سایر اشخاص
    #     - branch_dl_code: کد تفصیل شعبه
    #     - branch_dl_title: عنوان تفصیل شعبه
    #     - bank_account_dl_code: کد حساب بانکی
    #     - bank_account_dl_title: عنوان حساب بانکی
    #     - voucher_currency_title: ارز سند
    #     - currency_rate_type_title: نوع نرخ ارز
    #     - quantity_debit: گردش بدهکار مقدار
    # - Relations: None
    
FINANCIAL_BO = """
    vouchers:
    - Title: اقلام سند حسابداری
    - Context: financial
    - Parameters:
      - financial_vouchers_p1 (Int64): دفتر
      - financial_vouchers_p3 (Date): تاریخ شروع
      - financial_vouchers_p4 (Date): تاریخ پایان
    - Attributes:
      - Date Type:
        - voucher_date: تاریخ سند
        - follow_up_date: تاریخ پیگیری
      - Dec Type:
        - debit: گردش بدهکار ارز عملیاتی
        - credit: گردش بستانکار ارز عملیاتی
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
      - All other attributes are Str:
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
        - row_number: شماره ردیف
        - sl_code: کد حساب معین
        - sl_title: عنوان حساب معین
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
    - Relations: None
    """

# FINANCIAL_BO = """        
#         {
#             "id": {
#                 "contextName": "financial",
#                 "name": "voucherssummary"
#             },
#             "title": "گردش و مانده حساب ها",
#             "parameters": [
#                 {
#                     "type": "Int64Type",
#                     "name": "financial_voucherssummary_p1",
#                     "title": "دفتر",
#                     "dataview": {
#                         "name": "all-voucher-summery-all-ledgers",
#                         "key": "id",
#                         "title": "",
#                         "columns": [
#                             {
#                                 "key": "code",
#                                 "title": "کد"
#                             },
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": false,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "Int64ArrayType",
#                     "name": "financial_voucherssummary_p3",
#                     "title": "نوع سند",
#                     "dataview": {
#                         "name": "all-voucher-summery-all-voucher-types",
#                         "key": "id",
#                         "title": "",
#                         "columns": [
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": true,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "Int64ArrayType",
#                     "name": "financial_voucherssummary_p4",
#                     "title": "وضعیت سند",
#                     "dataview": {
#                         "name": "all-voucher-summery-all-voucher-state",
#                         "key": "id",
#                         "title": "",
#                         "columns": [
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": true,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "financial_voucherssummary_p5",
#                     "title": "تاریخ شروع",
#                     "dataview": null,
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "financial_voucherssummary_p6",
#                     "title": "تاریخ پایان",
#                     "dataview": null,
#                 },
#                 {
#                     "type": "Int64ArrayType",
#                     "name": "financial_voucherssummary_p7",
#                     "title": "نوع حساب",
#                     "dataview": {
#                         "name": "all-voucher-summery-all-account-type",
#                         "key": "id",
#                         "title": "",
#                         "columns": [
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": true,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "BoolType",
#                     "name": "financial_voucherssummary_p8",
#                     "title": "وضعیت معین",
#                     "dataview": null,
#                 }
#             ],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "header_branch_code",
#                     "title": "کد شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "header_branch_title",
#                     "title": "عنوان شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "account_group_code",
#                     "title": "کد گروه حساب",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "account_group_title",
#                     "title": "عنوان گروه حساب",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "gl_code",
#                     "title": "کد حساب کل",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "gl_title",
#                     "title": "عنوان حساب کل",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_code",
#                     "title": "کد حساب معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_title",
#                     "title": "عنوان حساب معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_dl_code",
#                     "title": "کد طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_dl_title",
#                     "title": "عنوان طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_role",
#                     "title": "نقش طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_dl_code",
#                     "title": "کد مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_dl_title",
#                     "title": "عنوان مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_dl_code",
#                     "title": "کد پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_dl_title",
#                     "title": "عنوان پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "pricing_area_dl_code",
#                     "title": "کد حوزه قیمت گذاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "pricing_area_dl_title",
#                     "title": "عنوان حوزه قیمت گذاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_dl_code",
#                     "title": "کد کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_dl_title",
#                     "title": "عنوان کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_dl_code",
#                     "title": "کد سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_dl_title",
#                     "title": "عنوان سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_role",
#                     "title": "نقش سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "branch_dl_code",
#                     "title": "کد تفصیل شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "branch_dl_title",
#                     "title": "عنوان تفصیل شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "bank_account_dl_code",
#                     "title": "کد حساب بانکی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "bank_account_dl_title",
#                     "title": "عنوان حساب بانکی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_currency_title",
#                     "title": "ارز سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "base_currency_title",
#                     "title": "ارز مبنا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "currency_rate_type_title",
#                     "title": "نوع نرخ ارز",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "debit",
#                     "title": " گردش بدهکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "credit",
#                     "title": "گردش بستانکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_debit",
#                     "title": "مانده بدهکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_credit",
#                     "title": "مانده بستانکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining",
#                     "title": "مانده ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "currency_debit",
#                     "title": "گردش بدهکار ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "currency_credit",
#                     "title": "گردش بستانکار ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_currency_debit",
#                     "title": "مانده بدهکار ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_currency_credit",
#                     "title": "مانده بستانکار ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_currency",
#                     "title": "مانده ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "base_currency_debit",
#                     "title": "گردش بدهکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "base_currency_credit",
#                     "title": "گردش بستانکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_base_currency_debit",
#                     "title": "مانده بدهکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_base_currency_credit",
#                     "title": "مانده بستانکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_base_currency",
#                     "title": "مانده ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "first_reporting_currency_debit",
#                     "title": "گردش بدهکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "first_reporting_currency_credit",
#                     "title": "گردش بستانکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_first_reporting_currency_debit",
#                     "title": "مانده بدهکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_first_reporting_currency_credit",
#                     "title": "مانده بستانکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_first_reporting_currency",
#                     "title": "مانده ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_reporting_currency_debit",
#                     "title": "گردش بدهکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_reporting_currency_credit",
#                     "title": "گردش بستانکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_second_reporting_currency_debit",
#                     "title": "مانده بدهکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_second_reporting_currency_credit",
#                     "title": "مانده بستانکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "remaining_second_reporting_currency",
#                     "title": "مانده ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "quantity_debit",
#                     "title": "گردش بدهکار مقدار",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "quantity_credit",
#                     "title": "گردش بستانکار مقدار",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "quantity_remaining",
#                     "title": "مانده مقدار",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
#         {
#             "id": {
#                 "contextName": "financial",
#                 "name": "vouchers"
#             },
#             "title": "اقلام سند حسابداری",
#             "parameters": [
#                 {
#                     "type": "Int64Type",
#                     "name": "financial_vouchers_p1",
#                     "title": "دفتر",
#                     "dataview": {
#                         "name": "all-voucher-items-all-ledgers",
#                         "key": "id",
#                         "title": "",
#                         "columns": [
#                             {
#                                 "key": "code",
#                                 "title": "کد"
#                             },
#                             {
#                                 "key": "title",
#                                 "title": "عنوان"
#                             }
#                         ],
#                         "isMultiselect": false,
#                         "displayField": "title"
#                     },
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "financial_vouchers_p3",
#                     "title": "تاریخ شروع",
#                     "dataview": null,
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "financial_vouchers_p4",
#                     "title": "تاریخ پایان",
#                     "dataview": null,
#                 }
#             ],
#             "columns": [
#                 {
#                     "type": "StringType",
#                     "name": "header_branch_code",
#                     "title": "کد شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "header_branch_title",
#                     "title": "عنوان شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_number",
#                     "title": "شماره سند",
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "voucher_date",
#                     "title": "تاریخ سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sequence_number",
#                     "title": "شماره عطف",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "daily_number",
#                     "title": "شماره روزانه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "auxiliary_number",
#                     "title": "شماره فرعی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_type_title",
#                     "title": "نوع سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_state",
#                     "title": "وضعیت سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_explanation",
#                     "title": "شرح سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "creator_name",
#                     "title": "صادر کننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "reviewer_name",
#                     "title": "بررسی کننده",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "row_number",
#                     "title": "شماره ردیف",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_code",
#                     "title": "کد حساب معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "sl_title",
#                     "title": "عنوان حساب معین",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_dl_code",
#                     "title": "کد طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_dl_title",
#                     "title": "عنوان طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "business_party_role",
#                     "title": "نقش طرف تجاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_dl_code",
#                     "title": "کد مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "cost_center_dl_title",
#                     "title": "عنوان مرکز هزینه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_dl_code",
#                     "title": "کد پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "project_dl_title",
#                     "title": "عنوان پروژه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "pricing_area_dl_code",
#                     "title": "کد حوزه قیمت گذاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "pricing_area_dl_title",
#                     "title": "عنوان حوزه قیمت گذاری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_dl_code",
#                     "title": "کد کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "part_dl_title",
#                     "title": "عنوان کالا",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_dl_code",
#                     "title": "کد سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_dl_title",
#                     "title": "عنوان سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "other_party_role",
#                     "title": "نقش سایر اشخاص",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "branch_dl_code",
#                     "title": "کد تفصیل شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "branch_dl_title",
#                     "title": "عنوان تفصیل شعبه",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "bank_account_dl_code",
#                     "title": "کد حساب بانکی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "bank_account_dl_title",
#                     "title": "عنوان حساب بانکی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "debit",
#                     "title": " گردش بدهکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "credit",
#                     "title": "گردش بستانکار ارز عملیاتی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_currency_title",
#                     "title": "ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "currency_debit",
#                     "title": "گردش بدهکار ارز سند",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "currency_credit",
#                     "title": "گردش بستانکار ارز سند",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "currency_rate_type_title",
#                     "title": "نوع نرخ ارز",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "functional_currency_exchange_rate",
#                     "title": "نرخ تبدیل ارز عملیاتی",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "base_currency_title",
#                     "title": "ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "base_currency_debit",
#                     "title": "گردش بدهکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "base_currency_credit",
#                     "title": "گردش بستانکار ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "base_currency_exchange_rate",
#                     "title": "نرخ تبدیل ارز مبنا",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "first_reporting_currency_debit",
#                     "title": "گردش بدهکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "first_reporting_currency_credit",
#                     "title": "گردش بستانکار ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "first_reporting_currency_exchange_rate",
#                     "title": "نرخ تبدیل ارز گزارشگری اول",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_reporting_currency_debit",
#                     "title": "گردش بدهکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_reporting_currency_credit",
#                     "title": "گردش بستانکار ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "second_reporting_currency_exchange_rate",
#                     "title": "نرخ تبدیل ارز گزارشگری دوم",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "voucher_item_explanation",
#                     "title": "شرح قلم سندحسابداری",
#                 },
#                 {
#                     "type": "StringType",
#                     "name": "follow_up_number",
#                     "title": "شماره پیگیری",
#                 },
#                 {
#                     "type": "DateType",
#                     "name": "follow_up_date",
#                     "title": "تاریخ پیگیری",
#                 },
#                 {
#                     "type": "DecimalType",
#                     "name": "quantity",
#                     "title": "مقدار",
#                 }
#             ],
#             "relations": [],
#             "enums": []
#         },
        
# """

INVOICE_BO_ORIGINAL = """
[
    {
        "id": {
            "contextName": "sales",
            "name": "invoice"
        },
        "title": "فاکتور",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "afy_title",
                "title": "سال مالی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "number_c",
                "title": "شماره فاکتور",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DateType",
                "name": "date_c",
                "title": "تاریخ فاکتور",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "description_c",
                "title": "توضیحات",
                "canSelect": true,
                "canFilter": true,
                "canOrder": false,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "cu_code",
                "title": "کد مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cu_full_name",
                "title": "نام و نام خانوادگی مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sa_title",
                "title": "حوزه فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "so_title",
                "title": "دفتر فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sm_title",
                "title": "روش تسویه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "pay_full_name",
                "title": "نام و نام خانوادگی پرداخت کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "invoice_state",
                "title": "وضعیت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "payer_code",
                "title": "کد پرداخت کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "rec_full_name",
                "title": "نام و نام خانوادگی تحویل گیرنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "receiver_code",
                "title": "کد تحویل گیرنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cur_title",
                "title": "ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "functional_currency_rate",
                "title": "نرخ ارز عملیاتی",
                "canSelect": true,
                "canFilter": false,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_rate",
                "title": "نرخ ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": false,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_rate",
                "title": "نرخ ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": false,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "total_price",
                "title": "مبلغ ناخالص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "net_price",
                "title": "مبلغ خالص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "deductions",
                "title": "جمع تخفیف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "surcharges",
                "title": "جمع عوامل افزاینده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "tax_total",
                "title": "جمع مالیات",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_total_price",
                "title": "مبلغ ناخالص به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_net_price",
                "title": "مبلغ خالص به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_deductions",
                "title": "جمع تخفیف به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_surcharges",
                "title": "جمع عوامل افزاینده به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_tax_total",
                "title": "جمع مالیات به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_total_price",
                "title": "جمع مبلغ ناخالص به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_net_price",
                "title": "مبلغ خالص به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_deductions",
                "title": "جمع تخفیف به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_surcharges",
                "title": "جمع عوامل افزاینده به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_tax_total",
                "title": "جمع مالیات به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_total_price",
                "title": "جمع مبلغ ناخالص به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_net_price",
                "title": "مبلغ خالص به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_deductions",
                "title": "جمع تخفیف به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_surcharges",
                "title": "جمع عوامل افزاینده به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_tax_total",
                "title": "جمع مالیات به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "invoicecustomergroup"
                },
                "title": "گروه مشتری",
                "name": "invoicecustomergroups",
                "foreignKey": {
                    "local": {
                        "name": "customer_id",
                        "title": "customer id"
                    },
                    "referenced": {
                        "name": "customer_id",
                        "title": "customer id"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "sales",
            "name": "invoiceitem"
        },
        "title": "قلم فاکتور",
        "parameters": [
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "invoice-companies-all-explorer",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "unit_title",
                "title": "واحد سنجش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "amount",
                "title": "مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": false,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "description_c",
                "title": "توضیحات",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "store_title",
                "title": "انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "total_price",
                "title": "مبلغ ناخالص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "net_price",
                "title": "مبلغ خالص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "deduction_price",
                "title": "جمع تخفیف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "surcharges",
                "title": "جمع عوامل افزاینده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "tax_total",
                "title": "مالیات بر ارزش افزوده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_total_price",
                "title": "مبلغ ناخالص به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_net_price",
                "title": "مبلغ خالص به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_deduction_price",
                "title": "جمع تخفیف به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_surcharges",
                "title": "جمع عوامل افزاینده به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "functional_tax_total",
                "title": "جمع مالیات به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_total_price",
                "title": "جمع مبلغ ناخالص به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_net_price",
                "title": "مبلغ خالص به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_deduction_price",
                "title": "جمع تخفیف به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_surcharges",
                "title": "جمع عوامل افزاینده به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_tax_total",
                "title": "جمع مالیات به ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_total_price",
                "title": "جمع مبلغ ناخالص به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_net_price",
                "title": "مبلغ خالص به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_deduction_price",
                "title": "جمع تخفیف به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_surcharges",
                "title": "جمع عوامل افزاینده به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_tax_total",
                "title": "جمع مالیات به ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "product"
                },
                "title": "کالا/خدمت",
                "name": "invoiceproducts",
                "foreignKey": {
                    "local": {
                        "name": "gnr_product_id",
                        "title": "product id"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "product id"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "productgroup"
                },
                "title": "گروه کالا/خدمت",
                "name": "invoiceproductgroup",
                "foreignKey": {
                    "local": {
                        "name": "gnr_product_id",
                        "title": "product id"
                    },
                    "referenced": {
                        "name": "product_id",
                        "title": "product id"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "invvoucheritem"
                },
                "title": "قلم سند انبار",
                "name": "invinvvchr",
                "foreignKey": {
                    "local": {
                        "name": "voucher_item_id",
                        "title": "invoice item id"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "sales invoice item id"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "invoice"
                },
                "title": "فاکتور",
                "name": "invitemrel",
                "foreignKey": {
                    "local": {
                        "name": "invoice_id",
                        "title": "invoice item invoice id"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "invoice id"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "sales",
            "name": "productgroup"
        },
        "title": "گروه بندی کالا/خدمت",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد گروه کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "group_title",
                "title": "عنوان گروه کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "grouping_title",
                "title": "عنوان گروهبندی کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "invoicecustomergroup"
        },
        "title": "اعضای گروه بندی مشتری",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "group_title",
                "title": "عنوان گروه مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "code",
                "title": "کد گروه مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان گروه بندی مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "product"
        },
        "title": "کالا/خدمت",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "major_unit_title",
                "title": "واحد سنجش اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "secondary_unit_title",
                "title": "واحد سنجش دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    }
]
"""


RETURNINVOICE_BO_ORIGINAL = """
[
  {
    "id": {
      "contextName": "sales",
      "name": "returninvoice"
    },
    "title": "فاکتور برگشتی",
    "parameters": [],
    "columns": [
      {
        "type": "StringType",
        "name": "afy_title",
        "title": "سال مالی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "cmp_title",
        "title": "شرکت",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "number_c",
        "title": "شماره فاکتور برگشتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "invoice_state",
        "title": "وضعیت",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DateType",
        "name": "date_c",
        "title": "تاریخ فاکتور برگشتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "description_c",
        "title": "توضیحات",
        "canSelect": true,
        "canFilter": true,
        "canOrder": false,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "cu_code",
        "title": "کد مشتری",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "cu_full_name",
        "title": "نام و نام خانوادگی مشتری",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "sa_title",
        "title": "حوزه فروش",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "so_title",
        "title": "دفتر فروش",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "cur_title",
        "title": "ارز",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_currency_rate",
        "title": "نرخ ارز عملیاتی",
        "canSelect": true,
        "canFilter": false,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_currency_rate",
        "title": "نرخ ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": false,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_currency_rate",
        "title": "نرخ ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": false,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "total_price",
        "title": "مبلغ ناخالص",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "net_price",
        "title": "مبلغ خالص",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "deductions",
        "title": "جمع تخفیف",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "surcharges",
        "title": "جمع عوامل افزاینده",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "tax_total",
        "title": "جمع مالیات",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_total_price",
        "title": "مبلغ ناخالص به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_net_price",
        "title": "مبلغ خالص به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_deductions",
        "title": "جمع تخفیف به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_surcharges",
        "title": "جمع عوامل افزاینده به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_tax_total",
        "title": "جمع مالیات به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_total_price",
        "title": "جمع مبلغ ناخالص به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_net_price",
        "title": "مبلغ خالص به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_deductions",
        "title": "جمع تخفیف به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_surcharges",
        "title": "جمع عوامل افزاینده به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_tax_total",
        "title": "جمع مالیات به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_total_price",
        "title": "جمع مبلغ ناخالص به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_net_price",
        "title": "مبلغ خالص به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_deductions",
        "title": "جمع تخفیف به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_surcharges",
        "title": "جمع عوامل افزاینده به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_tax_total",
        "title": "جمع مالیات به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      }
    ],
    "relations": [
      {
        "businessObjectId": {
          "contextName": "sales",
          "name": "invoicecustomergroup"
        },
        "title": "گروه مشتری",
        "name": "rinvcgroups",
        "foreignKey": {
          "local": {
            "name": "customer_id",
            "title": "customer id"
          },
          "referenced": {
            "name": "customer_id",
            "title": "customer id"
          }
        }
      }
    ],
    "enums": []
  },
  {
    "id": {
      "contextName": "sales",
      "name": "rinvoiceitem"
    },
    "title": "قلم فاکتور برگشتی",
    "parameters": [
      {
        "name": "p3",
        "type": "Int64ArrayType",
        "title": "شرکت",
        "dataview": {
          "name": "return-invoice-companies-all-explorer",
          "title": "شرکت",
          "valueMember": "id",
          "displayField": "title",
          "isMultiselect": true,
          "columns": [
            {
              "key": "title",
              "title": "شرکت"
            }
          ]
        }
      }
    ],
    "columns": [
      {
        "type": "StringType",
        "name": "cmp_title",
        "title": "شرکت",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "base_type_invoice",
        "title": "نوع مبنا",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "base_invoice_number",
        "title": "شماره سند مبنا",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "unit_title",
        "title": "واحد سنجش",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "amount",
        "title": "مقدار",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "fee",
        "title": "فی",
        "canSelect": true,
        "canFilter": false,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "description_c",
        "title": "توضیحات",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "StringType",
        "name": "store_title",
        "title": "انبار",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": true,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "total_price",
        "title": "مبلغ ناخالص",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "net_price",
        "title": "مبلغ خالص",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "deduction_price",
        "title": "جمع تخفیف",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "surcharges",
        "title": "جمع عوامل افزاینده",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "tax_total",
        "title": "مالیات بر ارزش افزوده",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_total_price",
        "title": "مبلغ ناخالص به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_net_price",
        "title": "مبلغ خالص به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_deduction_price",
        "title": "جمع تخفیف به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_surcharges",
        "title": "جمع عوامل افزاینده به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "functional_tax_total",
        "title": "جمع مالیات به ارز عملیاتی",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_total_price",
        "title": "جمع مبلغ ناخالص به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_net_price",
        "title": "مبلغ خالص به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_deduction_price",
        "title": "جمع تخفیف به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_surcharges",
        "title": "جمع عوامل افزاینده به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "first_reporting_tax_total",
        "title": "جمع مالیات به ارز گزارشگری اول",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_total_price",
        "title": "جمع مبلغ ناخالص به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_net_price",
        "title": "مبلغ خالص به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_deduction_price",
        "title": "جمع تخفیف به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_surcharges",
        "title": "جمع عوامل افزاینده به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      },
      {
        "type": "DecimalType",
        "name": "second_reporting_tax_total",
        "title": "جمع مالیات به ارز گزارشگری دوم",
        "canSelect": true,
        "canFilter": true,
        "canOrder": true,
        "canGroup": false,
        "enumId": ""
      }
    ],
    "relations": [
      {
        "businessObjectId": {
          "contextName": "sales",
          "name": "product"
        },
        "title": "کالا/خدمت",
        "name": "prdrinv",
        "foreignKey": {
          "local": {
            "name": "gnr_product_id",
            "title": "product id"
          },
          "referenced": {
            "name": "id",
            "title": "product id"
          }
        }
      },
      {
        "businessObjectId": {
          "contextName": "sales",
          "name": "productgroup"
        },
        "title": "گروه کالا/خدمت",
        "name": "pgrouprinv",
        "foreignKey": {
          "local": {
            "name": "gnr_product_id",
            "title": "product id"
          },
          "referenced": {
            "name": "product_id",
            "title": "product id"
          }
        }
      },
      {
        "businessObjectId": {
          "contextName": "logistics",
          "name": "invvoucheritem"
        },
        "title": "قلم سند انبار",
        "name": "rinvinvvchr",
        "foreignKey": {
          "local": {
            "name": "voucher_item_id",
            "title": "return invoice item id"
          },
          "referenced": {
            "name": "id",
            "title": "sales invoice item id"
          }
        }
      },
      {
        "businessObjectId": {
          "contextName": "sales",
          "name": "invoiceitem"
        },
        "title": "قلم فاکتور مبنا",
        "name": "rinvitembase",
        "foreignKey": {
          "local": {
            "name": "base_item_id",
            "title": "base item id"
          },
          "referenced": {
            "name": "id",
            "title": "invoice item id"
          }
        }
      },
      {
        "businessObjectId": {
          "contextName": "sales",
          "name": "returninvoice"
        },
        "title": "فاکتور برگشتی",
        "name": "rinvitemrel",
        "foreignKey": {
          "local": {
            "name": "return_invoice_id",
            "title": "return invoice item invoice id"
          },
          "referenced": {
            "name": "id",
            "title": "return invoice id"
          }
        }
      }
    ],
    "enums": []
  }
]
"""


PRICELIST_BO_ORIGINAL_2 = """
[
    {
        "id": {
            "contextName": "sales",
            "name": "pricelistitem"
        },
        "title": "قلم لیست قیمت",
        "parameters": [
            {
                "name": "p3",
                "type": "Int64Array",
                "title": "شرکت",
                "dataview": {
                    "name": "price-list-companies-all-explorer",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            },
            {
                "name": "p4",
                "type": "Int64Array",
                "title": "ارز",
                "dataview": {
                    "name": "price-list-currencies-all-explorer",
                    "title": "ارز",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "ارز"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "Decimal",
                "name": "plip_fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": false,
                "canOrder": false,
                "canGroup": false
            },
            {
                "type": "Date",
                "name": "plip_validity_start_date",
                "title": "تاریخ شروع اعتبار بازه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Date",
                "name": "plip_validity_end_date",
                "title": "تاریخ پایان اعتبار بازه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "pli_is_price_changeable",
                "title": "امکان تغییر در اسناد",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Int64",
                "name": "pli_max_decrease_fee_percent",
                "title": "حداکثر درصد کاهش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Int64",
                "name": "pli_max_increase_fee_percent",
                "title": "حداکثر درصد افزایش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "product_title",
                "title": "عنوان کالا/خدمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "unit_title",
                "title": "عنوان واحد سنجش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "pricelistheader"
                },
                "title": "لیست قیمت",
                "name": "pricelists",
                "foreignKey": {
                    "local": {
                        "name": "pl_id",
                        "title": "PriceListID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "PriceList ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "plparameters"
                },
                "title": "پارامتر های لیست قیمت",
                "name": "parameterrel",
                "foreignKey": {
                    "local": {
                        "name": "pl_id",
                        "title": "PriceListID"
                    },
                    "referenced": {
                        "name": "pl_id",
                        "title": "PriceList ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "sales",
            "name": "channel"
        },
        "title": "کانال فروش",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان کانال فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد کانال فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "salesarea"
        },
        "title": "حوزه فروش",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان حوزه فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد حوزه فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "division"
        },
        "title": "بخش فروش",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان بخش فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد بخش فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "organization"
        },
        "title": "سازمان فروش",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان سازمان فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد سازمان فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "settlementmethod"
        },
        "title": "روش تسویه",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان روش تسویه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "customergroup"
        },
        "title": "گروه بندی مشتری",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان گروه مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد گروه مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "grouping_title",
                "title": "عنوان گروه بندی مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "pricelistheader"
        },
        "title": "لیست قیمت",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان لیست قیمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "currency_title",
                "title": "عنوان ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Date",
                "name": "pl_validity_start_date",
                "title": "تاریخ شروع اعتبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Date",
                "name": "pl_validity_end_date",
                "title": "تاریخ پایان اعتبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "state",
                "title": "وضعیت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "office"
        },
        "title": "دفتر فروش",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "title",
                "title": "عنوان دفتر فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "code",
                "title": "کد دفتر فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "sales",
            "name": "plparameters"
        },
        "title": "پارامتر های لیست قیمت",
        "parameters": [],
        "columns": [
            {
                "type": "String",
                "name": "cmp_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "office"
                },
                "title": "دفتر فروش",
                "name": "office",
                "foreignKey": {
                    "local": {
                        "name": "sales_office_id",
                        "title": "OFFICE ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Office ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "customergroup"
                },
                "title": "گروه مشتری",
                "name": "customergroup",
                "foreignKey": {
                    "local": {
                        "name": "customer_group_id",
                        "title": "Customer Group ID"
                    },
                    "referenced": {
                        "name": "customer_group_id",
                        "title": "Group ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "settlementmethod"
                },
                "title": "روش تسویه",
                "name": "settlementmethod",
                "foreignKey": {
                    "local": {
                        "name": "settlement_method_id",
                        "title": "Settlement Method ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Settlement Method ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "organization"
                },
                "title": "سازمان فروش",
                "name": "organization",
                "foreignKey": {
                    "local": {
                        "name": "sales_organization_id",
                        "title": "Organization ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Organization ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "division"
                },
                "title": "بخش فروش",
                "name": "division",
                "foreignKey": {
                    "local": {
                        "name": "sales_division_id",
                        "title": "Division ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Division ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "salesarea"
                },
                "title": "حوزه فروش",
                "name": "salesarea",
                "foreignKey": {
                    "local": {
                        "name": "sales_area_id",
                        "title": "Sales Area ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Sales Area ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "sales",
                    "name": "channel"
                },
                "title": "کانال فروش",
                "name": "channel",
                "foreignKey": {
                    "local": {
                        "name": "sales_channel_id",
                        "title": "Sales Channel ID"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Sales Channel ID"
                    }
                }
            }
        ]
    }
]
"""


LOGISTICS_BO_ORIGINAL = """
[
    {
        "id": {
            "contextName": "logistics",
            "name": "partaltunit"
        },
        "title": "واحد فرعی کالا",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان واحد فرعی کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Float64Type",
                "name": "coeff",
                "title": "ضریب",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "major_unit_title",
                "title": "واحد سنجش اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "units"
        },
        "title": "واحد سنجش",
        "parameters": [],
        "columns": [
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان واحد سنجش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "Int64Type",
                "name": "dimension",
                "title": "بعد",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "store"
        },
        "title": "انبار",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "stores-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "storage_type_title",
                "title": "عنوان نوع انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "state",
                "title": "استان",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "plants"
                },
                "title": "مرکز نگهداری",
                "name": "plants",
                "foreignKey": {
                    "local": {
                        "name": "plant_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Plant ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "partaccountcategory"
        },
        "title": "طبقه حساب کالا",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "categories-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد طبقه حساب کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان طبقه حساب کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "pricing_method",
                "title": "روش قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "plants"
        },
        "title": "مرکز نگهداری",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "plants-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد مرکز نگهداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان مرکز نگهداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "branch_title",
                "title": "عنوان شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "state",
                "title": "استان",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "invvoucher"
        },
        "title": "سند انبار",
        "parameters": [
            {
                "name": "p1",
                "title": "از تاریخ سند انبار",
                "type": "DateType"
            },
            {
                "name": "p2",
                "title": "تا تاریخ سند انبار",
                "type": "DateType"
            },
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "vouchers-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "number",
                "title": "شماره سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DateType",
                "name": "date",
                "title": "تاریخ سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "description",
                "title": "شرح سربرگ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": false,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "sl_title",
                "title": "معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "state",
                "title": "وضعیت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "fy_title",
                "title": "دوره مالی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": false,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "extra_field1",
                "title": "فیلد اضافه 1",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field2",
                "title": "فیلد اضافه 2",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field3",
                "title": "فیلد اضافه 3",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field4",
                "title": "فیلد اضافه 4",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field5",
                "title": "فیلد اضافه 5",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "supplier_title",
                "title": "تامین کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "contractor_title",
                "title": "پیمانکار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cost_center_title",
                "title": "مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "project_title",
                "title": "پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "customer_title",
                "title": "مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "carrier_title",
                "title": "موسسه حمل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "consignment_party_title",
                "title": "طرف حساب امانی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "employee_title",
                "title": "کارمند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_person_title",
                "title": "کارمند فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "purchase_order_no",
                "title": "شماره سفارش خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "purchase_invoice_no",
                "title": "شماره فاکتور خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "deliver_to",
                "title": "تحویل گیرنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cottage_no",
                "title": "شماره کوتاژ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "customs_green_sheet",
                "title": "شماره برگ سبز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "asn_no",
                "title": "ASN NO",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_order_no",
                "title": "شماره سفارش فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_invoice_no",
                "title": "شماره فاکتور خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sale_organization",
                "title": "مرکز فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "shopping_store",
                "title": "فروشگاه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "delivery_person",
                "title": "تحویل دهنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "weighbridge_no",
                "title": "شماره برگه باسکول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_order_no",
                "title": "شماره دستور تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_plan_no",
                "title": "شماره سفارش تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_operation_no",
                "title": "شماره عملیات تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_shift",
                "title": "شیفت تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_date",
                "title": "تاریخ تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_inspection_no",
                "title": "شماره بازرسی کیفیت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_check_list_no",
                "title": "شماره چک لیست",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_lab_no",
                "title": "شماره آزمایشگاه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "conditional_approval",
                "title": "تایید ارفاقی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inspection_result",
                "title": "نتیجه بازرسی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "coa_no",
                "title": "شماره COA",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "transporter_name",
                "title": "نام راننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "vehicle_no",
                "title": "نام خودرو",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "license_plate_no",
                "title": "شماره پلاک",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "waybill_no",
                "title": "شماره بارنامه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "waybill_date",
                "title": "تاریخ بارنامه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "transporter_phone_no",
                "title": "تلفن راننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "voucherspecification"
                },
                "title": "الگوی سند انبار",
                "name": "ivs",
                "foreignKey": {
                    "local": {
                        "name": "voucher_specification_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "شناسه الگوی سند انبار"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "store"
                },
                "title": "انبار",
                "name": "store",
                "foreignKey": {
                    "local": {
                        "name": "store_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "شناسه انبار"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "store"
                },
                "title": "انبار مقابل",
                "name": "counterstore",
                "foreignKey": {
                    "local": {
                        "name": "counter_part_store_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "شناسه انبار مقابل"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "parts"
        },
        "title": "کالا",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "parts-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "major_unit_title",
                "title": "واحد سنجش اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "secondary_unit_title",
                "title": "واحد سنجش دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_account_category_title",
                "title": "طبقه حساب کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_type",
                "title": "نوع کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_usage",
                "title": "نوع کارکرد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "partaltunit"
                },
                "title": "واحد فرعی کالا",
                "name": "altunit",
                "foreignKey": {
                    "local": {
                        "name": "id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "part_id",
                        "title": "Part ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "partstoragetype"
                },
                "title": "نوع انبار کالا",
                "name": "storagetype",
                "foreignKey": {
                    "local": {
                        "name": "id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "part_id",
                        "title": "Storage Type ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "voucherspecification"
        },
        "title": "الگوی سند انبار",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "specs-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد الگو",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان الگو",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "voucher_type",
                "title": "نوع سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "direction",
                "title": "جهت سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "purchase_type",
                "title": "نوع خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "type_of_effect",
                "title": "نوع تاثیر بر موجودی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "counter_part_type",
                "title": "نوع طرف مقابل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "invvoucheritem"
        },
        "title": "قلم سند انبار",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "voucheritems-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "DecimalType",
                "name": "quantity",
                "title": "مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "major_quantity",
                "title": "مقدار به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "second_unit_quantity",
                "title": "مقدار به واحد دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "remained_major_quantity",
                "title": "مانده استفاده نشده به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "remained_second_unit_quantity",
                "title": "مانده استفاده نشده به واحد دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "row_number",
                "title": "شماره ردیف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "sl_title",
                "title": "معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "extra_field1",
                "title": "فیلد اضافه 1",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field2",
                "title": "فیلد اضافه 2",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field3",
                "title": "فیلد اضافه 3",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field4",
                "title": "فیلد اضافه 4",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "extra_field5",
                "title": "فیلد اضافه 5",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "supplier_title",
                "title": "تامین کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "contractor_title",
                "title": "پیمانکار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cost_center_title",
                "title": "مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "project_title",
                "title": "پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "customer_title",
                "title": "مشتری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "carrier_title",
                "title": "موسسه حمل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "consignment_party_title",
                "title": "طرف حساب امانی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "employee_title",
                "title": "کارمند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_person_title",
                "title": "کارمند فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "purchase_order_no",
                "title": "شماره سفارش خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "purchase_invoice_no",
                "title": "شماره فاکتور خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "deliver_to",
                "title": "تحویل گیرنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "cottage_no",
                "title": "شماره کوتاژ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "customs_green_sheet",
                "title": "شماره برگ سبز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "asn_no",
                "title": "ASN NO",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_order_no",
                "title": "شماره سفارش فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sales_invoice_no",
                "title": "شماره فاکتور خرید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "sale_organization",
                "title": "مرکز فروش",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "shopping_store",
                "title": "فروشگاه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "delivery_person",
                "title": "تحویل دهنده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "weighbridge_no",
                "title": "شماره برگه باسکول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_order_no",
                "title": "شماره دستور تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_plan_no",
                "title": "شماره سفارش تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_operation_no",
                "title": "شماره عملیات تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_shift",
                "title": "شیفت تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "production_date",
                "title": "تاریخ تولید",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_inspection_no",
                "title": "شماره بازرسی کیفیت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_check_list_no",
                "title": "شماره چک لیست",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "qc_lab_no",
                "title": "شماره آزمایشگاه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "conditional_approval",
                "title": "تایید ارفاقی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inspection_result",
                "title": "نتیجه بازرسی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "coa_no",
                "title": "شماره COA",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "transporter_name",
                "title": "نام راننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "vehicle_no",
                "title": "نام خودرو",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "license_plate_no",
                "title": "شماره پلاک",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "waybill_no",
                "title": "شماره بارنامه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "waybill_date",
                "title": "تاریخ بارنامه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "transporter_phone_no",
                "title": "تلفن راننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "invvoucher"
                },
                "title": "سند انبار",
                "name": "iv",
                "foreignKey": {
                    "local": {
                        "name": "inventory_voucher_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Inventory Voucher ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "parts"
                },
                "title": "کالا",
                "name": "part",
                "foreignKey": {
                    "local": {
                        "name": "part_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Part ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "units"
                },
                "title": "واحد سنجش",
                "name": "unit",
                "foreignKey": {
                    "local": {
                        "name": "unit_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Unit ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "invitemprice"
        },
        "title": "قلم قیمت",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64Type",
                "title": "حوزه قیمت‌گذاری",
                "dataview": {
                    "name": "item-price-pricing-areas",
                    "title": "حوزه قیمت‌گذاری",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": false,
                    "columns": [
                        {
                            "key": "code",
                            "title": "کد"
                        },
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p2",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "itemprices-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "DecimalType",
                "name": "fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "price",
                "title": "مبلغ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "major_fee",
                "title": "فی به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "major_price",
                "title": "مبلغ به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DateType",
                "name": "date",
                "title": "تاریخ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "price_type",
                "title": "نوع قیمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "currency_title",
                "title": "عنوان ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "acc_voucher_number",
                "title": "شماره سند حسابداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "invvoucheritem"
                },
                "title": "قلم سند انبار",
                "name": "ivi",
                "foreignKey": {
                    "local": {
                        "name": "inventory_voucher_item_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Voucher Item ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "invstockpricing"
        },
        "title": "گردش مبلغی",
        "parameters": [
            {
                "name": "p1",
                "title": "از تاریخ قیمت سند انبار",
                "type": "DateType"
            },
            {
                "name": "p2",
                "title": "تا تاریخ قیمت سند انبار",
                "type": "DateType"
            },
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "itemprices-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "DecimalType",
                "name": "fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "price",
                "title": "مبلغ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "price_in_functional_currency",
                "title": "مبلغ  به ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "total_fee",
                "title": "فی نهایی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "total_price",
                "title": "مبلغ نهایی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "major_fee",
                "title": "فی به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "عنوان شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "branch_title",
                "title": "عنوان شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "plant_code",
                "title": "کد مرکز نگهداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "plant_title",
                "title": "عنوان مرکز نگهداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "store_code",
                "title": "کد انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "store_title",
                "title": "عنوان انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "storage_type",
                "title": "نوع انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "pricing_area_title",
                "title": "عنوان حوزه قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_code",
                "title": "کد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_title",
                "title": "عنوان کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_type",
                "title": "نوع کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_usage",
                "title": "نوع کارکرد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "part_account_category",
                "title": "طبقه حساب کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "major_unit",
                "title": "واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "second_unit",
                "title": "واحد دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inv_voucher_unit",
                "title": "واحد ثبت سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inventory_voucher_specification_title",
                "title": "عنوان الگوی سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "inventory_voucher_type",
                "title": "نوع سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "type_of_effect",
                "title": "نوع تاثیر بر موجودی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "counter_part_title",
                "title": "طرف مقابل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inv_voucher_state",
                "title": "وضعیت سند انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "major_unit_quantity",
                "title": "مقدار واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "quantity",
                "title": "مقدار ثبت سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "second_unit_quantity",
                "title": "مقدار واحد دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "currency",
                "title": "ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "functional_currency",
                "title": "ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "itemprice_vouchering_state",
                "title": "وضعیت سند حسابداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "item_pricing_state",
                "title": "وضعیت قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "price_type",
                "title": "نوع قیمت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "acc_voucher_number",
                "title": "شماره سند حسابداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "invitemprice"
                },
                "title": "قلم قیمت",
                "name": "ivip",
                "foreignKey": {
                    "local": {
                        "name": "inventory_voucher_item_price_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Voucher Item Price ID"
                    }
                }
            },
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "invitempricefactor"
                },
                "title": "جزییات مبلغی ",
                "name": "ivip2",
                "foreignKey": {
                    "local": {
                        "name": "inventory_voucher_item_price_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "inventory_voucher_item_price_id",
                        "title": "Voucher Item Price ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "storagetype"
        },
        "title": "نوع انبار",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "storagetypes-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "code",
                "title": "کد نوع انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "title",
                "title": "عنوان نوع انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "partstoragetype"
        },
        "title": "نوع انبار کالا",
        "parameters": [],
        "columns": [],
        "relations": [
            {
                "businessObjectId": {
                    "contextName": "logistics",
                    "name": "storagetype"
                },
                "title": "نوع انبار",
                "name": "storagetype",
                "foreignKey": {
                    "local": {
                        "name": "storage_type_id",
                        "title": "شناسه"
                    },
                    "referenced": {
                        "name": "id",
                        "title": "Storage Type ID"
                    }
                }
            }
        ]
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "storeinventory"
        },
        "title": "گزارش مبلغی انبار",
        "parameters": [
            {
                "name": "p1",
                "title": "انبار ",
                "type": "Int64Type",
                "dataview": {
                    "name": "store-inventory-amount-stores",
                    "title": "انبار ",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": false,
                    "columns": [
                        {
                            "key": "code",
                            "title": "کد"
                        },
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p2",
                "title": "تا تاریخ",
                "type": "DateType"
            },
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "store-amount-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "Int64Type",
                "name": "part_id",
                "title": "شناسه کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "part_title",
                "title": "عنوان کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "part_code",
                "title": "کد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "store_title",
                "title": "عنوان انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "store_code",
                "title": "کد انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "StringType",
                "name": "unit_title",
                "title": "واحد سنجش اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "Int64Type",
                "name": "remaining",
                "title": "موجودی کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DecimalType",
                "name": "total_amount",
                "title": "موجودی مبلغی کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": false
            },
            {
                "type": "DateType",
                "name": "last_pricing_date",
                "title": "تاریخ آخرین قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    },
    {
        "id": {
            "contextName": "logistics",
            "name": "invitempricefactor"
        },
        "title": "جزییات مبلغی ",
        "parameters": [
            {
                "name": "p1",
                "title": "از تاریخ قیمت سند انبار",
                "type": "DateType"
            },
            {
                "name": "p2",
                "title": "تا تاریخ قیمت سند انبار",
                "type": "DateType"
            },
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "شرکت",
                "dataview": {
                    "name": "itemprices-companies-all",
                    "title": "شرکت",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "شرکت"
                        }
                    ]
                }
            }
        ],
        "columns": [
            {
                "type": "DecimalType",
                "name": "td_in_functional_currency",
                "title": "مالیات و عوارض",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "discount_in_functional_currency",
                "title": "تخفیف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "tf_in_functional_currency",
                "title": "کرایه حمل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "transfer_fee_title",
                "title": "ارز کرایه حمل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "fee",
                "title": "فی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "major_fee",
                "title": "فی به واحد اصلی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "price",
                "title": "مبلغ",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "price_in_reporting_currency1",
                "title": "مبلغ به ارز گزارشگری1",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DecimalType",
                "name": "price_in_reporting_currency2",
                "title": "مبلغ به ارز گزارشگری2",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "reporting1_currency",
                "title": "ارز گزارشگری 1",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "reporting2_currency",
                "title": "ارز گزارشگری 2",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "voucher_number",
                "title": "شماره سند حسابداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "inv_voucher_number",
                "title": "شماره سند انبار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "DateType",
                "name": "date_c",
                "title": "تاریخ سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            },
            {
                "type": "StringType",
                "name": "company_title",
                "title": "شرکت",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true
            }
        ],
        "relations": []
    }
]
"""


FINANCIAL_BO_ORIGINAL = """
[
    {
        "id": {
            "contextName": "financial",
            "name": "voucherssummary"
        },
        "title": "گردش و مانده حساب ها",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64Type",
                "title": "دفتر",
                "dataview": {
                    "name": "all-voucher-summery-all-ledgers",
                    "title": "دفتر",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": false,
                    "columns": [
                        {
                            "key": "code",
                            "title": "کد"
                        },
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p3",
                "type": "Int64ArrayType",
                "title": "نوع سند",
                "dataview": {
                    "name": "all-voucher-summery-all-voucher-types",
                    "title": "نوع سند",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p4",
                "type": "Int64ArrayType",
                "title": "وضعیت سند",
                "dataview": {
                    "name": "all-voucher-summery-all-voucher-state",
                    "title": "وضعیت سند",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p5",
                "type": "DateType",
                "title": "تاریخ شروع"
            },
            {
                "name": "p6",
                "type": "DateType",
                "title": "تاریخ پایان"
            },
            {
                "name": "p7",
                "type": "Int64ArrayType",
                "title": "نوع حساب",
                "dataview": {
                    "name": "all-voucher-summery-all-account-type",
                    "title": "نوع حساب",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": true,
                    "columns": [
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p8",
                "type": "BoolType",
                "title": "وضعیت معین"
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "header_branch_code",
                "title": "کد شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "header_branch_title",
                "title": "عنوان شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "account_group_code",
                "title": "کد گروه حساب",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "account_group_title",
                "title": "عنوان گروه حساب",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "gl_code",
                "title": "کد حساب کل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "gl_title",
                "title": "عنوان حساب کل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "sl_code",
                "title": "کد حساب معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "sl_title",
                "title": "عنوان حساب معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_dl_code",
                "title": "کد طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_dl_title",
                "title": "عنوان طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_role",
                "title": "نقش طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "cost_center_dl_code",
                "title": "کد مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "cost_center_dl_title",
                "title": "عنوان مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "project_dl_code",
                "title": "کد پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "project_dl_title",
                "title": "عنوان پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "pricing_area_dl_code",
                "title": "کد حوزه قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "pricing_area_dl_title",
                "title": "عنوان حوزه قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "part_dl_code",
                "title": "کد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "part_dl_title",
                "title": "عنوان کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_dl_code",
                "title": "کد سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_dl_title",
                "title": "عنوان سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_role",
                "title": "نقش سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "branch_dl_code",
                "title": "کد تفصیل شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "branch_dl_title",
                "title": "عنوان تفصیل شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "bank_account_dl_code",
                "title": "کد حساب بانکی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "bank_account_dl_title",
                "title": "عنوان حساب بانکی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_currency_title",
                "title": "ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "base_currency_title",
                "title": "ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "currency_rate_type_title",
                "title": "نوع نرخ ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "debit",
                "title": " گردش بدهکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "credit",
                "title": "گردش بستانکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_debit",
                "title": "مانده بدهکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_credit",
                "title": "مانده بستانکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining",
                "title": "مانده ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "currency_debit",
                "title": "گردش بدهکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "currency_credit",
                "title": "گردش بستانکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_currency_debit",
                "title": "مانده بدهکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_currency_credit",
                "title": "مانده بستانکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_currency",
                "title": "مانده ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "base_currency_debit",
                "title": "گردش بدهکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "base_currency_credit",
                "title": "گردش بستانکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_base_currency_debit",
                "title": "مانده بدهکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_base_currency_credit",
                "title": "مانده بستانکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_base_currency",
                "title": "مانده ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_debit",
                "title": "گردش بدهکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_credit",
                "title": "گردش بستانکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_first_reporting_currency_debit",
                "title": "مانده بدهکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_first_reporting_currency_credit",
                "title": "مانده بستانکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_first_reporting_currency",
                "title": "مانده ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_debit",
                "title": "گردش بدهکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_credit",
                "title": "گردش بستانکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_second_reporting_currency_debit",
                "title": "مانده بدهکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_second_reporting_currency_credit",
                "title": "مانده بستانکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "remaining_second_reporting_currency",
                "title": "مانده ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "quantity_debit",
                "title": "گردش بدهکار مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "quantity_credit",
                "title": "گردش بستانکار مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "quantity_remaining",
                "title": "مانده مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            }
        ],
        "relations": [],
        "enums": []
    },
    {
        "id": {
            "contextName": "financial",
            "name": "vouchers"
        },
        "title": "اقلام سند حسابداری",
        "parameters": [
            {
                "name": "p1",
                "type": "Int64Type",
                "title": "دفتر",
                "dataview": {
                    "name": "all-voucher-items-all-ledgers",
                    "title": "دفتر",
                    "valueMember": "id",
                    "displayField": "title",
                    "isMultiselect": false,
                    "columns": [
                        {
                            "key": "code",
                            "title": "کد"
                        },
                        {
                            "key": "title",
                            "title": "عنوان"
                        }
                    ]
                }
            },
            {
                "name": "p3",
                "type": "DateType",
                "title": "تاریخ شروع"
            },
            {
                "name": "p4",
                "type": "DateType",
                "title": "تاریخ پایان"
            }
        ],
        "columns": [
            {
                "type": "StringType",
                "name": "header_branch_code",
                "title": "کد شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "header_branch_title",
                "title": "عنوان شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_number",
                "title": "شماره سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DateType",
                "name": "voucher_date",
                "title": "تاریخ سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "sequence_number",
                "title": "شماره عطف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "daily_number",
                "title": "شماره روزانه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "auxiliary_number",
                "title": "شماره فرعی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_type_title",
                "title": "نوع سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_state",
                "title": "وضعیت سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_explanation",
                "title": "شرح سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "creator_name",
                "title": "صادر کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "reviewer_name",
                "title": "بررسی کننده",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "row_number",
                "title": "شماره ردیف",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "ag_code",
                "title": "کد گروه حساب",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "ag_title",
                "title": "عنوان گروه حساب",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "gl_code",
                "title": "کد حساب کل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "gl_title",
                "title": "عنوان حساب کل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "sl_code",
                "title": "کد حساب معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "sl_title",
                "title": "عنوان حساب معین",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "dl_code",
                "title": "کد تفصیل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "dl_title",
                "title": "عنوان تفصیل",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_dl_code",
                "title": "کد طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_dl_title",
                "title": "عنوان طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "business_party_role",
                "title": "نقش طرف تجاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "cost_center_dl_code",
                "title": "کد مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "cost_center_dl_title",
                "title": "عنوان مرکز هزینه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "project_dl_code",
                "title": "کد پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "project_dl_title",
                "title": "عنوان پروژه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "pricing_area_dl_code",
                "title": "کد حوزه قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "pricing_area_dl_title",
                "title": "عنوان حوزه قیمت گذاری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "part_dl_code",
                "title": "کد کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "part_dl_title",
                "title": "عنوان کالا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_dl_code",
                "title": "کد سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_dl_title",
                "title": "عنوان سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "other_party_role",
                "title": "نقش سایر اشخاص",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "branch_dl_code",
                "title": "کد تفصیل شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "branch_dl_title",
                "title": "عنوان تفصیل شعبه",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "bank_account_dl_code",
                "title": "کد حساب بانکی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "bank_account_dl_title",
                "title": "عنوان حساب بانکی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "debit",
                "title": " گردش بدهکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "credit",
                "title": "گردش بستانکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "debit_million",
                "title": "کسر میلیون گردش بدهکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "credit_million",
                "title": "کسر میلیون گردش بستانکار ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_currency_title",
                "title": "ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "currency_debit",
                "title": "گردش بدهکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "currency_credit",
                "title": "گردش بستانکار ارز سند",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "currency_rate_type_title",
                "title": "نوع نرخ ارز",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "functional_currency_exchange_rate",
                "title": "نرخ تبدیل ارز عملیاتی",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "base_currency_title",
                "title": "ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "base_currency_debit",
                "title": "گردش بدهکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "base_currency_credit",
                "title": "گردش بستانکار ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "base_currency_exchange_rate",
                "title": "نرخ تبدیل ارز مبنا",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_debit",
                "title": "گردش بدهکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_credit",
                "title": "گردش بستانکار ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "first_reporting_currency_exchange_rate",
                "title": "نرخ تبدیل ارز گزارشگری اول",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_debit",
                "title": "گردش بدهکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_credit",
                "title": "گردش بستانکار ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "second_reporting_currency_exchange_rate",
                "title": "نرخ تبدیل ارز گزارشگری دوم",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "voucher_item_explanation",
                "title": "شرح قلم سندحسابداری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "StringType",
                "name": "follow_up_number",
                "title": "شماره پیگیری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DateType",
                "name": "follow_up_date",
                "title": "تاریخ پیگیری",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            },
            {
                "type": "DecimalType",
                "name": "quantity",
                "title": "مقدار",
                "canSelect": true,
                "canFilter": true,
                "canOrder": true,
                "canGroup": true,
                "enumId": ""
            }
        ],
        "relations": [],
        "enums": []
    }
]

"""


INVOICE_BO_MODIFIED = """
    ## invoice
    - **Title**: فاکتور
    - **Context**: sales
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
      - invoicecustomergroups: گروه مشتری (foreign key customer_id to invoicecustomergroup.customer_id)


    ## invoiceitem:
    - **Title**: قلم فاکتور
    - **Context**: sales
    - **Parameters**:
      - p3: شرکت (Int64Array - multiselect from companies dataview)
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
      - invoiceproducts: کالا/خدمت (foreign key gnr_product_id to product.id)
      - invoiceproductgroup: گروه کالا/خدمت (foreign key gnr_product_id to productgroup.product_id)
      - invinvvchr: قلم سند انبار (foreign key voucher_item_id to invvoucheritem.id)
      - invitemrel: فاکتور (foreign key invoice_id to invoice.id)


    ## productgroup 
    - **Title**: گروه بندی کالا/خدمت
    - **Context**: sales
    - **Attributes (all String)**:
      - code: کد گروه کالا/خدمت
      - group_title: عنوان گروه کالا/خدمت
      - grouping_title: عنوان گروهبندی کالا/خدمت
      - cmp_title: شرکت
    - **Relations**: None


    ## invoicecustomergroup 
    - **Title**: اعضای گروه بندی مشتری
    - **Context**: sales
    - **Attributes (all String)**:
      - group_title: عنوان گروه مشتری
      - code: کد گروه مشتری
      - title: عنوان گروه بندی مشتری
      - cmp_title: شرکت
    - **Relations**: None


    ## product 
    - **Title**: کالا/خدمت
    - **Context**: sales
    - **Attributes (all String)**:
      - code: کد کالا/خدمت
      - major_unit_title: واحد سنجش اصلی
      - secondary_unit_title: واحد سنجش دوم
      - cmp_title: شرکت
      - title: عنوان کالا/خدمت
    - **Relations**: None
"""


RETURNINVOICE_BO_MODIFIED = """
    ## returninvoice
    - **Title**: فاکتور برگشتی
    - **Context**: sales
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
      - rinvcgroups: گروه مشتری (foreign key customer_id to invoicecustomergroup.customer_id)

    ## rinvoiceitem 
    - **Title**: قلم فاکتور برگشتی
    - **Context**: sales
    - **Parameters**:
      - p3: شرکت (Int64Array with dataview for company selection)
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
      - prdrinv: کالا/خدمت (foreign key gnr_product_id to product.id)
      - pgrouprinv: گروه کالا/خدمت (foreign key gnr_product_id to productgroup.product_id)
      - rinvinvvchr: قلم سند انبار (foreign key voucher_item_id to invvoucheritem.id)
      - rinvitembase: قلم فاکتور مبنا (foreign key base_item_id to invoiceitem.id)
      - rinvitemrel: فاکتور برگشتی (foreign key return_invoice_id to returninvoice.id)
"""


PRICELISTITEM_BO_MODIFIED = """
## pricelistitem 
- **Title**: قلم لیست قیمت
- **Parameters**:
  - p3: شرکت (Int64Array, multiselect)
  - p4: ارز (Int64Array, multiselect)
- **Attributes**:
  - **Decimal Type**:
    - plip_fee: فی 
  - **Str Type**:
    - product_title: عنوان کالا/خدمت 
    - unit_title: عنوان واحد سنجش 
    - cmp_title: شرکت 
    - pli_is_price_changeable: امکان تغییر در اسناد 
  - **Date Type**:
    - plip_validity_start_date: تاریخ شروع اعتبار بازه 
    - plip_validity_end_date: تاریخ پایان اعتبار بازه 
  - **Int64 Type**:
    - pli_max_decrease_fee_percent: حداکثر درصد کاهش 
    - pli_max_increase_fee_percent: حداکثر درصد افزایش 
- **Relations**:
  - pricelists: لیست قیمت (foreign key pl_id to pricelistheader.id)
  - parameterrel: پارامتر های لیست قیمت (foreign key pl_id to plparameters.pl_id)

## channel 
- **Title**: کانال فروش
- **Attributes** (all Str):
  - title: عنوان کانال فروش
  - cmp_title: شرکت
  - code: کد کانال فروش

## salesarea 
- **Title**: حوزه فروش
- **Attributes** (all Str):
  - title: عنوان حوزه فروش
  - code: کد حوزه فروش
  - cmp_title: شرکت

## division 
- **Title**: بخش فروش
- **Attributes** (all Str):
  - title: عنوان بخش فروش
  - code: کد بخش فروش
  - cmp_title: شرکت

## organization 
- **Title**: سازمان فروش
- **Attributes** (all Str):
  - title: عنوان سازمان فروش
  - code: کد سازمان فروش
  - cmp_title: شرکت

## settlementmethod 
- **Title**: روش تسویه
- **Attributes** (all Str):
  - title: عنوان روش تسویه
  - cmp_title: شرکت

## customergroup 
- **Title**: گروه بندی مشتری
- **Attributes** (all Str):
  - title: عنوان گروه مشتری
  - code: کد گروه مشتری
  - grouping_title: عنوان گروه بندی مشتری
  - cmp_title: شرکت

## pricelistheader 
- **Title**: لیست قیمت
- **Attributes**:
  - **Str Type**:
    - title: عنوان لیست قیمت 
    - currency_title: عنوان ارز 
  - **Date Type**:
    - pl_validity_start_date: تاریخ شروع اعتبار 
    - pl_validity_end_date: تاریخ پایان اعتبار 
  - **Str Type**:
    - state: وضعیت 
    - cmp_title: شرکت 

## office 
- **Title**: دفتر فروش
- **Attributes** (all Str):
  - title: عنوان دفتر فروش
  - code: کد دفتر فروش
  - cmp_title: شرکت

## plparameters 
- **Title**: پارامتر های لیست قیمت
- **Attributes**:
  - cmp_title: شرکت (all Str)
- **Relations**:
  - office: دفتر فروش (foreign key sales_office_id to office.id)
  - customergroup: گروه مشتری (foreign key customer_group_id to customergroup.customer_group_id)
  - settlementmethod: روش تسویه (foreign key settlement_method_id to settlementmethod.id)
  - organization: سازمان فروش (foreign key sales_organization_id to organization.id)
  - division: بخش فروش (foreign key sales_division_id to division.id)
  - salesarea: حوزه فروش (foreign key sales_area_id to salesarea.id)
  - channel: کانال فروش (foreign key sales_channel_id to channel.id)
"""


LOGISTICS_BO_MODIFIED = """
## partaltunit
- **Title**: واحد فرعی کالا 
- **Context**: logistics
- **Attributes**:
  - **Str Type**:
    - title: عنوان واحد فرعی کالا 
    - major_unit_title: واحد سنجش اصلی 
  - **Float64 Type**: 
    - coeff: ضریب 
- **Relations**: None


## units
- **Title**: واحد سنجش (Unit of Measure)
- **Context**: logistics
- **Attributes**:
  - **Str Type**:
    - title: عنوان واحد سنجش 
  - Int64 Type:
    - dimension: بعد 
- **Relations**: None


## store
- **Title**: انبار
- **Context**: logistics
- **Attributes**:
  - **Str Type**:
    - code: کد انبار 
    - title: عنوان انبار 
    - storage_type_title: عنوان نوع انبار 
    - state: استان 
    - company_title: شرکت 
- **Relations**:
  - plants: مرکز نگهداری (foreign key: plant_id to plants.id)


## partaccountcategory
- **Title**: طبقه حساب کالا 
- **Context**: logistics
- **Attributes**:
  - Str Type: 
    - code: کد طبقه حساب کالا 
    - title: عنوان طبقه حساب کالا 
    - pricing_method: روش قیمت گذاری 
    - company_title: شرکت 
- **Relations**: None


## plants
- **Title**: مرکز نگهداری 
- **Context**: logistics
- **Attributes**:
  - **Str Type**:
    - code: کد مرکز نگهداری 
    - title: عنوان مرکز نگهداری 
    - branch_title: عنوان شعبه 
    - state: استان 
    - company_title: شرکت 
- **Relations**: None


## invvoucher
- **Title**: سند انبار 
- **Context**: logistics
- **Attributes**:
  - **Date Type**: 
    - date: تاریخ سند
  - **Str Type**: 
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
    - production_date: تاریخ تولید 
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
    - waybill_date: تاریخ بارنامه 
    - transporter_phone_no: تلفن راننده 
    - company_title: شرکت 
- **Relations**:
  - ivs: الگوی سند انبار (foreign key: voucher_specification_id to voucherspecification.id)
  - store: انبار (foreign key: store_id to store.id)
  - counterstore: انبار مقابل (foreign key: counter_part_store_id to store.id)


## parts
- **Title**: کالا 
- **Context**: logistics
- **Attributes**:
  - **Str Type**:
    - code: کد کالا 
    - title: عنوان کالا 
    - major_unit_title: واحد سنجش اصلی 
    - secondary_unit_title: واحد سنجش دوم 
    - part_account_category_title: طبقه حساب کالا 
    - part_type: نوع کالا 
    - part_usage: نوع کارکرد کالا 
    - company_title: شرکت 
- **Relations**:
  - altunit: واحد فرعی کالا (foreign key: id to partaltunit.part_id)
  - storagetype: نوع انبار کالا (foreign key: id to partstoragetype.part_id)


## voucherspecification
- **Title**: الگوی سند انبار
- **Context**: logistics
- **Attributes**:
  - **Str Type**: 
    - code: کد الگو 
    - title: عنوان الگو 
    - voucher_type: نوع سند 
    - direction: جهت سند 
    - purchase_type: نوع خرید 
    - type_of_effect: نوع تاثیر بر موجودی 
    - counter_part_type: نوع طرف مقابل 
    - company_title: شرکت 
- **Relations**: None


## invvoucheritem
- **Title**: قلم سند انبار 
- **Context**: logistics
- **Attributes**:
  - **Decimal Type**: 
    - quantity: مقدار 
    - major_quantity: مقدار به واحد اصلی 
    - second_unit_quantity: مقدار به واحد دوم 
    - remained_major_quantity: مانده استفاده نشده به واحد اصلی 
    - remained_second_unit_quantity: مانده استفاده نشده به واحد دوم 
  - **Str Type**:
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
    - production_date: تاریخ تولید 
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
    - waybill_date: تاریخ بارنامه 
    - transporter_phone_no: تلفن راننده 
    - company_title: شرکت 
- **Relations**:
  - iv: سند انبار (foreign key: inventory_voucher_id to invvoucher.id)
  - part: کالا (foreign key: part_id to parts.id)
  - unit: واحد سنجش (foreign key: unit_id to units.id)


## invitemprice
- **Title**: قلم قیمت 
- **Context**: logistics
- **Attributes**:
  - **Date Type**: 
    - date: تاریخ 
  - **Decimal Type**: 
    - fee: فی 
    - price: مبلغ 
    - major_fee: فی به واحد اصلی 
    - major_price: مبلغ به واحد اصلی 
  - **Str Type**:
    - price_type: نوع قیمت 
    - currency_title: عنوان ارز 
    - acc_voucher_number: شماره سند حسابداری 
    - company_title: شرکت 
- **Relations**:
  - ivi: قلم سند انبار (foreign key: inventory_voucher_item_id to invvoucheritem.id)


## invstockpricing
- **Title**: گردش مبلغی (Inventory Stock Pricing)
- **Context**: logistics
- **Attributes**:
  - **Decimal Type**: 
    - fee: فی 
    - price: مبلغ 
    - price_in_functional_currency: مبلغ به ارز عملیاتی 
    - total_fee: فی نهایی 
    - total_price: مبلغ نهایی 
    - major_fee: فی به واحد اصلی 
    - inventory_voucher_type: نوع سند 
    - type_of_effect: نوع تاثیر بر موجودی 
    - major_unit_quantity: مقدار واحد اصلی 
    - quantity: مقدار ثبت سند 
    - second_unit_quantity: مقدار واحد دوم 
  - **Str Type**:
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
    - counter_part_title: طرف مقابل 
    - inv_voucher_state: وضعیت سند انبار 
    - currency: ارز 
    - functional_currency: ارز عملیاتی 
    - itemprice_vouchering_state: وضعیت سند حسابداری 
    - item_pricing_state: وضعیت قیمت گذاری 
    - price_type: نوع قیمت 
    - acc_voucher_number: شماره سند حسابداری 
    - company_title: شرکت 
- **Relations**:
  - ivip: قلم قیمت (foreign key: inventory_voucher_item_price_id to invitemprice.id)
  - ivip2: جزییات مبلغی (foreign key: inventory_voucher_item_price_id to invitempricefactor.inventory_voucher_item_price_id)


## storagetype
- **Title**: نوع انبار 
- **Context**: logistics
- **Attributes**:
  - **Str Type**: 
    - code: کد نوع انبار 
    - title: عنوان نوع انبار 
    - company_title: شرکت 
- **Relations**: None


## partstoragetype
- **Title**: نوع انبار کالا 
- **Context**: logistics
- **Attributes**: None
- **Relations**:
  - storagetype: نوع انبار (foreign key: storage_type_id to storagetype.id)


## storeinventory
- **Title**: گزارش مبلغی انبار (Warehouse Inventory Report)
- **Context**: logistics
- **Attributes**:
  - **Date Type**:
    - last_pricing_date: تاریخ آخرین قیمت گذاری 
  - **Int64 Type**:
    - part_id: شناسه کالا 
    - remaining: موجودی کالا 
  - **Str Type**:
    - part_title: عنوان کالا 
    - part_code: کد کالا 
    - store_title: عنوان انبار 
    - store_code: کد انبار 
    - unit_title: واحد سنجش اصلی 
    - company_title: شرکت 
  - **Decimal Type**: 
    - fee: فی 
    - total_amount: موجودی مبلغی کالا 
- **Relations**: None


## invitempricefactor
- **Title**: جزییات مبلغی (Item Price Factor)
- **Context**: logistics
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
  - Str Type:
    - transfer_fee_title: ارز کرایه حمل 
    - reporting1_currency: ارز گزارشگری 1 
    - reporting2_currency: ارز گزارشگری 2 
    - voucher_number: شماره سند حسابداری 
    - inv_voucher_number: شماره سند انبار 
    - company_title: شرکت 
- **Relations**: None
"""


LOGISTICS_SALES_MODIFIED = """
    ## logistics_partaltunit
    - **Title**: واحد فرعی کالا 
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**:
        - title: عنوان واحد فرعی کالا 
        - major_unit_title: واحد سنجش اصلی 
      - **Float64 Type**: 
        - coeff: ضریب 
    - **Relations**: None


    ## logistics_units
    - **Title**: واحد سنجش (Unit of Measure)
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**:
        - title: عنوان واحد سنجش 
      - Int64 Type:
        - dimension: بعد 
    - **Relations**: None


    ## logistics_store
    - **Title**: انبار
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**:
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
    - **Attributes**:
      - Str Type: 
        - code: کد طبقه حساب کالا 
        - title: عنوان طبقه حساب کالا 
        - pricing_method: روش قیمت گذاری 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_plants
    - **Title**: مرکز نگهداری 
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**:
        - code: کد مرکز نگهداری 
        - title: عنوان مرکز نگهداری 
        - branch_title: عنوان شعبه 
        - state: استان 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_invvoucher
    - **Title**: سند انبار 
    - **Context**: logistics
    - **Attributes**:
      - **Date Type**: 
        - date: تاریخ سند
      - **Str Type**: 
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
        - production_date: تاریخ تولید 
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
        - waybill_date: تاریخ بارنامه 
        - transporter_phone_no: تلفن راننده 
        - company_title: شرکت 
    - **Relations**:
      - logistics_voucherspecification: الگوی سند انبار (foreign key: voucher_specification_id to logistics_voucherspecification.id)
      - logistics_store: انبار (foreign key: store_id to logistics_store.id)
      - logistics_counterstore: انبار مقابل (foreign key: counter_part_store_id to logistics_store.id)


    ## logistics_parts
    - **Title**: کالا 
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**:
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
    - **Attributes**:
      - **Str Type**: 
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
    - **Attributes**:
      - **Decimal Type**: 
        - quantity: مقدار 
        - major_quantity: مقدار به واحد اصلی 
        - second_unit_quantity: مقدار به واحد دوم 
        - remained_major_quantity: مانده استفاده نشده به واحد اصلی 
        - remained_second_unit_quantity: مانده استفاده نشده به واحد دوم 
      - **Str Type**:
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
        - production_date: تاریخ تولید 
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
        - waybill_date: تاریخ بارنامه 
        - transporter_phone_no: تلفن راننده 
        - company_title: شرکت 
    - **Relations**:
      - logistics_invvoucher: سند انبار (foreign key: inventory_voucher_id to logistics_invvoucher.id)
      - logistics_part: کالا (foreign key: part_id to logistics_parts.id)
      - logistics_unit: واحد سنجش (foreign key: unit_id to logistics_units.id)


    ## logistics_invitemprice
    - **Title**: قلم قیمت 
    - **Context**: logistics
    - **Attributes**:
      - **Date Type**: 
        - date: تاریخ 
      - **Decimal Type**: 
        - fee: فی 
        - price: مبلغ 
        - major_fee: فی به واحد اصلی 
        - major_price: مبلغ به واحد اصلی 
      - **Str Type**:
        - price_type: نوع قیمت 
        - currency_title: عنوان ارز 
        - acc_voucher_number: شماره سند حسابداری 
        - company_title: شرکت 
    - **Relations**:
      - logistics_invvoucheritem: قلم سند انبار (foreign key: inventory_voucher_item_id to logistics_invvoucheritem.id)


    ## logistics_invstockpricing
    - **Title**: گردش مبلغی (Inventory Stock Pricing)
    - **Context**: logistics
    - **Attributes**:
      - **Decimal Type**: 
        - fee: فی 
        - price: مبلغ 
        - price_in_functional_currency: مبلغ به ارز عملیاتی 
        - total_fee: فی نهایی 
        - total_price: مبلغ نهایی 
        - major_fee: فی به واحد اصلی 
        - inventory_voucher_type: نوع سند 
        - type_of_effect: نوع تاثیر بر موجودی 
        - major_unit_quantity: مقدار واحد اصلی 
        - quantity: مقدار ثبت سند 
        - second_unit_quantity: مقدار واحد دوم 
      - **Str Type**:
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
        - counter_part_title: طرف مقابل 
        - inv_voucher_state: وضعیت سند انبار 
        - currency: ارز 
        - functional_currency: ارز عملیاتی 
        - itemprice_vouchering_state: وضعیت سند حسابداری 
        - item_pricing_state: وضعیت قیمت گذاری 
        - price_type: نوع قیمت 
        - acc_voucher_number: شماره سند حسابداری 
        - company_title: شرکت 
    - **Relations**:
      - logistics_invitemprice: قلم قیمت (foreign key: inventory_voucher_item_price_id to logistics_invitemprice.id)
      - logistics_invitempricefactor: جزییات مبلغی (foreign key: inventory_voucher_item_price_id to logistics_invitempricefactor.inventory_voucher_item_price_id)


    ## logistics_storagetype
    - **Title**: نوع انبار 
    - **Context**: logistics
    - **Attributes**:
      - **Str Type**: 
        - code: کد نوع انبار 
        - title: عنوان نوع انبار 
        - company_title: شرکت 
    - **Relations**: None


    ## logistics_partstoragetype
    - **Title**: نوع انبار کالا 
    - **Context**: logistics
    - **Attributes**: None
    - **Relations**:
      - storagetype: نوع انبار (foreign key: storage_type_id to storagetype.id)


    ## logistics_storeinventory
    - **Title**: گزارش مبلغی انبار (Warehouse Inventory Report)
    - **Context**: logistics
    - **Attributes**:
      - **Date Type**:
        - last_pricing_date: تاریخ آخرین قیمت گذاری 
      - **Int64 Type**:
        - part_id: شناسه کالا 
        - remaining: موجودی کالا 
      - **Str Type**:
        - part_title: عنوان کالا 
        - part_code: کد کالا 
        - store_title: عنوان انبار 
        - store_code: کد انبار 
        - unit_title: واحد سنجش اصلی 
        - company_title: شرکت 
      - **Decimal Type**: 
        - fee: فی 
        - total_amount: موجودی مبلغی کالا 
    - **Relations**: None


    ## logistics_invitempricefactor
    - **Title**: جزییات مبلغی (Item Price Factor)
    - **Context**: logistics
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
      - Str Type:
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
      - p3: شرکت (Int64Array, multiselect)
      - p4: ارز (Int64Array, multiselect)
    - **Attributes**:
      - **Decimal Type**:
        - plip_fee: فی 
      - **Str Type**:
        - product_title: عنوان کالا/خدمت 
        - unit_title: عنوان واحد سنجش 
        - cmp_title: شرکت 
        - pli_is_price_changeable: امکان تغییر در اسناد 
      - **Date Type**:
        - plip_validity_start_date: تاریخ شروع اعتبار بازه 
        - plip_validity_end_date: تاریخ پایان اعتبار بازه 
      - **Int64 Type**:
        - pli_max_decrease_fee_percent: حداکثر درصد کاهش 
        - pli_max_increase_fee_percent: حداکثر درصد افزایش 
    - **Relations**:
      - sales_pricelistheader: لیست قیمت (foreign key pl_id to sales_pricelistheader.id)
      - sales_plparameters: پارامتر های لیست قیمت (foreign key pl_id to sales_plparameters.pl_id)


    ## sales_channel 
    - **Title**: کانال فروش
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان کانال فروش
      - cmp_title: شرکت
      - code: کد کانال فروش


    ## sales_salesarea 
    - **Title**: حوزه فروش
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان حوزه فروش
      - code: کد حوزه فروش
      - cmp_title: شرکت


    ## sales_division 
    - **Title**: بخش فروش
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان بخش فروش
      - code: کد بخش فروش
      - cmp_title: شرکت


    ## sales_organization 
    - **Title**: سازمان فروش
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان سازمان فروش
      - code: کد سازمان فروش
      - cmp_title: شرکت


    ## sales_settlementmethod 
    - **Title**: روش تسویه
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان روش تسویه
      - cmp_title: شرکت


    ## sales_customergroup 
    - **Title**: گروه بندی مشتری
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان گروه مشتری
      - code: کد گروه مشتری
      - grouping_title: عنوان گروه بندی مشتری
      - cmp_title: شرکت


    ## sales_pricelistheader 
    - **Title**: لیست قیمت
    - **Context**: sales
    - **Attributes**:
      - **Str Type**:
        - title: عنوان لیست قیمت 
        - currency_title: عنوان ارز 
      - **Date Type**:
        - pl_validity_start_date: تاریخ شروع اعتبار 
        - pl_validity_end_date: تاریخ پایان اعتبار 
      - **Str Type**:
        - state: وضعیت 
        - cmp_title: شرکت 


    ## sales_office 
    - **Title**: دفتر فروش
    - **Context**: sales
    - **Attributes** (all Str):
      - title: عنوان دفتر فروش
      - code: کد دفتر فروش
      - cmp_title: شرکت


    ## sales_plparameters 
    - **Title**: پارامتر های لیست قیمت
    - **Context**: sales
    - **Attributes**:
      - cmp_title: شرکت (all Str)
    - **Relations**:
      - office: دفتر فروش (foreign key sales_office_id to office.id)
      - customergroup: گروه مشتری (foreign key customer_group_id to customergroup.customer_group_id)
      - settlementmethod: روش تسویه (foreign key settlement_method_id to settlementmethod.id)
      - organization: سازمان فروش (foreign key sales_organization_id to organization.id)
      - division: بخش فروش (foreign key sales_division_id to division.id)
      - salesarea: حوزه فروش (foreign key sales_area_id to salesarea.id)
      - channel: کانال فروش (foreign key sales_channel_id to channel.id)


    ## sales_returninvoice
    - **Title**: فاکتور برگشتی
    - **Context**: sales
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
      - p3: شرکت (Int64Array with dataview for company selection)
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
      - sales_product: کالا/خدمت (foreign key gnr_product_id to product.id)
      - sales_productgroup: گروه کالا/خدمت (foreign key gnr_product_id to productgroup.product_id)
      - logistics_invvoucheritem: قلم سند انبار (foreign key voucher_item_id to invvoucheritem.id)
      - sales_invoiceitem: قلم فاکتور مبنا (foreign key base_item_id to invoiceitem.id)
      - sales_returninvoice: فاکتور برگشتی (foreign key return_invoice_id to returninvoice.id)


    ## sales_invoice
    - **Title**: فاکتور
    - **Context**: sales
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
      - sales_invoicecustomergroup: گروه مشتری (foreign key customer_id to invoicecustomergroup.customer_id)


    ## sales_invoiceitem:
    - **Title**: قلم فاکتور
    - **Context**: sales
    - **Parameters**:
      - p3: شرکت (Int64Array - multiselect from companies dataview)
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
      - sales_invvoucheritem: قلم سند انبار (foreign key voucher_item_id to invvoucheritem.id)
      - sales_invoice: فاکتور (foreign key invoice_id to invoice.id)


    ## sales_productgroup 
    - **Title**: گروه بندی کالا/خدمت
    - **Context**: sales
    - **Attributes (all String)**:
      - code: کد گروه کالا/خدمت
      - group_title: عنوان گروه کالا/خدمت
      - grouping_title: عنوان گروهبندی کالا/خدمت
      - cmp_title: شرکت
    - **Relations**: None


    ## sales_invoicecustomergroup 
    - **Title**: اعضای گروه بندی مشتری
    - **Context**: sales
    - **Attributes (all String)**:
      - group_title: عنوان گروه مشتری
      - code: کد گروه مشتری
      - title: عنوان گروه بندی مشتری
      - cmp_title: شرکت
    - **Relations**: None


    ## sales_product 
    - **Title**: کالا/خدمت
    - **Context**: sales
    - **Attributes (all String)**:
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
      - financial_vouchers_p1 (Int64): دفتر
      - financial_vouchers_p3 (Date): تاریخ شروع
      - financial_vouchers_p4 (Date): تاریخ پایان
    - **Attributes**:
      - **Date Type**:
        - voucher_date: تاریخ سند
        - follow_up_date: تاریخ پیگیری
      - **Dec Type**:
        - debit: گردش بدهکار ارز عملیاتی
        - credit: گردش بستانکار ارز عملیاتی
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
      - **All other attributes are Str**:
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
        - row_number: شماره ردیف
        - sl_code: کد حساب معین
        - sl_title: عنوان حساب معین
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
