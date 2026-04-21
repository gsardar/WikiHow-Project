with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add two chart containers after shiftChart3's closing div
old_3grid = '                        <div class="chart-container medium"><canvas id="shiftChart3"></canvas></div>\r\n                    </div>\r\n                    <h5 style="text-align: center; font-family: sans-serif; color: #444; margin-top: 30px;">Table 1:'
new_3grid = '                        <div class="chart-container medium"><canvas id="shiftChart3"></canvas></div>\r\n                    </div>\r\n                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px;">\r\n                        <div class="chart-container medium"><canvas id="shiftChart4"></canvas></div>\r\n                        <div class="chart-container medium"><canvas id="shiftChart5"></canvas></div>\r\n                    </div>\r\n                    <h5 style="text-align: center; font-family: sans-serif; color: #444; margin-top: 30px;">Table 1:'

if old_3grid in html:
    html = html.replace(old_3grid, new_3grid)
    print('Inserted shiftChart4/5 div containers OK')
else:
    print('WARNING: could not find 3grid marker, trying LF...')
    old_3grid_lf = old_3grid.replace('\r\n', '\n')
    if old_3grid_lf in html:
        html = html.replace(old_3grid_lf, new_3grid.replace('\r\n', '\n'))
        print('Inserted with LF OK')
    else:
        idx = html.find('shiftChart3"></canvas>')
        print(f'shiftChart3 at {idx}: {repr(html[idx:idx+300])}')

# 2. Update Table header and rows to include year-by-year + articles
old_table_head = '<th>User Account</th>\r\n                                <th>Start Year</th>\r\n                                <th>Early Contributions (First 2 Years)</th>\r\n                                <th>Later Contributions (Last 2 Years)</th>\r\n                                <th>Measured Shift</th>'
new_table_head = '<th>User (Gender)</th>\r\n                                <th>Year Range / Total</th>\r\n                                <th>Year-by-Year Edits (Domain::Sub-domain)</th>\r\n                                <th>Top Articles Edited</th>\r\n                                <th>Measured Shift</th>'

if old_table_head in html:
    html = html.replace(old_table_head, new_table_head)
    print('Table header updated OK')
else:
    old_table_head_lf = old_table_head.replace('\r\n', '\n')
    if old_table_head_lf in html:
        html = html.replace(old_table_head_lf, new_table_head.replace('\r\n', '\n'))
        print('Table header updated with LF OK')
    else:
        print('WARNING: table head not found')

# 3. Replace old 3-row table body with full 5-user body
old_tbody_start = '<td><strong>Zack R. (Male)</strong></td>'
new_full_tbody = '''<td><strong>Zack R.</strong> (Male)</td>
                                <td>2010&#8211;2023 / 850 edits</td>
                                <td style="font-size:0.82em;line-height:1.8">2010: domestic::baking (150)<br>2015: domestic::baking (200)<br>2019: occ.::mech_eng (300)<br>2023: occ.::mech_eng (200)</td>
                                <td style="font-size:0.82em">Bake-a-Cake (45)<br>Fix-a-Car-Engine (42)</td>
                                <td><span style="color:rgba(52,152,219,1);font-weight:bold">F-coded (1.5) &rarr; M-coded (8.2)</span></td>'''

if old_tbody_start in html:
    old_zack_row = html[html.find(old_tbody_start)-24 : html.find('</tr>', html.find(old_tbody_start))+5]
    new_zack_row = '                            <tr>\r\n                                ' + new_full_tbody + '\r\n                            </tr>'
    html = html.replace(old_zack_row, new_zack_row)
    print('Zack row updated OK')

