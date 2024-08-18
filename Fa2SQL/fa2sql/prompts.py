SQL_GENERATOR_PROMPT_NO_HIST = """
You are a polite text to sql expert for Hamkaran System (همکاران سیستم) users. Your role it to convert a user's question to a sql based on a given database schema.\
Understand the user's needed information. First understood the question, then write the equivalent sql query and nothing more.\

Given the following SQL tables, your job is to write queries given a user’s question:\n\n
{schema}

Be reasonable and think step-by-step.\
Understand the user's question first, then generate the sql query for it.
All your communications should be in Persian text or sql queries.

User's Question:

{question}"""



SQL_GENERATOR_PROMPT_HIST = """
You are a polite text to sql chatbot for Hamkaran System (همکاران سیستم) users. Your role it to convert a user's question to a sql based on the given database schema.

Given the following tables, your job is to write queries given a user’s request:

<Database Schema>

{schema}

</Database Schema>

Here is the Conversation History so far:

<chat-history> 

{history} 

</chat-history>

Be reasonable and think step-by-step.
Understand the user's question first, then generate the sql query for it.

User's Question:

<question> 

{question} 

</question>
Output the sql query and nothing else.
**Dates are in Shamsi calender.**
"""

SCHEMA_INV= """\n
TABLE UNIT #واحد سنجش اندازه گیری کالا است که برای واحدهای اصلی، فرعی و دوم استفاده می شود\n
    ID int
    TITLE varchar
    DIMENSION varchar # نشان دهنده نوع واحد سنجش است.  مقادیر شامل: وزن، حجم، متراژ، شمارشی، زمان، انرژی، دما، فشار، فرکانس
\n\n
TABLE PLANT # مرکز نگهداری که به محل های جغرافیایی مجموعه ای از انبارها اطلاق می شود، هر انبار تنها می تواند در یک مرکز نگهداری تعریف شود.\n
    ID int
    CODE varchar
    TITLE varchar
    BRANCH_TITLE varchar
    STATE varchar #  مقادیر شامل: فعال (پیشفرض)، غیر فعال
\n\n
TABLE STORE # به محلهای فیزیکی برای نگهداری کالاها اطلاق می شود. هر انبار می تواند دارای تقسیم بندی های داخلی نیز باشد.\n
    ID int
    CODE varchar
    TITLE varchar
    STORAGE_TYPE_TITLE varchar # لیست نوع انبارها توسط کاربر تعریف می شود
    STATE varchar #  مقادیر شامل: فعال، غیر فعال (پیشفرض)
    PLANT_REF int
\n\n
TABLE PART # کلیه اقلامی که در شرکت مورد استفاده قرار میگیرند به عنوان کالا در سیستم تعریف می شود. در صورتی که یک کالا بتواند در تراکنش های انبار استفاده شود  نیاز است نوع انبار های آن تعیین گردد.\n
    ID int
    CODE varchar
    TITLE varchar
    MAJOR_UNIT_TITLE varchar
    SECONDARY_UNIT_TITLE varchar
    PART_ACCOUNT_CATEGORY_TITLE varchar
    PART_TYPE varchar #  مقادیر شامل: ماده اولیه، نیمه ساخته، محصول نهایی، دارایی ثابت، سایر
    PART_USAGE varchar # مقادیر شامل: خریدنی -  قابل فروش -  خریدنی، قابل فروش - ساختنی - خریدنی، ساختنی - ساختنی، قابل فروش - خریدنی، ساختنی ،قابل فروش - غیرموجودی - خریدنی، غیرموجودی - قابل فروش، غیرموجودی - خریدنی، قابل فروش، غیرموجودی - ساختنی، غیرموجودی - خریدنی، ساختنی، غیرموجودی - قابل فروش، ساختنی، غیرموجودی - خریدنی، قابل فروش، ساختنی، غیر موجودی
\n\n
TABLE VOUCHER_SPECIFICATION #  الگوی سند انبار قالب هایی هستند که تراکنش های انبار از طریق آنها انجام می شود. کلیه ورودیها و خروجهای مجاز برای استفاده در انبارها به صورت الگو تعریف می شوند.\n
    ID int
    CODE varchar
    TITLE varchar
    VOUCHER_TYPE varchar # مقادیر شامل: خرید - تولید - مصرف - ضایعات - انتقال بین انبار - فروش - انبارگردانی - امانی - تبدیل کالا - سایر - پایان دوره - ابتدای دوره - تحویل دارایی ثابت
    DIRECTION varchar # مقادیر شامل: ورودی - خروجی
    PURCHASE_TYPE varchar # مقادیر شامل: داخلی - خارجی
    TYPE_OF_EFFECT varchar #  مقادیر شامل: دائمی (پیشفرض) - موقت - ضایعات
    COUNTER_PART_TYPE varchar # مشخص کننده نوع تفصیل مورد نیاز برای هر الگوی سند می باشد. مقادیر شامل:تامین کننده - مشتری - مرکز هزینه - پروژه - طرف حساب امانی - شخص - شرکت
\n\n
TABLE INV_VOUCHER # گردش های کالا در انبار با استفاده از الگوها در قالب اسناد انبار ذخیره می گردد.\n
    ID int
    NUMBER varchar
    DATE date
    TITLE varchar 
    DESCRIPTION varchar
    SL_TITLE varchar # عنوان معین
    STATE varchar #   مقادیر شامل: ثبت شده (پیشفرض) - تایید شده - باطل شده
    FY_TITLE varchar # دوره مالی
    SUPPLIER_TITLE varchar
    CONTRACTOR_TITLE varchar
    COST_CENTER_TITLE varchar
    PROJECT_TITLE varchar
    CUSTOMER_TITLE varchar
    CARRIER_TITLE varchar
    CONSIGNMENT_PARTY_TITLE varchar
    EMPLOYEE_TITLE varchar
    SALES_PERSON_TITLE varchar
    SHOPPING_STORE varchar
    DELIVERY_PERSON varchar
    STORE_REF int # انبار اصلی
    STORE_REF2 # در تراکنش های انتقال، دو انبار وجود دارد. انبار اصلی و انبار مقابل
    VOUCHER_SPECIFICATION_REF int
\n\n
TABLE INV_VOUCHER_ITEM # گردش های کالا در انبار با استفاده از الگوها در قالب اسناد انبار به همراه اقلام اسناد انبار ذخیره می گردد. این بیزینس آبجکت جزئیات بیزینس آبجکت قبلی می باشد.\n
    ID int
    QUANTITY numeric
    MAJOR_QUANTITY numeric
    SECOND_UNIT_QUANTITY numeric
    REMAINED_MAJOR_QUANTITY numeric
    REMAINED_SECOND_UNIT_QUANTITY numeric
    ROW_NUMBER varchar
    SL_TITLE varchar # عنوان معین حسابداری ه در سند حسابداری استفاده شده است.
    SUPPLIER_TITLE varchar
    CONTRACTOR_TITLE varchar
    COST_CENTER_TITLE varchar
    PROJECT_TITLE varchar
    CUSTOMER_TITLE varchar
    CARRIER_TITLE varchar
    CONSIGNMENT_PARTY_TITLE varchar
    EMPLOYEE_TITLE varchar
    SALES_PERSON_TITLE varchar
    DELIVER_TO varchar
    COTTAGE_NO varchar
    VEHICLE_NO varchar
    PART_REF int
    UNIT_REF int
"""

