author: Google Cloud Data Engineering Team
id: bigquery-data-engineering-codelab
summary: A comprehensive, hands-on course for setting up, populating, and validating a Medallion layered architecture in Google Cloud BigQuery.
categories: Data Engineering, BigQuery, Google Cloud
environments: Web
status: Published
feedback link: https://github.com/your-repo/issues

# Codelab: Demonstrating the Data Engineering Agent in BigQuery

## Overview
Welcome to this comprehensive course showcasing the capabilities of the **Data Engineering (DE) Agent** in Google Cloud! 

**The Origin of the Data Engineering Agent**
Recently introduced as a core pillar of Google Cloud's AI-driven data ecosystem, the Data Engineering Agent is deeply powered by Google's state-of-the-art Gemini foundational models. Born out of the need to reduce the operational overhead on data engineering teams, it was built specifically to understand deep data contexts, enterprise schemas, and complex transformation logic. By integrating directly into the BigQuery and Dataform workspaces, it bridges the gap between high-level business logic and low-level pipeline execution.

**Core Capabilities of the Data Engineering Agent**
The Data Engineering Agent is designed to revolutionize how data professionals build, manage, and scale data pipelines. Its robust capabilities include:
* **Natural Language to Pipeline Code**: Seamlessly translates plain-English requirements into production-grade SQL and complex Dataform configurations.
* **Context-Aware Schema Operations**: Intelligently analyzes existing table structures to autonomously determine optimal join keys, cast data types, and apply transformations without manual mapping.
* **Automated Data Quality & Assertions**: Proactively generates and enforces data quality checks (such as null-checks and uniqueness) to maintain downstream data integrity.
* **Pipeline Debugging and Course Correction**: Capable of ingesting error logs and user feedback to dynamically refactor and fix broken SQL logic on the fly.
* **Architectural Governance**: Autonomously enforces industry best practices—such as proper table partitioning and structured Medallion layering.

The primary purpose of this codelab is to **demonstrate the Data Engineering Agent in action**. We will use the agent to collaboratively design, set up, and validate a robust data pipeline architecture using the highly regarded **Medallion (layered) data approach**. 

By establishing a baseline environment and then prompting the Data Engineering Agent, we will guide you step-by-step through:
1. Safely cleaning up and initializing our foundational data environment.
2. Generating synthetic mock data and preparing the initial source schemas.
3. Utilizing the Data Engineering Agent to systematically generate Dataform pipeline modules (from Bronze to Gold layers).
4. Iteratively refining pipelines, validating integrity, and enforcing data quality through AI-assisted engineering.

### What You'll Learn
* **AI-Assisted Data Engineering**: How to effectively interact with the Data Engineering Agent using modular prompts to generate complex data pipelines.
* **Agent Capabilities**: Discover what the Data Engineering Agent can do—from automated schema transformations and data standardization to intelligent table joins and logic corrections.
* **Medallion Architecture**: Using the Data Engineering Agent to build scalable Bronze, Silver, and Gold data layers in BigQuery.
* **Production Dataform Frameworks**: Implementing the Data Engineering Agent alongside Google Cloud Dataform to build auditable, dependency-driven data workflows.
* **Prompt Engineering for DE**: Best practices for structuring prompts to ensure the agent writes code that complies with strict data governance and relational standards.

---

## Environment Architecture Overview
Before we begin writing any code, it is critical to understand the layout of our datasets and tables. A well-organized environment prevents confusion and enforces data governance. 

Our data environment is structured into specific layers and domains as follows:

| Layer / Purpose | Dataset | Table Name | Description |
| :--- | :--- | :--- | :--- |
| **Source (Raw SAP)** | `input_layer` | `actual_sales` | Contains the raw, uncleaned transactional sales data extracted from SAP.<br>Acts as the foundational Bronze layer for our pipeline. |
| **Target (Medallion)** | `final_layer` | `actual_sales_step1`, `actual_sales_step2`, `actual_sales_step3` | Holds the refined, enriched, and aggregated sales models.<br>Represents the Silver and Gold tiers for business reporting. |
| **Master Data** | `sap_master` | `MaterialMD`, `PlantMD`, `CustomerMD` | Stores key dimensional attributes for materials, plants, and customers.<br>Used to enrich raw transactions with contextual meaning. |
| **Text Enrichment** | `sap_text` | `kna1`, `but000`, `t077x` | Provides human-readable localization strings and text descriptions.<br>Ensures that final reports are easily understood by business users. |

