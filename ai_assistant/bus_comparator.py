import plotly.graph_objects as go
from typing import List, Dict, Any

class BusComparator:
    """
    Generates Multi-Dimensional Radar Comparison Charts across Bus Operators.
    Dimensions: Comfort, Punctuality, Cleanliness, Staff Courtesy, Value for Money.
    """

    OPERATOR_METRICS = {
        "SRS Travels": {
            "Comfort": 4.6,
            "Punctuality": 4.7,
            "Cleanliness": 4.5,
            "Staff Courtesy": 4.3,
            "Value for Money": 4.4
        },
        "KPN Travels": {
            "Comfort": 4.2,
            "Punctuality": 4.4,
            "Cleanliness": 4.1,
            "Staff Courtesy": 4.2,
            "Value for Money": 4.7
        },
        "IntrCity SmartBus": {
            "Comfort": 4.9,
            "Punctuality": 4.8,
            "Cleanliness": 4.9,
            "Staff Courtesy": 4.7,
            "Value for Money": 4.2
        },
        "Sharma Transports": {
            "Comfort": 3.9,
            "Punctuality": 4.0,
            "Cleanliness": 3.8,
            "Staff Courtesy": 4.0,
            "Value for Money": 4.8
        }
    }

    @classmethod
    def compare(cls, buses_or_names: Any = None) -> go.Figure:
        """Convenience method accepting list of bus dicts or list of string names."""
        if not buses_or_names:
            return cls.generate_radar_chart()
        if isinstance(buses_or_names, list) and len(buses_or_names) > 0:
            if isinstance(buses_or_names[0], dict):
                names = [b.get("name", "Unknown") for b in buses_or_names]
                return cls.generate_radar_chart(names)
            elif isinstance(buses_or_names[0], str):
                return cls.generate_radar_chart(buses_or_names)
        return cls.generate_radar_chart()

    @classmethod
    def generate_radar_chart(cls, selected_operators: List[str] = None) -> go.Figure:
        categories = ["Comfort", "Punctuality", "Cleanliness", "Staff Courtesy", "Value for Money"]
        operators = selected_operators or ["SRS Travels", "KPN Travels", "IntrCity SmartBus"]

        fig = go.Figure()

        palette = ["#D84E55", "#1565C0", "#2E7D32", "#F57C00"]

        for idx, op in enumerate(operators):
            metrics = cls.OPERATOR_METRICS.get(op, {c: 4.0 for c in categories})
            values = [metrics[c] for c in categories]
            # Close polygon
            values.append(values[0])
            cats_closed = categories + [categories[0]]

            color = palette[idx % len(palette)]
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=cats_closed,
                fill='toself',
                name=op,
                line=dict(color=color, width=2),
                opacity=0.65
            ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[3.0, 5.0],
                    tickfont=dict(size=10, color="#666"),
                    linecolor="#E0E0E0"
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color="#333", family="Arial Black")
                )
            ),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=40, r=40, t=30, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=380
        )
        return fig

