import customtkinter as ctk
from tkintermapview import TkinterMapView
import requests
from geocoding import geocode_location
from utils import get_bbox
from export import export_csv
from export_sql import export_sql_file
from poi_types import poi_display_mapping
import sys
import os

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Ermittle den Pfad zur Ressource, egal ob als .py oder als .exe """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)

class POIDataMiner(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("POI-Harvester")
        self.iconbitmap(resource_path("assets/logo.ico"))

        self.after(100, lambda: self.state("zoomed"))
        self.sql_options_visible = False

        # Panels
        self.left_panel = ctk.CTkScrollableFrame(self, width=440)
        self.left_panel.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.middle_panel = ctk.CTkFrame(self)
        self.middle_panel.grid(row=0, column=1, sticky="nswe", padx=5, pady=10)
        self.right_panel = ctk.CTkScrollableFrame(self, width=300)
        self.right_panel.grid(row=0, column=2, sticky="nswe", padx=10, pady=10)

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Map
        self.map = TkinterMapView(self.middle_panel, width=850, height=800, corner_radius=0)
        self.map.pack(fill="both", expand=True)
        self.map.set_position(50.15, 9.1)
        self.map.set_zoom(10)

        # Location + Radius
        ctk.CTkLabel(self.left_panel, text="City or postal code and area").pack(pady=(10, 5))
        self.location_entry = ctk.CTkEntry(self.left_panel, placeholder_text="City or postal code")
        self.location_entry.pack(pady=5)
        self.radius_entry = ctk.CTkEntry(self.left_panel, placeholder_text="Area (km)")
        self.radius_entry.pack(pady=5)

        # Coordinates
        ctk.CTkLabel(self.left_panel, text="Coordinates").pack(pady=(15, 5))
        self.coord_frame = ctk.CTkFrame(self.left_panel)
        self.coord_frame.pack(pady=5)

        self.south = ctk.CTkEntry(self.coord_frame, placeholder_text="South")
        self.west = ctk.CTkEntry(self.coord_frame, placeholder_text="West")
        self.north = ctk.CTkEntry(self.coord_frame, placeholder_text="North")
        self.east = ctk.CTkEntry(self.coord_frame, placeholder_text="East")

        self.south.grid(row=0, column=0, padx=5, pady=5)
        self.west.grid(row=0, column=1, padx=5, pady=5)
        self.north.grid(row=1, column=0, padx=5, pady=5)
        self.east.grid(row=1, column=1, padx=5, pady=5)

        self.query_btn = ctk.CTkButton(self.left_panel, text="Fetch data", command=self.fetch_data)
        self.query_btn.pack(pady=10)

        self.status = ctk.CTkLabel(self.left_panel, text="Ready", wraplength=380)
        self.status.pack(pady=5)

        ctk.CTkLabel(self.left_panel, text="Overpass-API Keys:").pack(pady=(15, 5))
        self.toggle_tags_btn = ctk.CTkButton(self.left_panel, text="Toggle all tags", command=self.toggle_all_tags)
        self.toggle_tags_btn.pack(pady=(5, 0))

        self.tag_box = ctk.CTkScrollableFrame(self.left_panel, width=420, height=300)
        self.tag_box.pack(pady=5)
        self.tag_vars = {}

        # Right Panel POI options
        ctk.CTkLabel(self.right_panel, text="Select POI types").pack(pady=(10, 5))
        self.type_box = ctk.CTkScrollableFrame(self.right_panel, width=280, height=350)
        self.type_box.pack(fill="both", padx=5)
        self.poi_display_mapping = poi_display_mapping
        self.poi_vars = {}

        # Gruppierte POI-Checkboxen mit Überschriften
        grouped_pois = {
            "Amenities": {},
            "Leisure": {},
            "Shops": {},
            "Other": {}
        }

        for label, tags in self.poi_display_mapping.items():
            key = tags[0][0] if tags else ""
            if key == "amenity":
                grouped_pois["Amenities"][label] = tags
            elif key == "leisure":
                grouped_pois["Leisure"][label] = tags
            elif key == "shop":
                grouped_pois["Shops"][label] = tags
            else:
                grouped_pois["Other"][label] = tags

        for category, items in grouped_pois.items():
            if items:
                ctk.CTkLabel(self.type_box, text=category, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10,
                                                                                                 pady=(10, 2))
                for label in sorted(items):
                    var = ctk.BooleanVar(value=False)
                    cb = ctk.CTkCheckBox(self.type_box, text=label, variable=var)
                    cb.pack(anchor="w", padx=20)
                    self.poi_vars[label] = var

        export_frame = ctk.CTkFrame(self.right_panel)
        export_frame.pack(pady=10)

        self.export_btn = ctk.CTkButton(export_frame, text="Export to CSV", command=self.export_csv, state="disabled")
        self.export_btn.grid(row=0, column=0, padx=5)

        self.export_sql_btn = ctk.CTkButton(export_frame, text="Export to SQL", command=self.toggle_sql_options, state="disabled")
        self.export_sql_btn.grid(row=0, column=1, padx=5)

        # Neuer Frame für SQL Optionen - immer im Layout, Inhalt wird ein-/ausgeblendet
        self.sql_frame = ctk.CTkFrame(self.right_panel, width=280)
        self.sql_frame.pack(pady=10, fill="x")

        self.sql_options_label = ctk.CTkLabel(self.sql_frame, text="SQL Export Options")
        self.table_name_entry = ctk.CTkEntry(self.sql_frame, placeholder_text="Table name (optional)")
        self.sql_mapping_box = ctk.CTkScrollableFrame(self.sql_frame, width=280, height=200)
        self.sql_column_map = {}
        self.export_sql_file_btn = ctk.CTkButton(self.sql_frame, text="Save SQL as .sql file", command=self.export_sql_file)

        # Inhalte initial verstecken
        self.sql_options_label.pack_forget()
        self.table_name_entry.pack_forget()
        self.sql_mapping_box.pack_forget()
        self.export_sql_file_btn.pack_forget()

        self.data = []

    def fetch_data(self):
        location = self.location_entry.get().strip()
        radius_str = self.radius_entry.get().strip()

        if location and radius_str:
            try:
                lat, lon = geocode_location(location)
                radius = float(radius_str)
                s, w, n, e = get_bbox(lat, lon, radius)
            except Exception:
                self.status.configure(text="❌ Error in geocoding or radius")
                return
        else:
            try:
                s = float(self.south.get())
                w = float(self.west.get())
                n = float(self.north.get())
                e = float(self.east.get())
            except ValueError:
                self.status.configure(text="❌ Invalid coordinates")
                return

        self.status.configure(text="🔎 Query running...")
        self.update_idletasks()

        self.map.delete_all_polygon()
        self.map.delete_all_marker()
        # Pass bounding box points in (north, west), (south, east) order for fit_bounding_box
        self.map.fit_bounding_box((n, w), (s, e))
        self.map.set_polygon([(n, w), (n, e), (s, e), (s, w)], outline_color="red", border_width=3)

        query_parts = []
        for label, var in self.poi_vars.items():
            if var.get():
                for key, value in self.poi_display_mapping[label]:
                    for typ in ["node", "way", "relation"]:
                        query_parts.append(f'{typ}["{key}"="{value}"]({s},{w},{n},{e});')

        if not query_parts:
            self.status.configure(text="⚠️ No POI types selected.")
            return

        query_body = "\n  ".join(query_parts)
        query = f"""