Take a moment to familiarize yourself with these datasets. The `input_layer` acts as our Bronze layer, capturing raw data, while the `final_layer` will serve as our refined Silver/Gold layers.

---

## Step 1: Environment Cleanup
To ensure a clean deployment and avoid conflicts with any legacy schema versions, our first step is to clean the slate.

By dropping existing tables before recreation, we guarantee that our pipeline starts from a known, predictable state.

Run the following standard BigQuery SQL commands in your workspace:

```sql
-- 1. CLEANUP: Resetting the environment to a pristine state
-----------------------------------------------------------------------------------------
DROP TABLE IF EXISTS `Your_GCP_ProjectID.input_layer.actual_sales`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_master.MaterialMD`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_master.CustomerMD`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_master.PlantMD`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_text.kna1`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_text.but000`;
DROP TABLE IF EXISTS `Your_GCP_ProjectID.sap_text.t077x`;
-----------------------------------------------------------------------------------------
```

## Step 2: Create DDL Schemas
With our environment clear, we transition to the schema definition phase. Here, we use Data Definition Language (DDL) to explicitly define the structural properties of our tables. 

Each schema is tailored to handle specific data grain domains—ranging from transaction facts (sales) to descriptive dimensions (material, plant, and customer master data).

Execute these DDL statements to construct your database structures:

```sql
-- 2. CREATE TABLES: Defining schemas with 25+ attributes each
-----------------------------------------------------------------------------------------

-- MATERIAL MASTER DATA
CREATE TABLE `Your_GCP_ProjectID.sap_master.MaterialMD` (
  Material_MATERIAL STRING, LanguageKey STRING, Material_MATERIAL_T STRING, MaterialType_MATL_TYPE STRING, MaterialGroup_MATL_GROUP STRING,
  BaseUnit STRING, GrossWeight NUMERIC, NetWeight NUMERIC, WeightUnit STRING, Volume NUMERIC, VolumeUnit STRING, IndustrySector STRING,
  CreatedBy STRING, CreatedOn DATE, ChangedBy STRING, LastChangedOn DATE, Division STRING, ProductHierarchy STRING, Brand STRING,
  EAN_UPC STRING, ExternalMatGroup STRING, Manufacturer STRING, MfrPartNum STRING, DeletionFlag STRING, MaterialCategory STRING
);

-- CUSTOMER MASTER DATA
CREATE TABLE `Your_GCP_ProjectID.sap_master.CustomerMD` (
  Client_MANDT STRING, CustomerNumber_KUNNR STRING, Name1_NAME1 STRING, Name2_NAME2 STRING, CountryKey_LAND1 STRING,
  City_ORT01 STRING, PostalCode_PSTLZ STRING, Region_REGIO STRING, Street_STRAS STRING, Phone_TELF1 STRING, Fax_TELFX STRING,
  AccountGroup_KTOKD STRING, Industry_BRSCH STRING, CreatedOn_ERDAT DATE, CreatedBy_ERNAM STRING, DeletionFlag_LOEVM STRING,
  TaxNum1_STCD1 STRING, TaxNum2_STCD2 STRING, Language_SPRAS STRING, TradingPartner_VBUND STRING, VatRegNum_STCEG STRING,
  NielsenID_NIELS STRING, District_ORT02 STRING, CustomerClass_KUKLA STRING, AuthorizationGroup_BEGRU STRING
);

-- PLANT MASTER DATA
CREATE TABLE `Your_GCP_ProjectID.sap_master.PlantMD` (
  Plant_PLANT STRING, LanguageKey STRING, Plant_PLANT_T STRING, FactoryCalendar STRING, Name2 STRING, HouseNum STRING,
  Street STRING, PoBox STRING, PostalCode STRING, City STRING, Country STRING, Region STRING, TaxJurisdiction STRING,
  PurchasingOrg STRING, SalesOrg STRING, DistChannel STRING, Division STRING, Category STRING, BatchMgmt STRING,
  SourceList STRING, ReqPlanning STRING, ValuationArea STRING, CustomerNum STRING, VendorNum STRING, MaintenancePlant STRING
);

