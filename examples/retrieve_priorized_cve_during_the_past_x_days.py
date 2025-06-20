# Script to track priority vulnerabilities in one or more groups dating back X days.  
# Output is in the form of an HTML page or CSV table.
from cyberwatch_api import Cyberwatch_Pyhelper
from datetime import datetime, timedelta, timezone
import csv
import urllib3
import warnings

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Filter warnings related to unverified HTTPS requests
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

cyberwatch = Cyberwatch_Pyhelper()

# Here you can select the number of days to be included in the analysis
# By default it is set to 7
# If days=0, all the CVE are taken into account
NUMBER_OF_DAY = datetime.now(timezone.utc) - timedelta(days=7)

GROUPS_TO_INCLUDE = [
    "group1",
    "group2"
]


# Function to retrieve the list of unique assets
def get_all_assets():
    all_assets = []
    seen_hostnames = set()
    page = 1
    per_page = 500

    print(f"[DEBUG] Fetching page {page} of assets...")
    output = cyberwatch.request(
        method="get",
        endpoint="/api/v3/servers",
        body_params={"page": page, "per_page": per_page},
        verify_ssl=False
    )
    assets = next(output).json()

    while assets:
        # Keep only new hostnames
        new_assets = [asset for asset in assets if asset["hostname"] not in seen_hostnames]
        all_assets.extend(new_assets)
        seen_hostnames.update(asset["hostname"] for asset in new_assets)
        print(f"[DEBUG] Page {page} fetched, {len(new_assets)} unique assets added.")

        if len(assets) < per_page:
            print("[DEBUG] Fewer assets than 'per_page', reached the last page.")
            break

        if len(new_assets) == 0:
            print("[DEBUG] No new unique assets found on this page, stopping.")
            break

        page += 1
        print(f"[DEBUG] Fetching page {page} of assets...")
        output = cyberwatch.request(
            method="get",
            endpoint="/api/v3/servers",
            body_params={"page": page, "per_page": per_page},
            verify_ssl=False
        )
        assets = next(output).json()

    print(f"[DEBUG] Total unique assets retrieved: {len(all_assets)}")
    return all_assets

# Function to retrieve prioritized vulnerabilities
def get_latest_prioritized_vulnerabilities(server_id):
    output = cyberwatch.request(
        method="get",
        endpoint=f"/api/v3/vulnerabilities/servers/{server_id}",
        verify_ssl=False
    )
    
    server_data = next(output).json()
    vulnerabilities = {}

    if 'cve_announcements' in server_data:
        for cve in server_data['cve_announcements']:

            # Retrieve only prioritized CVEs
            if not cve.get('prioritized', False):
                continue

            # Compare publication dates with the defined threshold
            published = cve.get('published')
            if published:
                published_date = datetime.fromisoformat(published.replace('Z', '+00:00'))
                if published_date < NUMBER_OF_DAY:
                    product = "Not specified"
                    target_version = "Not specified"

                    # Match with updates to find the associated product and version
                    for update in server_data.get('updates', []):
                        if cve['cve_code'] in update.get('cve_announcements', []):
                            product = update.get('target', {}).get('product', "Not specified")
                            target_version = update.get('target', {}).get('version', "Not specified")
                            break

                    if product not in vulnerabilities:
                        vulnerabilities[product] = []

                    vulnerabilities[product].append({
                        'cve_code': cve.get('cve_code'),
                        'score': cve.get('score'),
                        'environmental_score': cve.get('environmental_score'),
                        'epss': cve.get('epss'),
                        'published_date': published_date.isoformat(),
                        'target_version': target_version,
                        'ignored': cve.get('ignored')
                    })
    else:
        print(f"No vulnerabilities found for server {server_id}")

    return vulnerabilities

# Function to group servers by vulnerability
def group_servers_by_vulnerabilities():
    servers = get_all_assets()  # Use the function to retrieve assets
    consolidated_data = {}

    for server in servers:
        server_id = server.get('id')
        server_name = server.get('hostname', 'Unknown')
        groups = [group['name'] for group in server.get('groups', [])]

        # Only include servers from the defined groups
        if not any(group in GROUPS_TO_INCLUDE for group in groups):
            continue

        vulnerabilities = get_latest_prioritized_vulnerabilities(server_id)
        if not vulnerabilities:
            print(f"Server {server_name} (ID {server_id}) has no prioritized vulnerabilities.")
            continue
        
        # Check if the asset & CVE are already present, otherwise add them to the list
        for product, vuln_list in vulnerabilities.items():
            if product not in consolidated_data:
                consolidated_data[product] = {
                    'prioritized_cve_count': 0,
                    'groups': set(),
                    'servers': set(),
                    'latest_published_date': None,
                    'target_version': "Not specified"
                }

            for cve in vuln_list:
                consolidated_data[product]['prioritized_cve_count'] += 1
                consolidated_data[product]['servers'].add(server_name)
                consolidated_data[product]['groups'].update(groups)

                if (not consolidated_data[product]['latest_published_date'] or
                        cve['published_date'] > consolidated_data[product]['latest_published_date']):
                    consolidated_data[product]['latest_published_date'] = cve['published_date']
                    consolidated_data[product]['target_version'] = cve['target_version']

    print(f"Consolidated data: {consolidated_data}")
    return consolidated_data

