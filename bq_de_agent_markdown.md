author: Google Cloud Data Engineering Team
id: bigquery-data-engineering-codelab
summary: Comprehensive guide to setting up, populating, and validating a Medallion layered architecture in BigQuery.
categories: Data Engineering, BigQuery, Google Cloud
environments: Web
status: Published
feedback link: https://github.com/your-repo/issues

# Codelab: Data Engineering - Preparing Data in BigQuery

## 1. Overview
In this codelab, you will learn how to set up and prepare a data pipeline architecture in Google Cloud BigQuery using a Medallion (layered) data approach. We will walk through cleaning up existing environments, establishing rigorous relational schemas across multiple staging layers, generating programmatic mock data, and writing key validation tests.

### What You'll Learn
* How to structure datasets for a layered data architecture.
* Cleaning up previous database states safely.
* Defining robust BigQuery table schemas (Source, Target, Master Data, Text Enrichment).
* Implementing automated mock data generation directly via standard SQL.
* Authoring integrity checking queries to trace missing joining keys across complex data boundaries.

---

## 2. Environment Architecture Overview
Before executing queries, it is essential to understand the organization of your datasets and tables within the project. The data environment is structured as follows:

| Layer / Purpose | Project ID | Dataset | Table Name |
| :--- | :--- | :--- | :--- |
| **Source (Raw SAP)** | `endless-gasket-348709` | `input_layer` | `actual_sales` |
| **Target (Medallion)** | `endless-gasket-348709` | `final_layer` | `actual_sales_step1` through `step4` |
| **Master Data** | `endless-gasket-348709` | `sap_master` | `MaterialMD`, `PlantMD`, `CustomerMD` |
| **Text Enrichment** | `endless-gasket-348709` | `sap_text` | `kna1`, `but000`, `t077x` |

---

## 3. Step 1: Environment Cleanup
To ensure a clean deployment and avoid conflicts with old schema versions, we start by dropping any existing tables.

Run the following standard BigQuery SQL commands in your workspace[cite: 1]:

```sql
-- 1. CLEANUP
-----------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `endless-gasket-348709.input_layer.actual_sales`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_master.MaterialMD`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_master.CustomerMD`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_master.PlantMD`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_text.kna1`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_text.but000`;
DROP TABLE IF EXISTS `endless-gasket-348709.sap_text.t077x`;
-----------------------------------------------------------------------------------------
```

## 4. Step 2: Create DDL Schemas
Now that the environment is clear, your next phase involves defining the structural properties for each layer. Each master schema handles specific data grain domains.

Execute these DDL statements to construct the empty database structures:

```sql
-- 2. CREATE TABLES (25+ COLUMNS EACH)
-----------------------------------------------------------------------------------------

-- MATERIAL MASTER DATA
CREATE TABLE `endless-gasket-348709.sap_master.MaterialMD` (
  Material_MATERIAL STRING, LanguageKey STRING, Material_MATERIAL_T STRING, MaterialType_MATL_TYPE STRING, MaterialGroup_MATL_GROUP STRING,
  BaseUnit STRING, GrossWeight NUMERIC, NetWeight NUMERIC, WeightUnit STRING, Volume NUMERIC, VolumeUnit STRING, IndustrySector STRING,
  CreatedBy STRING, CreatedOn DATE, ChangedBy STRING, LastChangedOn DATE, Division STRING, ProductHierarchy STRING, Brand STRING,
  EAN_UPC STRING, ExternalMatGroup STRING, Manufacturer STRING, MfrPartNum STRING, DeletionFlag STRING, MaterialCategory STRING
);

