import csv
import tkinter.filedialog

def export_csv(data, tag_vars, location, radius, type_options, status_label):
    selected_keys = [k for k, cb in tag_vars.items() if cb.get() == 1]

    location = location.replace(" ", "_")
    radius = radius.replace(" ", "_")
    selected_types = [tag.replace("=", "-") for tag, var in type_options.items() if var.get()]
    type_str = "_".join(selected_types) if selected_types else "no-types"

    default_filename = f"poi-harvester_{location}_{radius}_{type_str}.csv"
    filepath = tkinter.filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile=default_filename,
        title="Save POI data as CSV"
    )

    if not filepath:
        status_label.configure(text="⚠️ Export cancelled")
        return

    try:
        with open(filepath, "w", newline='', encoding="utf-8") as f:
            #writer = csv.DictWriter(f, fieldnames=["id", "type", "lat", "lon"] + selected_keys)
            writer = csv.DictWriter(f, fieldnames=["lat", "lon"] + selected_keys)
            writer.writeheader()
            for el in data:
                row = {
                    #"id": el.get("id"),
                    #"type": el.get("type"),
                    "lat": el.get("lat") or el.get("center", {}).get("lat"),
                    "lon": el.get("lon") or el.get("center", {}).get("lon"),
                }
                for key in selected_keys:
                    row[key] = el.get("tags", {}).get(key, "")
                writer.writerow(row)
        status_label.configure(text=f"✅ CSV saved as '{filepath}'")
    except Exception:
        status_label.configure(text="❌ Error during CSV export")
