"""ESD #2 fiscal model — web backend. Uses the v7 Excel as the calculation engine:
writes inputs into a copy, recalculates with LibreOffice, reads RESULTS back.
Guarantees the web app's numbers match the Excel exactly."""
import openpyxl, subprocess, tempfile, shutil, os, glob

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine_v7.xlsx")
SOFFICE = os.environ.get("SOFFICE", "soffice")

SCALAR = {  # friendly key -> INPUTS!D cell
 "city_share":"D6","edc":"D7","esd_share":"D8","pool_rate":"D9","city_pt_rate":"D10","esd_pt_rate":"D11",
 "pop":"D13","pop_cagr":"D14","pool_base":"D15","pool_cagr":"D16","av_cagr":"D17","capture":"D18",
 "opex_infl":"D19","cap_infl":"D20","city_res":"D21","esd_res":"D22","reserve_incl_cap":"D23","collection":"D24",
 "sfr_occ":"D26","mfr_occ":"D27","sfr_hh":"D28","mfr_hh":"D29","online_spend":"D30","online_taxable":"D31",
 "online_capture":"D32","online_growth":"D33","online_include":"D34","far":"D47","abatement":"D48","abate_term":"D49",
 "impact_fee":"D50"}
EXEMPT_ROW = {"Residential":38,"Commercial":39,"Industrial":40,"Civic":41,"Vacant":42}
SCEN_FIRST = 54  # INPUTS scenario rows 54..65 ; cols A=name B=active C=type D=qtytype E=qty F=acres G=start H=buildout I=capture

def _recalc(path):
    outdir = tempfile.mkdtemp()
    subprocess.run([SOFFICE,"--headless","--calc","--convert-to","xlsx","--outdir",outdir,path],
                   check=True, capture_output=True, timeout=120)
    out = glob.glob(os.path.join(outdir,"*.xlsx"))[0]
    shutil.copy(out, path); shutil.rmtree(outdir, ignore_errors=True)

def compute(inputs:dict, scenarios:list, exemptions:dict=None):
    """inputs: {key:value} for SCALAR keys. scenarios: list of dicts
    (name,active,type,qty_type,qty,manual_acres,start,buildout,capture).
    exemptions: {category:{'city':pct,'esd':pct}} effective haircut per category."""
    tmp = tempfile.mktemp(suffix=".xlsx"); shutil.copy(TEMPLATE, tmp)
    wb = openpyxl.load_workbook(tmp); INP = wb["INPUTS"]
    for k,v in (inputs or {}).items():
        if k in SCALAR and v is not None: INP[SCALAR[k]] = v
    if "city_share" in (inputs or {}):
        INP["D8"] = round(1 - inputs["city_share"], 6)
    for cat,row in EXEMPT_ROW.items():
        e = (exemptions or {}).get(cat, {})
        for c in range(2,8):  INP.cell(row,c, 0)
        for c in range(10,16):INP.cell(row,c, 0)
        if "city" in e: INP.cell(row,7, e["city"])
        if "esd"  in e: INP.cell(row,15,e["esd"])
    for i in range(12):
        r = SCEN_FIRST + i
        if i < len(scenarios):
            s = scenarios[i]
            INP.cell(r,1, s.get("name","")); INP.cell(r,2, "Yes" if s.get("active") else "No")
            INP.cell(r,3, s.get("type","")); INP.cell(r,4, s.get("qty_type",""))
            INP.cell(r,5, s.get("qty")); INP.cell(r,6, s.get("manual_acres"))
            INP.cell(r,7, s.get("start")); INP.cell(r,8, s.get("buildout")); INP.cell(r,9, s.get("capture"))
        else:
            INP.cell(r,2,"No")
    wb.save(tmp); _recalc(tmp)
    rb = openpyxl.load_workbook(tmp, data_only=True)
    res = rb["RESULTS"]; ci = rb["Capital_Items"]
    out = {}
    for rr in range(7, 40):                 # main results block only (capex block starts ~row 40)
        lbl = res.cell(rr,1).value
        if lbl and isinstance(res.cell(rr,2).value,(int,float)):
            out[str(lbl).strip()] = [res.cell(rr,c).value for c in range(2,7)]  # 5/10/15/20/30
    capex = []                              # large capital items currently Included in the fiscal net
    for r in range(4, 32):
        if str(ci.cell(r,18).value).strip().lower() == "yes":
            capex.append({"item": ci.cell(r,1).value, "qty": ci.cell(r,12).value, "unit": ci.cell(r,4).value,
                          "payer": ci.cell(r,17).value, "treatment": ci.cell(r,19).value,
                          "cost10y": (ci.cell(r,25).value or 0) + (ci.cell(r,30).value or 0)})
    out["__capex__"] = capex
    os.remove(tmp)
    return out