[out:json][timeout:25];
(
  {query_body}
);
out center;
"""

        try:
            response = requests.post("https://overpass-api.de/api/interpreter", data={"data": query})
            response.raise_for_status()
            self.data = response.json().get("elements", [])
        except Exception:
            self.status.configure(text="❌ Overpass query failed")
            return

        if not self.data:
            self.status.configure(text="⚠️ No entries found.")
            return

        for el in self.data:
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            name = el.get("tags", {}).get("name", "POI")
            if lat and lon:
                self.map.set_marker(lat, lon, text=name)

        all_keys = set()

        # Clear existing tag checkboxes
        all_keys = sorted({key for el in self.data for key in el.get('tags', {}).keys()})
        for widget in self.tag_box.winfo_children():
            widget.destroy()
        self.tag_vars = {}
        for i, key in enumerate(sorted(all_keys)):
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(self.tag_box, text=key, variable=var)
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=5, pady=2)
            self.tag_vars[key] = var

        if self.sql_options_visible:
            self.update_sql_mapping_fields()

        self.status.configure(text=f"✅ {len(self.data)} entries found.")
        self.export_btn.configure(state="normal")
        self.export_sql_btn.configure(state="normal")

        # Eingabefelder ausblenden
        #self.location_entry.pack_forget()
        #self.radius_entry.pack_forget()
        #self.coord_frame.pack_forget()

        # Ergebnis-Checkboxen anzeigen
        if not hasattr(self, 'result_frame'):
            self.result_frame = ctk.CTkScrollableFrame(self.left_panel, width=420, height=300)
            self.result_frame.pack(pady=10)
        else:
            for widget in self.result_frame.winfo_children():
                widget.destroy()
            self.result_frame.pack(pady=10)

        self.result_vars = {}
        for i, el in enumerate(self.data):
            name = el.get("tags", {}).get("name", f"POI {i + 1}")
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(self.result_frame, text=name, variable=var)
            cb.pack(anchor="w", padx=10, pady=2)
            self.result_vars[name] = var

    def toggle_all_tags(self):
        if not self.tag_vars:
            return
        all_selected = all(var.get() for var in self.tag_vars.values())
        for var in self.tag_vars.values():
            var.set(not all_selected)
        if self.sql_options_visible:
            self.update_sql_mapping_fields()

    def toggle_sql_options(self):
        self.sql_options_visible = not self.sql_options_visible
        if self.sql_options_visible:
            self.sql_options_label.pack(pady=(5, 0))
            self.table_name_entry.pack(pady=5)
            self.sql_mapping_box.pack(pady=5)
            self.export_sql_file_btn.pack(pady=(5, 10))
            self.update_sql_mapping_fields()
        else:
            self.sql_options_label.pack_forget()
            self.table_name_entry.pack_forget()
            self.sql_mapping_box.pack_forget()
            self.export_sql_file_btn.pack_forget()

    def update_sql_mapping_fields(self):
        for widget in self.sql_mapping_box.winfo_children():
            widget.destroy()
        self.sql_column_map = {}
        for i, (key, var) in enumerate(self.tag_vars.items()):
            if var.get():
                label = ctk.CTkLabel(self.sql_mapping_box, text=key)
                label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
                entry = ctk.CTkEntry(self.sql_mapping_box, placeholder_text=f"Column name for '{key}'")
                entry.grid(row=i, column=1, padx=5, pady=2)
                self.sql_column_map[key] = entry

    def get_selected_entries(self):
        selected = []
        for el in self.data:
            name = el.get("tags", {}).get("name", "POI")
            # Fallback für POIs ohne Namen (gleicher Name wie Checkbox)
            checkbox_name = name if name in self.result_vars else f"POI {self.data.index(el) + 1}"
            if self.result_vars.get(checkbox_name, ctk.BooleanVar(value=False)).get():
                selected.append(el)
        return selected

    def export_csv(self):
        selected_data = self.get_selected_entries()
        location = self.location_entry.get()
        radius = self.radius_entry.get()
        export_csv(
            data=selected_data,
            tag_vars=self.tag_vars,
            location=location,
            radius=radius,
            type_options=self.poi_vars,
            status_label=self.status
        )

    def export_sql_file(self):
        selected_data = self.get_selected_entries()
        table_name = self.table_name_entry.get().strip()
        export_sql_file(
            data=selected_data,
            tag_vars=self.tag_vars,
            column_map=self.sql_column_map,
            table_name=table_name,
            status_label=self.status,
            location=self.location_entry.get(),
            radius=self.radius_entry.get(),
            type_options=self.poi_vars
        )

if __name__ == "__main__":
    app = POIDataMiner()
    app.mainloop()