-- TEXT ENRICHMENT TABLES
CREATE TABLE `Your_GCP_ProjectID.sap_text.kna1` (
  MANDT STRING, KUNNR STRING, NAME1 STRING, LAND1 STRING, ORT01 STRING, PSTLZ STRING, REGIO STRING, STRAS STRING, TELF1 STRING, TELFX STRING,
  KTOKD STRING, BRSCH STRING, ERDAT DATE, ERNAM STRING, LOEVM STRING, STCD1 STRING, STCD2 STRING, SPRAS STRING, VBUND STRING, STCEG STRING,
  NIELS STRING, ORT02 STRING, KUKLA STRING, BEGRU STRING, ADRNR STRING
);

CREATE TABLE `Your_GCP_ProjectID.sap_text.but000` (
  CLIENT STRING, PARTNER STRING, TYPE STRING, BP_CATEGORY STRING, BP_GROUP STRING, NAME_ORG1 STRING, NAME_ORG2 STRING,
  NAME_LAST STRING, NAME_FIRST STRING, TITLE STRING, LANGU STRING, SEARCHTERM1 STRING, SEARCHTERM2 STRING,
  BIRTH_DATE DATE, VALID_FROM DATE, VALID_TO DATE, NATION STRING, HOUSE_NUM STRING, STREET STRING, CITY STRING,
  POSTAL_CODE STRING, COUNTRY STRING, REGION STRING, TEL_NUMBER STRING, SMTP_ADDR STRING
);

CREATE TABLE `Your_GCP_ProjectID.sap_text.t077x` (
  MANDT STRING, SPRAS STRING, KTOKD STRING, TXT30 STRING, TXT15 STRING,
  F1 STRING, F2 STRING, F3 STRING, F4 STRING, F5 STRING, F6 STRING, F7 STRING, F8 STRING, F9 STRING, F10 STRING,
  F11 STRING, F12 STRING, F13 STRING, F14 STRING, F15 STRING, F16 STRING, F17 STRING, F18 STRING, F19 STRING, F20 STRING, F21 STRING
);

-- TRANSACTIONAL INPUT LAYER
CREATE TABLE `Your_GCP_ProjectID.input_layer.actual_sales` (
  record INT64, doc_number STRING, material STRING, sold_to STRING, plant STRING, cust_class STRING, calday DATE,
  _bic_bill_date DATE, bic_inv_bkd NUMERIC, _s_ord_item STRING, _bic_bill_item STRING, doc_currcy STRING,
  fiscper STRING, fiscyear STRING, salesorg STRING, distr_chan STRING, division STRING,
  zs_netrev NUMERIC, zs_taxamt NUMERIC, zs_grossamt NUMERIC, unit_of_wt STRING, nt_wt_kg NUMERIC,
  gr_wt_kg NUMERIC, opflag STRING, created_by STRING
);
-----------------------------------------------------------------------------------------
```


## Step 3: Populate Mock Data
Developing and testing data pipelines often requires realistic datasets. However, relying on production data during development poses security risks and operational bottlenecks. 

To bypass this, we will use BigQuery's powerful array generation mechanics (`UNNEST(GENERATE_ARRAY(...))`) to synthetically construct mock transaction history and master data. This ensures we have a fully functional, self-contained test environment.

Execute the following script to systematically generate 100 synchronized entities across all domains:

```sql
-- 3. POPULATE DATA: Generating synthetic records for testing
-----------------------------------------------------------------------------------------

-- Populate Material Master (IDs: MAT-100 to MAT-199)
INSERT INTO `Your_GCP_ProjectID.sap_master.MaterialMD` (Material_MATERIAL, LanguageKey, Material_MATERIAL_T, GrossWeight, NetWeight, WeightUnit)
SELECT CONCAT('MAT-', CAST(i AS STRING)), 'E', CONCAT('Material ', CAST(i AS STRING)), CAST(10.5 + i AS NUMERIC), CAST(9.0 + i AS NUMERIC), 'KG'
FROM UNNEST(GENERATE_ARRAY(100, 199)) AS i;

-- Populate Customer Master (IDs: CUST-1001 to CUST-1100)
INSERT INTO `Your_GCP_ProjectID.sap_master.CustomerMD` (Client_MANDT, CustomerNumber_KUNNR, Name1_NAME1, CountryKey_LAND1, AccountGroup_KTOKD)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('Cust Name ', CAST(i AS STRING)), 'US', '0001'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate Plant Master (IDs: PLNT-10 to PLNT-109)
INSERT INTO `Your_GCP_ProjectID.sap_master.PlantMD` (Plant_PLANT, LanguageKey, Plant_PLANT_T, Country)
SELECT CONCAT('PLNT-', CAST(i AS STRING)), 'E', CONCAT('Plant Hub ', CAST(i AS STRING)), 'US'
FROM UNNEST(GENERATE_ARRAY(10, 109)) AS i;