-- CUSTOMER MASTER DATA
CREATE TABLE `endless-gasket-348709.sap_master.CustomerMD` (
  Client_MANDT STRING, CustomerNumber_KUNNR STRING, Name1_NAME1 STRING, Name2_NAME2 STRING, CountryKey_LAND1 STRING,
  City_ORT01 STRING, PostalCode_PSTLZ STRING, Region_REGIO STRING, Street_STRAS STRING, Phone_TELF1 STRING, Fax_TELFX STRING,
  AccountGroup_KTOKD STRING, Industry_BRSCH STRING, CreatedOn_ERDAT DATE, CreatedBy_ERNAM STRING, DeletionFlag_LOEVM STRING,
  TaxNum1_STCD1 STRING, TaxNum2_STCD2 STRING, Language_SPRAS STRING, TradingPartner_VBUND STRING, VatRegNum_STCEG STRING,
  NielsenID_NIELS STRING, District_ORT02 STRING, CustomerClass_KUKLA STRING, AuthorizationGroup_BEGRU STRING
);

-- PLANT MASTER DATA
CREATE TABLE `endless-gasket-348709.sap_master.PlantMD` (
  Plant_PLANT STRING, LanguageKey STRING, Plant_PLANT_T STRING, FactoryCalendar STRING, Name2 STRING, HouseNum STRING,
  Street STRING, PoBox STRING, PostalCode STRING, City STRING, Country STRING, Region STRING, TaxJurisdiction STRING,
  PurchasingOrg STRING, SalesOrg STRING, DistChannel STRING, Division STRING, Category STRING, BatchMgmt STRING,
  SourceList STRING, ReqPlanning STRING, ValuationArea STRING, CustomerNum STRING, VendorNum STRING, MaintenancePlant STRING
);

-- TEXT ENRICHMENT TABLES
CREATE TABLE `endless-gasket-348709.sap_text.kna1` (
  MANDT STRING, KUNNR STRING, NAME1 STRING, LAND1 STRING, ORT01 STRING, PSTLZ STRING, REGIO STRING, STRAS STRING, TELF1 STRING, TELFX STRING,
  KTOKD STRING, BRSCH STRING, ERDAT DATE, ERNAM STRING, LOEVM STRING, STCD1 STRING, STCD2 STRING, SPRAS STRING, VBUND STRING, STCEG STRING,
  NIELS STRING, ORT02 STRING, KUKLA STRING, BEGRU STRING, ADRNR STRING
);

CREATE TABLE `endless-gasket-348709.sap_text.but000` (
  CLIENT STRING, PARTNER STRING, TYPE STRING, BP_CATEGORY STRING, BP_GROUP STRING, NAME_ORG1 STRING, NAME_ORG2 STRING,
  NAME_LAST STRING, NAME_FIRST STRING, TITLE STRING, LANGU STRING, SEARCHTERM1 STRING, SEARCHTERM2 STRING,
  BIRTH_DATE DATE, VALID_FROM DATE, VALID_TO DATE, NATION STRING, HOUSE_NUM STRING, STREET STRING, CITY STRING,
  POSTAL_CODE STRING, COUNTRY STRING, REGION STRING, TEL_NUMBER STRING, SMTP_ADDR STRING
);

CREATE TABLE `endless-gasket-348709.sap_text.t077x` (
  MANDT STRING, SPRAS STRING, KTOKD STRING, TXT30 STRING, TXT15 STRING,
  F1 STRING, F2 STRING, F3 STRING, F4 STRING, F5 STRING, F6 STRING, F7 STRING, F8 STRING, F9 STRING, F10 STRING,
  F11 STRING, F12 STRING, F13 STRING, F14 STRING, F15 STRING, F16 STRING, F17 STRING, F18 STRING, F19 STRING, F20 STRING, F21 STRING
);

-- TRANSACTIONAL INPUT LAYER
CREATE TABLE `endless-gasket-348709.input_layer.actual_sales` (
  record INT64, doc_number STRING, material STRING, sold_to STRING, plant STRING, cust_class STRING, calday DATE,
  _bic_bill_date DATE, bic_inv_bkd NUMERIC, _s_ord_item STRING, _bic_bill_item STRING, doc_currcy STRING,
  fiscper STRING, fiscyear STRING, salesorg STRING, distr_chan STRING, division STRING,
  zs_netrev NUMERIC, zs_taxamt NUMERIC, zs_grossamt NUMERIC, unit_of_wt STRING, nt_wt_kg NUMERIC,
  gr_wt_kg NUMERIC, opflag STRING, created_by STRING
);
-----------------------------------------------------------------------------------------
```


## 5. Step 3: Populate Mock Data
To facilitate automated testing pipelines without relying on external file uploads, we use BigQuery's relational array mechanics (`UNNEST(GENERATE_ARRAY(...))`) to construct mock history. 

Execute this data initialization script to load 100 synchronized entities across all relational domains:


```sql
-- 3. POPULATE DATA (100 RECORDS)
-----------------------------------------------------------------------------------------

