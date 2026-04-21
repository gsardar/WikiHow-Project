import re

with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Fix minigraph overflow (createTemporalTrends y-axis scale)
html = html.replace('''scales: { x: { ticks: { font: { size: 9 }, maxTicksLimit: 5 } }, y: { display: false } }''',
                    '''scales: { x: { ticks: { font: { size: 9 }, maxTicksLimit: 5 } }, y: { display: false, beginAtZero: true, suggestedMax: Math.max(...dO)*1.2 } }''')

# 2. Replace Genuine and Non-Genuine Javascript charts
# Find #qualityGenuineChart and #qualityNonGenuineChart definitions
fig6a_idx = html.find("new Chart(document.getElementById('qualityGenuineChart')")
heatData_idx = html.find("const heatData = [")

if fig6a_idx != -1 and heatData_idx != -1:
    new_charts = """new Chart(document.getElementById('qualityGenuineChart'), {
            type: 'bar',
            data: {
                labels: ['Domestic', 'Occupational', 'Entertainment', 'Policy'],
                datasets: [
                    { label: 'Female', data: [6610000, 1130000, 2950000, 1530000], backgroundColor: colFemale },
                    { label: 'Male', data: [1410000, 6920000, 4320000, 2730000], backgroundColor: colMale },
                    { label: 'Non-Binary', data: [160000, 40000, 210000, 240000], backgroundColor: colNB }
                ]
            },
            options: { 
                responsive: true, maintainAspectRatio: false, 
                scales: { 
                    x: { stacked: true, title: { display: true, text: 'Macro-Topic Continuum', font: { weight: 'bold' } } }, 
                    y: { stacked: true, title: { display: true, text: 'Raw Accepted Edits', font: { weight: 'bold' } }, ticks: { callback: val => formatNumber(val) } } 
                }, 
                plugins: { 
                    datalabels: { display: false } 
                } 
            }
        });

        // FIGURE 7b
        new Chart(document.getElementById('qualityNonGenuineChart'), {
            type: 'bar',
            data: {
                labels: ['Vandalism', 'Maintenance Gate.', 'Spam/Promo', 'Sarcasm', 'Gender Gate.'],
                datasets: [
                    { label: 'Female', data: [120, 600, 200, 50, 120], backgroundColor: colFemale },
                    { label: 'Male', data: [650, 200, 400, 280, 40], backgroundColor: colMale },
                    { label: 'Non-Binary', data: [15, 0, 0, 0, 180], backgroundColor: colNB },
                    { label: 'Unknown', data: [665, 450, 290, 90, 0], backgroundColor: 'rgba(149, 165, 166, 0.8)' }
                ]
            },
            options: { 
                responsive: true, maintainAspectRatio: false, 
                scales: {
                    x: { stacked: true, title: { display: true, text: 'Type of Non-Genuine Edit', font: { weight: 'bold' } }, grid: { display: false } },
                    y: { stacked: true, title: { display: true, text: 'Number of Incidents', font: { weight: 'bold' } } }
                },
                plugins: { 
                    datalabels: { display: false } 
                } 
            }
        });

        // FIGURE 8
        """
    html = html[:fig6a_idx] + new_charts + html[heatData_idx:]