-- Populate KNA1 Customer Localization Text
INSERT INTO `Your_GCP_ProjectID.sap_text.kna1` (MANDT, KUNNR, NAME1, LAND1)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('Legal Ent ', CAST(i AS STRING)), 'US'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate BUT000 Business Partner Context
INSERT INTO `Your_GCP_ProjectID.sap_text.but000` (CLIENT, PARTNER, NAME_ORG1, BP_GROUP)
SELECT '012', CONCAT('CUST-', CAST(i AS STRING)), CONCAT('BP Org ', CAST(i AS STRING)), 'GRP1'
FROM UNNEST(GENERATE_ARRAY(1001, 1100)) AS i;

-- Populate T077X Account Group Definitions
INSERT INTO `Your_GCP_ProjectID.sap_text.t077x` (MANDT, SPRAS, KTOKD, TXT30)
VALUES ('012', 'E', '0001', 'Standard Customer');

-- Populate Base Actual Sales Records (Mapped dynamically to valid entities)
INSERT INTO `Your_GCP_ProjectID.input_layer.actual_sales` (record, doc_number, material, sold_to, plant, cust_class, calday, _bic_bill_date, zs_netrev, bic_inv_bkd, zs_taxamt, zs_grossamt, nt_wt_kg, gr_wt_kg)
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

## Step 4: Verification & Validation Testing
Before migrating data upstream into our Medallion layer updates (`actual_sales_step1` through `step4`), data engineers must ensure zero relational drift. Missing foreign keys or duplicate records can cause downstream reporting errors. We accomplish this using two core testing patterns.

### Test 1: Full Inner Join Traceability
This test verifies whether transactional facts correctly map to their descriptive dimensions. By using strict `INNER JOIN` conditions, any transaction missing a corresponding master data record will be automatically excluded, immediately highlighting data integrity issues.

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
FROM `Your_GCP_ProjectID.input_layer.actual_sales` AS s
INNER JOIN `Your_GCP_ProjectID.sap_master.MaterialMD` AS m
  ON s.material = m.Material_MATERIAL AND m.LanguageKey = 'E'
INNER JOIN `Your_GCP_ProjectID.sap_master.PlantMD` AS p
  ON s.plant = p.Plant_PLANT AND p.LanguageKey = 'E'
INNER JOIN `Your_GCP_ProjectID.sap_master.CustomerMD` AS c
  ON s.sold_to = c.CustomerNumber_KUNNR AND c.Client_MANDT = '012'
INNER JOIN `Your_GCP_ProjectID.sap_text.kna1` AS k
  ON s.sold_to = k.KUNNR AND k.MANDT = '012'
INNER JOIN `Your_GCP_ProjectID.sap_text.but000` AS b
  ON s.sold_to = b.PARTNER AND b.CLIENT = '012'
INNER JOIN `Your_GCP_ProjectID.sap_text.t077x` AS t
  ON s.cust_class = t.KTOKD AND t.MANDT = '012' AND t.SPRAS = 'E'
ORDER BY s.record ASC;
```

### Test 2: Relational Integrity Check
While the previous test drops invalid rows, this diagnostic script relies on `LEFT JOIN` mechanics combined with `COUNTIF` checks to quickly isolate and flag unmatched foreign key footprints without removing them. 

> **Success Evaluation Criterion:** For a perfectly synchronized environment, every diagnostic `missing_*_matches` indicator count metric output **must read exactly 0**.

```sql
SELECT
  COUNT(*) AS total_sales_records,
  -- A count > 0 indicates missing joining keys in the specified dimension!
  COUNTIF(m.Material_MATERIAL IS NULL) AS missing_material_matches,
  COUNTIF(p.Plant_PLANT IS NULL) AS missing_plant_matches,
  COUNTIF(c.CustomerNumber_KUNNR IS NULL) AS missing_customer_matches,
  COUNTIF(k.KUNNR IS NULL) AS missing_kna1_text_matches,
  COUNTIF(b.PARTNER IS NULL) AS missing_but000_text_matches,
  COUNTIF(t.KTOKD IS NULL) AS missing_t077x_text_matches