SCHEMA_GL= """\n
TABLE ACC_CHART_OF_ACCOUNT # این جدول اطلاعات مربوط به ساختار حساب ها را ذخیره می کند. ساختار حساب ها لیست درختواره ای حساب ها می باشد که شامل گروه حساب، حساب کل و حساب معین می باشد. در هر ساختار حساب می توان طول کد گروه و کل و معین را تعیین نمود تا حساب های تعریف شده از این موضوع تبعیت کنند. حداکثر مجموع طول گروه حساب و حساب کل و معین 12 کاراکتر می باشد\n
    ID int
    TITLE varchar
    CODE varchar
    ACCOUNT_GROUP_CODE_LENGTH int
    GL_CODE_LENGTH int
    SL_CODE_LENGTH int
    IS_USING_CHARACTER boolean # در صورت انتخاب این گزینه، در کد حساب ها غیر از عدد می توان از کارکترهای دیگر نیز استفاده نمود
\n\n
TABLE ACC_ACCOUNT_GROUP # این جدول اطلاعات مربوط به گروه حساب ها را ذخیره می کند. هر حساب گروه زیرمجموعه یک ساختار حساب ها می باشد\n
    ID int
    TITLE varchar
    CODE varchar
    ACCOUNT_TYPE varchar #  نوع حساب شامل سه مورد است: دائم - موقت - انتظامی
    ACCOUNT_NATURE # ماهیت حساب شامل سه مورد است: مهم نیست - بدهکار - بستانکار
    ACC_CHART_OF_ACCOUNT_REF int
\n\n
TABLE ACC_GL # این جدول اطلاعات مربوط به حساب های کل را ذخیره می کند. هر حساب کل زیرمجموعه یک گروه حساب می باشد\n
    ID int
    TITLE varchar
    CODE varchar    
    ACCOUNT_TYPE varchar #  نوع حساب شامل سه مورد است: دائم - موقت - انتظامی
    ACCOUNT_NATURE # ماهیت حساب شامل سه مورد است: مهم نیست - بدهکار - بستانکار
    ACC_ACCOUNT_GROUP_REF int
\n\n
TABLE ACC_SL # این جدول اطلاعات مربوط به حساب های معین را ذخیره می کند. هر حساب معین زیرمجموعه یک حساب کل می باشد. حساب معین سطح عملیاتی ساختار حساب ها است و در صدور اسناد حسابداری از آن استفاده می شود.\n
    ID int
    TITLE varchar
    CODE varchar
    ACCOUNT_TYPE varchar #  نوع حساب شامل سه مورد است: دائم - موقت - انتظامی
    ACCOUNT_NATURE # ماهیت حساب شامل سه مورد است: مهم نیست - بدهکار - بستانکار
    IS_ACTIVE boolean # وضعیت معین شامل دو مورد است: فعال - غیر فعال
    IS_TRACEABLE boolean
    IS_QUANTIFIABLE boolean
    IS_MULTI_CURRENCY boolean
    IS_MONETARY_ITEM boolean
    BUSINESS_PARTY int
    IS_FROM_GL boolean
    IS_FROM_INV boolean
    BUSINESS_PARTY int
    OTHER_PARTY int
    COST_CENTER int
    PROJECT int
    BRANCH int
    PART int
    COMPANY_REF int
    PRICING_AREA int # آیا تفصیل حوزه قیمت گذاری دارد یا خیر
    BANK_ACCOUNT int 
    ACC_GL_REF int   
\n\n
TABLE ACC_VOUCHER # این جدول اطلاعات مربوط به سند حسابداری را ذخیره می کند. هر سند حسابداری متعلق به یک شعبه از یک شرکت می باشد.\n
    ID int
    VOUCHER_NUMBER int
    VOUCHER_DATE date
    DAILY_NUMBER int
    SEQUENCE_NUMBER int
    AUXILIARY_NUMBER varchar 
    REFERENCE_NUMBER varchar
    EXPLANATION varchar
    STATE varchar # وضعیت سند حسابداری شامل چهار مورد است: یادداشت - موقت - بررسی شده  - قطعی شده. اسناد با وضعیت موقت به بعد اسناد بالانس و استاندارد هستند و در تمام گزارشات شرکت می کنند. اسناد یادداشت بالانس یا استاندارد نیستند و بعد باید تکمیل شده و به سند موقت تبدیل شوند. اسناد موقت بر اساس اسناد مثبته بررسی شده و وضعیت آنها از موقت به بررسی شده تغییر می ابد تا دیگر قابل حذف و ویرایش نباشد. در نهایت برای تحریر دفاتر قانونی باید اسناد از بررسی شده به قطعی شده تغییر وضعیت یابند تا دیگر امکان برگشت از آن وضعیت و تغییر و حذف آنها امکانپذیر نباشد
    LEDGER_ID int # اسناد حسابداری در دفاتر ثبت می شوند. هر سند در یک دفتر ثبت می شود. شرکت ها می توانند به دلایل مختلف مانند گزارشگری با استانداردهای متفاوت بیش از یک دفتر داشته باشند و در هر دفتر بر اساس استانداردهای مربوطه اسناد حسابداری را صادر نمایند.
    BRANCH_ID int
    FISCAL_YEAR_ID int
    FINANCIAL_INTERVAL_ID int
    VOUCHER_TYPE_ID int, # نوع سند نوعی گروه بندی اسناد حسابداری می باشد تا در زمان جستجو بر اساس نوع سند بتوان راحت تر اسناد را شناسایی نمود. انواع سند پیش فرض سیستم دفترکل عبارت هستند از افتتاحیه - اختتامیه - بستن حساب ها - تعدیل ماهیت ابتدای سال - تعدیل ماهیت پایان سال - تسعیر ارز اقلام پولی - تسعیر به ارز گزارشگری - عمومی. به ازای هر ماژول نیز یک نوع سند به سیستم اضافه می شود که اسناد صادر شده از آن ماژول با آن نوع سند صادر می گردد مانند انبار. علاوه بر انواع سند سیستمی، کاربر نیز می تواند انواع سند مورد نظر خود را تعریف و استفاده نماید. این انواع مشابه نوع سند عمومی در سیستم می باشند.
    CREATOR_ID int
    LAST_MODIFIER_ID int
    LAST_REVIEWER_ID int
    VOUCHER_ISSUANCE_DATE date
    COMPANY_ID int
\n\n
TABLE ACC_VOUCHER_ITEM # این جدول اطلاعات مربوط به اقلام سند حسابداری را ذخیره می کند. یک سند حسابداری استاندارد و کامل باید دارای اقلام با مبالغ موازنه بدهکار و بستانکار باشد\n
    ID int
    VOUCHER_ID int
    ROW_NUMBER int
    BUSINESS_PARTY_ROLE int
    OTHER_PARTY_ROLE int
    BRANCH_ID int
    CURRENCY_DEBIT number
    CURRENCY_CREDIT number
    DEBIT number
    CREDIT number
    BASE_CURRENCY_DEBIT number
    BASE_CURRENCY_CREDIT
    EXPLANATION varchar
    FOLLOW_UP_NUMBER varchar
    FOLLOW_UP_DATE date
    QUANTITY numeric
    BUSINESS_PARTY_ID int
    OTHER_PARTY_ID int
    COST_CENTER_ID int
    PROJECT_ID int
    CURRENCY_ID int
    BASE_CURRENCY_ID int
    PRICING_AREA_ID int
    BANK_ACCOUNT_ID int
    PART_ID int
"""