# Add WRM and Eric rows before </tbody>
old_tbody_end = '                        </tbody>'
new_rows = '''                            <tr>
                                <td><strong>WRM</strong> (Male)</td>
                                <td>2009&#8211;2021 / 105 edits</td>
                                <td style="font-size:0.82em;line-height:1.8">2009: occ.::elec_wiring (3)<br>2011: occ.::elec_wiring (39)<br>2012: domestic::baby_care (15)<br>2018: occ.::elec_wiring (6)<br>2019: occ.::elec_wiring (10)</td>
                                <td style="font-size:0.82em">Become-a-Home-Inspector (6)<br>Ready-Your-Vehicle-for-Hurricane (3)</td>
                                <td><span style="color:rgba(155,89,182,1);font-weight:bold">M (8.0) &rarr; F-bridge (2.1) &rarr; M (7.5) — oscillating</span></td>
                            </tr>
                            <tr>
                                <td><strong>Eric</strong> (Male)</td>
                                <td>2007&#8211;2024 / 96 edits</td>
                                <td style="font-size:0.82em;line-height:1.8">2007: occ.::elec_wiring (10)<br>2012: occ.::elec_wiring (4)<br>2013: policy::health (3)<br>2018: domestic::baking (3)<br>2021: domestic::baby_care (2)<br>2024: occ.::elec_wiring (8)</td>
                                <td style="font-size:0.82em">Lose-Weight (13)<br>Prepare-for-an-Earthquake (10)<br>Tie-a-Tie (8)</td>
                                <td><span style="color:rgba(100,100,180,1);font-weight:bold">Multi-domain / non-monotonic</span></td>
                            </tr>
                        </tbody>'''

html = html.replace(old_tbody_end, new_rows, 1)
print('WRM+Eric rows added OK')

# 4. Add shiftChart4 and shiftChart5 JS before closing </script>
sc_marker = "        options: shiftOptions('Lara M.', colFemale)\n        });\n\n    </script>"
sc_marker_crlf = "        options: shiftOptions('Lara M.', colFemale)\r\n        });\r\n\r\n    </script>"

new_charts_js = """        options: shiftOptions('Lara M.', colFemale)
        });

        // WRM 2009-2021: elec_wiring(occ/M-coded=8) | baby_care(dom/F-coded=2.1) | back to elec_wiring
        new Chart(document.getElementById('shiftChart4'), {
            type: 'line',
            data: {
                labels: [2009, 2011, 2012, 2018, 2019, 2021],
                datasets: [{
                    label: 'WRM (M) \u2013 Oscillating',
                    data: [8.0, 8.0, 2.1, 7.5, 7.5, 7.8],
                    borderColor: 'rgba(155,89,182,0.9)', backgroundColor: 'rgba(155,89,182,0.12)',
                    borderWidth: 3, pointRadius: 5, fill: true, tension: 0.3
                }]
            },
            options: shiftOptions('WRM', 'rgba(155,89,182,0.9)')
        });

        // Eric 2007-2024: elec_wiring M | policy::health neutral | domestic::baking F | baby_care F | back to elec_wiring M
        new Chart(document.getElementById('shiftChart5'), {
            type: 'line',
            data: {
                labels: [2007, 2012, 2013, 2018, 2021, 2024],
                datasets: [{
                    label: 'Eric (M) \u2013 Multi-domain',
                    data: [8.0, 8.0, 4.5, 1.8, 0.9, 8.0],
                    borderColor: 'rgba(230,126,34,0.9)', backgroundColor: 'rgba(230,126,34,0.12)',
                    borderWidth: 3, pointRadius: 5, fill: true, tension: 0.3
                }]
            },
            options: shiftOptions('Eric', 'rgba(230,126,34,0.9)')
        });

    </script>"""

if sc_marker in html:
    html = html.replace(sc_marker, new_charts_js)
    print('shiftChart4/5 JS injected OK (LF)')
elif sc_marker_crlf in html:
    html = html.replace(sc_marker_crlf, new_charts_js.replace('\n', '\r\n'))
    print('shiftChart4/5 JS injected OK (CRLF)')
else:
    idx = html.find("shiftOptions('Lara M.'")
    print(f'Lara shiftOptions at {idx}')
    print(repr(html[idx:idx+150]))

with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved canvas.html')