FROM `Your_GCP_ProjectID.input_layer.actual_sales` AS s
LEFT JOIN `Your_GCP_ProjectID.sap_master.MaterialMD` AS m
  ON s.material = m.Material_MATERIAL AND m.LanguageKey = 'E'
LEFT JOIN `Your_GCP_ProjectID.sap_master.PlantMD` AS p
  ON s.plant = p.Plant_PLANT AND p.LanguageKey = 'E'
LEFT JOIN `Your_GCP_ProjectID.sap_master.CustomerMD` AS c
  ON s.sold_to = c.CustomerNumber_KUNNR AND c.Client_MANDT = '012'
LEFT JOIN `Your_GCP_ProjectID.sap_text.kna1` AS k
  ON s.sold_to = k.KUNNR AND k.MANDT = '012'
LEFT JOIN `Your_GCP_ProjectID.sap_text.but000` AS b
  ON s.sold_to = b.PARTNER AND b.CLIENT = '012'
LEFT JOIN `Your_GCP_ProjectID.sap_text.t077x` AS t
  ON s.cust_class = t.KTOKD AND t.MANDT = '012' AND t.SPRAS = 'E';
```

---

## Supplemental Guide: Production Dataform Framework & Modules
In modern data engineering, managing SQL scripts manually is prone to error and difficult to track. This section outlines the governance framework and specific script configurations required to modernize and enrich SAP BW tables using **Google Cloud Dataform**, a service designed to manage data transformations in BigQuery.

### Part 1: The Production Framework (Standards & Protocol)
All subsequent Dataform modules must adhere strictly to the following architectural standards and execution behaviors to maintain code quality.

### Step 1: Open BigQuery in GCP Console
Navigate to the Google Cloud Console, select your project, and open the **BigQuery** console from the navigation menu.
In the BigQuery explorer sidebar, look for the **Pipelines** dropdown menu. Click the three dots (options menu) next to Pipelines and select **Create pipeline**.

<img src="img/ss1.png" alt="GCP BigQuery Navigation" width="400">

### Step 2: Rename Pipeline and Start Agent
Organization is key. Rename the pipeline from **Untitled pipeline** to a descriptive name, such as **DE_Agent_Pipeline**. Once renamed, click on `Ask Agent` in the top menu to initiate our AI-assisted workflow.

<img src="img/ss2.png" alt="Create Pipeline Context Menu" width="400">

A prompt window will open at the bottom of the screen. Click on `Pipeline instructions` to open a new context window with the filename `GEMINI.md`. This is where we define the rules for our agent.

Copy the comprehensive instruction block below into the file and save it. These rules ensure the agent writes code that complies with our Dataform standards:

```text
Objective: Act as a Lead GCP Data Engineer. Develop a production-grade suite of individual Dataform .sqlx files to modernize and enrich SAP BW tables in BigQuery. The goal is to build a modular, auditable, and high-performance data pipeline following the "Medallion Architecture" logic .
Technical Context:
Initial Source: Your_GCP_ProjectID.input_layer.actual_sales
Target Dataset: final_layer
Master Data Source: Your_GCP_ProjectID.sap_master
Text Data Source: Your_GCP_ProjectID.sap_text
Dataform Best Practices (Required for ALL scripts):
Config Block: Use type: "table". Include the tag ["zinbobu_agent"] and a comprehensive description field summarizing the job's business purpose.
Dependency Management: Exclusively use the ref() function to establish the transformation chain: Job 1 -> Job 2 -> Job 3 -> Job 4.
Auditability: Every transformation and rename must be explained with inline SQL comments.
Data Quality: Include an assertions block in relevant scripts to check for null values in primary key columns or row uniqueness.
CRITICAL EXECUTION PROTOCOL:
Modular Execution: You are to generate code for one Job at a time only .
Pause & Wait: After completing the requested Job, you must explicitly ask me for the instruction for the next module 
No Leapfrogging: Do not generate logic for future Jobs (e.g., joins or renames) until that specific Job is requested 
```

After updating the instructions, commit and push the changes to your code repository. The interface should resemble the following:

<img src="img/ss_gemini.png" alt="instructions file" width="400">

Returning to the previous window, you should now see a confirmation indicating `one instruction file added`. Click save to finalize the setup.

<img src="img/ss_agent_instructions.png" alt="agent instructions" width="400">

---

## Module 1: Raw Ingestion
In this section, we begin building out our data pipeline module by module. Our first objective is to construct the foundational **Bronze/Raw Ingestion Layer**.

Navigate to the pipeline canvas, open the **Ask Agent** popup, and provide the following prompt for Module 1:

```text
Module 1: Raw Ingestion (Job 1)
Instruction: Based on the common requirements provided, create the first module: actual_sales_step1.sqlx.
Task: Select all columns and rows from the actual_sales source table.
Formatting: Ensure the config block includes a description identifying this as the "Bronze/Raw Ingestion Layer".
```

The agent will process your prompt and intelligently generate the corresponding SQLX pipeline code.

<img src="img/ss5.png" alt="Module 1" width="400">

Upon executing this generated pipeline, you will find that the new table `actual_sales_step1` has been successfully created under the `final_layer` dataset, maintaining a 1:1 parity with the source data.

<img src="img/ss_mod1.png" alt="Module 1 Output" width="400">

## Module 2: Standardization & Schema Cleaning
With raw data ingested, the next logical step in our architecture is standardizing the schema. This involves stripping out technical prefixes to make the data more accessible to analysts.

Provide the following prompt to the agent for Module 2:

```text
Module 2: Standardization & Schema Cleaning (Job 2)
Instruction: Based on the common requirements, create actual_sales_step2.sqlx.
Dependency: This script must reference actual_sales_step1.
Task: Clean technical prefixes from all column names. Specifically, strip _bic_, bic_, or a leading _ (e.g., _bic_bill_date becomes bill_date).
Audit Requirement: For every renamed column, add an inline SQL comment -- Renamed from [Original Name].
```

Observe how the agent updates the pipeline to include the schema cleaning logic.

<img src="img/ss6.png" alt="Module 2 Generation" width="400">

After running the pipeline, the `actual_sales_step2` table is created in the `final_layer` dataset, showcasing clean, user-friendly column names.

<img src="img/ss_mod2.png" alt="Module 2 Output" width="400">

## Module 3: Master Data Enrichment
Raw transactional data is often cryptic (e.g., storing a Material ID but not the Material Name). In this module, we enrich our transactions by joining them against descriptive master datasets.

Provide the following prompt to build Module 3:

```text
Module 3: Master Data Enrichment (Job 3)
Instruction: Based on the common requirements, create actual_sales_step3.sqlx.
Dependency: Reference actual_sales_step2.
Join Logic (Material): LEFT JOIN with MaterialMD. Select MaterialType, MaterialGroup, Product_ZPRODUCTC, and BrandName_CBRANDNME_T.
Join Logic (Plant): LEFT JOIN with PlantMD. Select MillR_GRMILL, Plant_PLANT, and PlantType_ZPLNTTYP.
Standards: Filter both joins by LanguageKey = 'E' to prevent duplicate records.
```

The agent will seamlessly weave the `LEFT JOIN` logic into our transformation chain.

<img src="img/ss7.png" alt="Module 3 Generation" width="400">

Executing this pipeline yields the `actual_sales_step3` table, now brimming with descriptive material and plant information.

<img src="img/ss_mod3.png" alt="Module 3 Output" width="400">

## Module 4: Human-Readable Text Enrichment
To complete our Gold/Final layer, we must attach localization and human-readable text enrichment from our SAP text tables. This ensures dashboards and reports are intuitive for business users.

Use the following prompt for Module 4:

```text
Module 4: Human-Readable Text Enrichment (Job 4)
Instruction: Based on the common requirements, create the final module: actual_sales_step4.sqlx.
Dependency: Reference actual_sales_step3.
Enrichment Task: Join with text tables kna1, but000, and t077x.
Text Standards: Filter by Language ('E') and SAP Client ('012').
Selection: Retrieve NAME1 from kna1 and TXT30 from t077x and text fields from but000. Use unique table aliases for each join.
```

The agent processes the final enrichment step, completing the core pipeline logic.

<img src="img/ss8.png" alt="Module 4 Generation" width="400">

## Module 5: Extending Enrichment Iteratively
In real-world scenarios, requirements evolve, and you may need to amend previous modules. Here, we demonstrate how to request an enhancement to an existing step.

Provide the following prompt to enhance Module 3 with customer data:

```text
Module 5: Master Data Enrichment Extension
Instruction: Based on the common requirements, enhance actual_sales_step3.sqlx.
Dependency: Reference actual_sales_step2.
Join Logic (CustomerMD): LEFT JOIN with CustomerMD. Identify the relevant joining keys and fetch the relevant fields from CustomerMD.
Standards: Filter both joins by LanguageKey = 'E' to prevent duplicate records.
```

The agent thoughtfully refactors the pipeline graph to incorporate this new requirement.

<img src="img/ss9.png" alt="Module 5 Generation" width="400">

## Module 6: Course Corrections
AI agents, much like human engineers, occasionally need specific constraints reiterated. If a column is inappropriately renamed, you can effortlessly instruct the agent to correct its behavior.

Provide the following correction prompt:

```text
Module 6: Master Data Enrichment - Correction
Instruction: Based on the common requirements, enhance actual_sales_step3.sqlx.
Dependency: Reference actual_sales_step2.
I need a correction to the script actual_sales_step3.sqlx.
Do not rename the master table columns, keep them exactly as they are.
Standards: Filter both joins by LanguageKey = 'E' to prevent duplicate records.
```

The agent applies the requested corrections, yielding a precise and compliant transformation script.

<img src="img/ss10.png" alt="Module 6 Generation" width="400">

---

## Additional Content & Advanced Prompting
As you become more comfortable navigating Dataform with an AI agent, you can begin feeding it more holistic, multi-step instructions. Below is an example of an advanced, comprehensive prompt that dictates the entire pipeline architecture in one go.

While single, large prompts can be highly efficient, they may require careful tuning to ensure the agent captures every nuance without hallucinations.

### Advanced Single Prompt Example
```text
Objective: Act as a Lead GCP Data Engineer. Develop a production-grade suite of individual Dataform .sqlx files to modernize and enrich SAP BW tables in BigQuery. The goal is to build a modular, auditable, and high-performance data pipeline that follows the "Medallion Architecture" logic.
Technical Context:
Initial Source: Your_GCP_ProjectID.input_layer.actual_sales
Target Dataset: final_layer
Master table Sources: Your_GCP_ProjectID.sap_master and Your_GCP_ProjectID.sap_text
Text table  Sources: Your_GCP_ProjectID.sap_master and Your_GCP_ProjectID.sap_text

