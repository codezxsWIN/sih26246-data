"""Create factual offline NCS evidence, source register and town geography extracts."""
import hashlib,json,re
from bs4 import BeautifulSoup
import openpyxl
from .acquire import ROOT,write_json
from .extract_ncs import object_literal,csv_write

DETAILS={
 'nco_2015':('Occupation codes, titles, hierarchy, descriptions','2015','National','Edition based','skills'),
 'pmkvy_mh_centres_2021':('TCState, TCDistrict, PartnerName, TCName','21 November 2021','Training centre / district','Static annexure','training'),
 'pmkvy_district_training_2021_22':('State, district, trained count','FY 2021-22','District','Static annexure','training,supply'),
 'census_pune_2011':('Population, sex, literacy, main/marginal workers, households, codes','2011 Census','District / subdistrict / village / town','Census edition','geography,baseline'),
 'mh_economic_survey_2024_25':('Economic, industry, employment and education tables; units vary','Survey 2024-25; historical tables vary','State; selected district tables','Annual','baseline'),
 'automotive_qp':('ASC/Q3604 v4.0; Automotive Assembly Operator; NSQF 3; NOS criteria','Version 4.0; confirm current validity','National role standard','Versioned revisions','skills,training'),
 'ncs_integration_evidence':('Integration procurement requirements; not API contract','2024 indexed RFP','National','Procurement edition','access'),
 'plfs_download_guide':('Account and microdata download instructions','Guide edition unconfirmed','National','Irregular','access'),
 'aishe_2021_22':('Enrolment, out-turn, institutions, discipline, level, gender, social category; table dependent','Academic 2021-22','State / national report tables','Annual with lag','supply'),
 'plfs_2023_24_report':('LFPR, WPR, UR, age, sex, rural/urban, education, employment status; table dependent','July 2023-June 2024','State / national','Annual; separate quarterly series','baseline,supply'),
 'plfs_2023_24_metadata':('Study identifiers, coverage, producer, file descriptions and access metadata','July 2023-June 2024','Study metadata','Study release','baseline'),
 'census_mh_town_amenities':('State/district/subdistrict/town codes and names; households, sex population, amenities; 429 town columns','2011 Census; amenity reference years vary','Town','Census edition','geography'),
 'census_pune_inset_tables':('District handbook inset tables; inspect archive headers','2011 Census','Pune district / subdistrict','Census edition','baseline,geography'),
 'electronics_qp':('ELE/Q2501 v4.0; Electronics Machine Maintenance Technician - Shop Floor; NSQF 4; NOS criteria','Version 4.0; confirm validity','National role standard','Versioned revisions','skills,training'),
 'ncs_ogd_state_vacancies_2023':('States, Mobilised Vacancies, Data Upto','Up to 30 September 2023','State','Catalogue monthly; resource historical','demand'),
 'kaggle_india_tech_2026':('32 job fields: exact schema in data/manifests/kaggle_quality.json','Title 2026; all scraped_at 2025-06-10; updated June 2026','Job location; sometimes multi-city','Uploader snapshot','demand,parser testing'),
 'plfs_2023_24_layout':('Household/person file field names, positions, codes; sheets differ','July 2023-June 2024','Survey record schema','Study release','baseline,supply'),
 'nqr_python_sql':('Data Analysis with Python and SQL; NIE/SSC/N1110; NSQF 5; outcomes, hours, entry criteria','Approved 30 November 2023; register validity to 30 November 2026','National qualification','Versioned approvals','skills,training')}

