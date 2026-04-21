import re

with open('f:/Users/Admin/Documents/WikiHow Project/scratch/js_builder.txt', 'r') as f:
    js_data = f.read()

# Generate the wrapper logic for creating the gradient charts using the inserted data
js_data += """
function sumData(dataObj, categoryList, genderKey) {
    return categoryList.map(cat => {
        if(!dataObj[cat]) return 0;
        return dataObj[cat][genderKey].reduce((a, b) => a + b, 0);
    });
}

// Map the specific labels for the UI and extract the summed amounts
createGradientChart('domWordsChart', domL, {
    f: sumData(domTemporalData, domL, 'f'),
    m: sumData(domTemporalData, domL, 'm'),
    nb: sumData(domTemporalData, domL, 'nb')
});
createTemporalTrends('dom-trends', domL, domTemporalData, true);

createGradientChart('occChart', occL, {
    f: sumData(occTemporalData, occL, 'f'),
    m: sumData(occTemporalData, occL, 'm'),
    nb: sumData(occTemporalData, occL, 'nb')
});
createTemporalTrends('occ-trends', occL, occTemporalData, true);

createGradientChart('entChart', entL, {
    f: sumData(entTemporalData, entL, 'f'),
    m: sumData(entTemporalData, entL, 'm'),
    nb: sumData(entTemporalData, entL, 'nb')
});
createTemporalTrends('ent-trends', entL, entTemporalData, true);

createGradientChart('polChart', polL, {
    f: sumData(polTemporalData, polL, 'f'),
    m: sumData(polTemporalData, polL, 'm'),
    nb: sumData(polTemporalData, polL, 'nb')
});
createTemporalTrends('pol-trends', polL, polTemporalData, true);
"""

# Now replace it in canvas.html
with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We need to replace from "const domL =" to just before "// FIGURE 6a"
start_str = "        const domL = [\n            'Baby Care'"
end_str = "        // FIGURE 6a"

idx1 = html.find(start_str)
idx2 = html.find(end_str)

if idx1 != -1 and idx2 != -1:
    new_html = html[:idx1] + js_data + "\n" + html[idx2:]
    with open('f:/Users/Admin/Documents/WikiHow Project/draft/canvas.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Replaced successfully.")
else:
    print(f"Could not find start idx: {idx1} or end idx: {idx2}")