# 3. Handle Ideological shifts
shift_idx = html.find("new Chart(document.getElementById('shiftChart')")
if shift_idx != -1:
    end_shift_idx = html.find("</script>", shift_idx)
    new_shifts = """
        const shiftOptions = {
            responsive: true, maintainAspectRatio: false,
            scales: { y: { min: 0, max: 9, title: { display: true, text: 'Orientation (0=F, 9=M)' } } },
            plugins: {
                datalabels: { display: false },
                annotation: {
                    annotations: {
                        box1: { type: 'box', yMin: 0, yMax: 3, backgroundColor: 'rgba(232, 67, 147, 0.1)', borderWidth: 0, label: { display: true, content: 'Female-Coded', position: 'start' } },
                        box2: { type: 'box', yMin: 6, yMax: 9, backgroundColor: 'rgba(52, 152, 219, 0.1)', borderWidth: 0, label: { display: true, content: 'Male-Coded', position: 'end' } }
                    }
                }
            }
        };

        new Chart(document.getElementById('shiftChart1'), {
            type: 'line',
            data: {
                labels: ['Yr 1', 'Yr 2', 'Yr 3', 'Yr 4'],
                datasets: [{ label: 'Zack R.', data: [1.5, 1.8, 7.5, 8.2], borderColor: colMale, backgroundColor: colMale, borderWidth: 3, marker: 'o', tension: 0.3 }]
            },
            options: shiftOptions
        });

        new Chart(document.getElementById('shiftChart2'), {
            type: 'line',
            data: {
                labels: ['Yr 1', 'Yr 2', 'Yr 3', 'Yr 4'],
                datasets: [{ label: 'AndrejG', data: [8.1, 7.9, 5.2, 4.9], borderColor: colNB, backgroundColor: colNB, borderWidth: 3, marker: 's', tension: 0.3 }]
            },
            options: shiftOptions
        });

        new Chart(document.getElementById('shiftChart3'), {
            type: 'line',
            data: {
                labels: ['Yr 1', 'Yr 2', 'Yr 3', 'Yr 4'],
                datasets: [{ label: 'Lara M.', data: [1.8, 2.1, 4.8, 5.1], borderColor: colFemale, backgroundColor: colFemale, borderWidth: 3, marker: 'triangle', tension: 0.3 }]
            },
            options: shiftOptions
        });

    """
    html = html[:shift_idx] + new_shifts + html[end_shift_idx:]

# 4. Table 1: Case Studies update
old_table = '''<tbody>
                            <tr>
                                <td><strong>Pavel G (Male)</strong></td>
                                <td>2011</td>
                                <td>"How to Build a PC" (8), "How to Wire a Plug" (9)</td>
                                <td>"How to Bake a Cake" (1), "Baby Care Basics" (0)</td>
                                <td><span style="color: #e84393; font-weight: bold;">Male-Coded &rarr;
                                        Female-Coded</span></td>
                            </tr>
                            <tr>
                                <td><strong>Lara M (Female)</strong></td>
                                <td>2014</td>
                                <td>"How to Knit a Scarf" (0), "Applying Makeup" (0)</td>
                                <td>"Software Engineering" (8), "Python" (9)</td>
                                <td><span style="color: #2ecc71; font-weight: bold;">Female-Coded &rarr; Male-Coded</span></td>
                            </tr>
                        </tbody>'''

new_table = '''<tbody>
                            <tr>
                                <td><strong>Zack R. (Male)</strong></td>
                                <td>2010</td>
                                <td>"Bake a Cake" (1)</td>
                                <td>"Fix a Car Engine" (8)</td>
                                <td><span style="color: rgba(52, 152, 219, 1); font-weight: bold;">Female-Coded &rarr; Male-Coded</span></td>
                            </tr>
                            <tr>
                                <td><strong>AndrejG (NB/Male)</strong></td>
                                <td>2018</td>
                                <td>"Wire a Circuit Breaker" (8)</td>
                                <td>"Understand International Law" (5)</td>
                                <td><span style="color: rgba(46, 204, 113, 1); font-weight: bold;">Male-Coded &rarr; Neutral</span></td>
                            </tr>
                            <tr>
                                <td><strong>Lara M. (Female)</strong></td>
                                <td>2015</td>
                                <td>"Administer First Aid" (2)</td>
                                <td>"Run for Local Office" (5)</td>
                                <td><span style="color: rgba(232, 67, 147, 1); font-weight: bold;">Female-Coded &rarr; Neutral</span></td>
                            </tr>
                        </tbody>'''

html = html.replace(old_table, new_table)

with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'w', encoding='utf-8') as f:
    f.write(html)
