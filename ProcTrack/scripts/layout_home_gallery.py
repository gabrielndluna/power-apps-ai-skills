"""Project Home KPIs, attention list, tighter headers, gallery fit."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "src" / "Src"


def shrink_named_header(text: str, header_name: str, top_name: str, bottom_name: str) -> str:
    lines = text.splitlines(keepends=True)
    header_at = next(i for i, line in enumerate(lines) if line.strip() == f"- {header_name}:")
    top_at = next(i for i, line in enumerate(lines) if i > header_at and line.strip() == f"- {top_name}:")
    bottom_at = next(i for i, line in enumerate(lines) if i > top_at and line.strip() == f"- {bottom_name}:")

    def patch_height(start: int, end: int, old: str, new: str, limit: int = 1) -> None:
        seen = 0
        for index in range(start, end):
            if old in lines[index] and lines[index].strip().startswith(old.split(":")[0]):
                lines[index] = lines[index].replace(old, new, 1)
                seen += 1
                if seen >= limit:
                    return

    patch_height(header_at, top_at, "Height: =108", "Height: =72")
    patch_height(header_at, top_at, "LayoutMinHeight: =108", "LayoutMinHeight: =72")
    patch_height(header_at, top_at, "PaddingTop: =12", "PaddingTop: =6")
    patch_height(header_at, top_at, "PaddingBottom: =12", "PaddingBottom: =6")
    patch_height(header_at, top_at, "PaddingTop: =10", "PaddingTop: =6")
    patch_height(header_at, top_at, "PaddingBottom: =10", "PaddingBottom: =6")
    patch_height(header_at, top_at, "LayoutGap: =10", "LayoutGap: =4")
    patch_height(header_at, top_at, "LayoutGap: =8", "LayoutGap: =4")
    patch_height(top_at, bottom_at, "Height: =44", "Height: =32", 1)
    patch_height(top_at, bottom_at, "LayoutMinHeight: =44", "LayoutMinHeight: =32", 1)
    next_sibling = next(
        (i for i, line in enumerate(lines) if i > bottom_at + 2 and line.startswith("            - ")),
        bottom_at + 40,
    )
    patch_height(bottom_at, next_sibling, "Height: =32", "Height: =26", 1)
    patch_height(bottom_at, next_sibling, "LayoutMinHeight: =32", "LayoutMinHeight: =26", 1)
    return "".join(lines)


OPEN_PACKAGE = """Set(varPackageScreenLoaded, false);
Set(varSelectedPackageId, ThisItem.packageidentifier);
ClearCollect(
    colPackageDetails,
    {
        title: ThisItem.Title,
        packageidentifier: ThisItem.packageidentifier,
        projectidentifier: ThisItem.projectidentifier,
        itemnumber: ThisItem.itemnumber,
        packagedescription: ThisItem.packagedescription,
        packagetype: ThisItem.packagetype,
        qualityprogram: ThisItem.qualityprogram,
        prerequisitedesigndeliverable: ThisItem.prerequisitedesigndeliverable,
        bopsite: ThisItem.bopsite,
        contracttype: ThisItem.contracttype,
        Created: ThisItem.Created,
        comments: ThisItem.comments,
        sole_source: ThisItem.sole_source,
        packagefolderurl: ThisItem.packagefolderurl,
        archived: ThisItem.archived,
        procpackageleadname: ThisItem.procpackageleadname,
        procurementpackageleadid: ThisItem.procurementpackageleadid,
        opspackageleadname: ThisItem.opspackageleadname,
        operationspackageleadid: ThisItem.operationspackageleadid,
        engineeringcontactid: ThisItem.engineeringcontactid,
        engineeringcontactname: ThisItem.engineeringcontactname,
        operationspackagebundle: ThisItem.operationspackagebundle,
        leadtimesowtorfqissuedays: ThisItem.leadtimesowtorfqissuedays,
        leadtimerfqissuetoclosingdays: ThisItem.leadtimerfqissuetoclosingdays,
        leadtimeclosingtoevaluationdays: ThisItem.leadtimeclosingtoevaluationdays,
        leadtimeevaluationtoawarddays: ThisItem.leadtimeevaluationtoawarddays,
        standardleadtimemonths: ThisItem.standardleadtimemonths,
        originalplannedsowdate: ThisItem.originalplannedsowdate,
        originalplannedrfqissuedate: ThisItem.originalplannedrfqissuedate,
        originalplannedrfqclosingdate: ThisItem.originalplannedrfqclosingdate,
        originalplannedevaluationcompleti: ThisItem.originalplannedevaluationcompleti,
        originalplannedawarddate: ThisItem.originalplannedawarddate,
        plannedawarddate: ThisItem.plannedawarddate,
        requiredatsitedate: ThisItem.requiredatsitedate,
        ras_original_input: ThisItem.ras_original_input,
        actualsowdate: ThisItem.actualsowdate,
        actualrfqissuedate: ThisItem.actualrfqissuedate,
        actualrfqclosingdate: ThisItem.actualrfqclosingdate,
        actualevaluationcompletiondate: ThisItem.actualevaluationcompletiondate,
        actualawarddate: ThisItem.actualawarddate,
        actual_onsite: ThisItem.actual_onsite,
        revisedplannedsowdate: ThisItem.revisedplannedsowdate,
        revisedplannedrfqissuedate: ThisItem.revisedplannedrfqissuedate,
        revisedplannedrfqclosingdate: ThisItem.revisedplannedrfqclosingdate,
        revisedplannedevaluationcompletio: ThisItem.revisedplannedevaluationcompletio,
        revisedplannedawarddate: ThisItem.revisedplannedawarddate,
        subcontractorname: ThisItem.subcontractorname,
        purchaseordernumber: ThisItem.purchaseordernumber,
        awardvalue: ThisItem.awardvalue,
        indigenous_award: ThisItem.indigenous_award,
        ontario_award: ThisItem.ontario_award,
        budgetamount: ThisItem.budgetamount,
        buybackresaletarget: ThisItem.buybackresaletarget
    }
);
Set(varActualSOW, ThisItem.actualsowdate);
Set(varActualRFQIssue, ThisItem.actualrfqissuedate);
Set(varActualRFQClosing, ThisItem.actualrfqclosingdate);
Set(varActualEval, ThisItem.actualevaluationcompletiondate);
Set(varActualAward, ThisItem.actualawarddate);
Navigate('Package Details', ScreenTransition.Fade)"""


def yaml_formula(formula: str, indent: int) -> str:
    inner = " " * (indent + 2)
    lines = [f"{' ' * indent}OnSelect: |-", f"{inner}={formula.splitlines()[0]}"]
    for line in formula.splitlines()[1:]:
        lines.append(f"{inner}{line}" if line else "")
    return "\n".join(lines)


def home() -> None:
    path = ROOT / "Project Home.pa.yaml"
    text = path.read_text(encoding="utf-8")
    start = text.index("                  - ph_btn_all:")
    end = text.index("                  - ph_btn_add:")
    text = text[:start] + text[end:]
    text = text.replace(
        """            - ph_actions:
                Control: GroupContainer@1.5.0
                Variant: AutoLayout
                Properties:
                  DropShadow: =DropShadow.None
                  FillPortions: =0
                  Height: =44
                  LayoutAlignItems: =LayoutAlignItems.Center
                  LayoutDirection: =LayoutDirection.Horizontal
                  LayoutGap: =8
                  LayoutMinHeight: =0
                  LayoutMinWidth: =0