# Generate an HTML report with a predefined template filled with the data
def generate_html_report(data, filename="vulnerabilities_report.html"):
    html_content = """
    <html>
    <head>
        <title>Rapport des Vulnérabilités</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
            th { background-color: #f2f2f2; }
            .filter-group { margin-bottom: 10px; }
            .sortable th { cursor: pointer; }
            .hidden { display: none; }
        </style>
        <script>
            function sortTable(n) {
                let table = document.getElementById("vulnTable");
                let rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
                switching = true;
                dir = "asc"; 

                while (switching) {
                    switching = false;
                    rows = table.rows;
                    for (i = 1; i < (rows.length - 1); i++) {
                        shouldSwitch = false;
                        x = rows[i].getElementsByTagName("TD")[n];
                        y = rows[i + 1].getElementsByTagName("TD")[n];
                        if (dir === "asc") {
                            if (Number(x.innerHTML) < Number(y.innerHTML)) {
                                shouldSwitch = true;
                                break;
                            }
                        } else if (dir === "desc") {
                            if (Number(x.innerHTML) > Number(y.innerHTML)) {
                                shouldSwitch = true;
                                break;
                            }
                        }
                    }
                    if (shouldSwitch) {
                        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                        switching = true;
                        switchcount++;
                    } else {
                        if (switchcount === 0 && dir === "asc") {
                            dir = "desc";
                            switching = true;
                        }
                    }
                }
            }

            function toggleServers(id) {
                let element = document.getElementById(id);
                element.classList.toggle('hidden');
            }

            function filterGroup(group) {
                let rows = document.querySelectorAll("#vulnTable tbody tr");
                rows.forEach(row => {
                    row.style.display = group && !row.cells[2].textContent.includes(group) ? "none" : "";
                });
            }
        </script>
    </head>
    <body>
        <h1>Vulnerability Report</h1>
        <div class="filter-group">
            <label>Filtrer par groupe:</label>
            <input type="text" id="groupFilter" onkeyup="filterGroup(this.value)" placeholder="Rechercher un groupe...">
        </div>
        <table id="vulnTable" class="sortable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Produit</th>
                    <th onclick="sortTable(1)">Nombre de CVEs</th>
                    <th>Group</th>
                    <th>Servers</th>
                    <th>Last Publish Date</th>
                    <th>Fix Version</th>
                </tr>
            </thead>
            <tbody>
    """

    # Adding data to the table
    for product, vuln_data in data.items():
        html_content += f"""
        <tr>
            <td>{product}</td>
            <td>{vuln_data['prioritized_cve_count']}</td>
            <td>{', '.join(vuln_data['groups'])}</td>
            <td><button onclick="toggleServers('{product}')">Voir</button></td>
            <td>{vuln_data['latest_published_date']}</td>
            <td>{vuln_data['target_version']}</td>
        </tr>
        """
    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    with open(filename, 'w') as f:
        f.write(html_content)

# Generate a CSV report with a defined structure
def generate_csv_report(data, filename="vulnerabilities_report.csv"):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product', 'Critical CVE Count', 'Groups', 'Impacted Asset Count', 'Latest Publication Date', 'Target Version', 'Impacted Assets']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product, details in data.items():
            group_list = ", ".join(details['groups'])
            server_list = ", ".join(details['servers'])
            server_count = len(details['servers'])
            writer.writerow({
                'Product': product,
                'Critical CVE Count': details['prioritized_cve_count'],
                'Groups': group_list,
                'Impacted Asset Count': server_count,
                'Latest Publication Date': details['latest_published_date'],
                'Target Version': details['target_version'],
                'Impacted Assets': server_list
            })


if __name__ == "__main__":
    try:
        vuln_data = group_servers_by_vulnerabilities()
        generate_html_report(vuln_data)
        generate_csv_report(vuln_data)
        print("\nFiles vulnerabilities_report.html and vulnerabilities_report.csv were successfully generated.")
    except Exception as e:
        print(f"Error: {str(e)}")