def main():
    scratch=ROOT.parent.parent/'work/ncs_evidence'
    html=(scratch/'NCSReportDashboard.html').read_text(encoding='utf-8')
    js=(scratch/'main-2UJ5AQIL.js').read_text(encoding='utf-8')
    cols=json.loads(re.search(r'this\.allColumns=(\[[^\]]+\])',js).group(1))
    tables=object_literal(js,'this.allTabData=')
    target=ROOT/'data/raw/ncs/evidence';target.mkdir(parents=True,exist_ok=True)
    soup=BeautifulSoup(html,'html.parser')
    (target/'dashboard_table.html').write_text('<p>Last Updated on 15th July, 2026</p>'+str(soup.select_one('button.tab-btn.active'))+str(soup.find('table')),encoding='utf-8')
    (target/'dashboard_tables.js').write_text('this.allColumns='+json.dumps(cols)+';this.allTabData='+json.dumps(tables)+';',encoding='utf-8')
    write_json(ROOT/'data/manifests/ncs_offline_evidence.json',{'source_url':'https://ncs.gov.in/NCSReportDashboard','publisher_updated_at':'15 July 2026','original_html_sha256':hashlib.sha256(html.encode()).hexdigest(),'original_bundle_sha256':hashlib.sha256(js.encode()).hexdigest(),'packaging':'Extracted factual table markup and table literals only; unrelated website code and keys excluded','retrieval_timestamp':'Initial page retrieval timestamp not recorded; imported offline 1 October 2026'})
    wb=openpyxl.load_workbook(ROOT/'data/raw/geography/census_mh_town_amenities_2011.xlsx',read_only=True,data_only=True)
    values=iter(wb['Town_2700'].values);headers=next(values)
    fields=['state_code','state','district_code','district','subdistrict_code','subdistrict','town_code','town','households','population','male_population','female_population']
    rows=[dict(zip(fields,row[:12])) for row in values if row[0] is not None]
    pune=[r for r in rows if str(r['district']).strip().lower()=='pune']
    csv_write(ROOT/'data/processed/geography/maharashtra_towns_census_2011.csv',rows,fields)
    csv_write(ROOT/'data/processed/geography/pune_towns_census_2011.csv',pune,fields)
    write_json(ROOT/'data/manifests/geography_extract.json',{'maharashtra_towns':len(rows),'pune_district_towns':len(pune),'source_sheet':'Town_2700','vintage':'2011 Census','original_columns_selected':list(headers[:12])})
    logs=json.loads((ROOT/'data/manifests/download_log.json').read_text());success={r['filename'] for r in logs if r['status']=='downloaded'}
    register=[]
    for item in json.loads((ROOT/'config/downloads.json').read_text()):
        if item['id'] not in DETAILS:continue
        fields,period,geo,frequency,modules=DETAILS[item['id']]
        status='downloaded' if 'data/raw/'+item['filename'] in success else 'failed; see download log'
        tier=3 if item['id'].startswith('kaggle') else 2 if item['id']=='ncs_integration_evidence' else 1
        quality='Official source; historical vintage retained. See data dictionary for unit and coverage limits.'
        if status.startswith('failed'):quality='Not acquired; do not substitute catalogue metadata for data records.'
        if tier==3:quality='Inconsistent dates, duplicate URLs, truncated descriptions; prototype only.'
        licence='Public download; dataset-specific open licence unverified. Attribute publisher; do not assume unrestricted redistribution.'
        if tier==3:licence='Uploader CC BY-SA 4.0; original job-board rights unverified. Local-only posting extract.'
        if item['id']=='ncs_ogd_state_vacancies_2023':licence='NDSAP catalogue; verify resource-level GODL-India applicability and attribution.'
        register.append({**item,'tier':tier,'official_public_status':'Public third-party uploader' if tier==3 else 'Official government or recognized sector skill council','access_method':'public static download','fields_available':fields,'date_coverage':period,'geography_granularity':geo,'update_frequency':frequency,'license_usage_constraints':licence,'quality_reliability':quality,'project_modules':modules.split(','),'acquisition_status':status,'scraping_required':False})
    additional=[
      ('ncs_dashboard',1,'https://ncs.gov.in/NCSReportDashboard','Offline extraction of acquired public page/bundle','metric, state, financial_year, value, publisher_updated_at','2015-16 through partial 2026-2027; updated 15 July 2026','State / national','Cadence unconfirmed','1788 records; totals reconcile; no Pune detail; stock/flow definitions unresolved','demand,supply,baseline','extracted'),
      ('ncs_live_vacancies',1,'https://api.ncs.gov.in/api/v1/job-posts/search?page=0&size=20','POST website-internal search; approved partner export/feed needed','Observed filters: keyword, cities, states, jobTitles, skills, functionalAreas, functionalRoles, industries, educationTypes, salary/experience bounds, sortBy. Response fields not verified.','Live service intended; no postings acquired','City/state filters observed','Feed cadence unknown','Plain JSON HTTP 400 Invalid or unencrypted request payload; browser permission later declined; no workaround','demand','blocked: access permission or approved export/credentials required'),
      ('ncs_metadata',1,'https://ncs.gov.in/','Public linked XLSX on NCS document storage; refresh expiring link via homepage','section, field, value','Acquired October 2026; coverage described in workbook','Metadata describes state/demographic disaggregation','Workbook cadence unspecified','54 nonempty rows; not vacancy records','provenance','downloaded/extracted'),
      ('plfs_person_microdata',1,'https://microdata.gov.in/nada/index.php/catalog/213/get-microdata','Account login and study terms; manual download','File-dependent household/person IDs, age, sex, education, industry/occupation/activity, survey weights, geographic codes; inspect acquired layout','July 2023-June 2024; newer studies separate','Survey persons; district codes do not establish representative district estimates','Study release','Weighted anonymized sample; person files not acquired','baseline,supply','login required'),
      ('lgd_current_geography',2,'https://lgdirectory.gov.in/','Official report/export; report-specific CAPTCHA/login may apply','Expected administrative codes/names/status; exact export not inspected','Current directory candidate; not acquired','Administrative units','Administrative changes','Discovery candidate, not verified export endpoint; keep separate from Census codes','geography','not downloaded')]
    for id,tier,url,access,fields,period,geo,freq,quality,modules,status in additional:
        register.append({'id':id,'tier':tier,'url':url,'official_public_status':'Government official service/directory','access_method':access,'fields_available':fields,'date_coverage':period,'geography_granularity':geo,'update_frequency':freq,'license_usage_constraints':'Publisher terms apply; confirm reuse conditions. No bypass of login, denied permission or CAPTCHA; no personal candidate data.','quality_reliability':quality,'project_modules':modules.split(','),'acquisition_status':status,'scraping_required':'Authorized website/feed only' if id=='ncs_live_vacancies' else False})
    existing_path=ROOT/'config/sources.json'
    existing=json.loads(existing_path.read_text()) if existing_path.exists() else []
    ids={r['id'] for r in register}
    register.extend(r for r in existing if r['id'] not in ids)
    write_json(existing_path,register)
    print('Registered',len(register),'sources; towns',len(rows),'Pune towns',len(pune))

if __name__=='__main__':main()