-- Populate Material Master (IDs: MAT-100 to MAT-199)
INSERT INTO `endless-gasket-348709.sap_master.MaterialMD` (Material_MATERIAL, LanguageKey, Material_MATERIAL_T, GrossWeight, NetWeight, WeightUnit)
SELECT CONCAT('MAT-', CAST(i AS STRING)), 'E', CONCAT('Material ', CAST(i AS STRING)), CAST(10.5 + i AS NUMERIC), CAST(9.0 + i AS NUMERIC), 'KG'
FROM UNNEST(GENERATE_ARRAY(100, 199)) AS i;

-- Populate Customer Master (IDs: CUST-1001 to CUST-1100)
INSERT INTO `endless-gasket-348709.sap_master.CustomerMD` (Client_MANDT, CustomerNumber_KUNNR, Name1_NAME1, CountryKey_LAND1, AccountGroup_KTOKD)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('Cust Name ', CAST(i AS STRING)), 'US', '0001'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate Plant Master (IDs: PLNT-10 to PLNT-109)
INSERT INTO `endless-gasket-348709.sap_master.PlantMD` (Plant_PLANT, LanguageKey, Plant_PLANT_T, Country)
SELECT CONCAT('PLNT-', CAST(i AS STRING)), 'E', CONCAT('Plant Hub ', CAST(i AS STRING)), 'US'
FROM UNNEST(GENERATE_ARRAY(10, 109)) AS i;

-- Populate KNA1 Customer Localization Text
INSERT INTO `endless-gasket-348709.sap_text.kna1` (MANDT, KUNNR, NAME1, LAND1)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('Legal Ent ', CAST(i AS STRING)), 'US'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate BUT000 Business Partner Context
INSERT INTO `endless-gasket-348709.sap_text.but000` (CLIENT, PARTNER, NAME_ORG1, BP_GROUP)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('BP Org ', CAST(i AS STRING)), 'GRP1'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate T077X Account Group Definitions
INSERT INTO `endless-gasket-348709.sap_text.t077x` (MANDT, SPRAS, KTOKD, TXT30)
VALUES ('012', 'E', '0001', 'Standard Customer');

-- Populate Base Actual Sales Records (Mapped dynamically to valid entities)
INSERT INTO `endless-gasket-348709.input_layer.actual_sales` (record, doc_number, material, sold_to, plant, cust_class, calday, _bic_bill_date, zs_netrev, bic_inv_bkd, zs_taxamt, zs_grossamt, nt_wt_kg, gr_wt_kg)
SELECT
  i, 
  CONCAT('DOC-', CAST(5000+i AS STRING)), 
  CONCAT('MAT-', CAST(100+i AS STRING)), 
  CONCAT('CUST-', CAST(1000+i AS STRING)),
  CONCAT('PLNT-', CAST(10+i AS STRING)), 
  '0001', 
  CURRENT_DATE(), 
  CURRENT_DATE(),
  CAST(500.00 * i AS NUMERIC), 
  CAST(1.0 * i AS NUMERIC), 
  CAST(50.0 * i AS NUMERIC), 
  CAST(550.0 * i AS NUMERIC), 
  CAST(9.0 + i AS NUMERIC), 
  CAST(10.5 + i AS NUMERIC)