""",
        """            - ph_actions:
                Control: GroupContainer@1.5.0
                Variant: AutoLayout
                Properties:
                  DropShadow: =DropShadow.None
                  FillPortions: =0
                  Height: =40
                  LayoutAlignItems: =LayoutAlignItems.Center
                  LayoutDirection: =LayoutDirection.Horizontal
                  LayoutJustifyContent: =LayoutJustifyContent.End
                  LayoutGap: =8
                  LayoutMinHeight: =0
                  LayoutMinWidth: =0
""",
        1,
    )
    clicks = {
        "- ph_kpi_total:": 'Set(varPackageFilter, "all"); Navigate(\'Welcome screen\', ScreenTransition.Fade)',
        "- ph_kpi_awarded:": 'Set(varPackageFilter, "awarded"); Navigate(\'Welcome screen\', ScreenTransition.Fade)',
        "- ph_kpi_delayed:": 'Set(varPackageFilter, "delayed"); Navigate(\'Welcome screen\', ScreenTransition.Fade)',
        "- ph_kpi_risk:": 'Set(varPackageFilter, "at_risk"); Navigate(\'Welcome screen\', ScreenTransition.Fade)',
    }
    for marker, formula in clicks.items():
        at = text.index(f"                  {marker}")
        props = text.index("                      Properties:", at)
        insert = f"                        OnSelect: ={formula}\n"
        text = text[: props + len("                      Properties:\n")] + insert + text[props + len("                      Properties:\n") :]

    archived = """
                  - ph_kpi_archived:
                      Control: GroupContainer@1.5.0
                      Variant: AutoLayout
                      Properties:
                        OnSelect: =Set(varPackageFilter, "archived"); Navigate('Welcome screen', ScreenTransition.Fade)
                        DropShadow: =DropShadow.Light
                        Fill: =RGBA(237, 237, 237, 1)
                        FillPortions: =1
                        LayoutAlignItems: =LayoutAlignItems.Center
                        LayoutDirection: =LayoutDirection.Vertical
                        LayoutGap: =2
                        LayoutMinHeight: =0
                        LayoutMinWidth: =0
                        PaddingBottom: =8
                        PaddingLeft: =8
                        PaddingRight: =8
                        PaddingTop: =8
                        RadiusBottomLeft: =8
                        RadiusBottomRight: =8
                        RadiusTopLeft: =8
                        RadiusTopRight: =8
                      Children:
                        - ph_kpi_archived_n:
                            Control: Label@2.5.1
                            Properties:
                              Align: =Align.Center
                              Color: =RGBA(90, 96, 102, 1)
                              Font: =Font.'Segoe UI'
                              FontWeight: =FontWeight.Bold
                              Height: =28
                              PaddingBottom: =0
                              PaddingTop: =0
                              Size: =20
                              Text: =CountRows(Filter(colProjectPackages, archived = true))
                              Width: =Parent.Width
                        - ph_kpi_archived_l:
                            Control: Label@2.5.1
                            Properties:
                              Align: =Align.Center
                              Color: =RGBA(90, 96, 102, 1)
                              Font: =Font.'Segoe UI'
                              Height: =16
                              PaddingBottom: =0
                              PaddingTop: =0
                              Size: =11
                              Text: ="Archived"
                              Width: =Parent.Width
