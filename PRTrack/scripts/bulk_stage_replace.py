from pathlib import Path

files = [
    Path(__file__).resolve().parents[1] / "src" / "Src" / "PR Detail.pa.yaml",
    Path(__file__).resolve().parents[1] / "src" / "Src" / "PR Log.pa.yaml",
    Path(__file__).resolve().parents[1] / "src" / "Src" / "Dashboard.pa.yaml",
]

reps = [
    (
        '"Pending approval", 4,\n                                                        "Approved", 5,',
        '"Pending approval", 4,\n                                                        "PO creation", 5,\n                                                        "Approved", 5,',
    ),
    (
        '"Pending approval", 4,\n                                                                  "Approved", 5,',
        '"Pending approval", 4,\n                                                                  "PO creation", 5,\n                                                                  "Approved", 5,',
    ),
    (
        '"Pending approval", 4,\n                                                                                "Approved", 5,',
        '"Pending approval", 4,\n                                                                                "PO creation", 5,\n                                                                                "Approved", 5,',
    ),
    (
        '"Pending approval", 4,\n                                    "Approved", 5,',
        '"Pending approval", 4,\n                                    "PO creation", 5,\n                                    "Approved", 5,',
    ),
    (
        '"Pending approval", "DOA Approval",\n                                                                  "Approved", "PO created in SAP",',
        '"Pending approval", "DOA Approval",\n                                                                  "PO creation", "PO Creation",\n                                                                  "Approved", "PO created in SAP",',
    ),
    (
        'CountRows(Filter(colPRLines, stage.Value = "Rejected")) > 0',
        'CountRows(colPRLines) > 0 && CountRows(Filter(colPRLines, stage.Value = "Rejected")) = CountRows(colPRLines)',
    ),
    (
        'CountRows(colPRLines) > 0 && CountRows(Filter(colPRLines, stage.Value = "Approved")) = CountRows(colPRLines)',
        'CountRows(Filter(colPRLines, stage.Value <> "Rejected")) > 0 && CountRows(Filter(colPRLines, stage.Value <> "Rejected" && stage.Value = "Approved" && !IsBlank(ponumber))) = CountRows(Filter(colPRLines, stage.Value <> "Rejected"))',
    ),
]

for p in files:
    t = p.read_text(encoding="utf-8")
    orig = t
    for a, b in reps:
        t = t.replace(a, b)
    # Dashboard / PR Log: all lines Approved means PO created
    t = t.replace(
        'CountRows(Filter(colProjectLines, pridentifier = Title && stage.Value = "Approved")) = CountRows(Filter(colProjectLines, pridentifier = Title)),\n                                                  "PO created in SAP",',
        'CountRows(Filter(colProjectLines, pridentifier = Title && stage.Value <> "Rejected")) > 0 && CountRows(Filter(colProjectLines, pridentifier = Title && stage.Value <> "Rejected" && stage.Value = "Approved" && !IsBlank(ponumber))) = CountRows(Filter(colProjectLines, pridentifier = Title && stage.Value <> "Rejected")),\n                                                  "PO created in SAP",',
    )
    t = t.replace(
        '4, "DOA Approval",\n                                                      5, "PO created in SAP",',
        '4, "DOA Approval",\n                                                      5, "PO Creation",',
    )
    t = t.replace(
        '"Approved", "PO created in SAP",\n                                                          "On Hold", "Draft",',
        '"Pending PO", "PO Creation",\n                                                          "Approved", "PO created in SAP",\n                                                          "On Hold", "Draft",',
    )
    if t != orig:
        p.write_text(t, encoding="utf-8")
        print("updated", p.name, "delta", len(t) - len(orig))
    else:
        print("no change", p.name)
