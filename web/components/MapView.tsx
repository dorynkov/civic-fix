"use client";

import Map, { Marker } from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";
import type { Issue } from "@/lib/api";

type Props = { issues: Issue[] };

export default function MapView({ issues }: Props) {
  return (
    <div className="h-64 rounded-xl overflow-hidden border border-slate-800">
      <Map
        initialViewState={{ longitude: 37.618, latitude: 55.751, zoom: 11 }}
        style={{ width: "100%", height: "100%" }}
        mapStyle="https://demotiles.maplibre.org/style.json"
      >
        {issues.map((issue) => (
          <Marker key={issue.id} longitude={issue.longitude} latitude={issue.latitude} anchor="bottom">
            <div className="w-3 h-3 bg-emerald-500 rounded-full border-2 border-white shadow" />
          </Marker>
        ))}
      </Map>
    </div>
  );
}
