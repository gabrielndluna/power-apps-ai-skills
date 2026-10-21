"""Build a legacy Power Automate package for the DNNP invoiced-to-date import."""

import json
import zipfile
from pathlib import Path

FLOW_GUID = "0896a2e3-753b-46f5-b02b-fbe57ca25982"
SP_API_GUID = "7257e41e-ae01-475d-b9f0-4848eaf92148"
SP_CONN_GUID = "d48194c0-71ec-42b2-8640-c65f158cb15f"
EXCEL_API_GUID = "94dbe29f-5f97-41f2-97f9-7693d32aa423"
EXCEL_CONN_GUID = "1688c760-c8fb-4d0c-b4d3-5e5c4f11b498"

SITE = "https://aecon1.sharepoint.com/sites/CivilPlanningteam"
LIST_ID = "3e786a14-7ee1-4d06-a960-f7e4dc131bdc"
FOLDER = (
    "/Shared Documents/02-Reporting and Analytics/"
    "1. Data Warehouse/A01760- DNNP Post Award Dashboard"
)
DISPLAY_NAME = "PostAward - DNNP invoiced to date"
DESCRIPTION = (
    "When a DNNP Post Award Dashboard xlsx is added to the SharePoint folder, "
    "write Actual Cost Obj into PostAward - Subcontracts invoicedtodate for "
    "project codes A01760 and A02180. Blank actuals are left unchanged."
)

SP_API = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
EXCEL_API = "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness"


def host(api_id, operation_id, connection_name):
    return {
        "apiId": api_id,
        "connectionName": connection_name,
        "connectionReferenceName": connection_name,
        "operationId": operation_id,
    }


definition = {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "$connections": {"defaultValue": {}, "type": "Object"},
        "$authentication": {"defaultValue": {}, "type": "SecureObject"},
    },
    "triggers": {
        "When_a_file_is_created": {
            "type": "OpenApiConnection",
            "recurrence": {"frequency": "Minute", "interval": 5},
            "splitOn": "@triggerOutputs()?['body/value']",
            "conditions": [
                {
                    "expression": "@and(contains(toLower(triggerBody()?['{FilenameWithExtension}']), 'post award dashboard dnnp'), endsWith(toLower(triggerBody()?['{FilenameWithExtension}']), '.xlsx'))"
                }
            ],
            "inputs": {
                "host": host(SP_API, "GetOnNewFileItems", "shared_sharepointonline"),
                "parameters": {
                    "dataset": SITE,
                    "table": "Documents",
                    "folderPath": FOLDER,
                },
            },
        }
    },
    "actions": {
        "Delay": {
            "type": "Wait",
            "inputs": {"interval": {"count": 1, "unit": "Minute"}},
            "runAfter": {},
        },
        "Initialize_updated_count": {
            "type": "InitializeVariable",
            "inputs": {
                "variables": [
                    {"name": "UpdatedCount", "type": "integer", "value": 0}
                ]
            },
            "runAfter": {"Delay": ["Succeeded"]},
        },
        "Create_table": {
            "type": "OpenApiConnection",
            "inputs": {
                "host": host(EXCEL_API, "CreateTable", "shared_excelonlinebusiness"),
                "parameters": {
                    "source": SITE,
                    "drive": "Documents",
                    "file": "@triggerBody()?['{Identifier}']",
                    "TableName": "POActuals",
                    "Range": "=OFFSET(PO!A1,0,0,SUBTOTAL(103,PO!$A:$A),5)",
                },
            },
            "runAfter": {"Delay": ["Succeeded"]},
        },
        "List_rows": {
            "type": "OpenApiConnection",
            "inputs": {
                "host": host(EXCEL_API, "GetItems", "shared_excelonlinebusiness"),
                "parameters": {
                    "source": SITE,
                    "drive": "Documents",
                    "file": "@triggerBody()?['{Identifier}']",
                    "table": "POActuals",
                },
            },
            "runtimeConfiguration": {
                "paginationPolicy": {"minimumItemCount": 25000}
            },
            "runAfter": {"Create_table": ["Succeeded", "Failed"]},
        },
        "Select_PO": {
            "type": "Select",
            "inputs": {
                "from": "@coalesce(body('List_rows')?['value'], json('[]'))",
                "select": {
                    "po": "@trim(string(coalesce(item()?['Po Purchase Document'], '')))",
                    "actual": "@item()?['Actual Cost Obj']",
                },
            },
            "runAfter": {"List_rows": ["Succeeded"]},
        },
        "Get_subcontracts": {
            "type": "OpenApiConnection",
            "inputs": {
                "host": host(SP_API, "GetItems", "shared_sharepointonline"),
                "parameters": {
                    "dataset": SITE,
                    "table": LIST_ID,
                    "$filter": "projectidentifier eq 'A01760' or projectidentifier eq 'A02180'",
                    "$select": "ID,ponumber,projectidentifier,invoicedtodate",
                },
            },
            "runtimeConfiguration": {
                "paginationPolicy": {"minimumItemCount": 5000}
            },
            "runAfter": {
                "Select_PO": ["Succeeded"],
                "Initialize_updated_count": ["Succeeded"],
            },
        },
        "Apply_to_each_subcontract": {
            "type": "Foreach",
            "foreach": "@coalesce(body('Get_subcontracts')?['value'], json('[]'))",
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "actions": {
                "Filter_PO": {
                    "type": "Query",
                    "inputs": {
                        "from": "@body('Select_PO')",
                        "where": "@equals(item()?['po'], trim(string(coalesce(items('Apply_to_each_subcontract')?['ponumber'], ''))))",
                    },
                    "runAfter": {},
                },
                "Has_actual": {
                    "type": "If",
                    "expression": {
                        "and": [
                            {"greater": ["@length(body('Filter_PO'))", 0]},
                            {
                                "equals": [
                                    "@empty(first(body('Filter_PO'))?['actual'])",
                                    False,
                                ]
                            },
                        ]
                    },
                    "actions": {
                        "Update_invoicedtodate": {
                            "type": "OpenApiConnection",
                            "inputs": {
                                "host": host(SP_API, "PatchItem", "shared_sharepointonline"),
                                "parameters": {
                                    "dataset": SITE,
                                    "table": LIST_ID,
                                    "id": "@items('Apply_to_each_subcontract')?['ID']",
                                    "item/invoicedtodate": "@float(first(body('Filter_PO'))?['actual'])",
                                },
                            },
                            "runAfter": {},
                        },
                        "Increment_updated": {
                            "type": "IncrementVariable",
                            "inputs": {"name": "UpdatedCount", "value": 1},
                            "runAfter": {"Update_invoicedtodate": ["Succeeded"]},
                        },
                    },
                    "else": {"actions": {}},
                    "runAfter": {"Filter_PO": ["Succeeded"]},
                },
            },
            "runAfter": {"Get_subcontracts": ["Succeeded"]},
        },
    },
}

