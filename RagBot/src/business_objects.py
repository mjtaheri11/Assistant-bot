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
    - Attributes (all Str):
      - code: کد طبقه حساب کالا
      - title: عنوان طبقه حساب کالا
      - pricing_method: روش قیمت گذاری [ENUM: "میانگین", "شناسایی ویژه", "فایفو"]
    - Relations: None


    units:
    - Title: واحد سنجش
    - Attributes:
      - Str: title: عنوان واحد سنجش
      - Int64: dimension: بعد
    - Relations: None


    storeinventory:
    - Title: گزارش مبلغی انبار
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
      - All other attributes are Str:
        - price_type: نوع قیمت [ENUM: "براوردی", "واقعی", "براوردی به واقعی", "اصلاح بها", "تعدیل"]
        - currency_title: عنوان ارز
        - acc_voucher_number: شماره سند حسابداری
    - Relations:
      - invvoucheritem: قلم سند انبار (foreign key inventory_voucher_item_id to invvoucheritem.id)


    plants:
    - Title: مرکز نگهداری
    - Attributes (all Str):
      - code: کد مرکز نگهداری
      - title: عنوان مرکز نگهداری
      - branch_title: عنوان شعبه
      - state: وضعیت [ENUM: "فعال", "غیرفعال"]
    - Relations: None


    storagetype:
    - Title: نوع انبار
    - Attributes (all Str):
      - code: کد نوع انبار
      - title: عنوان نوع انبار
    - Relations: None


    parts:
    - Title: کالا
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
    - Attributes: None
    - Relations:
      - storagetype: نوع انبار (foreign key storage_type_id to storagetype.id)


    partaltunit:
    - Title: واحد فرعی کالا
    - Attributes:
      - Str:
        - title: عنوان واحد فرعی کالا
        - major_unit_title: واحد سنجش اصلی
      - Float64: coeff: ضریب
    - Relations: None
    

    voucherspecification:
    - Title: الگوی سند انبار
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
    - Attributes (all Str):
      - code: کد انبار
      - title: عنوان انبار
      - storage_type_title: عنوان نوع انبار
      - state: وضعیت [ENUM: "غیر فعال", "فعال", "ثبت اولیه"]
    - Relations:
      - plants: مرکز نگهداری (foreign key plant_id to plants.id)

    
    invvoucheritem:
    - Title: قلم سند انبار
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