SCHEMA_INV_SQL= """
-- واحد سنجش اندازه گیری کالا است که برای واحدهای اصلی، فرعی و دوم استفاده می شود\n
CREATE TABLE UNIT (
    ID INT PRIMARY KEY,
    TITLE VARCHAR(255),
    DIMENSION VARCHAR(50) COMMENT 'نشان دهنده نوع واحد سنجش است.  مقادیر شامل: وزن، حجم، متراژ، شمارشی، زمان، انرژی، دما، فشار، فرکانس'
);
\n
-- مرکز نگهداری که به محل های جغرافیایی مجموعه ای از انبارها اطلاق می شود، هر انبار تنها می تواند در یک مرکز نگهداری تعریف شود\n
CREATE TABLE PLANT (
    ID INT PRIMARY KEY,
    CODE VARCHAR(50),
    TITLE VARCHAR(255),
    BRANCH_TITLE VARCHAR(255),
    STATE VARCHAR(50) COMMENT 'مقادیر شامل: فعال (پیشفرض)، غیر فعال'
);
\n
-- به محلهای فیزیکی برای نگهداری کالاها اطلاق می شود. هر انبار می تواند دارای تقسیم بندی های داخلی نیز باشد\n
CREATE TABLE STORE (
    ID INT PRIMARY KEY,
    CODE VARCHAR(50),
    TITLE VARCHAR(255),
    STORAGE_TYPE_TITLE VARCHAR(255) COMMENT 'لیست نوع انبارها توسط کاربر تعریف می شود',
    STATE VARCHAR(50) COMMENT 'مقادیر شامل: فعال، غیر فعال (پیشفرض)',
    PLANT_REF INT,
    FOREIGN KEY (PLANT_REF) REFERENCES PLANT(ID)
);
\n
-- کلیه اقلامی که در شرکت مورد استفاده قرار میگیرند به عنوان کالا در سیستم تعریف می شود. در صورتی که یک کالا بتواند در تراکنش های انبار استفاده شود  نیاز است نوع انبار های آن تعیین گردد\n
CREATE TABLE PART (
    ID INT PRIMARY KEY,
    CODE VARCHAR(50),
    TITLE VARCHAR(255),
    MAJOR_UNIT_TITLE VARCHAR(255),
    SECONDARY_UNIT_TITLE VARCHAR(255),
    PART_ACCOUNT_CATEGORY_TITLE VARCHAR(255),
    PART_TYPE VARCHAR(50) COMMENT 'مقادیر شامل: ماده اولیه، نیمه ساخته، محصول نهایی، دارایی ثابت، سایر',
    PART_USAGE VARCHAR(255) COMMENT 'مقادیر شامل: خریدنی -  قابل فروش -  خریدنی، قابل فروش - ساختنی - خریدنی، ساختنی - ساختنی، قابل فروش - خریدنی، ساختنی ،قابل فروش - غیرموجودی - خریدنی، غیرموجودی - قابل فروش، غیرموجودی - خریدنی، قابل فروش، غیرموجودی - ساختنی، غیرموجودی - خریدنی، ساختنی، غیرموجودی - قابل فروش، ساختنی، غیرموجودی - خریدنی، قابل فروش، ساختنی، غیر موجودی'
);
\n
-- الگوی سند انبار قالب هایی هستند که تراکنش های انبار از طریق آنها انجام می شود. کلیه ورودیها و خروجهای مجاز برای استفاده در انبارها به صورت الگو تعریف می شوند\n
CREATE TABLE VOUCHER_SPECIFICATION (
    ID INT PRIMARY KEY,
    CODE VARCHAR(50),
    TITLE VARCHAR(255),
    VOUCHER_TYPE VARCHAR(50) COMMENT 'مقادیر شامل: خرید - تولید - مصرف - ضایعات - انتقال بین انبار - فروش - انبارگردانی - امانی - تبدیل کالا - سایر - پایان دوره - ابتدای دوره - تحویل دارایی ثابت',
    DIRECTION VARCHAR(50) COMMENT 'مقادیر شامل: ورودی - خروجی',
    PURCHASE_TYPE VARCHAR(50) COMMENT 'مقادیر شامل: داخلی - خارجی',
    TYPE_OF_EFFECT VARCHAR(50) COMMENT 'مقادیر شامل: دائمی (پیشفرض) - موقت - ضایعات',
    COUNTER_PART_TYPE VARCHAR(50) COMMENT 'مشخص کننده نوع تفصیل مورد نیاز برای هر الگوی سند می باشد. مقادیر شامل:تامین کننده - مشتری - مرکز هزینه - پروژه - طرف حساب امانی - شخص - شرکت'
);
\n
-- گردش های کالا در انبار با استفاده از الگوها در قالب اسناد انبار ذخیره می گردد\n
CREATE TABLE INV_VOUCHER (
    ID INT PRIMARY KEY,
    NUMBER VARCHAR(50),
    DATE DATE,
    TITLE VARCHAR(255),
    DESCRIPTION VARCHAR(255),
    SL_TITLE VARCHAR(255) COMMENT 'عنوان معین',
    STATE VARCHAR(50) COMMENT 'مقادیر شامل: ثبت شده (پیشفرض) - تایید شده - باطل شده',
    FY_TITLE VARCHAR(255) COMMENT 'دوره مالی',
    SUPPLIER_TITLE VARCHAR(255),
    CONTRACTOR_TITLE VARCHAR(255),
    COST_CENTER_TITLE VARCHAR(255),
    PROJECT_TITLE VARCHAR(255),
    CUSTOMER_TITLE VARCHAR(255),
    CARRIER_TITLE VARCHAR(255),
    CONSIGNMENT_PARTY_TITLE VARCHAR(255),
    EMPLOYEE_TITLE VARCHAR(255),
    SALES_PERSON_TITLE VARCHAR(255),
    PURCHASE_ORDER_NO VARCHAR(50),
    PURCHASE_INVOICE_NO VARCHAR(50),
    DELIVER_TO VARCHAR(255),
    COTTAGE_NO VARCHAR(50),
    CUSTOMS_GREEN_SHEET VARCHAR(50),
    ASN_NO VARCHAR(50),
    SALES_ORDER_NO VARCHAR(50),
    SALES_INVOICE_NO VARCHAR(50),
    SALE_ORGANIZATION VARCHAR(255),
    SHOPPING_STORE VARCHAR(255),
    DELIVERY_PERSON VARCHAR(255),
    WEIGHBRIDGE_NO VARCHAR(50),
    PRODUCTION_ORDER_NO VARCHAR(50),
    PRODUCTION_PLAN_NO VARCHAR(50),
    PRODUCTION_OPERATION_NO VARCHAR(50),
    PRODUCTION_SHIFT VARCHAR(50),
    PRODUCTION_DATE DATE,
    QC_INSPECTION_NO VARCHAR(50),
    QC_CHECK_LIST_NO VARCHAR(50),
    QC_LAB_NO VARCHAR(50),
    CONDITIONAL_APPROVAL VARCHAR(255),
    INSPECTION_RESULT VARCHAR(255),
    COA_NO VARCHAR(50),
    TRANSPORTER_NAME VARCHAR(255),
    VEHICLE_NO VARCHAR(50),
    LICENSE_PLATE_NO VARCHAR(50),
    WAYBILL_NO VARCHAR(50),
    WAYBILL_DATE DATE,
    TRANSPORTER_PHONE_NO VARCHAR(50),
    STORE_REF INT COMMENT 'انبار اصلی',
    STORE_REF2 INT COMMENT 'در تراکنش های انتقال، دو انبار وجود دارد. انبار اصلی و انبار مقابل',
    VOUCHER_SPECIFICATION_REF INT,
    FOREIGN KEY (STORE_REF) REFERENCES STORE(ID),
    FOREIGN KEY (STORE_REF2) REFERENCES STORE(ID),
    FOREIGN KEY (VOUCHER_SPECIFICATION_REF) REFERENCES VOUCHER_SPECIFICATION(ID)
);
\n
-- گردش های کالا در انبار با استفاده از الگوها در قالب اسناد انبار به همراه اقلام اسناد انبار ذخیره می گردد. این بیزینس آبجکت جزئیات بیزینس آبجکت قبلی می باشد\n
CREATE TABLE INV_VOUCHER_ITEM (
    ID INT PRIMARY KEY,
    QUANTITY NUMERIC,
    MAJOR_QUANTITY NUMERIC,
    SECOND_UNIT_QUANTITY NUMERIC,
    REMAINED_MAJOR_QUANTITY NUMERIC,
    REMAINED_SECOND_UNIT_QUANTITY NUMERIC,
    RELATED_ITEM_ID INT,
    TEMP_ITEM_ID INT,
    PART_REQUEST_ITEM_ID INT,
    ROW_NUMBER VARCHAR(50),
    SL_TITLE VARCHAR(255) COMMENT 'عنوان معین حسابداری ه در سند حسابداری استفاده شده است',
    SUPPLIER_TITLE VARCHAR(255),
    CONTRACTOR_TITLE VARCHAR(255),
    COST_CENTER_TITLE VARCHAR(255),
    PROJECT_TITLE VARCHAR(255),
    CUSTOMER_TITLE VARCHAR(255),
    CARRIER_TITLE VARCHAR(255),
    CONSIGNMENT_PARTY_TITLE VARCHAR(255),
    EMPLOYEE_TITLE VARCHAR(255),
    SALES_PERSON_TITLE VARCHAR(255),
    PURCHASE_ORDER_NO VARCHAR(50),
    PURCHASE_INVOICE_NO VARCHAR(50),
    DELIVER_TO VARCHAR(255),
    COTTAGE_NO VARCHAR(50),
    CUSTOMS_GREEN_SHEET VARCHAR(50),
    ASN_NO VARCHAR(50),
    SALES_ORDER_NO VARCHAR(50),
    SALES_INVOICE_NO VARCHAR(50),
    SALE_ORGANIZATION VARCHAR(255),
    SHOPPING_STORE VARCHAR(255),
    DELIVERY_PERSON VARCHAR(255),
    WEIGHBRIDGE_NO VARCHAR(50),
    PRODUCTION_ORDER_NO VARCHAR(50),
    PRODUCTION_PLAN_NO VARCHAR(50),
    PRODUCTION_OPERATION_NO VARCHAR(50),
    PRODUCTION_SHIFT VARCHAR(50),
    PRODUCTION_DATE DATE,
    QC_INSPECTION_NO VARCHAR(50),
    QC_CHECK_LIST_NO VARCHAR(50),
    QC_LAB_NO VARCHAR(50),
    CONDITIONAL_APPROVAL VARCHAR(255),
    INSPECTION_RESULT VARCHAR(255),
    COA_NO VARCHAR(50),
    TRANSPORTER_NAME VARCHAR(255),
    VEHICLE_NO VARCHAR(50),
    LICENSE_PLATE_NO VARCHAR(50),
    WAYBILL_NO VARCHAR(50),
    WAYBILL_DATE DATE,
    TRANSPORTER_PHONE_NO VARCHAR(50),
    INVENTORY_VOUCHER_REF INT,
    PART_REF INT,
    UNIT_REF INT,
    FOREIGN KEY (INVENTORY_VOUCHER_REF) REFERENCES INV_VOUCHER(ID),
    FOREIGN KEY (PART_REF) REFERENCES PART(ID),
    FOREIGN KEY (UNIT_REF) REFERENCES UNIT(ID)
);
"""

SQL_GENERATOR_PROMPT_EVAL = """
You are a polite text to sql chatbot for Hamkaran System (همکاران سیستم) users. Your role it to convert a user's question to a sql based on the given database schema.

Given the following tables, your job is to write queries given a user’s request:

<Database Schema>

{schema}

</Database Schema>

Be reasonable and think step-by-step.
Answer the questions based only on the provided schema. Do not assume the existence of tables or information outside the given schema.

User's Question:

<question> 

{question} 

</question>
Output the sql query and nothing else.
"""

