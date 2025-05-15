def apply_custom_layout(fig, xaxis_label="X Axis", yaxis_label="Y Axis"):
    fig.update_layout(
        font_family="Courier New",
        font_color="black",
        title_font_family="Times New Roman",
        title_font_color="black",
        coloraxis_colorbar=dict(
            title_font=dict(color="black", family="Courier New", size=14),
            tickfont=dict(color="black", family="Courier New", size=12),
        ),
        xaxis_title=f"<b>{xaxis_label}</b>",
        yaxis_title=f"<b>{yaxis_label}</b>",
        xaxis=dict(
            title_font=dict(color="black", family="Courier New"),
            tickfont=dict(color="black", family="Courier New"),
        ),
        yaxis=dict(
            title_font=dict(color="black", family="Courier New"),
            tickfont=dict(color="black", family="Courier New"),
        ),
    )
    return fig