"""
    attn_select = yaml_formula(OPEN_PACKAGE, 30)
    attention = f"""
            - ph_attn:
                Control: GroupContainer@1.5.0
                Variant: AutoLayout
                Properties:
                  DropShadow: =DropShadow.Light
                  Fill: =RGBA(255, 255, 255, 1)
                  FillPortions: =1
                  LayoutAlignItems: =LayoutAlignItems.Stretch
                  LayoutDirection: =LayoutDirection.Vertical
                  LayoutGap: =0
                  LayoutMinHeight: =120
                  LayoutMinWidth: =0
                  RadiusBottomLeft: =8
                  RadiusBottomRight: =8
                  RadiusTopLeft: =8
                  RadiusTopRight: =8
                Children:
                  - ph_attn_head:
                      Control: Label@2.5.1
                      Properties:
                        Color: =RGBA(255, 255, 255, 1)
                        Fill: =RGBA(214, 12, 48, 1)
                        Font: =Font.'Segoe UI'
                        FontWeight: =FontWeight.Bold
                        Height: =32
                        PaddingLeft: =12
                        Size: =12
                        Text: ="NEEDS ATTENTION"
                        VerticalAlign: =VerticalAlign.Middle
                        Width: =Parent.Width
                  - ph_attn_empty:
                      Control: Label@2.5.1
                      Properties:
                        Align: =Align.Center
                        Color: =RGBA(106, 122, 127, 1)
                        Font: =Font.'Segoe UI'
                        Height: =64
                        Size: =12
                        Text: ="No delayed or at-risk packages."
                        VerticalAlign: =VerticalAlign.Middle
                        Visible: =CountRows(ph_attn_gal.AllItems) = 0
                        Width: =Parent.Width
                  - ph_attn_gal:
                      Control: Gallery@2.15.0
                      Variant: BrowseLayout_Vertical_TwoTextOneImageVariant_ver5.0
                      Properties:
                        BorderThickness: =0
                        FillPortions: =1
                        Items: |-
                          =Filter(
                              colProjectPackages,
                              archived <> true &&
                              IsBlank(actualawarddate) &&
                              !IsBlank(revisedplannedawarddate) &&
                              revisedplannedawarddate <= Today() + 30
                          )
                        LayoutMinHeight: =80
                        TemplatePadding: =0
                        TemplateSize: =52
                        Width: =Parent.Width
                      Children:
                        - ph_attn_row:
                            Control: GroupContainer@1.5.0
                            Variant: AutoLayout
                            Properties:
                              DropShadow: =DropShadow.None
                              Fill: =If(ThisItem.revisedplannedawarddate < Today(), RGBA(253, 236, 236, 1), RGBA(255, 244, 229, 1))
                              Height: =Parent.TemplateHeight
                              LayoutAlignItems: =LayoutAlignItems.Center
                              LayoutDirection: =LayoutDirection.Horizontal
                              LayoutGap: =8
                              PaddingLeft: =12
                              PaddingRight: =12
                              Width: =Parent.TemplateWidth
{attn_select}
                            Children:
                              - ph_attn_id:
                                  Control: Label@2.5.1
                                  Properties:
                                    Color: =RGBA(214, 12, 48, 1)
                                    Font: =Font.'Segoe UI'
                                    FontWeight: =FontWeight.Bold
                                    Height: =22
                                    Size: =12
                                    Text: =ThisItem.projectidentifier & "-" & ThisItem.itemnumber
                                    VerticalAlign: =VerticalAlign.Middle
                                    Width: =110
                              - ph_attn_desc:
                                  Control: Label@2.5.1
                                  Properties:
                                    Color: =RGBA(35, 38, 43, 1)
                                    FillPortions: =1
                                    Font: =Font.'Segoe UI'
                                    Height: =22
                                    LayoutMinWidth: =0
                                    Size: =12
                                    Text: =ThisItem.packagedescription
                                    VerticalAlign: =VerticalAlign.Middle
                              - ph_attn_when:
                                  Control: Label@2.5.1
                                  Properties:
                                    Align: =Align.Right
                                    Color: =RGBA(90, 96, 102, 1)
                                    Font: =Font.'Segoe UI'
                                    Height: =22
                                    Size: =11
                                    Text: =Text(ThisItem.revisedplannedawarddate, "mmm dd, yyyy")
                                    VerticalAlign: =VerticalAlign.Middle
                                    Width: =110
                              - ph_attn_go:
                                  Control: Classic/Icon@2.5.0
                                  Properties:
                                    Color: =RGBA(214, 12, 48, 1)
                                    Height: =20
                                    Icon: =Icon.ChevronRight
                                    Width: =20