FROM UNNEST(GENERATE_ARRAY(1, 100)) AS i;
-----------------------------------------------------------------------------------------
```

---

## 6. Step 4: Verification & Validation Testing
Before shipping upstream Medallion layer updates (`actual_sales_step1` through `step4`), data engineers must ensure zero relational drift. We accomplish this using two core testing patterns.

### Test 1: Full Inner Join Traceability
This test verifies whether transactional facts correctly trace cleanly across dimensions using strict `INNER JOIN` conditions.

```sql
SELECT
  -- Transactional Data
  s.record,
  s.doc_number AS sales_document,
  s.calday AS posting_date,
  s.zs_netrev AS net_revenue,
  -- Material Master Data
  m.Material_MATERIAL AS mat_id,
  m.Material_MATERIAL_T AS material_description,
  m.GrossWeight AS mat_gross_weight,
  -- Plant Master Data
  p.Plant_PLANT AS plant_id,
  p.Plant_PLANT_T AS plant_name,
  -- Customer Master & Text Data
  c.CustomerNumber_KUNNR AS customer_id,
  k.NAME1 AS customer_legal_name,
  b.NAME_ORG1 AS business_partner_org,
  -- Account Group Text
  t.TXT30 AS account_group_desc
FROM `endless-gasket-348709.input_layer.actual_sales` AS s
INNER JOIN `endless-gasket-348709.sap_master.MaterialMD` AS m
  ON s.material = m.Material_MATERIAL AND m.LanguageKey = 'E'
INNER JOIN `endless-gasket-348709.sap_master.PlantMD` AS p
  ON s.plant = p.Plant_PLANT AND p.LanguageKey = 'E'
INNER JOIN `endless-gasket-348709.sap_master.CustomerMD` AS c
  ON s.sold_to = c.CustomerNumber_KUNNR AND c.Client_MANDT = '012'
INNER JOIN `endless-gasket-348709.sap_text.kna1` AS k
  ON s.sold_to = k.KUNNR AND k.MANDT = '012'
INNER JOIN `endless-gasket-348709.sap_text.but000` AS b
  ON s.sold_to = b.PARTNER AND b.CLIENT = '012'
INNER JOIN `endless-gasket-348709.sap_text.t077x` AS t
  ON s.cust_class = t.KTOKD AND t.MANDT = '012' AND t.SPRAS = 'E'
ORDER BY s.record ASC;
```

### Test 2: Relational Integrity Check
This diagnostic script relies on `LEFT JOIN` mechanics combined with `COUNTIF` checks to quickly isolate unmatched foreign key footprints. 

> **Success Evaluation Criterion:** Every diagnostic `missing_*_matches` indicator count metric output **must read exactly 0**.

```sql
SELECT
  COUNT(*) AS total_sales_records,
  -- If any of these counts are > 0, that dimension is missing joining keys!
  COUNTIF(m.Material_MATERIAL IS NULL) AS missing_material_matches,
  COUNTIF(p.Plant_PLANT IS NULL) AS missing_plant_matches,
  COUNTIF(c.CustomerNumber_KUNNR IS NULL) AS missing_customer_matches,
  COUNTIF(k.KUNNR IS NULL) AS missing_kna1_text_matches,
  COUNTIF(b.PARTNER IS NULL) AS missing_but000_text_matches,
  COUNTIF(t.KTOKD IS NULL) AS missing_t077x_text_matches
FROM `endless-gasket-348709.input_layer.actual_sales` AS s
LEFT JOIN `endless-gasket-348709.sap_master.MaterialMD` AS m
  ON s.material = m.Material_MATERIAL AND m.LanguageKey = 'E'
LEFT JOIN `endless-gasket-348709.sap_master.PlantMD` AS p
  ON s.plant = p.Plant_PLANT AND p.LanguageKey = 'E'
LEFT JOIN `endless-gasket-348709.sap_master.CustomerMD` AS c
  ON s.sold_to = c.CustomerNumber_KUNNR AND c.Client_MANDT = '012'
LEFT JOIN `endless-gasket-348709.sap_text.kna1` AS k
  ON s.sold_to = k.KUNNR AND k.MANDT = '012'
LEFT JOIN `endless-gasket-348709.sap_text.but000` AS b
  ON s.sold_to = b.PARTNER AND b.CLIENT = '012'
LEFT JOIN `endless-gasket-348709.sap_text.t077x` AS t
  ON s.cust_class = t.KTOKD AND t.MANDT = '012' AND t.SPRAS = 'E';
```