envelope = {
    "name": FLOW_GUID,
    "id": f"/providers/Microsoft.Flow/flows/{FLOW_GUID}",
    "type": "Microsoft.Flow/flows",
    "properties": {
        "apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows",
        "displayName": DISPLAY_NAME,
        "description": DESCRIPTION,
        "definition": definition,
        "connectionReferences": {
            "shared_sharepointonline": {
                "connectionName": "shared_sharepointonline",
                "source": "Embedded",
                "id": SP_API,
                "tier": "NotSpecified",
            },
            "shared_excelonlinebusiness": {
                "connectionName": "shared_excelonlinebusiness",
                "source": "Embedded",
                "id": EXCEL_API,
                "tier": "NotSpecified",
            },
        },
        "flowFailureAlertSubscribed": False,
        "isManaged": False,
    },
}

root_manifest = {
    "schema": "1.0",
    "details": {
        "displayName": DISPLAY_NAME,
        "description": DESCRIPTION,
        "createdTime": "2026-10-15T19:45:00.0000000Z",
        "packageTelemetryId": "c4e8a1b2-7d63-4f0a-9e15-2b6a8c0d4f71",
        "creator": "N/A",
        "sourceEnvironment": "",
    },
    "resources": {
        FLOW_GUID: {
            "type": "Microsoft.Flow/flows",
            "suggestedCreationType": "New",
            "creationType": "Existing, New, Update",
            "details": {"displayName": DISPLAY_NAME},
            "configurableBy": "User",
            "hierarchy": "Root",
            "dependsOn": [SP_API_GUID, SP_CONN_GUID, EXCEL_API_GUID, EXCEL_CONN_GUID],
        },
        SP_API_GUID: {
            "id": SP_API,
            "name": "shared_sharepointonline",
            "type": "Microsoft.PowerApps/apis",
            "suggestedCreationType": "Existing",
            "details": {"displayName": "SharePoint"},
            "configurableBy": "System",
            "hierarchy": "Child",
            "dependsOn": [],
        },
        SP_CONN_GUID: {
            "type": "Microsoft.PowerApps/apis/connections",
            "suggestedCreationType": "Existing",
            "creationType": "Existing",
            "details": {"displayName": "SharePoint"},
            "configurableBy": "User",
            "hierarchy": "Child",
            "dependsOn": [SP_API_GUID],
        },
        EXCEL_API_GUID: {
            "id": EXCEL_API,
            "name": "shared_excelonlinebusiness",
            "type": "Microsoft.PowerApps/apis",
            "suggestedCreationType": "Existing",
            "details": {"displayName": "Excel Online (Business)"},
            "configurableBy": "System",
            "hierarchy": "Child",
            "dependsOn": [],
        },
        EXCEL_CONN_GUID: {
            "type": "Microsoft.PowerApps/apis/connections",
            "suggestedCreationType": "Existing",
            "creationType": "Existing",
            "details": {"displayName": "Excel Online (Business)"},
            "configurableBy": "User",
            "hierarchy": "Child",
            "dependsOn": [EXCEL_API_GUID],
        },
    },
}

inner_manifest = {
    "packageSchemaVersion": "1.0",
    "flowAssets": {"assetPaths": [FLOW_GUID]},
}

apis_map = {
    "shared_sharepointonline": SP_API_GUID,
    "shared_excelonlinebusiness": EXCEL_API_GUID,
}
connections_map = {
    "shared_sharepointonline": SP_CONN_GUID,
    "shared_excelonlinebusiness": EXCEL_CONN_GUID,
}

out_dir = Path(__file__).resolve().parent
zip_path = out_dir / "PostAward - DNNP invoiced to date.zip"

files = {
    "manifest.json": root_manifest,
    "Microsoft.Flow/flows/manifest.json": inner_manifest,
    f"Microsoft.Flow/flows/{FLOW_GUID}/definition.json": envelope,
    f"Microsoft.Flow/flows/{FLOW_GUID}/apisMap.json": apis_map,
    f"Microsoft.Flow/flows/{FLOW_GUID}/connectionsMap.json": connections_map,
}

with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for name, payload in files.items():
        zf.writestr(name, json.dumps(payload, ensure_ascii=True, indent=2))

print(zip_path)
print("entries", zipfile.ZipFile(zip_path).namelist())