"""
    text = text.rstrip() + "\n" + archived + attention
    text = shrink_named_header(text, "ph_header", "ph_header_top", "ph_header_bottom")
    path.write_text(text, encoding="utf-8")
    print("home")


def gallery() -> None:
    path = ROOT / "Welcome screen.pa.yaml"
    text = path.read_text(encoding="utf-8")
    start = text.index("                                    - gallery_lead:")
    end = text.index("                                    - variable_row_1:")
    text = (
        text[:start]
        + """                                    - gallery_leads:
                                        Control: GroupContainer@1.5.0
                                        Variant: AutoLayout
                                        Properties:
                                          DropShadow: =DropShadow.None
                                          FillPortions: =16
                                          LayoutAlignItems: =LayoutAlignItems.Center
                                          LayoutDirection: =LayoutDirection.Vertical
                                          LayoutGap: =0
                                          LayoutMinHeight: =0
                                          LayoutMinWidth: =0
                                        Children:
                                          - gallery_lead:
                                              Control: Text@0.0.51
                                              Properties:
                                                Align: ='TextCanvas.Align'.Center
                                                FontColor: =RGBA(60, 60, 60, 1)
                                                Height: =18
                                                Size: =11
                                                Text: =ThisItem.procpackageleadname
                                                VerticalAlign: =VerticalAlign.Middle
                                                LayoutMinWidth: =0
                                                Wrap: =false
                                          - opslead:
                                              Control: Text@0.0.51
                                              Properties:
                                                Align: ='TextCanvas.Align'.Center
                                                FontColor: =RGBA(90, 96, 102, 1)
                                                Height: =18
                                                Size: =11
                                                Text: =ThisItem.opspackageleadname
                                                VerticalAlign: =VerticalAlign.Middle
                                                LayoutMinWidth: =0
                                                Wrap: =false
