def apply_custom_layout(fig, xaxis_label="X Axis", yaxis_label="Y Axis", update_trace = True):
    # Update general layout
    fig.update_layout(
        font_family="Courier New",
        font_color="black",
        title_font_family="Times New Roman",
        title_font_color="black",
        title_font_size=20,
        coloraxis_colorbar=dict(
            title_font=dict(color="black", family="Courier New", size=18),
            tickfont=dict(color="black", family="Courier New", size=16),
        ),
        legend=dict(
            font=dict(color="black", family="Courier New"),
            title_font=dict(color="black", family="Courier New", size=18)
        ),
        xaxis_title=f"<b>{xaxis_label}</b>",
        yaxis_title=f"<b>{yaxis_label}</b>",
        xaxis=dict(
            title_font=dict(color="black", family="Courier New", size=18),
            tickfont=dict(color="black", family="Courier New", size=16),
        ),
        yaxis=dict(
            title_font=dict(color="black", family="Courier New", size=18),
            tickfont=dict(color="black", family="Courier New", size=16),
        ),
    )

    # Update inner chart labels (trace text)
    if update_trace:
        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            insidetextanchor='middle',
            textfont=dict(family="Courier New", color="black", size=16)
        )

    return fig