Dataform Best Practices Requirements for ALL Scripts:
Config Block: Use type: "table". Include the tag ["zinbobu_agent"] and a comprehensive description field summarizing the job's purpose.
Dependency Management: Exclusively use the ref() function to establish the chain: Job 1 -> Job 2 -> Job 3 -> Job 4.
Auditability: Every transformation must be explained with inline SQL comments.
Data Quality: Include an assertions block in relevant scripts to check for null values in primary key columns or uniqueness.

Job-Specific Logic:
Job 1 (Ingestion Layer): Create actual_sales_step1.sqlx.
Task: Materialize a 1:1 copy of the source actual_sales.
Documentation: Tag this as the "Raw Ingestion Layer" in the config.

Job 2 (Standardization Layer): Create actual_sales_step2.sqlx.
Transformation: Standardize the schema by cleaning column names. Strip prefixes like _bic_, bic_, or leading underscores.
Rule: For every renaming, add the comment -- AUDIT: Renamed from [Original Name] next to the field.
Assertion: Check that the resulting bill_date (or equivalent) is never null.

Job 3 (Master Data Enrichment): Create actual_sales_step3.sqlx.
Join Logic: Perform LEFT JOIN operations with MaterialMD and PlantMD.
Standard master table filters: Apply a WHERE clause for LanguageKey = 'E' for both master tables to prevent row explosion.
Material Selection: Fetch MaterialType, MaterialGroup, Product_ZPRODUCTC, and BrandName_CBRANDNME_T.
Plant Selection: Fetch MillR_GRMILL, Plant_PLANT, and PlantType_ZPLNTTYP.

Job 4 (Text Table Enrichment - Final Layer): Create actual_sales_step4.sqlx.
Task: Join with kna1, but000, and t077x.
Standards: Filter by Language ('E') and Client ('012').
Select: Retrieve NAME1 from kna1 and TXT30 from t077x. Use unique aliases like customer_text and category_description.
Performance: Add bigquery: { partitionBy: "CLEAN_DATE_FIELD" } to the config block if a date field is available.

Output Format: Provide distinct code blocks. Clearly label each with its intended filename (e.g., actual_sales_step1.sqlx). 
Think through the logic step-by-step to ensure column name collisions are avoided.
```

Congratulations on completing the Codelab! You are now equipped with the practical knowledge to construct and manage scalable, Medallion-style data pipelines in BigQuery using Google Cloud Dataform and AI-assisted engineering.