"""
        + text[end:]
    )
    text = text.replace("FillPortions: =9", "FillPortions: =12")
    text = text.replace(
        """                        - header_arrow_gap:
                            Control: Label@2.5.1
                            Properties:
                              FillPortions: =4
                              Height: =32
                              LayoutMinWidth: =0
                              Text: =""
""",
        """                        - header_arrow_gap:
                            Control: Label@2.5.1
                            Properties:
                              FillPortions: =0
                              Height: =32
                              LayoutMinWidth: =0
                              Text: =""
                              Width: =32
""",
    )
    text = text.replace(
        """                                          PaddingBottom: =16
                                          PaddingLeft: =16
                                          PaddingRight: =16
                                          PaddingTop: =16
                                          Tooltip: ="View item details"
""",
        """                                          PaddingBottom: =0
                                          PaddingLeft: =0
                                          PaddingRight: =0
                                          PaddingTop: =0
                                          Tooltip: ="View item details"
""",
    )
    text = text.replace("PaddingLeft: =20", "PaddingLeft: =2", 1)
    text = text.replace(
        """                              - gallery_row:
                                  Control: GroupContainer@1.5.0
                                  Variant: AutoLayout
                                  Properties:
                                    DropShadow: =DropShadow.None
                                    FillPortions: =1
                                    LayoutAlignItems: =LayoutAlignItems.Start
""",
        """                              - gallery_row:
                                  Control: GroupContainer@1.5.0
                                  Variant: AutoLayout
                                  Properties:
                                    DropShadow: =DropShadow.None
                                    FillPortions: =1
                                    LayoutAlignItems: =LayoutAlignItems.Center
""",
        1,
    )
    text = shrink_named_header(text, "HeaderContainer1", "welcome_header_top", "welcome_header_bottom")
    path.write_text(text, encoding="utf-8")
    print("gallery")


def details_and_create() -> None:
    details = ROOT / "Package Details.pa.yaml"
    text = details.read_text(encoding="utf-8")
    text = shrink_named_header(text, "header_container", "details_header_top", "details_header_bottom")
    text = text.replace("Height: =66", "Height: =48", 1)
    text = text.replace("LayoutMinHeight: =66", "LayoutMinHeight: =48", 1)
    text = text.replace("LayoutMinHeight: =54", "LayoutMinHeight: =40")
    text = text.replace("Size: =18", "Size: =14", 1)
    text = text.replace("LayoutOverflowY: =LayoutOverflow.Scroll", "LayoutOverflowY: =LayoutOverflow.Hidden")
    text = text.replace("Height: =320", "Height: =248", 1)
    text = text.replace("LayoutMinHeight: =320", "LayoutMinHeight: =0", 1)
    text = text.replace("LayoutMinHeight: =300", "LayoutMinHeight: =0", 1)
    text = text.replace("Height: =236", "Height: =200", 1)
    # Basics rows only: the 48px rows sit before the path grid.
    head, mid, tail = text.partition("                              - Container11:")
    mid_rows = head.replace("Height: =48", "Height: =40").replace("LayoutMinHeight: =48", "LayoutMinHeight: =40")
    text = mid_rows + "                              - Container11:" + tail
    text = text.replace(
        """                                          Text: ="PACKAGE BASICS"
                                          VerticalAlign: =VerticalAlign.Middle
                                          Width: =118
""",
        """                                          Text: ="PACKAGE BASICS"
                                          VerticalAlign: =VerticalAlign.Middle
                                          FillPortions: =1
                                          LayoutMinWidth: =0
""",
        1,
    )
    text = text.replace(
        """                                          Text: ="PREREQ DESIGN"
                                          VerticalAlign: =VerticalAlign.Middle
                                          Width: =78
""",
        """                                          Text: ="PREREQ DESIGN"
                                          VerticalAlign: =VerticalAlign.Middle
                                          Width: =108
""",
        1,
    )
    details.write_text(text, encoding="utf-8")
    create = ROOT / "Create New Package.pa.yaml"
    create.write_text(
        shrink_named_header(
            create.read_text(encoding="utf-8"),
            "header_container_1",
            "create_header_top",
            "create_header_bottom",
        ),
        encoding="utf-8",
    )
    print("details create")


if __name__ == "__main__":
    home()
    gallery()
    details_and_create()
